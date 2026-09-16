from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"


# Embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"}
)


# Load all PDF files
documents = []

for pdf_file in DOCUMENTS_DIR.glob("*.pdf"):
    print(f"Loading PDF: {pdf_file.name}")

    loader = PyPDFLoader(str(pdf_file))
    docs = loader.load()

    documents.extend(docs)


if not documents:
    raise RuntimeError("No PDF found inside data/documents/")


print(f"Total pages loaded: {len(documents)}")


# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)

chunks = text_splitter.split_documents(documents)

print(f"Total chunks created: {len(chunks)}")


# Store chunks in Qdrant
vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
   url="http://qdrant:6333",
    collection_name="sih_agentic_workbench"
)

print("Documents indexed successfully!")