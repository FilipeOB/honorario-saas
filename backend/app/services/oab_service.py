"""
Servico para carregar e gerenciar tabelas OAB
"""
import json
from typing import Dict, Optional
from pathlib import Path
from ..schemas import UF


class OABService:
    _instance = None
    _tabelas = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OABService, cls).__new__(cls)
            cls._instance._carregadas = False
        return cls._instance

    def __init__(self):
        if not self._carregadas:
            self._carregar_tabelas()
            self._carregadas = True

    def _carregar_tabelas(self):
        oab_dir = Path(__file__).parent.parent / "data" / "oab"
        if not oab_dir.exists():
            return
        for arquivo in oab_dir.glob("*.json"):
            try:
                with open(arquivo, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    estado = dados.get("estado", arquivo.stem.split("_")[0].upper())
                    self._tabelas[estado] = dados
            except Exception as e:
                print(f"Erro ao carregar {arquivo}: {e}")

    def get_tabela(self, uf: UF) -> Optional[Dict]:
        return self._tabelas.get(uf.value)

    def get_valor_minimo(self, uf: UF, area: str, servico: str) -> Optional[float]:
        tabela = self.get_tabela(uf)
        if not tabela:
            return None
        areas = tabela.get("areas", {})
        if area.lower() not in areas:
            return None
        servicos = areas[area.lower()].get("servicos", {})
        if servico.lower() not in servicos:
            return None
        return servicos[servico.lower()].get("valor_minimo")

    def listar_areas(self, uf: UF) -> Dict[str, str]:
        tabela = self.get_tabela(uf)
        if not tabela:
            return {}
        return {k: v.get("nome", k) for k, v in tabela.get("areas", {}).items()}

    def listar_servicos(self, uf: UF, area: str) -> Dict[str, Dict]:
        tabela = self.get_tabela(uf)
        if not tabela:
            return {}
        areas = tabela.get("areas", {})
        if area.lower() not in areas:
            return {}
        return areas[area.lower()].get("servicos", {})

    def get_info_servico(self, uf: UF, area: str, servico: str) -> Optional[Dict]:
        tabela = self.get_tabela(uf)
        if not tabela:
            return None
        areas = tabela.get("areas", {})
        if area.lower() not in areas:
            return None
        servicos = areas[area.lower()].get("servicos", {})
        return servicos.get(servico.lower())

    def listar_estados(self) -> list:
        return list(self._tabelas.keys())

    def esta_disponivel(self, uf: UF) -> bool:
        return uf.value in self._tabelas

    def importar_tabela(self, uf: str, dados: Dict) -> bool:
        try:
            if "areas" not in dados:
                raise ValueError("Estrutura invalida: falta campo 'areas'")
            self._tabelas[uf.upper()] = dados
            return True
        except Exception as e:
            print(f"Erro ao importar tabela {uf}: {e}")
            return False


oab_service = OABService()
