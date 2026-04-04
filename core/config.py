from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Provider selection: "azure" or "local"
    PROVIDER = os.getenv("PROVIDER", "azure")

    # Azure OpenAI
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-54-mini")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    # Azure Speech
    AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")
    AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "germanywestcentral")

    # Local fallback (Ollama)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")
