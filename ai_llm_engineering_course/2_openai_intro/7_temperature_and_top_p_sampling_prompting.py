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
        {"role":"system","content":"You are a philosopher"},
        {
            "role":"user",
            "content":"Write a creative tagline for the meaning of life"}
    ],
    temperature=0.7,# controls the randomness of the output
    top_p=0.9 # controls the diversity of the output
)

print(completion.choices[0].message.content)
