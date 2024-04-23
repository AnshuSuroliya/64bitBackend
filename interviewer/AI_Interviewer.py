import os
import time

from openai import AzureOpenAI
import os
import azure.cognitiveservices.speech as speechsdk
client = AzureOpenAI(
    api_key="6746cd17136e40518b23dc57ca42a669",
    api_version="2023-09-15-preview",
    azure_endpoint="https://maje-hi-maje.openai.azure.com/"
)
def recognize_from_microphone():
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_config.speech_recognition_language="en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")

def start_questioning():
    Starting_messages = [
        {"role": "system", "content": f"You are Interviewer who is interviewing for beginner level {user_input} skill"},
        {"role": "user", "content": f"Ask me a question on {user_input}"}
    ]
    return client.chat.completions.create(temperature=0.3, model=mode_name, messages=Starting_messages).choices[0].message.content

user_input = input("Enter Your Skill: ")

mode_name = "gpt-4"
print('Sending a test completion job')



Starting_messages = [
    {"role": "system", "content": f"You are Interviewer who is interviewing for beginner level {user_input} skill"},
    {"role": "user", "content": f"Ask me a question on {user_input}"}
]
Chat_Messages = Starting_messages
Chat_Messages.append({"role": "system", "content": f"{start_questioning()}"})

for i in range(0,2):

    print(Chat_Messages[len(Chat_Messages) - 1]["content"])

    user_follow_up_answer = recognize_from_microphone()
    print(user_follow_up_answer)

    Chat_Messages.append({"role": "user", "content": f"My answer is : \n {user_follow_up_answer} \n is this answer is in the context of previous asked questions give output as yes or no onlywithout extra text"})
    response_follow_up = client.chat.completions.create(temperature=0.3, model=mode_name, messages=Chat_Messages).choices[0].message.content
    if response_follow_up == "No":
        print("Answer is out of context!")
        Chat_Messages.pop()
        Chat_Messages.pop()
        Chat_Messages.pop()
        Chat_Messages.append({"role": "system", "content": f"{start_questioning()}"})

    elif response_follow_up =="Yes":
        Chat_Messages.append({"role":"user","content":f"since it was an answer in context to question. give me a rating out of 10 only without extra text and ask a followup question sperated by a line break."})
        Chat_Messages.append({"role":"system","content" : f"{client.chat.completions.create(temperature=0.3, model=mode_name, messages=Chat_Messages).choices[0].message.content}"})
