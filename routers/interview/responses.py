from datetime import datetime, timedelta
from pydantic import BaseModel


class Question(BaseModel):
    question: str
    ans: str | None
    score: int = 0


class Skill(BaseModel):
    name: str
    experience: int = 1
    questions: list[Question] | None
    score: float = 0
class InterviewScheduleResponse(BaseModel):
    owner: str
    start_time: datetime = datetime.now()
    duration: int = 30
    end_time: datetime = datetime.now()
    candidate_email: str
    skills: list[Skill]

class IResponse(BaseModel):
    candidate_name:str | None=""
    skill_name:str | None=""
    experience:int=1