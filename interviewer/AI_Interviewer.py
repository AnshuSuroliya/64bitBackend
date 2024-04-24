import os
import random
import time

from fastapi import HTTPException
from openai import AzureOpenAI
import os
import azure.cognitiveservices.speech as speechsdk
client = AzureOpenAI(
    api_key="6746cd17136e40518b23dc57ca42a669",
    api_version="2023-09-15-preview",
    azure_endpoint="https://maje-hi-maje.openai.azure.com/"
)
recognized_texts = []


def on_recognized(evt):
    recognized_text = evt.result.text
    recognized_texts.append(recognized_text)
    print('RECOGNIZED: {}'.format(recognized_text))

def recognize_from_microphone():
    try:
        done = False
        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'),
                                               region=os.environ.get('SPEECH_REGION'))
        speech_config.speech_recognition_language = "en-US"
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        speech_recognizer.recognized.connect(on_recognized)
        print("Speak into Your Microphone")
        speech_recognizer.start_continuous_recognition()
        time.sleep(20)
        speech_recognizer.stop_continuous_recognition()
        str1 = ""
        for ele in recognized_texts:
            str1 += ele
        return str1

        # def stop_cb(evt):
        #     print('CLOSING on {}'.format(evt))
        #     speech_recognizer.stop_continuous_recognition()
        #     nonlocal done
        #     done = True
        #
        # speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
        # speech_recognizer.recognized.connect(on_recognized)
        # speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
        #
        # speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
        #
        # speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
        #
        # speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
        #
        # speech_recognizer.session_stopped.connect(stop_cb)
        #
        # speech_recognizer.canceled.connect(stop_cb)
        #
        # speech_recognizer.start_continuous_recognition()
        # while not done:
        #     time.sleep(.5)
        # # print(recognized_texts)
        # return recognized_texts
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

name =input("Enter YOur Name.")
user_input = input("Enter Your Skill: ")

def start_questioning(messages: list):
    if len(messages)==0:
        messages.append({"role": "system", "content": f" You are Interviewer who is interviewing for beginner level {user_input} skill"})
    messages.append({"role": "user", "content": f"Ask {name} a random question on {user_input} which you haven't asked before."})
    res = client.chat.completions.create(temperature=1, model=mode_name, messages=messages).choices[0].message.content
    messages.append({"role":"system","content":f"{res}"})
    return messages



mode_name = "gpt-4"
print('Sending a test completion job')

Chat_Messages = start_questioning([])
count = 0
while count < 3:
    print(Chat_Messages[len(Chat_Messages) - 1]["content"])

    user_follow_up_answer = recognize_from_microphone()
    recognized_texts = []
    print(user_follow_up_answer)
    Chat_Messages.append({"role": "user", "content": "My answer is : \n " + user_follow_up_answer + " \n is this answer is in the context of previous asked questions give output as yes or no only without extra text"})
    response_follow_up = client.chat.completions.create(temperature=0.3, model=mode_name, messages=Chat_Messages).choices[0].message.content
    if response_follow_up == "No":
        print("Answer is out of context!")
        Chat_Messages.pop()
        Chat_Messages.pop()
        Chat_Messages.pop()
        Chat_Messages = start_questioning(Chat_Messages)

    elif response_follow_up == "Yes":
        count += 1
        Chat_Messages.append({"role":"user","content":f"since it was an answer in context to question. give me a rating out of 10 only without extra text and ask a followup question which is not previously asked and is related to previous conversation sperated by a line break."})
        Chat_Messages.append({"role":"assistant","content" : f"{client.chat.completions.create(temperature=0.3, model=mode_name, messages=Chat_Messages).choices[0].message.content}"})

Chat_Messages.append({"role":"user","content":f"give me the overall rating of skill based on the questions asked and answers provided by me without any extra text and also tell those topics on which i should work upon recommending some udemy courses link"})
feedback = client.chat.completions.create(temperature=0.3, model=mode_name, messages=Chat_Messages).choices[0].message.content
print(feedback)