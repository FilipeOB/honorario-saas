"""
Schemas Pydantic para calculo de honorarios
Validacao de entrada/saida
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from enum import Enum


class UF(str, Enum):
    RS = "RS"; SP = "SP"; MG = "MG"; BA = "BA"; RJ = "RJ"
    PA = "PA"; CE = "CE"; PE = "PE"; SC = "SC"; GO = "GO"
    PB = "PB"; MA = "MA"; ES = "ES"; PI = "PI"; RN = "RN"
    AL = "AL"; MT = "MT"; DF = "DF"; MS = "MS"; SE = "SE"
    TO = "TO"; RO = "RO"; AC = "AC"; AM = "AM"; RR = "RR"; AP = "AP"

class TipoAcao(str, Enum):
    CIVIL_COBRANCA = "civil_cobranca"
    CIVIL_RESPONSABILIDADE = "civil_responsabilidade"
    CIVIL_FAMILIA = "civil_familia"
    CIVIL_EMPRESARIAL = "civil_empresarial"
    CIVIL_IMOBILIARIO = "civil_imobiliario"
    CIVIL_REVISIONAL = "civil_revisional"
    TRABALHISTA_EMPREGADO = "trabalhista_empregado"
    TRABALHISTA_EMPREGADOR = "trabalhista_empregador"
    TRIBUTARIO = "tributario"
    CRIMINAL = "criminal"
    PREVIDENCIARIO = "previdenciario"
    AMBIENTAL = "ambiental"

class Fase(str, Enum):
    PRE_PROCESSUAL = "pre_processual"
    PETICION_INICIAL = "peticion_inicial"
    DEFESA = "defesa"
    EM_ANDAMENTO = "em_andamento"
    RECURSOS = "recursos"
    TRIBUNAIS_SUPERIORES = "tribunais_superiores"
    EXECUCAO = "execucao"
    HC_MS = "habeas_corpus_mandado_seguranca"

class Complexidade(str, Enum):
    SIMPLES = "simples"; BAIXA = "baixa"; MEDIA = "media"
    ALTA = "alta"; MUITO_ALTA = "muito_alta"

class Urgencia(str, Enum):
    NORMAL = "normal"; URGENTE = "urgente"; MUITO_URGENTE = "muito_urgente"

class Duracao(str, Enum):
    CURTA = "curta"; MEDIA = "media"; LONGA = "longa"; MUITO_LONGA = "muito_longa"

class RiscosJuridicos(str, Enum):
    BAIXO = "baixo"; MEDIO = "medio"; ALTO = "alto"; CRITICO = "critico"

class MetodoPagamento(str, Enum):
    PIX = "pix"; BOLETO = "boleto"; DEBITO = "debito"
    CRED_AV = "cred_av"; CRED_26 = "cred_26"; CRED_712 = "cred_712"

class ConfiguracaoEscritorio(BaseModel):
    overhead_mensal: float = Field(..., gt=0)
    horas_uteis_mes: int = Field(..., gt=0)
    custo_hora_adv: float = Field(..., gt=0)
    margem_objetivo: float = Field(..., gt=1.0, le=6.0)

class EncargosAguilhon(BaseModel):
    iss: float = Field(..., ge=0, le=10)
    pis_cofins: float = Field(..., ge=0, le=15)
    irrf: float = Field(..., ge=0, le=15)

class TaxaMetodoPagamento(BaseModel):
    nome: str
    fixo: float = Field(..., ge=0)
    percentual: float = Field(..., ge=0)

class MetodosPagamento(BaseModel):
    pix: TaxaMetodoPagamento
    boleto: TaxaMetodoPagamento
    debito: TaxaMetodoPagamento
    cred_av: TaxaMetodoPagamento
    cred_26: TaxaMetodoPagamento
    cred_712: TaxaMetodoPagamento

class DadosCaso(BaseModel):
    nome_caso: str
    tipo_acao: TipoAcao
    fase: Fase = Field(default=Fase.PETICION_INICIAL)
    complexidade: Complexidade = Field(default=Complexidade.MEDIA)
    valor_causa: float = Field(ge=0, default=0)
    horas_estimadas: float = Field(..., gt=0)
    probabilidade_exito: RiscosJuridicos = Field(default=RiscosJuridicos.MEDIO)
    urgencia: Urgencia = Field(default=Urgencia.NORMAL)
    duracao: Duracao = Field(default=Duracao.MEDIA)
    metodo_pagamento: MetodoPagamento = Field(default=MetodoPagamento.PIX)
    uf: UF = Field(default=UF.RS)

class ResultadoCalculoBase(BaseModel):
    custo_direto: float
    overhead_alocado: float
    custo_total: float
    multiplicador_total: float
    honor_base: float
    margem_bruta: float
    roi: float

class ResultadoTributario(BaseModel):
    iss_valor: float; iss_pct: float
    pis_cofins_valor: float; pis_cofins_pct: float
    irrf_valor: float; irrf_pct: float
    total_tributario: float; total_tributario_pct: float

class ResultadoAsaas(BaseModel):
    metodo: MetodoPagamento
    fixo: float; percentual: float; valor_total: float

class ResultadoComposicao(BaseModel):
    honor_base: float; iss: float; pis_cofins: float; irrf: float
    asaas_fixo: float; asaas_percentual: float
    total_impostos_taxas: float; valor_final: float

class ResultadoHonorarios(BaseModel):
    caso: str
    uf: UF
    calculo_base: ResultadoCalculoBase
    tributario: ResultadoTributario
    asaas: ResultadoAsaas
    composicao: ResultadoComposicao
    valor_oab_minimo: Optional[float] = None
    percentual_causa: Optional[float] = None
    honor_exito_sugerido: Optional[float] = None
    viabilidade: str
    observacoes: List[str] = Field(default_factory=list)

class RequestCalculoHonorarios(BaseModel):
    configuracao: ConfiguracaoEscritorio
    encargos: EncargosAguilhon
    metodos_pagamento: MetodosPagamento
    caso: DadosCaso
