# Import libs
from openai import OpenAI 
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

model="gpt-4o-mini"

# Create opeani cliet
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

## Role-played
# completion = client.chat.completions.create(
#     model=model,
#     messages=[
#         {"role":"system","content":"You are a character in a fantasy novel"},
#         {
#             "role":"user",
#             "content":"Describe the setting of the story"}
#     ]
# )

# print(completion.choices[0].message.content)

# Open-ended
completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role":"system","content":"You are a philosopher that gives short and deepful answers"},
        {
            "role":"user",
            "content":"What is the meaning of life?"}
    ]
)

print(completion.choices[0].message.content)
