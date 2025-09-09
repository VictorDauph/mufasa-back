from pydantic_settings import BaseSettings

#liste des variables d'environnement du projet
class Settings(BaseSettings):
    replicate_api_token: str

    class Config:
        env_file = ".env"

settings = Settings()
