"""
Endpoints da API para calculo de honorarios
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, List
from ....schemas import (
    RequestCalculoHonorarios,
    ResultadoHonorarios,
    UF,
)
from ....calculators import MotorCalculoHonorarios
from ....services import oab_service

router = APIRouter(prefix="/honorarios", tags=["Honorarios"])
motor = MotorCalculoHonorarios()


@router.post("/calcular", response_model=ResultadoHonorarios)
def calcular_honorarios(request: RequestCalculoHonorarios) -> ResultadoHonorarios:
    try:
        metodo = request.caso.metodo_pagamento
        metodos_dict = request.metodos_pagamento.dict()
        metodo_info = metodos_dict.get(metodo.value, {})
        if not metodo_info:
            raise ValueError(f"Metodo de pagamento nao configurado: {metodo.value}")
        taxa_asaas_fixa = metodo_info.get("fixo", 0.0)
        taxa_asaas_percentual = metodo_info.get("percentual", 0.0)
        valor_oab_minimo = 0.0
        resultado = motor.calcular(
            configuracao=request.configuracao,
            encargos=request.encargos,
            caso=request.caso,
            taxa_asaas_fixa=taxa_asaas_fixa,
            taxa_asaas_percentual=taxa_asaas_percentual,
            valor_oab_minimo=valor_oab_minimo,
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/oab/{uf}/areas", response_model=Dict[str, str])
def listar_areas_oab(uf: UF) -> Dict[str, str]:
    if not oab_service.esta_disponivel(uf):
        raise HTTPException(status_code=404, detail=f"Tabela OAB nao disponivel para {uf.value}")
    areas = oab_service.listar_areas(uf)
    if not areas:
        raise HTTPException(status_code=404, detail="Nenhuma area encontrada")
    return areas


@router.get("/oab/{uf}/areas/{area}/servicos", response_model=Dict[str, Dict])
def listar_servicos_area(uf: UF, area: str) -> Dict[str, Dict]:
    if not oab_service.esta_disponivel(uf):
        raise HTTPException(status_code=404, detail=f"Tabela OAB nao disponivel para {uf.value}")
    servicos = oab_service.listar_servicos(uf, area)
    if not servicos:
        raise HTTPException(status_code=404, detail=f"Nenhum servico encontrado para area: {area}")
    return servicos


@router.get("/oab/{uf}/areas/{area}/servicos/{servico}/valor")
def obter_valor_minimo_oab(uf: UF, area: str, servico: str):
    if not oab_service.esta_disponivel(uf):
        raise HTTPException(status_code=404, detail=f"Tabela OAB nao disponivel para {uf.value}")
    valor = oab_service.get_valor_minimo(uf, area, servico)
    if valor is None:
        raise HTTPException(status_code=404, detail=f"Servico nao encontrado: {area}/{servico}")
    info = oab_service.get_info_servico(uf, area, servico)
    return {
        "valor_minimo": valor,
        "nome": info.get("nome", servico) if info else servico,
        "descricao": info.get("descricao", "") if info else "",
    }


@router.get("/oab/estados", response_model=List[str])
def listar_estados_oab() -> List[str]:
    estados = oab_service.listar_estados()
    if not estados:
        raise HTTPException(status_code=404, detail="Nenhuma tabela OAB disponivel")
    return sorted(estados)
