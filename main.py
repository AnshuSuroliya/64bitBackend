import tempfile

from fastapi import FastAPI, File, UploadFile, HTTPException


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
done = False
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
import azure.cognitiveservices.speech as speechsdk

def recognize_from_file(audio_file_path):
    try:
        print(audio_file_path)
        print(
            "dcdvdv"
        )
        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'),
                                               region=os.environ.get('SPEECH_REGION'))
        speech_config.speech_recognition_language = "en-US"
        print("fdbcv")
        audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        print("fdcvdcv")
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        print("dvfbdc")
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return ("Recognized: {}".format(speech_recognition_result.text))
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-audio-to-text/")
async def convert_audio_to_text(audio: UploadFile = File(...)):
    try:
        print(audio)
        with tempfile.NamedTemporaryFile(delete=False) as tmp_audio:
            tmp_audio.write(await audio.read())
            audio_file_path = tmp_audio.name
        print("dvbcbd")
        text = recognize_from_file(audio_file_path)
        print("dvbdc")
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
