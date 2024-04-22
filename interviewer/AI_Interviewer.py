import os
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


skills = {(1, "Reactjs"), (2, "Angular"), (3, "Java")}
user_input = input("Enter Your Skill: ")

mode_name = "gpt-4"
print('Sending a test completion job')

messages = [
    {"role": "system", "content": "You are Interviewer who ask different question."},
    {"role": "user", "content": f"Ask me a question on {user_input}"}
]

response = client.chat.completions.create(temperature=0.3, model=mode_name, messages=messages)
print(response.choices[0].message.content)

for _ in range(4):
    user_follow_up_answer = recognize_from_microphone()
    print(user_follow_up_answer)
    messages_follow_up = [
        {"role": "system", "content": "You are Interviewer who ask different question."},
        {"role": "user", "content": f"ask me a follow up question on {user_follow_up_answer}"}
    ]

    response_follow_up = client.chat.completions.create(temperature=0.3, model=mode_name, messages=messages_follow_up)
    print(response_follow_up.choices[0].message.content)
