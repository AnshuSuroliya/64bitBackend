from pydantic import BaseModel


class QuestionRes(BaseModel):
    messages: list = []
    score: list =[]
    question:str | None=""
    audio_url:str | None=""
class QResponse(BaseModel):
    question:str | None=""
    audio_url:str | None=""

class EResponse(BaseModel):
    final:str | None=""
    score:int=0
    link:str | None=""
    skill:str | None=""
