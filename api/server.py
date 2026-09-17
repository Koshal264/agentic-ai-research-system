
from pathlib import Path

from fastapi import FastAPI, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from rq import Queue
from redis import Redis

from agents.supervisor import supervisor_agent
from agents.vision_agent import vision_agent
from rag.pdf_ingest import ingest_pdf


app = FastAPI(
    title="Sovereign Agentic AI Workbench",
    description="Multi-agent AI system for confidential document work",
    version="1.0.0"
)


# ========================================
# CORS
# ========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# REDIS + RQ
# ========================================

redis_connection = Redis(
    host="localhost",
    port=6379
)

queue = Queue(
    "agentic",
    connection=redis_connection
)


# ========================================
# CURRENT PDF
# ========================================
# This stores the PDF uploaded most recently.
#
# Example:
#
# current_pdf = "412KB.pdf"
#
# Questions asked afterwards will use this PDF.
# ========================================

current_pdf = None


# ========================================
# ROOT
# ========================================

@app.get("/")
def root():

    return {
        "status": "server is running",
        "service": "Sovereign Agentic AI Workbench",
        "current_pdf": current_pdf
    }


# ========================================
# NORMAL CHAT
# ========================================

@app.post("/chat")
def chat(
    query: str = Query(
        ...,
        description="User query"
    )
):

    print("========================================")
    print("TEXT CHAT REQUEST")
    print("Query:", query)
    print("Current PDF:", current_pdf)
    print("========================================")


    job = queue.enqueue(
        supervisor_agent,
        query,
        None,
        current_pdf
    )


    return {
        "status": "queued",
        "job_id": job.id,
        "source": current_pdf
    }


# ========================================
# VISION CHAT
# ========================================

@app.post("/vision-chat")
async def vision_chat(
    query: str = Form(...),
    image: UploadFile = File(...)
):

    images_dir = Path("data/images")

    images_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    if not image.filename:

        return {
            "status": "error",
            "message": "No image selected."
        }


    image_path = images_dir / image.filename

    image_bytes = await image.read()


    with open(
        image_path,
        "wb"
    ) as buffer:

        buffer.write(image_bytes)


    print("========================================")
    print("VISION REQUEST RECEIVED")
    print("Query:", query)
    print("Image:", image_path)
    print("Image exists:", image_path.exists())
    print("Image size:", image_path.stat().st_size)
    print("========================================")


    job = queue.enqueue(
        vision_agent,
        str(image_path),
        query
    )


    return {
        "status": "queued",
        "job_id": job.id
    }


# ========================================
# PDF UPLOAD
# ========================================

@app.post("/upload-pdf")
async def upload_pdf(
    pdf: UploadFile = File(...)
):

    global current_pdf


    documents_dir = Path("data/documents")

    documents_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    if not pdf.filename:

        return {
            "status": "error",
            "message": "No PDF selected."
        }


    if not pdf.filename.lower().endswith(".pdf"):

        return {
            "status": "error",
            "message": "Only PDF files are allowed."
        }


    pdf_path = documents_dir / pdf.filename


    pdf_bytes = await pdf.read()


    with open(
        pdf_path,
        "wb"
    ) as buffer:

        buffer.write(pdf_bytes)


    print("========================================")
    print("PDF UPLOAD RECEIVED")
    print("PDF:", pdf_path)
    print("PDF exists:", pdf_path.exists())
    print("PDF size:", pdf_path.stat().st_size)
    print("========================================")


    try:

        result = ingest_pdf(
            str(pdf_path)
        )


        # --------------------------------
        # Remember uploaded PDF
        # --------------------------------

        current_pdf = pdf.filename


        print("========================================")
        print("CURRENT PDF UPDATED")
        print("Current PDF:", current_pdf)
        print("========================================")


        return {
            "status": "success",
            "message": "PDF uploaded and indexed successfully.",
            "current_pdf": current_pdf,
            "result": result
        }


    except Exception as error:

        print("PDF INGESTION ERROR:", error)


        return {
            "status": "error",
            "message": "PDF upload succeeded but ingestion failed.",
            "error": str(error)
        }


# ========================================
# JOB STATUS
# ========================================

@app.get("/job-status")
def get_job_status(
    job_id: str = Query(
        ...,
        description="Job ID"
    )
):

    job = queue.fetch_job(
        job_id
    )


    if job is None:

        return {
            "status": "not_found",
            "result": None
        }


    return {
        "status": job.get_status(),
        "result": job.result
    }

