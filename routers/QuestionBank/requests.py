from pydantic import BaseModel


class QuestionReq(BaseModel):
    name: str = ""
    skill: str = ""
    experience: int = 1
    prevMessages: list = []
    answer: str = ""
    score: list = []
    totalQuestion: int = 3

class validateQuestionReq(BaseModel):
    skill: str = ""
    question: str = ""
