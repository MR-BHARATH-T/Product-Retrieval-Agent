import os
from pathlib import Path
from dotenv import load_dotenv

# Load env file from backend root if it exists
env_path = Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Also attempt standard loading in current working directory
    load_dotenv()

class Settings:
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")
    LM_STUDIO_BASE_URL: str = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
    LM_STUDIO_API_KEY: str = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
    
    # Provider keys for OpenRouter, Gemini, Groq, and Grok
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROK_API_KEY: str = os.getenv("GROK_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "lm-studio")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///products.db")
    
    # Storage settings
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", str(Path(__file__).resolve().parent.parent / "chroma_db"))

settings = Settings()
