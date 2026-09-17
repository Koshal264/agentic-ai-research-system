from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "data" / "documents"


# =========================================================
# EMBEDDING MODEL
# =========================================================

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={
        "device": "cpu"
    }
)


# =========================================================
# PDF INGESTION
# =========================================================

def ingest_pdf(pdf_path: str):

    print("========================================")
    print("PDF INGESTION STARTED")
    print("PDF:", pdf_path)
    print("========================================")


    # -----------------------------------------------------
    # Check PDF
    # -----------------------------------------------------

    pdf_file = Path(pdf_path)

    if not pdf_file.exists():

        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )


    # -----------------------------------------------------
    # Load PDF
    # -----------------------------------------------------

    loader = PyPDFLoader(
        str(pdf_file)
    )

    documents = loader.load()


    print(
        f"Total pages loaded: {len(documents)}"
    )


    if not documents:

        raise RuntimeError(
            "No content found inside PDF."
        )


    # -----------------------------------------------------
    # Split into chunks
    # -----------------------------------------------------

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400
    )

    chunks = text_splitter.split_documents(
        documents
    )


    print(
        f"Total chunks created: {len(chunks)}"
    )


    # -----------------------------------------------------
    # Add source metadata
    # -----------------------------------------------------

    for chunk in chunks:

        chunk.metadata["source"] = pdf_file.name


    # -----------------------------------------------------
    # Store in Qdrant
    # -----------------------------------------------------

    vector_store = QdrantVectorStore.from_documents(

        documents=chunks,

        embedding=embedding_model,

        url="http://localhost:6333",

        collection_name="sih_agentic_workbench"
    )


    print("========================================")
    print("PDF INGESTION COMPLETED")
    print("PDF:", pdf_file.name)
    print("Chunks:", len(chunks))
    print("========================================")


    return {
        "filename": pdf_file.name,
        "pages": len(documents),
        "chunks": len(chunks)
    }