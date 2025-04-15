from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate 
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model("gpt-4o-mini", model_provider="openai")

system_template = "Translate the following from English to {language}:"

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_template),
        ("user", "{text}"),
    ]
)

prompt = prompt_template.invoke({"language":"italian", "text":"Hello, how are you?"})

response = model.invoke(prompt)
print(response.content)