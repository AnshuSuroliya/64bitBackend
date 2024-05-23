from fastapi import APIRouter, Depends
from .requests import *
from .question_bank_service import *
from ..authentication.jwt_service import get_current_user

router = APIRouter()


@router.post("/ask")
async def ask_question(req: QuestionReq):
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

@router.post("/chk/IsQuestionReleveant")
async def get_audio(req:validateQuestionReq):
    messages: list = [
        {"role": "user",
         "content": f"tell me if the question: {req.question} is releveant to the skill {req.skill}. if its relevant send only 'True' else send 'False' dont send any other extra text."}
    ]
    res = client.chat.completions.create(temperature=1, model=model_name, messages=messages).choices[0].message.content

    return {"isRelevant":res=="True"}