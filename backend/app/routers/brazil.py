"""API endpoints for Brazilian official government data."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Leader, VotingRecord, Proposal, ExpenseRecord
from ..brazil_api import camara, senado, tse

router = APIRouter(prefix="/api/brazil", tags=["brazil"])


@router.get("/deputados/search")
async def search_deputados(nome: str):
    """Search for Brazilian deputies by name."""
    results = await camara.search_deputados(nome)
    return {"total": len(results), "results": results}


@router.get("/deputados/{deputado_id}/gastos")
async def get_deputado_gastos(deputado_id: int, ano: int):
    """Get deputy expenses for a given year."""
    gastos = await camara.get_deputado_gastos(deputado_id, ano)
    return {"total": len(gastos), "ano": ano, "results": gastos}


@router.get("/deputados/{deputado_id}/votacoes")
async def get_deputado_votacoes(deputado_id: int, ano: int):
    """Get deputy voting records for a given year."""
    votacoes = await camara.get_deputado_votacoes(deputado_id, ano)
    return {"total": len(votacoes), "ano": ano, "results": votacoes}


@router.get("/deputados/{deputado_id}/proposicoes")
async def get_deputado_proposicoes(deputado_id: int, ano: int):
    """Get deputy proposals for a given year."""
    proposicoes = await camara.get_deputado_proposicoes(deputado_id, ano)
    return {"total": len(proposicoes), "ano": ano, "results": proposicoes}


@router.get("/senadores/search")
async def search_senadores(nome: str):
    """Search for Brazilian senators by name."""
    results = await senado.search_senadores(nome)
    return {"total": len(results), "results": results}


@router.get("/senadores/{senador_id}/gastos")
async def get_senador_gastos(senador_id: int, ano: int):
    """Get senator expenses for a given year."""
    gastos = await senado.get_senador_gastos(senador_id, ano)
    return {"total": len(gastos), "ano": ano, "results": gastos}


@router.get("/tse/eleicoes/{uf}/{ano}")
async def get_resultado_eleicao(uf: str, ano: str, cargo: str = "presidente"):
    """Get election results for a state and year."""
    resultados = await tse.get_resultado_eleicao(uf, ano, cargo)
    return {"uf": uf, "ano": ano, "cargo": cargo, "candidatos": resultados}
