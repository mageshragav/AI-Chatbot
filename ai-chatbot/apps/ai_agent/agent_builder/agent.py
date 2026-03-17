__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy

from pipeline.vector_store import ChromaVectorStore
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import List, Optional
from prompts.prompts_v1 import PROMPT_AGENT_BETA, PROMPT_AGENT_BETA_STRUCTURED
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.agents.middleware.tool_call_limit import ToolCallLimitMiddleware
from langchain.agents.middleware.model_call_limit import ModelCallLimitMiddleware

load_dotenv()
AI_API_KEY = os.getenv("AI_API_KEY")
AI_API_BASE_URL = os.getenv("AI_API_BASE_URL")
AI_MODEL = os.getenv("AI_MODEL")

chroma_ejl_multidb = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chroma_ejl_multidb'))

# Two vector store instances
schema_store = ChromaVectorStore(
    persist_dir=chroma_ejl_multidb,
    collection_name="schema_vec"
)

examples_store = ChromaVectorStore(
    persist_dir=chroma_ejl_multidb,
    collection_name="fewshot_vec"
)

class ORMQueryOutput(BaseModel):
    django_orm_code: str
    explanation: str
    models_used: List[str]
    filters_applied: List[str]

@tool
def search_schema_docs(query: str) -> str:
    """
    Fetch and return *only the schema-related documentation* for the given query.
    Use this when the agent needs to understand:
    - Django model definitions
    - Fields and their types
    - Foreign key / many-to-many relationships
    - Business notes relevant to the data model
    """

    # Query schema documents only
    schema_results = schema_store.query(query, top_k=5)
    # print(schema_results)

    if not schema_results:
        return "No schema documents found."

    raw_text = "\n\n".join([r["text"] for r in schema_results])

    # Clean & Extract Schema Section

    lines = raw_text.splitlines()
    cleaned = []

    for line in lines:
        # Skip noisy markdown lines
        if line.strip().startswith(("---", "===", "|", "# **Examples**")):
            continue

        # Skip example query sections
        if "user_query" in line or "orm_query" in line:
            continue

        # Keep only schema-related content
        cleaned.append(line)

    # Final cleaned schema text
    final_text = "\n".join([ln for ln in cleaned if ln.strip()])

    if not final_text.strip():
        return "Schema found, but could not cleanly extract fields."

    return f"[SCHEMA]\n{final_text}".strip()

@tool
def search_examples_docs(query: str) -> str:
    """
    Fetch and return *only the examples-related documentation* for the given query.
    Use this when the agent needs to understand:
    - user query
    - orm query
    examples
    """

    # Query schema documents only
    example_results = examples_store.query(query, top_k=5)
    # print(schema_results)

    if not example_results:
        return "No schema documents found."

    raw_text = "\n\n".join([r["text"] for r in example_results])

    # Clean & Extract Schema Section

    lines = raw_text.splitlines()
    cleaned = []

    for line in lines:
        # Skip noisy markdown lines
        if line.strip().startswith(("---", "===", "|", "# **Examples**")):
            continue

        # # Skip example query sections
        # if "user_query" in line or "orm_query" in line:
        #     continue

        # Keep only schema-related content
        cleaned.append(line)

    # Final cleaned schema text
    final_text = "\n".join([ln for ln in cleaned if ln.strip()])

    if not final_text.strip():
        return "Examples found, but could not cleanly extract fields."

    return f"[EXAMPLES]\n{final_text}".strip()


# model = init_chat_model("gpt-4o-mini")

model = ChatOpenAI(
    model = AI_MODEL,
    api_key= AI_API_KEY,
    base_url=AI_API_BASE_URL,
    temperature=0.3,
    timeout=30,
    max_tokens=1000,
)

# model = ChatOpenAI(
#     model = 'gpt-4o-mini',
#     temperature=0.3,
#     timeout=30,
#     max_tokens=1000,
# )

tool_call_limiter = ToolCallLimitMiddleware(
                    run_limit=7,
                    thread_limit=10,
                    exit_behavior="end"
                )

model_call_limiter = ModelCallLimitMiddleware(
                    thread_limit=10,
                    run_limit=7,
                    exit_behavior="end",
                )

agent = create_agent(
    model=model,
    tools=[search_schema_docs, search_examples_docs],
    response_format=ProviderStrategy(ORMQueryOutput),
    middleware=[tool_call_limiter, model_call_limiter],
    system_prompt= PROMPT_AGENT_BETA_STRUCTURED

)

def get_orm_response(query: str) -> ORMQueryOutput:

    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": query
        }]
    })

    structured = result.get("structured_response")
    # print(result)
    if not structured:
        raise ValueError("No structured response received from agent")

    return structured