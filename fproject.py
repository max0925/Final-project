import os
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

messages = [{"role": "assistant", "content": "How can I help?"}]


def display_chat_history(messages):
    for message in messages:
        print(f"{message['role'].capitalize()}: {message['content']}")


def get_assistant_response(messages):
    r = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": m["role"], "content": m["content"]} for m in messages],
    )
    response = r.choices[0].message.content
    return response


while True:
    display_chat_history(messages)
    
    prompt = input("User: ")
    messages.append({"role": "user", "content": prompt})
    
    response = get_assistant_response(messages)
    messages.append({"role": "assistant", "content": response})
    