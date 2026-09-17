import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
FRAMES_DIR = STATIC_DIR / "frames"
UPLOADS_DIR = BASE_DIR / "uploads"
SAMPLE_DIR = BASE_DIR / "sample_data"

for d in [STATIC_DIR, FRAMES_DIR, UPLOADS_DIR, SAMPLE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    # Provider options: "openrouter", "groq", "gemini", "custom"
    API_PROVIDER: str = "openrouter"
    API_KEY: str = ""
    BASE_URL: str = "https://openrouter.ai/api/v1"
    MODEL_NAME: str = "openrouter/free"
    
    # Pricing defaults for cost tracking (USD per 1M tokens)
    INPUT_TOKEN_PRICE_PER_M: float = 0.10
    OUTPUT_TOKEN_PRICE_PER_M: float = 0.40

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Support fallback to environment variables directly if set
if not settings.API_KEY:
    settings.API_KEY = (
        os.getenv("OPENROUTER_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("GROQ_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or ""
    )
