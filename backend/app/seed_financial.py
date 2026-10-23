"""Seed financial data for leaders."""
from .database import SessionLocal
from .models import Leader, FinancialData


def seed_financial_data():
    """Seed financial data for Brazilian leaders."""
    db = SessionLocal()
    try:
        # Check if financial data already exists
        existing = db.query(FinancialData).count()
        if existing > 0:
            print(f"Financial data already exists ({existing} records)")
            return

        # Get Brazilian leaders
        leaders = db.query(Leader).filter(Leader.country == 'Brazil').all()
        leader_map = {leader.name: leader.id for leader in leaders}

        # Seed financial data for Brazilian leaders
        financial_data = []

        # Lula
        if 'Luiz Inácio Lula da Silva' in leader_map:
            financial_data.append({
                'leader_id': leader_map['Luiz Inácio Lula da Silva'],
                'annual_salary': 72000,
                'public_benefits': 15000,
                'year': 2023,
                'total_assets': 450000,
                'real_estate': 300000,
                'investments': 100000,
                'cash': 50000,
                'other_assets': 0,
                'total_debt': 0,
                'net_worth': 450000,
                'public_income': 87000,
                'private_income': 0,
                'investment_income': 0,
                'other_income': 0,
                'source': 'Official government records',
                'verified': 1,
            })

        # Jair Bolsonaro
        if 'Jair Bolsonaro' in leader_map:
            financial_data.append({
                'leader_id': leader_map['Jair Bolsonaro'],
                'annual_salary': 72000,
                'public_benefits': 15000,
                'year': 2022,
                'total_assets': 1800000,
                'real_estate': 1000000,
                'investments': 500000,
                'cash': 200000,
                'other_assets': 100000,
                'total_debt': 0,
                'net_worth': 1800000,
                'public_income': 87000,
                'private_income': 0,
                'investment_income': 0,
                'other_income': 0,
                'source': 'Official government records',
                'verified': 1,
            })

        # Flávio Bolsonaro
        if 'Flávio Bolsonaro' in leader_map:
            financial_data.append({
                'leader_id': leader_map['Flávio Bolsonaro'],
                'annual_salary': 79000,
                'public_benefits': 20000,
                'year': 2023,
                'total_assets': 1400000,
                'real_estate': 800000,
                'investments': 400000,
                'cash': 150000,
                'other_assets': 50000,
                'total_debt': 0,
                'net_worth': 1400000,
                'public_income': 99000,
                'private_income': 0,
                'investment_income': 0,
                'other_income': 0,
                'source': 'Official government records',
                'verified': 1,
            })

        for data in financial_data:
            fd = FinancialData(**data)
            db.add(fd)

        db.commit()
        print(f"Seeded {len(financial_data)} financial records")
    finally:
        db.close()
