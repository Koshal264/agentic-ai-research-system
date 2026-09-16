from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore


# Embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"}
)


# Connect to Qdrant
vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    collection_name="sih_agentic_workbench",
    url="http://localhost:6333"
)


# Retrieve relevant documents
def retrieve_documents(query: str, k: int = 4):

    results = vector_db.similarity_search(
        query,
        k=k
    )

    return results