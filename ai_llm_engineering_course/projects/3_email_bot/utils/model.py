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