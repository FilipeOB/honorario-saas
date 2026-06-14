"""
Configuração da aplicação FastAPI
Suporta variáveis de ambiente via .env
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Honorários Advocatícios SaaS"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # API
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list = ["*"]

    # Database (SQLite path — montar volume Railway em /data)
    DATABASE_PATH: str = "./honorarios.db"

    # JWT (7 dias = 10080 minutos)
    SECRET_KEY: str = "sua-chave-secreta-muito-segura-mudar-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # Admin (para criar usuarios via API)
    ADMIN_SECRET_KEY: str = "admin-secret-mudar-em-producao"

    # Default values calculadora
    DEFAULT_OVERHEAD_BRL: float = 10000.0
    DEFAULT_HORAS_UTEIS_MES: int = 160
    DEFAULT_CUSTO_HORA_ADV: float = 250.0
    DEFAULT_MARGEM: float = 2.5

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
