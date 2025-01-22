from dotenv import load_dotenv
import os
import openai 
from colorama import Fore,Style, init 

# Carregar variáveis do arquivo .env
load_dotenv()

# Verificar se a chave foi carregada
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")

# Configurar o cliente OpenAI com a chave carregada
openai.api_key = api_key

# Criar client do OpenAi
client = openai.Client()

# Inicializar o colorama
init(autoreset=True)

def geracao_texto(mensagens):
    resposta = client.chat.completions.create(
        messages=mensagens,
        model="gpt-3.5-turbo-0125",
        max_tokens=100,
        temperature=0,
        stream=True
    )
    print(f"{Fore.CYAN}Bot: ", end="")
    texto_completo = ""
    for resposta_stream in resposta:
        texto = resposta_stream.choices[0].delta.content
        if texto:
            print(texto, end="")
            texto_completo += texto 
    print()
    mensagens.append({"role":"assistant","content": texto_completo})
    return mensagens

if __name__ == "__main__":
    print(f"{Fore.YELLOW}Bem Vindo ao Chatbot")
    mensagens = []
    while True:
        in_user = input(f"{Fore.GREEN}User: {Style.RESET_ALL}")
        mensagens.append({"role":"user","content":in_user})
        mensagens = geracao_texto(mensagens)