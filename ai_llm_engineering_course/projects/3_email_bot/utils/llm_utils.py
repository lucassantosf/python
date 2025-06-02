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