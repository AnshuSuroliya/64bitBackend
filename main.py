from fastapi import FastAPI
from routers import speech_handler_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(speech_handler_router.router)

@app.get("/")
def greet():
    return "Hello"
