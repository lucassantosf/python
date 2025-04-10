import ollama

response = ollama.list()

# 1. Chat Call
res = ollama.chat(
    model="llama3.2:1b",
    messages=[
        {"role":"user","content":"why the sky is blue?"}
    ]
)
print(res["message"]["content"])
# 1. END Chat Call

# 2. With Stream
# res = ollama.chat(
#     model="llama3.2:1b",
#     messages=[
#         {"role":"user","content":"why the sky is blue?"}
#     ],
#     stream=True
# )

# for chunck in res:
#     print(chunck["message"]["content"], end="", flush=True)
# 2. END With Stream

# 3. Generate Example
# res = ollama.generate(
#     model="llama3.2:1b",
#     prompt="why the sky is blue?",
# )
# print(ollama.show("llama3.2:1b"))
# print(res['response'])
# 3. END Generate Example

# 4. Create a new model with modelfile (NOT WORKING - CAUSE THE CREATE_MODEL IS NOT A FUNTION)
# modelfile = """
# FROM llama3.2:1b
# SYSTEM You are a very smart assistant who knows everything about ocean. You are very succinct and informative.
# PARAMETER temperature 0.1
# """

# # Criando o modelo corretamente
# ollama.create_model(name="knowitall", modelfile=modelfile)

# # Gerando a resposta do modelo criado
# res = ollama.generate(model="knowitall", prompt="why is the ocean so salty?")

# print(res["response"])
# 4. END Create a new model with modelfile
