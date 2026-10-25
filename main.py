"""Chapter 14 console application for Visual Studio 2026."""
import sys
from ollama import ResponseError
from agent import DatabaseAgent
from database import initialize_database
from settings import DATABASE_FILE, MODEL_NAME


def main():
    initialize_database()
    agent = DatabaseAgent()
    print("CHAPTER 14 - DATABASE-CONNECTED AI AGENT")
    print("Model:", MODEL_NAME)
    print("Database:", DATABASE_FILE)
    print("Python:", sys.executable)
    print("Ask about products, low stock, categories, or inventory value.")
    print("Type /exit to quit. Database tools are read-only.\n")

    while True:
        try:
            question = input("You: ").strip()
            if question.lower() == "/exit":
                break
            if not question:
                continue
            print("Assistant:", agent.ask(question), "\n")
        except (ValueError, ResponseError,
                ConnectionError, TimeoutError) as exc:
            print("Operation failed:", exc, "\n")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()
