from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str

    model_config = ConfigDict(env_file=".env")

settings = Settings()
