import openai
import speech_recognition as sr
print(sr.Microphone.list_microphone_names())
from playsound import playsound
from pathlib import Path
from io import BytesIO
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

# Verificar se a chave foi carregada
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")

# Configurar o cliente OpenAI com a chave carregada
openai.api_key = api_key

client = openai.Client()

arquivo_audio = "hello.mp3"

recognizer = sr.Recognizer()

# Identifique o índice correto do microfone (use sr.Microphone.list_microphone_names() se necessário)
microfone_indice = 1  # Índice do dispositivo 'ALC272 Analog'

def grava_audio():
    """Captura áudio do microfone e retorna o áudio gravado"""
    try:
        with sr.Microphone() as source:
            print("Ouvindo...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)
        return audio
    except Exception as e:
        print(f"Erro ao capturar áudio: {e}")
        return None


def transcricao_audio(audio):
    """Transcreve o áudio utilizando o modelo Whisper"""
    try:
        wav_data = BytesIO(audio.get_wav_data())
        wav_data.name = "audio.wav"
        transcricao = client.audio.transcriptions.create(
            model="whisper-1",
            file=wav_data
        )
        return transcricao.text
    except Exception as e:
        print(f"Erro na transcrição do audio {e}")
        return ""
    
def completa_texto(mensagens):
    """Gera uma resposta com base no histórico de mensagens usando GPT 3.5"""
    try:
        resposta = client.chat.completions.create(
            messages=mensagens,
            model="gpt-3.5-turbo-0125",
            max_tokens=1000,
            temperature=0
        )
        return resposta.choices[0].message.content
    except Exception as e:
        print(f"Erro na geração de resposta {e}")
        return "Desculpe, não consegui entender"
    
def cria_audio(texto):
    """Cria um arquivo de áudio a partir do texto usando a API do TTS"""
    if Path(arquivo_audio).exists():
        Path(arquivo_audio).unlink()
    try:
        resposta = client.audio.speech.create(
            model="tts-1",
            voice="echo",
            input=texto
        )
        resposta.write_to_file(arquivo_audio)
    except Exception as e:
        print(f"Erro na criação de áudio {e}")
        
def roda_audio():
    """Reproduz o arquivo de áudio gerado"""
    if Path(arquivo_audio).exists():
        playsound(arquivo_audio)
    else:
        print("Erro: O arquivo de áudio não foi encontrado.")
        
def main():
    """Função principal para executar o assistente de voz"""
    mensagens = []
    while True:
        audio = grava_audio()
        transcricao = transcricao_audio(audio)
        
        if not transcricao:
            print("Não foi possível transcrever o áudio. Tente novamente")
            continue
    
        mensagens.append({"role":"user", "content":transcricao})
        # print(f"User: {mensagens[-1]["content"]}")
        
        resposta_texto = completa_texto(mensagens)
        mensagens.append({"role":"assistant", "content": resposta_texto})
        # print(f"Assistant: {mensagens[-1]["content"]}")
        
        cria_audio(resposta_texto)
        roda_audio()

if __name__ == "__main__":
    main()