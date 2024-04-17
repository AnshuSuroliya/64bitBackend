import tempfile
import time

from fastapi import FastAPI, File, UploadFile, HTTPException


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

recognized_texts = []
def on_recognized(evt):

    recognized_text = evt.result.text
    recognized_texts.append(recognized_text)
    print('RECOGNIZED: {}'.format(recognized_text))
def recognize_from_file(audio_file_path):
    try:
        done = False
        print(audio_file_path)

        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'),
                                               region=os.environ.get('SPEECH_REGION'))
        speech_config.speech_recognition_language = "en-US"

        audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)

        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        def stop_cb(evt):
            print('CLOSING on {}'.format(evt))
            speech_recognizer.stop_continuous_recognition()
            nonlocal done
            done = True

        speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
        speech_recognizer.recognized.connect(on_recognized)
        speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))

        speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
        speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
        speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))

        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)
        speech_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(.5)
        # print(recognized_texts)
        return recognized_texts
        # if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        #     return ("Recognized: {}".format(speech_recognition_result.text))
        # elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        #     print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        # elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        #     cancellation_details = speech_recognition_result.cancellation_details
        #     print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        #     if cancellation_details.reason == speechsdk.CancellationReason.Error:
        #         print("Error details: {}".format(cancellation_details.error_details))
        #         print("Did you set the speech resource key and region values?")
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

        text = recognize_from_file(audio_file_path)
        str1 = ""
        for ele in text:
            str1 += ele
        print(str1)
        return {"text":str1}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
