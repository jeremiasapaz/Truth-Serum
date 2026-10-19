"""API endpoints for financial transparency data."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Leader, FinancialData

router = APIRouter(prefix="/api/financial", tags=["financial"])


class FinancialDataCreate(BaseModel):
    leader_id: int
    annual_salary: float | None = None
    public_benefits: float | None = None
    year: int
    total_assets: float | None = None
    real_estate: float | None = None
    investments: float | None = None
    cash: float | None = None
    other_assets: float | None = None
    total_debt: float | None = None
    net_worth: float | None = None
    public_income: float | None = None
    private_income: float | None = None
    investment_income: float | None = None
    other_income: float | None = None
    source: str | None = None
    source_url: str | None = None
    notes: str | None = None


class FinancialDataResponse(BaseModel):
    id: int
    leader_id: int
    leader_name: str
    annual_salary: float | None
    public_benefits: float | None
    year: int
    total_assets: float | None
    real_estate: float | None
    investments: float | None
    cash: float | None
    other_assets: float | None
    total_debt: float | None
    net_worth: float | None
    public_income: float | None
    private_income: float | None
    investment_income: float | None
    other_income: float | None
    source: str | None
    source_url: str | None
    verified: int
    notes: str | None
    created_at: str
    updated_at: str


@router.get("", response_model=List[FinancialDataResponse])
def list_financial_data(
    leader_id: int | None = None,
    year: int | None = None,
    verified_only: bool = False,
    db: Session = Depends(get_db),
):
    """List all financial data with optional filters."""
    query = db.query(FinancialData).join(Leader)
    
    if leader_id:
        query = query.filter(FinancialData.leader_id == leader_id)
    if year:
        query = query.filter(FinancialData.year == year)
    if verified_only:
        query = query.filter(FinancialData.verified == 1)
    
    data = query.order_by(FinancialData.year.desc()).all()
    
    return [
        FinancialDataResponse(
            id=d.id,
            leader_id=d.leader_id,
            leader_name=d.leader.name,
            annual_salary=d.annual_salary,
            public_benefits=d.public_benefits,
            year=d.year,
            total_assets=d.total_assets,
            real_estate=d.real_estate,
            investments=d.investments,
            cash=d.cash,
            other_assets=d.other_assets,
            total_debt=d.total_debt,
            net_worth=d.net_worth,
            public_income=d.public_income,
            private_income=d.private_income,
            investment_income=d.investment_income,
            other_income=d.other_income,
            source=d.source,
            source_url=d.source_url,
            verified=d.verified,
            notes=d.notes,
            created_at=d.created_at.isoformat(),
            updated_at=d.updated_at.isoformat(),
        )
        for d in data
    ]


@router.get("/{data_id}", response_model=FinancialDataResponse)
def get_financial_data(data_id: int, db: Session = Depends(get_db)):
    """Get a single financial data entry by ID."""
    data = db.query(FinancialData).filter(FinancialData.id == data_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="Financial data not found")
    
    return FinancialDataResponse(
        id=data.id,
        leader_id=data.leader_id,
        leader_name=data.leader.name,
        annual_salary=data.annual_salary,
        public_benefits=data.public_benefits,
        year=data.year,
        total_assets=data.total_assets,
        real_estate=data.real_estate,
        investments=data.investments,
        cash=data.cash,
        other_assets=data.other_assets,
        total_debt=data.total_debt,
        net_worth=data.net_worth,
        public_income=data.public_income,
        private_income=data.private_income,
        investment_income=data.investment_income,
        other_income=data.other_income,
        source=data.source,
        source_url=data.source_url,
        verified=data.verified,
        notes=data.notes,
        created_at=data.created_at.isoformat(),
        updated_at=data.updated_at.isoformat(),
    )


@router.post("", response_model=FinancialDataResponse)
def create_financial_data(data: FinancialDataCreate, db: Session = Depends(get_db)):
    """Create new financial data entry."""
    leader = db.query(Leader).filter(Leader.id == data.leader_id).first()
    if not leader:
        raise HTTPException(status_code=404, detail="Leader not found")
    
    new_data = FinancialData(
        leader_id=data.leader_id,
        annual_salary=data.annual_salary,
        public_benefits=data.public_benefits,
        year=data.year,
        total_assets=data.total_assets,
        real_estate=data.real_estate,
        investments=data.investments,
        cash=data.cash,
        other_assets=data.other_assets,
        total_debt=data.total_debt,
        net_worth=data.net_worth,
        public_income=data.public_income,
        private_income=data.private_income,
        investment_income=data.investment_income,
        other_income=data.other_income,
        source=data.source,
        source_url=data.source_url,
        notes=data.notes,
    )
    
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    
    return FinancialDataResponse(
        id=new_data.id,
        leader_id=new_data.leader_id,
        leader_name=new_data.leader.name,
        annual_salary=new_data.annual_salary,
        public_benefits=new_data.public_benefits,
        year=new_data.year,
        total_assets=new_data.total_assets,
        real_estate=new_data.real_estate,
        investments=new_data.investments,
        cash=new_data.cash,
        other_assets=new_data.other_assets,
        total_debt=new_data.total_debt,
        net_worth=new_data.net_worth,
        public_income=new_data.public_income,
        private_income=new_data.private_income,
        investment_income=new_data.investment_income,
        other_income=new_data.other_income,
        source=new_data.source,
        source_url=new_data.source_url,
        verified=new_data.verified,
        notes=new_data.notes,
        created_at=new_data.created_at.isoformat(),
        updated_at=new_data.updated_at.isoformat(),
    )


@router.put("/{data_id}", response_model=FinancialDataResponse)
def update_financial_data(
    data_id: int,
    verified: int | None = None,
    db: Session = Depends(get_db),
):
    """Update financial data (currently only verification status)."""
    data = db.query(FinancialData).filter(FinancialData.id == data_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="Financial data not found")
    
    if verified is not None:
        data.verified = verified
    
    db.commit()
    db.refresh(data)
    
    return FinancialDataResponse(
        id=data.id,
        leader_id=data.leader_id,
        leader_name=data.leader.name,
        annual_salary=data.annual_salary,
        public_benefits=data.public_benefits,
        year=data.year,
        total_assets=data.total_assets,
        real_estate=data.real_estate,
        investments=data.investments,
        cash=data.cash,
        other_assets=data.other_assets,
        total_debt=data.total_debt,
        net_worth=data.net_worth,
        public_income=data.public_income,
        private_income=data.private_income,
        investment_income=data.investment_income,
        other_income=data.other_income,
        source=data.source,
        source_url=data.source_url,
        verified=data.verified,
        notes=data.notes,
        created_at=data.created_at.isoformat(),
        updated_at=data.updated_at.isoformat(),
    )


@router.delete("/{data_id}")
def delete_financial_data(data_id: int, db: Session = Depends(get_db)):
    """Delete financial data."""
    data = db.query(FinancialData).filter(FinancialData.id == data_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="Financial data not found")
    
    db.delete(data)
    db.commit()
    
    return {"message": "Financial data deleted"}
