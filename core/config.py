from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OPENAI_API_KEY: str
    MONGO_CONNECTION_STRING: str

    class Config:
        env_file = ".env"

settings = Settings()
