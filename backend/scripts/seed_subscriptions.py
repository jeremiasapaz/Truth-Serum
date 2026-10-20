"""
Seed subscription plans into the database.
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models import Subscription


def seed_subscriptions():
    """Seed subscription plans."""
    db = SessionLocal()
    try:
        # Check if subscriptions already exist
        existing = db.query(Subscription).first()
        if existing:
            print("Subscriptions already exist")
            return
        
        # Create subscription plans
        plans = [
            Subscription(
                name="free",
                display_name="Free",
                description="Basic access with limited features",
                price_monthly=0,
                price_yearly=0,
                max_api_calls_per_month=100,
                max_comparisons=5,
                max_reports=0,
                has_ads=True,
                has_advanced_analytics=False,
                has_api_access=False,
                has_data_export=False,
                has_custom_reports=False,
                has_real_time_alerts=False,
            ),
            Subscription(
                name="pro",
                display_name="Pro",
                description="Advanced analytics and unlimited comparisons",
                price_monthly=9,
                price_yearly=90,
                max_api_calls_per_month=10000,
                max_comparisons=999,
                max_reports=10,
                has_ads=False,
                has_advanced_analytics=True,
                has_api_access=True,
                has_data_export=True,
                has_custom_reports=True,
                has_real_time_alerts=False,
            ),
            Subscription(
                name="enterprise",
                display_name="Enterprise",
                description="Full API access and white-label options",
                price_monthly=99,
                price_yearly=990,
                max_api_calls_per_month=100000,
                max_comparisons=9999,
                max_reports=999,
                has_ads=False,
                has_advanced_analytics=True,
                has_api_access=True,
                has_data_export=True,
                has_custom_reports=True,
                has_real_time_alerts=True,
            ),
        ]
        
        for plan in plans:
            db.add(plan)
        
        db.commit()
        print("Subscription plans seeded successfully")
        
    finally:
        db.close()


if __name__ == "__main__":
    seed_subscriptions()
