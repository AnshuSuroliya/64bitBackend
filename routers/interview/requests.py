from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel


class Question(BaseModel):
    question: str = None
    ans: str = None
    score: int = None


class Skill(BaseModel):
    name: str
    experience: int = 1
    tot : int = 3
    questions: list[Question] = None
    score: float = 0
    feedback: str = None


class ScheduleReq(BaseModel):
    owner: str =""
    start_time: datetime = datetime.now()
    duration: int = 30
    end_time: datetime = datetime.now() + timedelta(minutes=duration)
    candidate_name:str
    candidate_email: str
    skills: list[Skill]=[]


