from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Honorarios Advocaticios SaaS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list = ["*"]
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "chave-secreta-mudar-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEFAULT_OVERHEAD_BRL: float = 10000.0
    DEFAULT_HORAS_UTEIS_MES: int = 160
    DEFAULT_CUSTO_HORA_ADV: float = 250.0
    DEFAULT_MARGEM: float = 2.5

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
