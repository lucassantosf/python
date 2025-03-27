# Import libs
from openai import OpenAI 
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

model="gpt-4o-mini"

# Create opeani cliet
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role":"system","content":"You are a knowledgeable personal trainer and writer"},
        {
            "role":"user",
            "content":""" 
            Write a 100-word summary of the benefits of exercise, using bullet points.
            """}
    ]
)

print(completion.choices[0].message.content)
