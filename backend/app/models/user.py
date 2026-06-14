"""
Modelos do banco de dados: User, UserSettings, CalculationHistory
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    plan = Column(String(50), default="pro")
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    history = relationship("CalculationHistory", back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    # Armazena configurações como JSON serializado
    overhead_mensal = Column(String(50), default="10000")
    horas_uteis_mes = Column(String(50), default="160")
    custo_hora_adv = Column(String(50), default="250")
    margem_objetivo = Column(String(50), default="2.5")
    uf = Column(String(5), default="SP")
    regime_tributario = Column(String(20), default="simples")
    iss = Column(String(10), default="5.0")
    pis_cofins = Column(String(10), default="3.65")
    irrf = Column(String(10), default="0")
    taxa_asaas = Column(String(10), default="2.99")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="settings")


class CalculationHistory(Base):
    __tablename__ = "calculation_history"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    nome_caso = Column(String(500), nullable=True)
    horas_estimadas = Column(String(50), nullable=True)
    complexidade = Column(String(20), nullable=True)
    # Resultado serializado
    valor_final = Column(String(50), nullable=True)
    custo_direto = Column(String(50), nullable=True)
    margem_bruta = Column(String(50), nullable=True)
    roi = Column(String(50), nullable=True)
    # JSON completo do input e resultado para consulta
    input_json = Column(Text, nullable=True)
    result_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="history")
