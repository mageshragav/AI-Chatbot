__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from pipeline.document_loader import load_all_documents
from pipeline.vector_store import ChromaVectorStore
import os

chroma_ejl_multidb = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chroma_ejl_multidb'))


def build_vector_store(
        collection_name: str,
        data_path: str,
        persist_dir: str = chroma_ejl_multidb,
        embedding_model: str = "all-MiniLM-L6-v2"
):
    """ Create and build a chroma vector store from raw documents"""

    print(f"[INFO] Loading documents from: {data_path}")
    documents = load_all_documents(data_path)
    print(f"[INFO] Loaded {len(documents)} documents.")

    store = ChromaVectorStore(
        persist_dir=persist_dir,
        embedding_model=embedding_model,
        collection_name=collection_name
    )

    store.build_documents(documents)

    print("[INFO] Vector store successfully created.")
    return store

schema_data = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ejl_data/schema'))
fewshot_data = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ejl_data/fewshot'))


if __name__ == "__main__":
    # build_vector_store('schema_vec', schema_data)
    build_vector_store('fewshot_vec', fewshot_data)