from fastapi import APIRouter
from .requests import *
from .question_bank_service import *

router = APIRouter()


@router.post("/ask")
async def ask_question(req: QuestionReq):
    print(req)
    question_count = get_question_count(req.prevMessages)

    if question_count == 0:
        return ask_first_question(req.name, req.skill, req.experience)
    else:
        return evaluate_and_ask_questions(req.prevMessages,req.answer, req.score)
