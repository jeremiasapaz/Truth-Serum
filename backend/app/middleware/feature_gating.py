"""Middleware for feature gating based on subscription tier."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User


def require_feature(feature: str):
    """Decorator to check if user has access to a specific feature."""
    def decorator(func):
        async def wrapper(*args, user: User, db: Session = next(get_db()), **kwargs):
            # Get user's subscription tier
            subscription = db.query(User).filter(User.id == user.id).first()
            if not subscription:
                raise HTTPException(status_code=401, detail="User not found")
            
            # Get subscription plan details
            from ..models import Subscription
            plan = db.query(Subscription).filter(Subscription.name == subscription.subscription_tier).first()
            
            # Check if feature is available
            if not hasattr(plan, f"has_{feature}"):
                raise HTTPException(status_code=400, detail=f"Invalid feature: {feature}")
            
            if not getattr(plan, f"has_{feature}"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This feature requires a {plan.display_name} subscription"
                )
            
            return await func(*args, user=user, db=db, **kwargs)
        return wrapper
    return decorator


def check_api_limit(user: User, db: Session):
    """Check if user has exceeded API call limit."""
    from ..models import Subscription
    plan = db.query(Subscription).filter(Subscription.name == user.subscription_tier).first()
    
    # Reset counter if new month
    from datetime import UTC, datetime
    now = datetime.now(UTC)
    if not user.api_calls_reset_date or user.api_calls_reset_date.month != now.month:
        user.api_calls_this_month = 0
        user.api_calls_reset_date = now
        db.commit()
    
    # Check limit
    if user.api_calls_this_month >= plan.max_api_calls_per_month:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"API limit exceeded. Maximum: {plan.max_api_calls_per_month} calls/month"
        )
    
    # Increment counter
    user.api_calls_this_month += 1
    db.commit()
