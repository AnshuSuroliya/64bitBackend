from fastapi import FastAPI
from routers.speech import speech_handler_router
from routers.QuestionBank import question_bank_router
from routers.authentication import authenticaton_router
from routers.interview import interview_router
from fastapi.middleware.cors import CORSMiddleware

from dotenv import dotenv_values

from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions

from routers.interview.interview_router import get_or_create_interview_container

config = dotenv_values(".env")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

# all the routers in router package
app.include_router(speech_handler_router.router)
app.include_router(question_bank_router.router)
app.include_router(interview_router.router)
app.include_router(authenticaton_router.router)

async def get_or_create_db(db_name):
    try:
        app.database = app.cosmos_client.get_database_client(db_name)
        return await app.database.read()
    except exceptions.CosmosResourceNotFoundError:
        print("Creating database")
        return await app.cosmos_client.create_database(db_name)


@app.on_event("startup")
async def startup_db_client():
    app.cosmos_client = CosmosClient(config["db_uri"], credential = config["db_key"]+"==")
    await get_or_create_db(config["db_name"])
    await get_or_create_interview_container(app)


@app.get("/")
def greet():
    return "Hello"
