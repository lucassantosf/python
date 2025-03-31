from openai import OpenAI
import sys 

def simple_chat_without_memory(user_input: str, use_ollama: bool = True) -> str:
    """
    This function demonstrates a chatbot WITHOUT memory/context management.
    Each call is independent and has no knowledge of previous interactions.
    """
    # Initialize OpenAI or Ollama 
    if use_ollama:
        client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        model_name = "llama3.2:1b"  # Verifique se o modelo correto está instalado no Ollama
    else:
        client = OpenAI()
        model_name = "gpt-4o"

    try:
        response = client.chat.completions.create(
            model=model_name, messages=[{"role": "user", "content": user_input}]
        )

        # Debug: Ver o que o Ollama retorna
        # print(f"DEBUG: API Response -> {response}")

        # Ajustar conforme a resposta do Ollama
        if hasattr(response, "choices") and len(response.choices) > 0:
            return response.choices[0].message.content

        return "Error: No response from model."

    except Exception as e: 
        return f"Error: {str(e)}"

def main():
    print("\n=== Simple chatbot WITHOUT Memory ===")
    print("Notice how the bot won't remember anything from previous messages")
    print("\n=== Select model type: ===")
    print("1. OpenAI GPT-4o")
    print("2. Ollama (local)")

    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice in ["1", "2"]:
            break
        print("Please enter either 1 or 2")

    use_ollama = choice == "2"

    print("\n=== Chat Session Started ===")
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'clear' to clear the screen")
    print("Each message is independent - the bot has no memory of previous messages")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["quit", "exit"]:
            print("\nGoodbye!")
            sys.exit()

        if user_input.lower() == "clear":
            print("\033[H\033[J", end="")
            continue

        if not user_input:
            continue

        response = simple_chat_without_memory(user_input, use_ollama)
        print(f"\nBot: {response}")
        print("\n" + "-" * 50)

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        print("\n\nChat session ended by user. Goodbye!")
        sys.exit()
