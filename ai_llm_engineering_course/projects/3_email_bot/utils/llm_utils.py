import re
import json 

class LLMUtils:
    def extract_json(self, text):
        start = text.find("[")
        end = text.rfind("]") + 1
        if start != -1 and end != -1:
            return text[start:end]
        return text

    def is_valid_json(self, text):
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            return False

    def extract_json_from_response(self, text):
        # Remove blocos de código markdown (```json ... ```)
        code_blocks = re.findall(r"```(?:json)?(.*?)```", text, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()
        
        # Se não houver blocos markdown, tenta encontrar array JSON diretamente
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            return match.group(0).strip()
        
        raise ValueError("Nenhum JSON encontrado na resposta do modelo.")