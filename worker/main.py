from redis import Redis
from rq import Worker


redis_connection = Redis(
    host="localhost",
    port=6379
)


if __name__ == "__main__":

    worker = Worker(
        ["agentic"],
        connection=redis_connection
    )

    print("Agentic worker started...")

    worker.work()
    # uvicorn api.server:app --reload
#     cd /Users/koshalmehra/New_project
# source venv/bin/activate
# # python -m worker.main