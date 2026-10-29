"""Câmara dos Deputados (Chamber of Deputies) API integration.

API documentation: https://dadosabertos.camara.leg.br/api/v2/
"""
import httpx
from typing import List, Dict, Any

CAMARA_API_BASE = "https://dadosabertos.camara.leg.br/api/v2"


async def get_deputado_details(deputado_id: int) -> Dict[str, Any]:
    """Get detailed information about a deputy."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CAMARA_API_BASE}/deputados/{deputado_id}")
        response.raise_for_status()
        return response.json()


async def get_deputado_gastos(deputado_id: int, ano: int, itens: int = 100) -> List[Dict[str, Any]]:
    """Get deputy expenses (gastos de gabinete) for a given year."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CAMARA_API_BASE}/deputados/{deputado_id}/gastos",
            params={"ano": ano, "itens": itens, "ordem": "ASC", "ordenarPor": "ano"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("dados", [])


async def get_deputado_votacoes(deputado_id: int, ano: int, itens: int = 100) -> List[Dict[str, Any]]:
    """Get deputy voting records for a given year."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CAMARA_API_BASE}/deputados/{deputado_id}/votacoes",
            params={"ano": ano, "itens": itens, "ordem": "DESC", "ordenarPor": "dataHoraVotacao"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("dados", [])


async def get_deputado_proposicoes(deputado_id: int, ano: int, itens: int = 100) -> List[Dict[str, Any]]:
    """Get deputy proposals (proposições) for a given year."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CAMARA_API_BASE}/deputados/{deputado_id}/proposicoes",
            params={"ano": ano, "itens": itens, "ordem": "DESC", "ordenarPor": "dataApresentacao"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("dados", [])


async def get_deputado_discursos(deputado_id: int, ano: int, itens: int = 100) -> List[Dict[str, Any]]:
    """Get deputy speeches (discursos) for a given year."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CAMARA_API_BASE}/deputados/{deputado_id}/discursos",
            params={"ano": ano, "itens": itens, "ordem": "DESC", "ordenarPor": "dataHoraInicio"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("dados", [])


async def search_deputados(nome: str, itens: int = 100) -> List[Dict[str, Any]]:
    """Search for deputies by name."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CAMARA_API_BASE}/deputados",
            params={"nome": nome, "itens": itens, "ordem": "ASC", "ordenarPor": "nome"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("dados", [])


async def get_deputado_frentes(deputado_id: int) -> List[Dict[str, Any]]:
    """Get deputy's party/bloc (frente) information."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CAMARA_API_BASE}/deputados/{deputado_id}/frentes")
        response.raise_for_status()
        data = response.json()
        return data.get("dados", [])
