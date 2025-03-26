# Import libs
from openai import OpenAI 
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Create opeani cliet
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role":"system","content":"You are a geographer"},
        {"role":"user","content":"What is the capital of China?"}
    ]
)

print(response.choices[0].message.content)
