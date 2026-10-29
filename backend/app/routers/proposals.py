"""API endpoints for proposal/legislation tracking."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Leader, Proposal

router = APIRouter(prefix="/api/proposals", tags=["proposals"])


@router.get("/leader/{leader_id}")
async def get_leader_proposals(leader_id: int, db: Session = Depends(get_db)):
    """Get all proposals for a specific leader."""
    proposals = db.query(Proposal).filter(Proposal.leader_id == leader_id).all()
    return {
        "leader_id": leader_id,
        "total": len(proposals),
        "proposals": [
            {
                "id": p.id,
                "proposal_id": p.proposal_id,
                "title": p.title,
                "description": p.description,
                "type": p.type,
                "status": p.status,
                "presentation_date": p.presentation_date.isoformat() if p.presentation_date else None,
                "source": p.source,
                "source_url": p.source_url,
            }
            for p in proposals
        ]
    }


@router.get("/leader/{leader_id}/year/{year}")
async def get_leader_proposals_by_year(leader_id: int, year: int, db: Session = Depends(get_db)):
    """Get proposals for a specific leader and year."""
    proposals = db.query(Proposal).filter(
        Proposal.leader_id == leader_id,
        Proposal.presentation_date != None
    ).all()
    
    # Filter by year
    filtered = [p for p in proposals if p.presentation_date and p.presentation_date.year == year]
    
    return {
        "leader_id": leader_id,
        "year": year,
        "total": len(filtered),
        "proposals": [
            {
                "id": p.id,
                "proposal_id": p.proposal_id,
                "title": p.title,
                "description": p.description,
                "type": p.type,
                "status": p.status,
                "presentation_date": p.presentation_date.isoformat() if p.presentation_date else None,
                "source": p.source,
                "source_url": p.source_url,
            }
            for p in filtered
        ]
    }


@router.get("/all")
async def get_all_proposals(db: Session = Depends(get_db)):
    """Get all proposals organized by leader."""
    proposals = db.query(Proposal).all()
    
    by_leader = {}
    for p in proposals:
        if p.leader_id not in by_leader:
            by_leader[p.leader_id] = []
        by_leader[p.leader_id].append({
            "id": p.id,
            "proposal_id": p.proposal_id,
            "title": p.title,
            "type": p.type,
            "status": p.status,
            "presentation_date": p.presentation_date.isoformat() if p.presentation_date else None,
        })
    
    return {
        "total_leaders": len(by_leader),
        "total_proposals": len(proposals),
        "by_leader": by_leader
    }
