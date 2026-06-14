"""
Motor de calculo de honorarios advocaticios
Logica pura e modular para calculo de precos
"""
from typing import Dict, Tuple
from dataclasses import dataclass
from ..schemas import (
    ConfiguracaoEscritorio,
    EncargosAguilhon,
    DadosCaso,
    ResultadoCalculoBase,
    ResultadoTributario,
    ResultadoAsaas,
    ResultadoComposicao,
    ResultadoHonorarios,
    Fase,
    Complexidade,
    RiscosJuridicos,
    Urgencia,
    Duracao,
)


@dataclass
class Multiplicadores:
    fase: float
    complexidade: float
    risco: float
    urgencia: float
    duracao: float

    @property
    def total(self) -> float:
        return self.fase * self.complexidade * self.risco * self.urgencia * self.duracao


class MultiplicadorFactory:
    FASE_MAP = {
        Fase.PRE_PROCESSUAL: 0.75,
        Fase.PETICION_INICIAL: 1.00,
        Fase.DEFESA: 0.90,
        Fase.EM_ANDAMENTO: 1.10,
        Fase.RECURSOS: 1.40,
        Fase.TRIBUNAIS_SUPERIORES: 1.80,
        Fase.EXECUCAO: 1.25,
        Fase.HC_MS: 1.30,
    }
    COMPLEXIDADE_MAP = {
        Complexidade.SIMPLES: 1.00,
        Complexidade.BAIXA: 1.30,
        Complexidade.MEDIA: 1.70,
        Complexidade.ALTA: 2.20,
        Complexidade.MUITO_ALTA: 3.00,
    }
    RISCO_MAP = {
        RiscosJuridicos.BAIXO: 0.85,
        RiscosJuridicos.MEDIO: 1.10,
        RiscosJuridicos.ALTO: 1.50,
        RiscosJuridicos.CRITICO: 1.80,
    }
    URGENCIA_MAP = {
        Urgencia.NORMAL: 1.00,
        Urgencia.URGENTE: 1.35,
        Urgencia.MUITO_URGENTE: 1.70,
    }
    DURACAO_MAP = {
        Duracao.CURTA: 1.00,
        Duracao.MEDIA: 1.15,
        Duracao.LONGA: 1.30,
        Duracao.MUITO_LONGA: 1.50,
    }

    @staticmethod
    def criar(caso: DadosCaso) -> Multiplicadores:
        return Multiplicadores(
            fase=MultiplicadorFactory.FASE_MAP.get(caso.fase, 1.0),
            complexidade=MultiplicadorFactory.COMPLEXIDADE_MAP.get(caso.complexidade, 1.0),
            risco=MultiplicadorFactory.RISCO_MAP.get(caso.probabilidade_exito, 1.0),
            urgencia=MultiplicadorFactory.URGENCIA_MAP.get(caso.urgencia, 1.0),
            duracao=MultiplicadorFactory.DURACAO_MAP.get(caso.duracao, 1.0),
        )


class CalculadoraCustos:
    @staticmethod
    def custo_hora_real(config: ConfiguracaoEscritorio) -> float:
        taxa_overhead = config.overhead_mensal / config.horas_uteis_mes
        return taxa_overhead + config.custo_hora_adv

    @staticmethod
    def calcular_custos(config: ConfiguracaoEscritorio, horas: float) -> Tuple[float, float, float, float]:
        taxa_overhead = config.overhead_mensal / config.horas_uteis_mes
        custo_direto = config.custo_hora_adv * horas
        overhead_alocado = taxa_overhead * horas
        custo_total = custo_direto + overhead_alocado
        return custo_direto, overhead_alocado, custo_total, taxa_overhead


class CalculadoraHonorarios:
    @staticmethod
    def calcular(custo_total: float, multiplicadores: Multiplicadores, margem: float, honor_minimo: float = 0.0) -> Tuple[float, float, float]:
        honor_base = custo_total * multiplicadores.total * margem
        if honor_minimo > 0 and honor_base < honor_minimo:
            honor_base = honor_minimo
        margem_bruta = honor_base - custo_total
        roi = (margem_bruta / custo_total * 100) if custo_total > 0 else 0
        return honor_base, margem_bruta, roi


class CalculadoraTributaria:
    @staticmethod
    def calcular_grossup(valor_base: float, encargos: EncargosAguilhon, taxa_asaas_percentual: float) -> Tuple[float, Dict[str, float]]:
        taxa_total = (encargos.iss + encargos.pis_cofins + encargos.irrf + taxa_asaas_percentual) / 100
        if taxa_total >= 1.0:
            valor_final = valor_base * (1 + taxa_total)
        else:
            valor_final = valor_base / (1 - taxa_total) if taxa_total < 1.0 else valor_base
        iss = valor_final * (encargos.iss / 100)
        pis_cofins = valor_final * (encargos.pis_cofins / 100)
        irrf = valor_final * (encargos.irrf / 100)
        total_trib = iss + pis_cofins + irrf
        return valor_final, {"iss": iss, "pis_cofins": pis_cofins, "irrf": irrf, "total": total_trib}

    @staticmethod
    def detalhamento(valor_final: float, encargos: EncargosAguilhon) -> Dict[str, float]:
        return {
            "iss_valor": valor_final * (encargos.iss / 100),
            "iss_pct": encargos.iss,
            "pis_cofins_valor": valor_final * (encargos.pis_cofins / 100),
            "pis_cofins_pct": encargos.pis_cofins,
            "irrf_valor": valor_final * (encargos.irrf / 100),
            "irrf_pct": encargos.irrf,
            "total_tributario": valor_final * ((encargos.iss + encargos.pis_cofins + encargos.irrf) / 100),
            "total_tributario_pct": encargos.iss + encargos.pis_cofins + encargos.irrf,
        }


