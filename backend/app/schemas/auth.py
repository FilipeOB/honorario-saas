"""
Schemas Pydantic para autenticação e dados do usuário
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: Optional[str] = None
    email: str


class CreateUserRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    plan: str = "pro"
    must_change_password: bool = False


class UserOut(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    plan: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserSettingsSchema(BaseModel):
    overhead_mensal: Optional[str] = "10000"
    horas_uteis_mes: Optional[str] = "160"
    custo_hora_adv: Optional[str] = "250"
    margem_objetivo: Optional[str] = "2.5"
    uf: Optional[str] = "SP"
    regime_tributario: Optional[str] = "simples"
    iss: Optional[str] = "5.0"
    pis_cofins: Optional[str] = "3.65"
    irrf: Optional[str] = "0"
    taxa_asaas: Optional[str] = "2.99"


class HistoryItemIn(BaseModel):
    nome_caso: Optional[str] = None
    horas_estimadas: Optional[str] = None
    complexidade: Optional[str] = None
    valor_final: Optional[str] = None
    custo_direto: Optional[str] = None
    margem_bruta: Optional[str] = None
    roi: Optional[str] = None
    input_json: Optional[str] = None
    result_json: Optional[str] = None


class HistoryItemOut(HistoryItemIn):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
