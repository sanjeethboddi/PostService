from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from routes import router as book_router
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

config = dotenv_values(".env")

app = FastAPI()

origins = [
    "*",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"],
                # username=config["MONGO_INITDB_ROOT_USERNAME"],
                # password=config["MONGO_INITDB_ROOT_PASSWORD"]
                )
    app.database = app.mongodb_client[config["DB_NAME"]]
    app.auth_service = config["AUTH_SERVICE_URL"]
    app.feed_service = config["FEED_SERVICE_URL"]
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(book_router, tags=["posts"], prefix="")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)