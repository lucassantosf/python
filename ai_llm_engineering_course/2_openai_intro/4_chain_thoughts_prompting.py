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
        {"role":"system","content":"You are a math tutor"},
        {
            "role":"user",
            "content":""" 
                Solve this math problem step by step: 
                If John has 5 apples and gives 2 to Mary, how many does he has left?
            """}
    ]
)

print(completion.choices[0].message.content)
