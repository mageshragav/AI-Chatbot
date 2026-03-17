import os

from pipeline.document_loader import load_all_documents
from pipeline.vector_store import ChromaVectorStore
from pipeline.search import RAGSearch


def run_rag_system():
    # data_dir = "../ejl_data"
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ejl_data'))
    persist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chroma_ejl'))

    # persist_dir = "../chroma_ejl"

    # Initialize Chroma vector store
    store = ChromaVectorStore(persist_dir=persist_dir)

    # Check if Chroma collection already has data
    if store.collection.count() > 0:
        print("[INFO] Existing Chroma DB found. Loading...")
        store.load()
    else:
        print("[INFO] No Chroma DB found. Building new one...")

        docs = load_all_documents(data_dir)
        store.build_documents(docs)

    # Create RAG Pipeline
    rag_search = RAGSearch(
        persist_dir=persist_dir,
        collection_name="ejl_kb_1"
    )

    query = input("Enter your query: ")

    orm_query = rag_search.search_and_summarize(query, top_k=3)

    print("\nGenerated ORM Query:")
    print(orm_query)

    # allowed_locals = {'Product': Product, 'Q': Q}

    # try:
    #     queryset = eval(orm_query, {}, allowed_locals)
    #     queryset = queryset.filter(is_deleted=False)
    # except Exception as e:
    #     return f"Error evaluating ORM query: {e}"

    # print(queryset)


