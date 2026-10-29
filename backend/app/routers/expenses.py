"""API endpoints for detailed expense tracking with supplier information."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Leader, ExpenseRecord

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.get("/leader/{leader_id}")
async def get_leader_expenses(leader_id: int, db: Session = Depends(get_db)):
    """Get all expense records for a specific leader."""
    expenses = db.query(ExpenseRecord).filter(ExpenseRecord.leader_id == leader_id).all()
    return {
        "leader_id": leader_id,
        "total": len(expenses),
        "expenses": [
            {
                "id": e.id,
                "expense_type": e.expense_type,
                "amount": e.amount,
                "currency": e.currency,
                "date": e.date.isoformat() if e.date else None,
                "year": e.year,
                "supplier_name": e.supplier_name,
                "supplier_cnpj": e.supplier_cnpj,
                "description": e.description,
                "receipt_url": e.receipt_url,
                "source": e.source,
                "source_url": e.source_url,
            }
            for e in expenses
        ]
    }


@router.get("/leader/{leader_id}/year/{year}")
async def get_leader_expenses_by_year(leader_id: int, year: int, db: Session = Depends(get_db)):
    """Get expenses for a specific leader and year."""
    expenses = db.query(ExpenseRecord).filter(
        ExpenseRecord.leader_id == leader_id,
        ExpenseRecord.year == year
    ).all()
    
    total_amount = sum(e.amount for e in expenses if e.amount)
    
    return {
        "leader_id": leader_id,
        "year": year,
        "total_expenses": len(expenses),
        "total_amount": total_amount,
        "expenses": [
            {
                "id": e.id,
                "expense_type": e.expense_type,
                "amount": e.amount,
                "currency": e.currency,
                "date": e.date.isoformat() if e.date else None,
                "supplier_name": e.supplier_name,
                "supplier_cnpj": e.supplier_cnpj,
                "description": e.description,
                "receipt_url": e.receipt_url,
                "source": e.source,
                "source_url": e.source_url,
            }
            for e in expenses
        ]
    }


@router.get("/leader/{leader_id}/summary")
async def get_leader_expense_summary(leader_id: int, db: Session = Depends(get_db)):
    """Get expense summary by year and type for a leader."""
    expenses = db.query(ExpenseRecord).filter(ExpenseRecord.leader_id == leader_id).all()
    
    summary = {}
    for e in expenses:
        year = e.year
        if year not in summary:
            summary[year] = {"total": 0, "by_type": {}}
        
        summary[year]["total"] += e.amount or 0
        
        exp_type = e.expense_type or "other"
        if exp_type not in summary[year]["by_type"]:
            summary[year]["by_type"][exp_type] = 0
        summary[year]["by_type"][exp_type] += e.amount or 0
    
    return {
        "leader_id": leader_id,
        "summary": summary
    }
