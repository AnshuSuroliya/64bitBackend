from pydantic import BaseModel


class QuestionRes(BaseModel):
    messages: list = []
    score: list =[]
