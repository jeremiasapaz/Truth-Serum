"""API endpoints for voting records."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Leader, VotingRecord

router = APIRouter(prefix="/api/voting", tags=["voting"])


@router.get("/leader/{leader_id}")
async def get_leader_voting_records(leader_id: int, db: Session = Depends(get_db)):
    """Get all voting records for a specific leader."""
    records = db.query(VotingRecord).filter(VotingRecord.leader_id == leader_id).all()
    return {
        "leader_id": leader_id,
        "total": len(records),
        "records": [
            {
                "id": r.id,
                "proposal_id": r.proposal_id,
                "proposal_title": r.proposal_title,
                "vote": r.vote,
                "vote_date": r.vote_date.isoformat() if r.vote_date else None,
                "source": r.source,
                "source_url": r.source_url,
            }
            for r in records
        ]
    }


@router.get("/leader/{leader_id}/year/{year}")
async def get_leader_voting_by_year(leader_id: int, year: int, db: Session = Depends(get_db)):
    """Get voting records for a specific leader and year."""
    records = db.query(VotingRecord).filter(
        VotingRecord.leader_id == leader_id,
        VotingRecord.vote_date != None
    ).all()
    
    # Filter by year
    filtered = [r for r in records if r.vote_date and r.vote_date.year == year]
    
    return {
        "leader_id": leader_id,
        "year": year,
        "total": len(filtered),
        "records": [
            {
                "id": r.id,
                "proposal_id": r.proposal_id,
                "proposal_title": r.proposal_title,
                "vote": r.vote,
                "vote_date": r.vote_date.isoformat() if r.vote_date else None,
                "source": r.source,
                "source_url": r.source_url,
            }
            for r in filtered
        ]
    }
