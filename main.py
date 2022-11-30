from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from routes import router as book_router
import uvicorn

config = dotenv_values(".env")

app = FastAPI()

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"],
                # username=config["MONGO_INITDB_ROOT_USERNAME"],
                # password=config["MONGO_INITDB_ROOT_PASSWORD"]
                )
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(book_router, tags=["profiles"], prefix="")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)