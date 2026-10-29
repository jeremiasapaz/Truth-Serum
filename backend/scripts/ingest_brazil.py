"""Ingestion script for Brazilian official government data.

Fetches voting records, proposals, and expenses from Brazilian APIs
and stores them in the database.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models import Leader, VotingRecord, Proposal, ExpenseRecord
from app.brazil_api import camara, senado
from app.ingest.roster import ROSTER


async def ingest_brazilian_leader_data(leader_name: str, year: int = 2024):
    """Ingest voting records, proposals, and expenses for a Brazilian leader."""
    db = SessionLocal()
    try:
        # Find the leader in our database
        leader = db.query(Leader).filter(Leader.name == leader_name).first()
        if not leader:
            print(f"  SKIP {leader_name} - not found in database")
            return
        
        print(f"Processing {leader_name} for year {year}...")
        
        # Try to find deputy ID from Câmara API
        deputados = await camara.search_deputados(leader_name)
        if deputados:
            deputado_id = deputados[0]["id"]
            print(f"  Found deputy ID: {deputado_id}")
            
            # Ingest voting records
            votacoes = await camara.get_deputado_votacoes(deputado_id, year)
            for voto in votacoes:
                existing = db.query(VotingRecord).filter(
                    VotingRecord.leader_id == leader.id,
                    VotingRecord.proposal_id == str(voto.get("id")),
                    VotingRecord.vote_date == datetime.fromisoformat(voto.get("dataHoraVotacao").replace("T", " ").replace("Z", ""))
                ).first()
                
                if not existing:
                    db.add(VotingRecord(
                        leader_id=leader.id,
                        proposal_id=str(voto.get("id")),
                        proposal_title=voto.get("proposicao", {}).get("titulo", ""),
                        vote=voto.get("voto"),
                        vote_date=datetime.fromisoformat(voto.get("dataHoraVotacao").replace("T", " ").replace("Z", "")),
                        source="Câmara dos Deputados",
                        source_url=f"https://www.camara.leg.br/deputados/{deputado_id}/votacoes"
                    ))
            print(f"  Ingested {len(votacoes)} voting records")
            
            # Ingest proposals
            proposicoes = await camara.get_deputado_proposicoes(deputado_id, year)
            for prop in proposicoes:
                existing = db.query(Proposal).filter(
                    Proposal.leader_id == leader.id,
                    Proposal.proposal_id == str(prop.get("id"))
                ).first()
                
                if not existing:
                    db.add(Proposal(
                        leader_id=leader.id,
                        proposal_id=str(prop.get("id")),
                        title=prop.get("titulo", ""),
                        description=prop.get("ementa", ""),
                        type=prop.get("tipo", ""),
                        status=prop.get("situacao", ""),
                        presentation_date=datetime.fromisoformat(prop.get("dataApresentacao").replace("T", " ").replace("Z", "")) if prop.get("dataApresentacao") else None,
                        source="Câmara dos Deputados",
                        source_url=f"https://www.camara.leg.br/deputados/{deputado_id}/proposicoes"
                    ))
            print(f"  Ingested {len(proposicoes)} proposals")
            
            # Ingest expenses
            gastos = await camara.get_deputado_gastos(deputado_id, year)
            for gasto in gastos:
                existing = db.query(ExpenseRecord).filter(
                    ExpenseRecord.leader_id == leader.id,
                    ExpenseRecord.description == gasto.get("txtFornecedor"),
                    ExpenseRecord.date == datetime.fromisoformat(gasto.get("dataDocumento").replace("T", " ").replace("Z", "")) if gasto.get("dataDocumento") else None
                ).first()
                
                if not existing:
                    db.add(ExpenseRecord(
                        leader_id=leader.id,
                        expense_type="gabinete",
                        amount=gasto.get("valorLiquido", 0),
                        currency="BRL",
                        date=datetime.fromisoformat(gasto.get("dataDocumento").replace("T", " ").replace("Z", "")) if gasto.get("dataDocumento") else None,
                        year=year,
                        supplier_name=gasto.get("txtFornecedor"),
                        supplier_cnpj=gasto.get("cnpjFornecedor"),
                        description=gasto.get("txtDescricao"),
                        receipt_url=gasto.get("urlDocumento"),
                        source="Câmara dos Deputados",
                        source_url=f"https://www.camara.leg.br/deputados/{deputado_id}/gastos"
                    ))
            print(f"  Ingested {len(gastos)} expense records")
        
        # Try to find senator ID from Senado API
        senadores = await senado.search_senadores(leader_name)
        if senadores:
            senador_id = senadores[0].get("id") or senadores[0].get("identificacao")
            if senador_id:
                print(f"  Found senator ID: {senador_id}")
                
                # Ingest senator expenses
                gastos = await senado.get_senador_gastos(senador_id, year)
                for gasto in gastos:
                    existing = db.query(ExpenseRecord).filter(
                        ExpenseRecord.leader_id == leader.id,
                        ExpenseRecord.description == gasto.get("descricao"),
                        ExpenseRecord.date == datetime.fromisoformat(gasto.get("data", "").replace("T", " ").replace("Z", "")) if gasto.get("data") else None
                    ).first()
                    
                    if not existing:
                        db.add(ExpenseRecord(
                            leader_id=leader.id,
                            expense_type="CEAP",
                            amount=gasto.get("valor", 0),
                            currency="BRL",
                            date=datetime.fromisoformat(gasto.get("data", "").replace("T", " ").replace("Z", "")) if gasto.get("data") else None,
                            year=year,
                            supplier_name=gasto.get("fornecedor"),
                            description=gasto.get("descricao"),
                            receipt_url=gasto.get("urlNota"),
                            source="Senado Federal",
                            source_url=f"https://legis.senado.leg.br/senador/{senador_id}/gastos"
                        ))
                print(f"  Ingested {len(gastos)} senator expense records")
        
        db.commit()
        print(f"  OK {leader_name} data ingested")
        
    except Exception as e:
        print(f"  FAIL {leader_name} failed: {e}")
        db.rollback()
    finally:
        db.close()


async def ingest_all_brazilian_leaders(year: int = 2024):
    """Ingest data for all Brazilian leaders in the roster."""
    brazilian_leaders = [
        (slug, spec) for slug, spec in ROSTER.items() 
        if spec.country == "Brazil"
    ]
    
    print(f"Starting ingestion for {len(brazilian_leaders)} Brazilian leaders for year {year}...")
    
    for slug, spec in brazilian_leaders:
        await ingest_brazilian_leader_data(spec.name, year)
    
    print("Brazilian data ingestion complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest Brazilian official government data")
    parser.add_argument("--year", type=int, default=2024, help="Year to ingest (default: 2024)")
    parser.add_argument("--leader", type=str, help="Specific leader name to ingest (optional)")
    
    args = parser.parse_args()
    
    if args.leader:
        asyncio.run(ingest_brazilian_leader_data(args.leader, args.year))
    else:
        asyncio.run(ingest_all_brazilian_leaders(args.year))
