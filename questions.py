import os
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="6746cd17136e40518b23dc57ca42a669",
    api_version="2023-09-15-preview",
    azure_endpoint="https://maje-hi-maje.openai.azure.com/"
)

mode_name = "gpt-4"
print('Sending a test completion job')
messages=[
        {"role": "system", "content": "You are AI Interviewer"},
        {"role": "user", "content": "Ask me a question on MachineLearning"}
    ]
response = client.chat.completions.create(temperature=0.3, model=mode_name, messages=messages)
print(response.choices[0].message.content)