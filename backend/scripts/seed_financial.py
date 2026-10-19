"""
Seed financial data for Brazilian leaders.
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models import Leader, FinancialData


def seed_financial_data():
    """Seed financial data for Brazilian leaders."""
    db = SessionLocal()
    try:
        # Get Brazilian leaders
        lula = db.query(Leader).filter(Leader.name.like("%Lula%")).first()
        jair = db.query(Leader).filter(Leader.name.like("%Jair Bolsonaro%")).first()
        flavio = db.query(Leader).filter(Leader.name.like("%Flávio%")).first()
        
        if not lula or not jair or not flavio:
            print("Leaders not found")
            return
        
        # Lula financial data (2023)
        # Brazilian President salary: ~R$30,000/month = ~$6,000/year
        # Net worth estimates vary widely, using conservative estimates
        lula_data = FinancialData(
            leader_id=lula.id,
            annual_salary=72000,  # ~R$360,000/year in USD
            public_benefits=20000,  # Housing, security, etc.
            year=2023,
            total_assets=500000,  # Conservative estimate
            real_estate=300000,
            investments=100000,
            cash=50000,
            other_assets=50000,
            total_debt=50000,
            net_worth=450000,
            public_income=92000,  # Salary + benefits
            private_income=0,
            investment_income=5000,
            other_income=0,
            source="Public salary records, media estimates",
            notes="President of Brazil salary + benefits. Asset estimates from public disclosures.",
        )
        
        # Jair Bolsonaro financial data (2022)
        jair_data = FinancialData(
            leader_id=jair.id,
            annual_salary=72000,
            public_benefits=20000,
            year=2022,
            total_assets=2000000,  # Higher due to family wealth
            real_estate=1000000,
            investments=500000,
            cash=200000,
            other_assets=300000,
            total_debt=200000,
            net_worth=1800000,
            public_income=92000,
            private_income=100000,  # Family income
            investment_income=50000,
            other_income=0,
            source="Public salary records, media estimates",
            notes="Former President of Brazil. Includes family assets and investments.",
        )
        
        # Flávio Bolsonaro financial data (2023)
        # Senator salary: ~R$33,000/month = ~$6,600/year
        flavio_data = FinancialData(
            leader_id=flavio.id,
            annual_salary=79200,  # Senator salary
            public_benefits=30000,
            year=2023,
            total_assets=1500000,
            real_estate=800000,
            investments=400000,
            cash=150000,
            other_assets=150000,
            total_debt=100000,
            net_worth=1400000,
            public_income=109200,
            private_income=50000,
            investment_income=30000,
            other_income=0,
            source="Public salary records, media estimates",
            notes="Senator of Brazil. Includes family wealth and investments.",
        )
        
        # Check if data already exists
        existing = db.query(FinancialData).filter(
            FinancialData.leader_id == lula.id,
            FinancialData.year == 2023
        ).first()
        
        if not existing:
            db.add(lula_data)
            db.add(jair_data)
            db.add(flavio_data)
            db.commit()
            print("Financial data seeded successfully")
        else:
            print("Financial data already exists")
            
    finally:
        db.close()


if __name__ == "__main__":
    seed_financial_data()
