"""Tribunal Superior Eleitoral (TSE) API integration.

API documentation: https://dadosabertos.tse.jus.br/
"""
import httpx
from typing import List, Dict, Any

TSE_API_BASE = "https://dadosabertos.tse.jus.br"


async def get_candidato_bens(candidato_id: str, ano_eleicao: str) -> Dict[str, Any]:
    """Get candidate's declared assets (bens declarados)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TSE_API_BASE}/candidato/{candidato_id}/bens/{ano_eleicao}"
        )
        response.raise_for_status()
        return response.json()


async def get_candidato_despesas(candidato_id: str, ano_eleicao: str) -> Dict[str, Any]:
    """Get candidate's campaign expenses (despesas de campanha)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TSE_API_BASE}/candidato/{candidato_id}/despesas/{ano_eleicao}"
        )
        response.raise_for_status()
        return response.json()


async def get_resultado_eleicao(uf: str, ano: str, cargo: str = "presidente") -> List[Dict[str, Any]]:
    """Get election results for a state and year."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TSE_API_BASE}/eleicoes/{ano}/{uf}/{cargo}/candidatos"
        )
        response.raise_for_status()
        data = response.json()
        return data.get("candidatos", [])