class CalculadoraAsaas:
    @staticmethod
    def calcular_taxa(valor: float, taxa_fixa: float, taxa_percentual: float) -> float:
        return taxa_fixa + (valor * taxa_percentual / 100)


class AnalisadorViabilidade:
    @staticmethod
    def classificar(roi: float) -> Tuple[str, str]:
        if roi < 50:
            return "danger", f"ROI de {roi:.0f}% - abaixo do minimo sustentavel. Reavalie as horas estimadas."
        elif roi < 120:
            return "warning", f"ROI de {roi:.0f}% - margem baixa. Aceitavel apenas para clientes estrategicos."
        elif roi < 300:
            return "ok", f"ROI de {roi:.0f}% - faixa saudavel. Caso bem precificado."
        else:
            return "ok", f"ROI de {roi:.0f}% - excelente margem. Avalie alinhamento com mercado."


class MotorCalculoHonorarios:
    def __init__(self):
        self.calculadora_custos = CalculadoraCustos()
        self.calculadora_honorarios = CalculadoraHonorarios()
        self.calculadora_tributaria = CalculadoraTributaria()
        self.calculadora_asaas = CalculadoraAsaas()
        self.analisador = AnalisadorViabilidade()

    def calcular(self, configuracao, encargos, caso, taxa_asaas_fixa, taxa_asaas_percentual, valor_oab_minimo=0.0):
        custo_direto, overhead_alocado, custo_total, taxa_overhead = self.calculadora_custos.calcular_custos(configuracao, caso.horas_estimadas)
        multiplicadores = MultiplicadorFactory.criar(caso)
        honor_base, margem_bruta, roi = self.calculadora_honorarios.calcular(custo_total, multiplicadores, configuracao.margem_objetivo, valor_oab_minimo)
        valor_final, _ = self.calculadora_tributaria.calcular_grossup(honor_base, encargos, taxa_asaas_percentual)
        detalhe_tributario = self.calculadora_tributaria.detalhamento(valor_final, encargos)
        taxa_asaas_valor = self.calculadora_asaas.calcular_taxa(valor_final, taxa_asaas_fixa, taxa_asaas_percentual)
        viabilidade_status, viabilidade_msg = self.analisador.classificar(roi)
        percentual_causa = (honor_base / caso.valor_causa * 100) if caso.valor_causa > 0 else None
        honor_exito = None
        if caso.valor_causa > 0:
            perc_exito = min(0.10 * multiplicadores.complexidade * multiplicadores.risco, 0.30)
            honor_exito = caso.valor_causa * perc_exito
        resultado = ResultadoHonorarios(
            caso=caso.nome_caso,
            uf=caso.uf,
            calculo_base=ResultadoCalculoBase(
                custo_direto=custo_direto,
                overhead_alocado=overhead_alocado,
                custo_total=custo_total,
                multiplicador_total=multiplicadores.total,
                honor_base=honor_base,
                margem_bruta=margem_bruta,
                roi=roi,
            ),
            tributario=ResultadoTributario(
                iss_valor=detalhe_tributario["iss_valor"],
                iss_pct=detalhe_tributario["iss_pct"],
                pis_cofins_valor=detalhe_tributario["pis_cofins_valor"],
                pis_cofins_pct=detalhe_tributario["pis_cofins_pct"],
                irrf_valor=detalhe_tributario["irrf_valor"],
                irrf_pct=detalhe_tributario["irrf_pct"],
                total_tributario=detalhe_tributario["total_tributario"],
                total_tributario_pct=detalhe_tributario["total_tributario_pct"],
            ),
            asaas=ResultadoAsaas(
                metodo=caso.metodo_pagamento,
                fixo=taxa_asaas_fixa,
                percentual=taxa_asaas_percentual,
                valor_total=taxa_asaas_valor,
            ),
            composicao=ResultadoComposicao(
                honor_base=honor_base,
                iss=detalhe_tributario["iss_valor"],
                pis_cofins=detalhe_tributario["pis_cofins_valor"],
                irrf=detalhe_tributario["irrf_valor"],
                asaas_fixo=taxa_asaas_fixa,
                asaas_percentual=valor_final * (taxa_asaas_percentual / 100),
                total_impostos_taxas=detalhe_tributario["total_tributario"] + taxa_asaas_valor,
                valor_final=valor_final + taxa_asaas_valor,
            ),
            valor_oab_minimo=valor_oab_minimo if valor_oab_minimo > 0 else None,
            percentual_causa=percentual_causa,
            honor_exito_sugerido=honor_exito,
            viabilidade=viabilidade_status,
            observacoes=[viabilidade_msg],
        )
        return resultado
