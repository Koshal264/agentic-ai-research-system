
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
    # WITH PDF FILTER
    # ------------------------------------

    results = vector_db.similarity_search(
        query,
        k=k,
        filter={
            "must": [
                {
                    "key": "metadata.source",
                    "match": {
                        "value": source
                    }
                }
            ]
        }
    )

    return results

