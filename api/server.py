from fastapi import FastAPI, Query
from rq import Queue
from redis import Redis
from agents.supervisor import supervisor_agent
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Sovereign Agentic AI Workbench",
    description="Multi-agent AI system for confidential document work",
    version="1.0.0"
)


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


redis_connection = Redis(
    host="localhost",
    port=6379
)


queue = Queue(
    "agentic",
    connection=redis_connection
)


@app.get("/")
def root():
    return {
        "status": "server is running",
        "service": "Sovereign Agentic AI Workbench"
    }


@app.post("/chat")
def chat(
    query: str = Query(..., description="User query")
):
    job = queue.enqueue(
        supervisor_agent,
        query
    )

    return {
        "status": "queued",
        "job_id": job.id
    }


@app.get("/job-status")
def get_job_status(
    job_id: str = Query(..., description="Job ID")
):
    job = queue.fetch_job(job_id)

    if job is None:
        return {
            "status": "not_found",
            "result": None
        }

    return {
        "status": job.get_status(),
        "result": job.result
    }
# export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES