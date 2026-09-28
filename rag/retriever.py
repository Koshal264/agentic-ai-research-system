from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore


# ========================================
# EMBEDDING MODEL
# ========================================

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={
        "device": "cpu"
    }
)


# ========================================
# QDRANT
# ========================================

vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    collection_name="sih_agentic_workbench",
    url="http://localhost:6333"
)


# ========================================
# RETRIEVE DOCUMENTS
# ========================================

def retrieve_documents(
    query: str,
    k: int = 4,
    source: str = None
):

    # ------------------------------------
    # WITHOUT PDF FILTER
    # ------------------------------------

    if not source:
        return vector_db.similarity_search(
            query,
            k=k
        )

    # ------------------------------------
    # PDF NAME FROM TEMP PATH
    # ------------------------------------

    source_name = source.split("/")[-1]

    # ------------------------------------
    # SEARCH USING STORED PDF NAME
    # ------------------------------------

    results = vector_db.similarity_search(
        query,
        k=k,
        filter={
            "must": [
                {
                    "key": "metadata.source",
                    "match": {
                        "value": source_name
                    }
                }
            ]
        }
    )

    return results
# python -m uvicorn api.server:app --host 127.0.0.1 --port 8000
# ollama run gemma3:4b
# ollama serve

# worker command

# cd /Users/koshalmehra/New_project
# source venv/bin/activate
# export HF_HUB_OFFLINE=1
# export TRANSFORMERS_OFFLINE=1
# export HF_DATASETS_OFFLINE=1
# export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
# python -m worker.main