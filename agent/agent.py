import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from tavily import TavilyClient
from pypdf import PdfReader
from typing import List, Dict, Any
from copilotkit import CopilotKitMiddleware
import json

load_dotenv()

MAIN_SYSTEM_PROMPT = """
You are a tool-using agent.

Rules (hard):
- Never include job details, URLs, or JSON in assistant messages.

Steps:
1) Call internet_search(query)
2) Build 5 job objects
3) Call update_jobs_list(jobs_json) once
4) Call finalize()
5) Output: Found 5 jobs.

If you cannot find 5, still call update_jobs_list(jobs_json) with as many as found.
"""

# MAIN_SYSTEM_PROMPT = (
#     "You must do these steps in order:\n"
#     "1) Call internet_search(query) to get results.\n"
#     "2) Convert results into EXACTLY 5 job objects with keys: company, title, location, url, Good Match.\n"
#     "3) Call update_jobs_list(jobs) exactly once with that 5-item list, wait for confirmation.\n"
#     "4) Do NOT print the JSON in chat.\n"
#     "5) Only after that, reply with: Found 5 jobs.\n"
#     "6) Then Call finalize().\n"
#     "Rules: Never output JSON or tool results in chat. If you cannot find 5, still call update_jobs_list with as many as found.\n"
# )


# MAIN_SYSTEM_PROMPT = (
#     "You are a job search assistant.\n"
#     "Use internet_search to find exactly 5 CURRENT job postings.\n"
#     "Then call update_jobs_list(jobs) with a list of exactly 5 objects.\n"
#     "Each object must have: company, title, location, link, Good Match.\n"
#     "Do NOT print the JSON in chat.\n"
#     "After calling update_jobs_list, reply with ONE short sentence like: 'Found 5 jobs.'\n"
#     "Finally call finalize()."
# )

# MAIN_SYSTEM_PROMPT = (
#     "You are a job search assistant.\n"
#     "Use internet_search to find exactly 5 CURRENT job postings.\n\n"
#     "Return your FINAL assistant message as ONLY this format (no extra text):\n"
#     "<JOBS>\n"
#     "[\n"
#     '  {"company":"...","title":"...","location":"...","link":"https://...","Good Match":"..."},\n'
#     '  {"company":"...","title":"...","location":"...","link":"https://...","Good Match":"..."},\n'
#     '  {"company":"...","title":"...","location":"...","link":"https://...","Good Match":"..."},\n'
#     '  {"company":"...","title":"...","location":"...","link":"https://...","Good Match":"..."},\n'
#     '  {"company":"...","title":"...","location":"...","link":"https://...","Good Match":"..."}\n'
#     "]\n"
#     "</JOBS>\n\n"
#     "Rules:\n"
#     "- Do NOT wrap in markdown fences.\n"
#     "- Do NOT escape quotes.\n"
#     "- Output exactly one <JOBS> block.\n"
#     "- Do not invent jobs.\n"
# )


# MAIN_SYSTEM_PROMPT = (
#     "You are a job application assistant. Do two things:\n"
#     "1) Use the internet_search tool to find exactly 5 CURRENT job postings "
#     "(matching the user's target title, locations, and skills). "
#     "Return them ONLY as JSON in this exact wrapper:\n"
#     "<JOBS>\n"
#     '[{"company":"...","title":"...","location":"...",'
#     '"link":"https://...","Good Match":"one sentence"}, ... five total]\n'
#     "</JOBS>\n"
#     "Rules: The list must be valid JSON (no comments), real links to the job page "
#     "or application page, no duplicates.\n"
#     "Prefer reputable sources (company career pages, Lever, Greenhouse, Ashby, Workday, LinkedIn job detail pages).\n"
#     "2) For each job, write a concise cover letter (≤150 words) with a subject line, "
#     "appended to cover_letters.md under a heading per job using the write_file tool.\n"
#     "Do not invent jobs.\n"
#     "Output in this format:\n\n"
#     "[Job Title] at [Company] in [Location]\n"
#     "Subject Line: [subject]\n"
#     "[body text, max 150 words, no markdown]\n\n"
#     "---\n\n"
#     "[Next job...]\n\n"
#     "Rules:\n"
#     "- Do NOT use markdown or special formatting\n"
#     "- Do NOT mention 'Dear Hiring Manager' if you don't have a contact name\n"
#     "- Tailor each letter to the specific job\n"
#     "- Keep it professional and genuine\n"
#     "- Do NOT output <JOBS> block again after cover letters\n"
#     " - After processing all jobs and letters, ALWAYS call finalize() to end"
#     "- Do NOT call tools after finalize()"
# )

