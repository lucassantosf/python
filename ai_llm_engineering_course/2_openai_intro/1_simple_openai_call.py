from openai import OpenAI 
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role":"system","content":"You are an web developer assistant"},
        {"role":"user","content":"""
            Make a hello world! program in five diferents languages.
            Make sure to specify which language each example is.
        """}
    ]
)

print(response.choices[0].message.content)