from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Honorarios Advocaticios SaaS"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    APP_URL: str = "https://honorario-saas-production.up.railway.app"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list = ["*"]
    DATABASE_PATH: str = "./honorarios.db"
    SECRET_KEY: str = "sua-chave-secreta-muito-segura-mudar-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    ADMIN_SECRET_KEY: str = "admin-secret-mudar-em-producao"
    DEFAULT_OVERHEAD_BRL: float = 10000.0
    DEFAULT_HORAS_UTEIS_MES: int = 160
    DEFAULT_CUSTO_HORA_ADV: float = 250.0
    DEFAULT_MARGEM: float = 2.5
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_FROM_NAME: str = "Honorarios PRO"
    HOTMART_HOTTOK: str = ""
    KIWIFY_WEBHOOK_SECRET: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
