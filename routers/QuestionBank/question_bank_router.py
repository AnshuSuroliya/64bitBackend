from fastapi import APIRouter, Depends
from .requests import *
from .question_bank_service import *
from ..authentication.jwt_service import get_current_user

router = APIRouter()


@router.post("/ask")
async def ask_question(req: QuestionReq,user: dict = Depends(get_current_user)):
    print(req)
    question_count = get_question_count(req.prevMessages)
    if question_count == 0:
        data = await ask_first_question(req.name, req.skill, req.experience)
        return data
    elif question_count == req.totalQuestion:
        data1 = await evaluate(req.prevMessages,req.skill,req.experience)
        return data1
    else :
        data2 = await ask_followup_questions(req.prevMessages,req.answer,req.score,req.name ,req.skill ,req.experience)
        return data2

@router.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(".", filename)
    print(file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)