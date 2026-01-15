import os
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are a blog post generator assistant.

Workflow:

1) Use write_todos to make a short plan (3-6 items).
2) Write a compelling blog post based on the approved plan.
3) Ask for human approval before finalizing.
4) After approval, write the final blog post to a file named post.md using write_file.

Rules:
-- Keep the post engaging and informative.
-- Use markdown formatting as appropriate.
"""


def build_agent():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")

    llm = ChatOpenAI(
        model_name=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
        temperature=0.2,
    )

    # Deep Agents includes planning + filesystem tools (ls/read_file/write_file/edit_file)
    agent = create_deep_agent(
        # tools=[
        #     tools.write_todos,
        #     tools.write_file,
        #     tools.read_file,
        # ],
        # tools=[count_words],  # only pass custom tools here
        system_prompt=SYSTEM_PROMPT,
        model=llm,
        subagents=[],
    )
    return agent


# if __name__ == "__main__":
#     print("🚀 Building agent...")
#     agent = build_agent()

#     print("📝 Testing agent with a request...\n")
#     result = agent.invoke(
#         {"messages": [{"role": "user", "content": "Write a blog post about LangGraph"}]}
#     )

#     print("✅ Agent response:")
#     print(result)