JOB_SEARCH_PROMPT = (
    "Search and select 5 real postings that match the user's title, locations, and skills. "
    "Output ONLY this block format (no extra text before/after the wrapper):\n"
    "<JOBS>\n"
    '[{"company":"...","title":"...","location":"...","link":"https://...","Good Match":"one sentence"},'
    ' {"company":"...","title":"...","location":"...","link":"https://...","Good Match":"one sentence"},'
    ' {"company":"...","title":"...","location":"...","link":"https://...","Good Match":"one sentence"},'
    ' {"company":"...","title":"...","location":"...","link":"https://...","Good Match":"one sentence"},'
    ' {"company":"...","title":"...","location":"...","link":"https://...","Good Match":"one sentence"}]'
    "\n</JOBS>"
    "You must:"
    "- Use internet_search to find relevant jobs."
    "- Do NOT output job listings, JSON, or URLs in messages."
    "- Return everything ONLY by calling the parent tool `update_jobs_list` with a JSON string."
)


COVER_LETTER_PROMPT = (
    "You are a cover letter specialist.\n"
    "The main agent has already selected 5 jobs and stored them in the conversation.\n"
    "For EACH job, write:\n"
    "- A subject line\n"
    "- A concise cover letter (≤200 words) that ties the user's skills/resume to the role\n"
    "Append all output to cover_letters.md using the write_file tool, under a heading per job.\n"
    "Keep writing tight and specific."
)


def parse_pdf_resume(file_path: str) -> str:
    """
    Parse PDF resume using pypdf.

    Args:
        file_path: Path to PDF file

    Returns:
        Extracted text from PDF
    """
    try:
        with open(file_path, "rb") as file:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"[ERROR] Failed to parse PDF: {str(e)}")
        return ""


def extract_skills_from_resume(resume_text: str) -> List[str]:
    """Extract technical skills from resume text"""
    skills_db = {
        "languages": ["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust"],
        "frameworks": ["React", "Next.js", "FastAPI", "Django", "Express"],
        "ai_ml": ["LLM", "RAG", "PyTorch", "TensorFlow", "Transformers"],
        "databases": ["PostgreSQL", "MongoDB", "Redis", "Elasticsearch"],
        "cloud": ["AWS", "GCP", "Azure", "Docker", "Kubernetes"],
    }

    skills = set()
    resume_lower = resume_text.lower()

    for category, skill_list in skills_db.items():
        for skill in skill_list:
            if skill.lower() in resume_lower:
                skills.add(skill)

    return list(skills)


@tool
def update_jobs_list(jobs_json: str) -> Dict[str, Any]:
    """Send jobs list to UI state."""
    jobs = json.loads(jobs_json)
    print(f"[TOOL] update_jobs_list: {len(jobs)} jobs")
    return {"jobs_list": jobs}


# def append_cover_letter(title: str, letter: str) -> Dict[str, str]:
#     """Append cover letter to UI"""
#     print(f"[TOOL] append_cover_letter: {title}")
#     return {"cover_letter_title": title, "cover_letter_append": letter}


@tool
def finalize() -> dict:
    """Signal completion."""
    print("[TOOL] finalize: Job search complete")
    return {"status": "done"}


BAD_URL_SUBSTRINGS = [
    "linkedin.com/jobs/search",
    "linkedin.com/jobs/",
    "builtin.com/jobs",
    "indeed.com",
    "naukri.com",
    "glassdoor.",
    "/jobs/search",
    "/search?",
]


def _is_bad(url: str) -> bool:
    u = (url or "").lower()
    return any(p in u for p in BAD_URL_SUBSTRINGS)


@tool
def internet_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search for jobs using Tavily API. Always returns up to 5 results.
    """
    tavily_key = os.environ.get("TAVILY_API_KEY")
    if not tavily_key:
        raise RuntimeError("TAVILY_API_KEY not set")

    client = TavilyClient(api_key=tavily_key)
    res = client.search(
        query=query,
        max_results=max_results * 3,  # get more, then filter
        include_raw_content=False,
        topic="general",
    )

    trimmed = []
    for r in res.get("results", []):
        url = r.get("url") or ""
        if _is_bad(url):
            continue
        trimmed.append(
            {
                "title": r.get("title"),
                "url": url,
                "content": (r.get("content") or "")[:400],
            }
        )
        if len(trimmed) == max_results:
            break

    print(f"[SEARCH] Returning {len(trimmed)} filtered results")
    print(trimmed)
    return trimmed


def build_agent():
    """Build Deep Agents graph with proper recursion limit"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")

    llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4-turbo"),
        temperature=0.7,
        api_key=api_key,
    )

    tools = [
        internet_search,
        update_jobs_list,
        finalize,
        # append_cover_letter,
    ]

    subagents = [
        {
            "name": "job-search-agent",
            "description": "Finds relevant jobs and outputs <JOBS> JSON.",
            "system_prompt": JOB_SEARCH_PROMPT,
            "tools": [internet_search],
        },
        {
            "name": "cover-letter-writer-agent",
            "description": "Writes cover letters into cover_letters.md.",
            "system_prompt": COVER_LETTER_PROMPT,
        },
    ]

    agent_graph = create_deep_agent(
        model=llm,
        system_prompt=MAIN_SYSTEM_PROMPT,
        tools=tools,
        subagents=subagents,
        middleware=[CopilotKitMiddleware()],
        checkpointer=MemorySaver(),
    )

    print("[AGENT] Deep Agents graph created")
    print(agent_graph)

    return agent_graph.with_config({"recursion_limit": 100})
