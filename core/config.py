from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Provider selection: "azure" | "groq"
    PROVIDER = os.getenv("PROVIDER", "azure")

    # Azure OpenAI
    AZURE_OPENAI_API_KEY    = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT   = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-54-mini")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    # Groq (free tier — https://console.groq.com)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
