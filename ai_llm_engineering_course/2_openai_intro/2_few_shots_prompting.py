# Import libs
from openai import OpenAI 
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Create opeani cliet
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role":"system","content":"You are a historer of football"},
        {"role":"user","content":"""
            Translate theses sentences:
            'Pele'->'Best of all time',
            'Lionel Messi'->'Best argentinian player ever',
            'Cristiano Ronaldo'->'Best portuguese player ever',
            Now classify: 'Iker Cassilas'            
        """}
    ]
)

print(completion.choices[0].message.content)
