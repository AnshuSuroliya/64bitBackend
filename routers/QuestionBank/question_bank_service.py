from .response import *
from dotenv import dotenv_values
from openai import AzureOpenAI

config = dotenv_values(".env")

client = AzureOpenAI(
    api_key=config["gpt_api_key"],
    api_version=config["gpt_api_version"],
    azure_endpoint=config["gpt_azure_endpoint"]
)
model_name = "gpt-4"


def get_question_count(messages: list):
    count = 0
    for x in messages:
        if x["role"] == "user":
            count = count+1

    if count % 2 == 1:
        count = count + 1

    return count/2


def ask_first_question(name: str, skill: str, experience: int):
    messages: list = [
        {"role": "system",
         "content": f" You are Interviewer who is interviewing for {skill} skill for nearly {experience} years of experience and who don't ask repetitive questions. also you have to evaluate the answers when asked to do so. while rating the answer you also consider is candidate is giving extra information along with bare minimum information."},
        {"role": "user",
         "content": f"Ask {name} a random question on {skill} which you haven't asked in the above conversation. and onle send question as response no extra words in response."}
    ]
    res = client.chat.completions.create(temperature=1, model=model_name, messages=messages).choices[0].message.content
    messages.append({"role": "system", "content": f"{res}"})
    print(res)

    response: QuestionRes = QuestionRes()
    response.messages = messages
    response.score = []

    return response


def in_context(messages: list, answer: str):
    messages.append({
        "role": "user",
        ##"content": f"My answer is '{answer}' \n check weather this answer is in the context of last question you asked. if its not in the context of previously asked question send 'False' as a response no other word should be in response. else if answer is in context of questions asked the rate the answer out of 10 marks and only send marks in response no extra letters."
        "content": f"My answer is '{answer}' \n check weather this answer is in the context of last question you asked.if in Context send 'answer is in context.' as response and if not send 'answer is not in context.' as response no extra irrelevant text."
    })

    res = client.chat.completions.create(temperature=1, model=model_name, messages=messages).choices[0].message.content
    messages.append({"role": "system", "content": res})
    return messages


def ask_followup_questions(messages: list, answer: str, scores:list):

    if messages[-1]["content"] != "answer is not in context.":
        return

    messages.append({
        "role": "user",
        "content": "According to past conversations ask another followup question which is different to" +
                   "previous asked question but may related to more deeper topic from previous " +
                   "questions and answers. Only send response consisting of question no other extra " +
                   "irrelevant text other than question."
    })
    res = client.chat.completions.create(temperature=1, model=model_name, messages=messages).choices[0].message.content
    messages.append({"role": "system", "content": f"{res}"})

    response: QuestionRes = QuestionRes()
    response.messages = messages
    response.score = scores

    return response
