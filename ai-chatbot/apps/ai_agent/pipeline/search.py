__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pipeline.vector_store import ChromaVectorStore
from prompts.prompts_v1 import ORM_QUERY_PROMPT

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class RAGSearch:

    def __init__(
            self,
            persist_dir: str = "chroma_ejl",
            embedding_model: str = "all-MiniLM-L6-v2",
            llm_model: str = "gpt-4.1-nano-2025-04-14",
            collection_name='ejl_kb_1'
    ):
        self.vectorstore = ChromaVectorStore(
            persist_dir=persist_dir,
            embedding_model=embedding_model,
            collection_name=collection_name
        )

        chroma_index_dir = os.path.join(persist_dir)
        has_existing = (
                os.path.exists(chroma_index_dir)
                and len(os.listdir(chroma_index_dir)) > 0
                and self.vectorstore.collection.count() > 0
        )

        if not has_existing:
            from pipeline.document_loader import load_all_documents
            print("[INFO] No existing Chroma DB found. Building from documents...")
            docs = load_all_documents("ejl_data")
            self.vectorstore.build_documents(docs)
        else:
            print("[INFO] Loading existing Chroma DB...")
            self.vectorstore.load()

        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name=llm_model)
        print(f"[INFO] OpenAI LLM initialized: {llm_model}")

    def generate(self, query: str, top_k: int = 5) -> str:
        """
        1. Retrieve context
        2. Insert into your ORM prompt
        3. Return LLM output
        """
        results = self.vectorstore.query(query, top_k=top_k)

        context = "\n\n".join([r["text"] for r in results])
        if not context:
            return "No relevant documents found."

        prompt = ORM_QUERY_PROMPT.format(query=query, context=context)

        response = self.llm.invoke(prompt)

        return response.content