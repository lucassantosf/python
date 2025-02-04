import yfinance as yf
import openai
from dotenv import load_dotenv
import os
import json

# Carregar variáveis do arquivo .env
load_dotenv()

# Verificar se a chave foi carregada
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")

# Configurar o cliente OpenAI com a chave carregada
openai.api_key = api_key
  
client = openai.Client()

def retorna_cotacao(ticker,periodo="1mo"):
    ticker_obj = yf.Ticker(f"{ticker}.SA")
    hist = ticker_obj.history(period=periodo)["Close"]
    hist.index = hist.index.strftime("%Y-%m-%d")
    hist = round(hist,2)

    # limitando em 30 resultados
    if len(hist) > 30:
        slice_size = int(len(hist) / 30)
        hist = hist.iloc[::-slice_size][::-1]

    return hist.to_json()

tools = [
    {
        "type":"function",
        "function":{
            "name":"retorna_cotacao",
            "description":"Retorna a cotação de ações da Ibovespa",
            "parameters":{
                "type":"object",
                "properties":{
                    "ticker":{
                        "type":"string",
                        "description":"O ticker da ação. EX: BBAS3, BBDC4, etc"
                    },
                    "periodo":{
                        "type":"string",
                        "description":"O periodo retornado dos dados históricos da cotação, \
                            sendo '1mo' equiavalente a um mes, '1d' equivalente a 1 dia \
                            e '1y' eeuivale a um ano e 'ytd' equivale a todos os tempos",
                        "enum":["1d","5d","1mo","6mo","1y","5y","10y","ytd","max"]
                    }
                },
                "required":["hora"]
            }
        }
    }
]

funcao_disponivel = {"retorna_cotacao": retorna_cotacao}

mensagens = [{"role":"user","content":"Qual é a cotação da Vale no ultimo ano?"}]

resposta = client.chat.completions.create(
    messages = mensagens,
    model="gpt-3.5-turbo-0125",
    tools=tools,
    tool_choice="auto"
)

tool_calls = resposta.choices[0].message.tool_calls

if tool_calls:
    mensagens.append(resposta.choices[0].message) 
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = funcao_disponivel[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_return = function_to_call(**function_args)

        mensagens.append({
            "tool_call_id": tool_call.id,
            "role":"tool",
            "name":function_name,
            "content":function_return 
        })

        segunda_resposta = client.chat.completions.create(
            messages=mensagens,
            model="gpt-3.5-turbo-0125"
        )

        mensagens.append(segunda_resposta.choices[0].message)
        print(segunda_resposta.choices[0].message.content)