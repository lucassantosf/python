import ollama

# response = ollama.list()
## Chat Call

# res = ollama.chat(
#     model="llama3.2:1b",
#     messages=[
#         {"role":"user","content":"why the sky is blue?"}
#     ]
# )

#print(res["messages"]["content"])

# With Stream

# res = ollama.chat(
#     model="llama3.2:1b",
#     messages=[
#         {"role":"user","content":"why the sky is blue?"}
#     ],
#     stream=True
# )

# for chunck in res:
#     print(chunck["message"]["content"], end="", flush=True)

## Generate Example
# res = ollama.generate(
#     model="llama3.2:1b",
#     prompt="why the sky is blue?",
# )
# print(ollama.show("llama3.2"))

# Create a new model with modelfile
modelfile = """
FROM llama3.2:1b
SYSTEM You are a very smart assistant who knows everything about ocean. You are very succinct and informative.
PARAMETER temperature 0.1
"""

# Criando o modelo corretamente
ollama.create_model(name="knowitall", modelfile=modelfile)

# Gerando a resposta do modelo criado
res = ollama.generate(model="knowitall", prompt="why is the ocean so salty?")

print(res["response"])
