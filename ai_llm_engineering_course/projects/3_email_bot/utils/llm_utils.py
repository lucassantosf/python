import re
import json 

class LLMUtils:
    def clean_json_string(self, json_str):
        """
        Limpa erros comuns de sintaxe JSON que podem ser gerados pelo LLM.
        
        Args:
            json_str (str): String JSON potencialmente mal formada
            
        Returns:
            str: String JSON corrigida
        """
        if not json_str:
            return json_str
            
        # Substituir ponto e vírgula por vírgula no final de valores
        json_str = re.sub(r'";(\s*})', '"\1', json_str)
        json_str = re.sub(r'";(\s*,)', '",\1', json_str)
        
        # Substituir vírgula extra no final de objetos
        json_str = re.sub(r',(\s*})', r'\1', json_str)
        
        # Substituir aspas simples por aspas duplas
        json_str = re.sub(r"'([^']*)'", r'"\1"', json_str)
        
        # Corrigir chaves sem aspas
        json_str = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', json_str)
        
        # Substituir todos os pontos e vírgulas por vírgulas
        json_str = json_str.replace(";", ",")
        
        return json_str
        
    def robust_json_parse(self, text):
        """
        Tenta analisar JSON de forma robusta, lidando com vários tipos de erros comuns.
        
        Args:
            text (str): Texto contendo JSON potencialmente mal formado
            
        Returns:
            dict ou list: O objeto JSON analisado
            
        Raises:
            ValueError: Se não for possível analisar o JSON
        """
        # Primeiro, tenta extrair o JSON da resposta
        try:
            json_text = self.extract_json_from_response(text)
        except ValueError:
            # Se não conseguir extrair, usa o texto completo
            json_text = text
            
        # Limpa o JSON
        clean_json = self.clean_json_string(json_text)
        
        # Tenta analisar o JSON limpo
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError as e:
            print(f"Erro ao analisar JSON após limpeza inicial: {e}")
            print(f"Posição do erro: linha {e.lineno}, coluna {e.colno}, char {e.pos}")
            
            # Tenta uma limpeza mais agressiva
            clean_json = clean_json.replace(";", ",")
            
            # Tenta corrigir problemas com aspas
            clean_json = re.sub(r'([^\\])(")(.*?)([^\\])(")(\s*:)', r'\1\2\3\4\5\6', clean_json)
            
            # Tenta corrigir problemas com vírgulas
            clean_json = re.sub(r'(}|"])\s*(}|])', r'\1,\2', clean_json)
            
            try:
                return json.loads(clean_json)
            except json.JSONDecodeError as e2:
                print(f"Erro ao analisar JSON após limpeza agressiva: {e2}")
                print(f"Posição do erro: linha {e2.lineno}, coluna {e2.colno}, char {e2.pos}")
                
                # Tenta extrair manualmente os objetos JSON
                try:
                    return self.manual_json_extraction(json_text)
                except Exception as e3:
                    print(f"Falha na extração manual: {e3}")
                    raise ValueError(f"Não foi possível analisar o JSON: {e2}")
                    
    def manual_json_extraction(self, text):
        """
        Tenta extrair manualmente objetos JSON de um texto.
        
        Args:
            text (str): Texto contendo JSON potencialmente mal formado
            
        Returns:
            list: Lista de objetos JSON extraídos
            
        Raises:
            ValueError: Se não for possível extrair objetos JSON
        """
        # Procura por padrões de objetos JSON
        objects = []
        
        # Padrão para encontrar objetos JSON
        pattern = r'{[^{}]*"message_id"[^{}]*"from"[^{}]*"subject"[^{}]*"problem"[^{}]*"solution"[^{}]*}'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            obj_text = match.group(0)
            # Limpa o objeto
            obj_text = self.clean_json_string(obj_text)
            # Substitui pontos e vírgulas por vírgulas
            obj_text = obj_text.replace(";", ",")
            
            try:
                obj = json.loads(obj_text)
                objects.append(obj)
            except json.JSONDecodeError:
                print(f"Não foi possível analisar objeto: {obj_text[:100]}...")
        
        if not objects:
            raise ValueError("Não foi possível extrair objetos JSON")
            
        return objects
        
    def fix_json_at_position(self, json_str, error_line, error_col):
        """
        Tenta corrigir um JSON em uma posição específica onde ocorreu um erro.
        
        Args:
            json_str (str): String JSON com erro
            error_line (int): Linha onde ocorreu o erro
            error_col (int): Coluna onde ocorreu o erro
            
        Returns:
            str: JSON corrigido
        """
        lines = json_str.split('\n')
        
        # Verificar se a linha de erro está dentro dos limites
        if error_line <= 0 or error_line > len(lines):
            return json_str
            
        # Ajustar para índice baseado em zero
        line_idx = error_line - 1
        problematic_line = lines[line_idx]
        
        print(f"Linha problemática ({error_line}): {problematic_line}")
        
        # Se o erro está próximo do final da linha, pode ser um ponto e vírgula
        if error_col > 0 and error_col <= len(problematic_line):
            # Verificar caracteres próximos à posição do erro
            start_pos = max(0, error_col - 10)
            end_pos = min(len(problematic_line), error_col + 10)
            context = problematic_line[start_pos:end_pos]
            print(f"Contexto do erro: ...{context}...")
            
            # Tentar identificar e corrigir problemas comuns
            
            # 1. Substituir ponto e vírgula por vírgula
            if error_col < len(problematic_line) and problematic_line[error_col-1] == ';':
                fixed_line = problematic_line[:error_col-1] + ',' + problematic_line[error_col:]
                lines[line_idx] = fixed_line
                print(f"Substituído ';' por ',' na posição {error_col}")
            
            # 2. Adicionar vírgula faltante após aspas duplas seguidas por espaço e aspas duplas
            elif re.search(r'"(\s*)"', problematic_line[error_col-5:error_col+5]):
                fixed_line = problematic_line[:error_col] + ',' + problematic_line[error_col:]
                lines[line_idx] = fixed_line
                print(f"Adicionada vírgula faltante na posição {error_col}")
                
            # 3. Corrigir aspas simples para aspas duplas
            elif "'" in problematic_line[error_col-5:error_col+5]:
                fixed_line = problematic_line.replace("'", '"')
                lines[line_idx] = fixed_line
                print(f"Substituídas aspas simples por aspas duplas na linha {error_line}")
                
            # 4. Remover caracteres inválidos
            else:
                # Remover caracteres não-ASCII e caracteres de controle
                fixed_line = ''.join(c if (c.isascii() and c.isprintable()) or c in ['\n', '\t', ' '] else '' for c in problematic_line)
                # Substituir qualquer caractere suspeito por vírgula se estiver entre aspas e chaves/colchetes
                fixed_line = re.sub(r'"(\s*[^\s,\{\}\[\]"\']+\s*)["\{\}\[\]]', r'",\2', fixed_line)
                lines[line_idx] = fixed_line
                print(f"Removidos caracteres inválidos na linha {error_line}")
        
        # Reconstruir o JSON
        return '\n'.join(lines)
        
    def emergency_json_fix(self, json_str):
        """
        Método de emergência para tentar corrigir JSON severamente corrompido.
        
        Args:
            json_str (str): String JSON com erro
            
        Returns:
            list: Lista de objetos JSON extraídos ou lista vazia se falhar
        """
        try:
            # Verificar se é um array JSON
            if json_str.strip().startswith('[') and json_str.strip().endswith(']'):
                # Extrair objetos individuais
                objects_text = re.findall(r'{[^{}]*}', json_str)
                
                results = []
                for obj_text in objects_text:
                    # Limpar o objeto
                    clean_obj = self.clean_json_string(obj_text)
                    
                    # Garantir que todas as chaves estão entre aspas duplas
                    clean_obj = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', clean_obj)
                    
                    # Substituir aspas simples por aspas duplas em valores
                    clean_obj = re.sub(r':\s*\'([^\']*)\'', r':"\1"', clean_obj)
                    
                    # Remover vírgulas extras antes de fechar chaves
                    clean_obj = re.sub(r',\s*}', '}', clean_obj)
                    
                    # Tentar analisar o objeto
                    try:
                        obj = json.loads(clean_obj)
                        
                        # Verificar se tem os campos necessários
                        required_fields = ["message_id", "from", "subject", "solution"]
                        if all(field in obj for field in required_fields):
                            results.append(obj)
                    except json.JSONDecodeError:
                        # Ignorar objetos que não podem ser analisados
                        pass
                
                if results:
                    print(f"Extração de emergência bem-sucedida! Encontrados {len(results)} objetos válidos.")
                    return results
            
            # Se não for um array ou não encontrar objetos válidos
            raise ValueError("Não foi possível extrair objetos JSON válidos")
            
        except Exception as e:
            print(f"Falha na extração de emergência: {e}")
            return []
            
    def manual_json_construction(self, text):
        """
        Constrói manualmente objetos JSON a partir de texto não estruturado.
        Útil para casos onde o JSON está severamente corrompido.
        
        Args:
            text (str): Texto contendo informações que podem ser convertidas em JSON
            
        Returns:
            list: Lista de objetos JSON construídos ou lista vazia se falhar
        """
        try:
            # Para seeder_incidents.py - procurar por padrões de título e descrição
            if "title" in text and "description" in text:
                # Procurar por padrões que parecem ser títulos
                title_matches = re.findall(r'"title"\s*:\s*"([^"]+)"', text)
                desc_matches = re.findall(r'"description"\s*:\s*"([^"]+)"', text)
                
                # Se encontramos títulos e descrições
                if title_matches and desc_matches:
                    # Construir objetos JSON manualmente
                    results = []
                    for i in range(min(len(title_matches), len(desc_matches))):
                        obj = {
                            "title": title_matches[i],
                            "description": desc_matches[i]
                        }
                        results.append(obj)
                    
                    if results:
                        print(f"Construção manual bem-sucedida! Encontrados {len(results)} objetos.")
                        return results
            
            # Para seeder_reply.py - procurar por padrões de message_id, from, subject, etc.
            elif "message_id" in text and "from" in text and "subject" in text:
                # Procurar por padrões que parecem ser message_ids
                msgid_matches = re.findall(r'"message_id"\s*:\s*"([^"]+)"', text)
                from_matches = re.findall(r'"from"\s*:\s*"([^"]+)"', text)
                subject_matches = re.findall(r'"subject"\s*:\s*"([^"]+)"', text)
                solution_matches = re.findall(r'"solution"\s*:\s*"([^"]+)"', text)
                
                # Se encontramos os campos necessários
                if msgid_matches and from_matches and subject_matches and solution_matches:
                    # Construir objetos JSON manualmente
                    results = []
                    for i in range(min(len(msgid_matches), len(from_matches), len(subject_matches), len(solution_matches))):
                        obj = {
                            "message_id": msgid_matches[i],
                            "from": from_matches[i],
                            "subject": subject_matches[i],
                            "solution": solution_matches[i]
                        }
                        results.append(obj)
                    
                    if results:
                        print(f"Construção manual bem-sucedida! Encontrados {len(results)} objetos.")
                        return results
            
            # Se não conseguimos construir objetos JSON
            return []
            
        except Exception as e:
            print(f"Falha na construção manual: {e}")
            return []
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
