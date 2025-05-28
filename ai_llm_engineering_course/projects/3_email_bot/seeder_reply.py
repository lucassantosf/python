from openai import OpenAI

class LLMModel:
    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:11434/v1",api_key="ollama")
        self.model_name = "llama3.2:1b"

    def generate_completion(self,messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.0
            )
            return response.choices[0].message.content 
        except Exception as e:
            return f"Error generating response: {str(e)}" 

class IncidentSeeder:
    def __init__(self, llm_model):
        self.llm_model = llm_model

    def generate_incidents_from_problem(self, base_problem):
        prompt = (
            f"Considere o seguinte problema relatado por um usuário de um sistema web: '{base_problem}'.\n"
            f"Crie uma única resposta como se fosse de um técnico especialista respondendo esse problema.\n"
            f"A resposta deve conter:\n"
            f"- Um campo 'description' com o relato do problema em até 200 palavras\n"
            f"- Um campo 'solution' com a proposta de solução técnica em até 200 palavras sendo proativo e pedindo evidencias do problema (print, anexo, etc) se necessário\n"
            f"Retorne SOMENTE o JSON, sem nenhuma explicação adicional, sem formatação em Markdown, e sem comentários.\n"
            f"Formato de exemplo:\n"
            f"""[
                {{
                    "description": "O botão de login não funciona mesmo após inserir as credenciais corretamente.",
                    "solution": "Isso pode estar relacionado a scripts JavaScript não carregados corretamente. Verifique o console do navegador para erros e valide se todos os arquivos estão sendo carregados na rede."
                }}
            ]"""
        ) 

        messages = [
            {
                "role": "system",
                "content": "Você é um gerador de dados fictícios para simular respostas à incidentes de suporte técnico com base em problemas reais",
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.llm_model.generate_completion(messages)
        return response

def main():
    llm_model = LLMModel()
    seeder = IncidentSeeder(llm_model)

    problema_base = "O botão de login não funciona mesmo após inserir as credenciais corretamente."
    incidents = seeder.generate_incidents_from_problem(base_problem=problema_base)

    print(incidents)

if __name__ == "__main__":
    main()
