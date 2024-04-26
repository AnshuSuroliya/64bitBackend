import os
import random
import time

from fastapi import HTTPException
from openai import AzureOpenAI
import os
import azure.cognitiveservices.speech as speechsdk

client = AzureOpenAI(
    api_key=os.environ.get("api_key"),
    api_version=os.environ.get("api_version"),
    azure_endpoint=os.environ.get("azure_endpoint")
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


    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

skills = ["Java","Python","ReactJs","JavaScript","Angular",".NET","Vue","C#","C++","Golang","NextJs","NodeJs"]

name =input("Enter Your Name: ")

for i in range(0,12):
    print(f"{i+1} : {skills[i]}")

user_input = int(input("Enter Your Choice: "))
user_input = user_input-1

while(user_input>=len(skills) or user_input<0):
    user_input = int(input("Enter Your Choice: "))
    user_input = user_input - 1

def start_questioning(messages: list):
    if len(messages) == 0:
        messages.append({"role": "system", "content": f" You are Interviewer who is interviewing for {skills[user_input]} skill for experience in the range of 0-2  onths and who don't ask repetitive questions"})
    messages.append({"role": "user", "content": f"Ask {name} a random question on {skills[user_input]} which you haven't asked in the above conversation."})
    res = client.chat.completions.create(temperature=1, model=model_name, messages=messages).choices[0].message.content
    messages.append({"role":"system","content":f"{res}"})
    return messages

model_name = "gpt-4"
print('Sending a test completion job')

Chat_Messages = start_questioning([])
count = 0
while count < 5:
    print(Chat_Messages[len(Chat_Messages) - 1]["content"])
    user_follow_up_answer = recognize_from_microphone()
    recognized_texts = []
    print(user_follow_up_answer)
    Chat_Messages.append({"role": "user", "content": "My answer is : \n " + user_follow_up_answer + " \n is this answer is in the context of previous asked questions give output as yes or no only without extra text"})
    response_follow_up = client.chat.completions.create(temperature=1, model=model_name, messages=Chat_Messages).choices[0].message.content
    if response_follow_up == "No":
        print("Answer is out of context!")
        Chat_Messages.pop()
        Chat_Messages.pop()
        #Chat_Messages.pop()
        Chat_Messages = start_questioning(Chat_Messages)

    elif response_follow_up == "Yes":
        count += 1
        Chat_Messages.append({"role":"user","content": f"since it was an answer in context to question. give me a rating out of 10 only without extra text and ask a followup question which is not previously asked and is related to previous conversation sperated by a line break."})
        Chat_Messages.append({"role":"assistant","content": f"{client.chat.completions.create(temperature=1, model=model_name, messages=Chat_Messages).choices[0].message.content}"})

Chat_Messages.append({"role":"user","content":f"give me the overall rating of skill based on the questions asked and answers provided by me without any extra text and also tell those topics on which i should work upon recommending some udemy courses link"})
feedback = client.chat.completions.create(temperature=1, model=model_name, messages=Chat_Messages).choices[0].message.content
print(feedback)