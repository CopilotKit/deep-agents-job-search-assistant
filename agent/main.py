from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

from copilotkit import CopilotKitRemoteEndpoint, LangGraphAGUIAgent, Agent as _AgentBase
from copilotkit.integrations.fastapi import add_fastapi_endpoint

from agent import build_agent

load_dotenv()

app = FastAPI()
graph = build_agent()


def _dict_repr_agui(self):
    base = _AgentBase.dict_repr(self)
    base["type"] = "langgraph"
    return base


LangGraphAGUIAgent.dict_repr = _dict_repr_agui

sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAGUIAgent(
            name="post_generator",
            description="Creates a blog post via planning + subagents + filesystem.",
            graph=graph,
        )
    ]
)

add_fastapi_endpoint(app, sdk, "/copilotkit")


@app.get("/healthz")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
