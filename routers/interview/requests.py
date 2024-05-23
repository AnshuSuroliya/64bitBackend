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
    totalQuestion : int = 5
    questions: list[Question] = None
    score: float = 0
    feedback: str = None


class ScheduleReq(BaseModel):
    candidate_name: str=""
    start_time: datetime = datetime.now()
    duration: int = 30
    end_time: datetime = datetime.now() + timedelta(minutes=duration)
    candidate_email: str
    skills: list[Skill]=[]


