import random

from .response import *
from dotenv import dotenv_values
from openai import AzureOpenAI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import azure.cognitiveservices.speech as speechsdk
import os
config = dotenv_values(".env")

client = AzureOpenAI(
    api_key=config["gpt_api_key"],
    api_version=config["gpt_api_version"],
    azure_endpoint=config["gpt_azure_endpoint"]
)
model_name = "gpt-4"

speech_config = speechsdk.SpeechConfig(subscription='fd5dcbcfc3b540b1ab9cdea54a76ac0f', region='eastus')
speech_config.speech_synthesis_voice_name = 'en-US-AvaNeural'
async def textToSpeech(question:str):
    print(question)
    random_number = random.randint(1,1000)
    audio_file_path = f"question_{random_number}.wav"
    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file_path)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    speech_synthesis_result = speech_synthesizer.speak_text_async(question).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        res=QResponse()
        res.question=question
        res.audio_url=f"/audio/question_{random_number}.wav"
        # return {"question": question, "audio_url": f"/audio/question_{random_number}.wav"}
        return res
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        error_details = cancellation_details.error_details if cancellation_details.error_details else "No details available"
        raise HTTPException(status_code=500, detail={"reason": cancellation_details.reason, "details": error_details})

def get_question_count(messages: list):
    count = 0
    for x in messages:
        if x["role"] == "user":
            count = count+1

    if count % 2 == 1:
        count = count + 1
    return count/2


async def ask_first_question(name: str, skill: str, experience: int):
    print(name)
    messages: list = [
        {"role": "system",
         "content": f" You are Interviewer who is interviewing for {skill} skill for nearly {experience} years of experience and who don't ask repetitive questions. also you have to evaluate the answers when asked to do so. while rating the answer you also consider is candidate is giving extra information along with bare minimum information."},
        {"role": "user",
         "content": f"Ask {name} a random question on {skill} which you haven't asked in the above conversation. and only send question as response no extra words in response."}
    ]
    res = client.chat.completions.create(temperature=1, model=model_name, messages=messages).choices[0].message.content
    messages.append({"role": "system", "content": f"{res}"})
    print(res)
    print("fhhhd")
    data = await textToSpeech(res)
    print(data)
    print("dgshd")
    response: QuestionRes = QuestionRes()
    response.messages = messages
    response.score = []
    response.question = data.question
    response.audio_url = data.audio_url
    return response


async def in_context(messages: list, answer: str):
    messages.append({
        "role": "user",
        ##"content": f"My answer is '{answer}' \n check weather this answer is in the context of last question you asked. if its not in the context of previously asked question send 'False' as a response no other word should be in response. else if answer is in context of questions asked the rate the answer out of 10 marks and only send marks in response no extra letters."
        "content": f"My answer is '{answer}' \n check weather this answer is in the context of last question you asked.if in Context send 'answer is in context.' as response and if not send 'answer is not in context.' as response no extra irrelevant text."
    })
    res = client.chat.completions.create(temperature=1, model=model_name, messages=messages).choices[0].message.content
    messages.append({"role": "system", "content": res})
    return messages

async def evaluate(messages:list,skill:str,experience:int):
    messages.append({
        "role": "user",
        "content": f"According to past conversations first give me the score of '{skill}' out of 10 based on the answers given for each questions asked "+
                   "and give the udemy courses link also for the improvement on the areas of that skill" +
                    "give these seperated by space and don't give any extra words"
    })
    res = client.chat.completions.create(temperature=1, model=model_name, messages=messages).choices[0].message.content
    print(res)
    a = res.split(' ')
    score = a[0].split('/')[0]
    link = a[1]
    response = EResponse()
    response.final = "Thank you! Your Interview is now Completed,You can view your results"
    response.score = score
    response.link = link
    response.skill=skill
    return response


async def ask_followup_questions(messages: list, answer: str, scores:list, name:str, skill:str, experience:int):
    print(messages)
    messages = await in_context(messages,answer)
    if messages[-1]["content"] == "answer is not in context.":
        print(messages)
        que = await ask_first_question(name,skill,experience)
        return que
    messages.append({
        "role": "user",
        "content": "According to past conversations ask another followup question which is different to" +
                   "previous asked question but may related to more deeper topic from previous " +
                   "questions and answers. Only send response consisting of question no other extra " +
                   "irrelevant text other than question."
    })
    res = client.chat.completions.create(temperature=1, model=model_name, messages=messages).choices[0].message.content
    messages.append({"role": "system", "content": f"{res}"})
    data = await textToSpeech(res)
    response: QuestionRes = QuestionRes()
    response.messages = messages
    response.score = scores
    response.question = data.question
    response.audio_url = data.audio_url
    print(response)
    return response
