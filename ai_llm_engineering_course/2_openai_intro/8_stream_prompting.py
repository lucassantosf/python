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
        {"role":"system","content":"You are a travel blogger"},
        {
            "role":"user",
            "content":"Write a 100-word blog post about your recent trip to Paris. Make sure to give a step-by-step itinerary of your trip"}
    ],
    temperature=0.9,# controls the randomness of the output
    stream=True
)

for chunck in completion:
    if chunck.choices[0].delta.content is not None:
        print(chunck.choices[0].delta.content, end="")
    # print("\n")