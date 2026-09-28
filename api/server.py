import os
import uuid
import subprocess
import tempfile

import whisper

from fastapi import (
    FastAPI,
    Depends,
    UploadFile,
    File,
    HTTPException
)
from fastapi.middleware.cors import CORSMiddleware

from redis import Redis
from rq import Queue
from rq.job import Job

from auth.database import init_db
from auth.routes import router as auth_router
from auth.dependencies import get_current_user
from history.routes import router as history_router

from agents.supervisor import supervisor_agent

from rag.pdf_ingest import ingest_pdf


# =========================================================
# WHISPER MODEL
# =========================================================

whisper_model = whisper.load_model("base")


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Sovereign AI Workbench",
    description="Privacy-focused Agentic AI Workbench",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://separately-process-mandate-portrait.trycloudflare.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# DATABASE
# =========================================================

init_db()

app.include_router(auth_router)
app.include_router(history_router)


# =========================================================
# REDIS + RQ
# =========================================================

redis_conn = Redis(
    host="localhost",
    port=6379,
    decode_responses=False
)

task_queue = Queue(
    "agentic",
    connection=redis_conn
)


# =========================================================
# CURRENT PDF
# =========================================================

current_pdf = None


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Sovereign AI Workbench API is running",
        "status": "online"
    }


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
def chat(
    query: str,
    current_user: dict = Depends(get_current_user)
):

    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    job = task_queue.enqueue(
        supervisor_agent,
        query,
        None,
        current_pdf
    )

    return {
        "status": "queued",
        "job_id": job.id,
        "source": current_pdf,
        "user": current_user["username"]
    }


# =========================================================
# VISION CHAT
# =========================================================

@app.post("/vision-chat")
async def vision_chat(
    query: str,
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):

    if not image.filename:
        raise HTTPException(
            status_code=400,
            detail="Image file is required"
        )

    extension = os.path.splitext(
        image.filename
    )[1]

    filename = f"{uuid.uuid4()}{extension}"

    temp_dir = tempfile.gettempdir()

    image_path = os.path.join(
        temp_dir,
        filename
    )

    contents = await image.read()

    with open(image_path, "wb") as f:
        f.write(contents)

    job = task_queue.enqueue(
        supervisor_agent,
        query,
        image_path,
        None
    )

    return {
        "status": "queued",
        "job_id": job.id,
        "user": current_user["username"]
    }


# =========================================================
# VOICE CHAT - FULLY LOCAL WHISPER
# =========================================================

@app.post("/voice-chat")
async def voice_chat(
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):

    if not audio.filename:
        raise HTTPException(
            status_code=400,
            detail="Audio file is required"
        )

    temp_dir = tempfile.gettempdir()

    input_path = os.path.join(
        temp_dir,
        f"{uuid.uuid4()}_{audio.filename}"
    )

    wav_path = os.path.join(
        temp_dir,
        f"{uuid.uuid4()}.wav"
    )

    # -----------------------------------------------------
    # Save uploaded audio
    # -----------------------------------------------------

    audio_data = await audio.read()

    with open(input_path, "wb") as f:
        f.write(audio_data)

    # -----------------------------------------------------
    # Convert browser audio to WAV
    # -----------------------------------------------------

    try:

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-ar",
                "16000",
                "-ac",
                "1",
                wav_path
            ],
            check=True,
            capture_output=True
        )

    except subprocess.CalledProcessError:

        if os.path.exists(input_path):
            os.remove(input_path)

        raise HTTPException(
            status_code=500,
            detail="Audio conversion failed"
        )

    # -----------------------------------------------------
    # LOCAL WHISPER TRANSCRIPTION
    # -----------------------------------------------------

    try:

        result = whisper_model.transcribe(
            wav_path,
            fp16=False
        )

        query = result["text"].strip()

        if not query:

            raise HTTPException(
                status_code=400,
                detail="Could not understand the audio"
            )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Local speech recognition failed: {str(e)}"
        )

    finally:

        if os.path.exists(input_path):
            os.remove(input_path)

        if os.path.exists(wav_path):
            os.remove(wav_path)

    # -----------------------------------------------------
    # SEND TRANSCRIBED QUERY TO LOCAL WORKER
    # -----------------------------------------------------

    job = task_queue.enqueue(
        supervisor_agent,
        query,
        None,
        None,
        True
    )

    return {
        "status": "queued",
        "job_id": job.id,
        "transcript": query,
        "user": current_user["username"]
    }


# =========================================================
# PDF UPLOAD
# =========================================================

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):

    global current_pdf

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="PDF file is required"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    temp_dir = tempfile.gettempdir()

    pdf_path = os.path.join(
        temp_dir,
        f"{uuid.uuid4()}.pdf"
    )

    contents = await file.read()

    with open(pdf_path, "wb") as f:
        f.write(contents)

    try:

        ingest_pdf(pdf_path)

        current_pdf = pdf_path

    except Exception as e:

        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        raise HTTPException(
            status_code=500,
            detail=f"PDF ingestion failed: {str(e)}"
        )

    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename,
        "source": current_pdf,
        "user": current_user["username"]
    }


# =========================================================
# JOB STATUS
# =========================================================

@app.get("/job-status")
def job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):

    try:

        job = Job.fetch(
            job_id,
            connection=redis_conn
        )

    except Exception:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    if job.is_finished:

        return {
            "status": "finished",
            "result": job.result
        }

    if job.is_failed:

        return {
            "status": "failed",
            "result": "Task failed"
        }

    return {
        "status": "processing"
    }