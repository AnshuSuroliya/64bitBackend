from fastapi import APIRouter,UploadFile,File, HTTPException
import tempfile
from .speech_handler_service import *

router = APIRouter()
@router.post("/convert-audio-to-text/")
async def convert_audio_to_text(audio: UploadFile = File(...)):
    try:
        print(audio)
        with tempfile.NamedTemporaryFile(delete=False) as tmp_audio:
            tmp_audio.write(await audio.read())
            audio_file_path = tmp_audio.name

        text = recognize_from_file(audio_file_path)
        str1 = ""
        for ele in text:
            str1 += ele
        print(str1)
        return {"text": str1}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))