"""Senado Federal (Senate) API integration.

API documentation: https://legis.senado.leg.br/dadosabertos/
"""
import httpx
from typing import List, Dict, Any

SENADO_API_BASE = "https://legis.senado.leg.br/dadosabertos"


async def get_senador_details(senador_id: int) -> Dict[str, Any]:
    """Get detailed information about a senator."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SENADO_API_BASE}/senador/{senador_id}")
        response.raise_for_status()
        return response.json()


async def get_senador_gastos(senador_id: int, ano: int) -> List[Dict[str, Any]]:
    """Get senator expenses (CEAP - Cota para Exercício da Atividade Parlamentar)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SENADO_API_BASE}/senador/{senador_id}/gastos",
            params={"ano": ano}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("dados", [])


async def get_senador_votacoes(senador_id: int, ano: int) -> List[Dict[str, Any]]:
    """Get senator voting records for a given year."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SENADO_API_BASE}/senador/{senador_id}/votacoes",
            params={"ano": ano}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("dados", [])


async def search_senadores(nome: str) -> List[Dict[str, Any]]:
    """Search for senators by name."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SENADO_API_BASE}/senador/lista/atual",
            params={"nome": nome}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("dados", [])


async def get_senador_proposicoes(senador_id: int, ano: int) -> List[Dict[str, Any]]:
    """Get senator proposals for a given year."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SENADO_API_BASE}/senador/{senador_id}/proposicoes",
            params={"ano": ano}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("dados", [])
