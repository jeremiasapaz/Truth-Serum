"""API endpoints for user authentication and subscription management."""
from datetime import UTC, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import User, Subscription

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Move to env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    subscription_tier: str
    subscription_status: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class SubscriptionResponse(BaseModel):
    name: str
    display_name: str
    description: str
    price_monthly: float
    price_yearly: Optional[float]
    features: dict


# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# Endpoints
@router.post("/signup", response_model=Token)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
        subscription_tier="free",
        subscription_status="active",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": new_user.email})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            subscription_tier=new_user.subscription_tier,
            subscription_status=new_user.subscription_status,
        ),
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            subscription_tier=user.subscription_tier,
            subscription_status=user.subscription_status,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        subscription_tier=current_user.subscription_tier,
        subscription_status=current_user.subscription_status,
    )


@router.get("/subscriptions", response_model=list[SubscriptionResponse])
async def list_subscriptions(db: Session = Depends(get_db)):
    """List available subscription plans."""
    subscriptions = db.query(Subscription).all()
    return [
        SubscriptionResponse(
            name=sub.name,
            display_name=sub.display_name,
            description=sub.description,
            price_monthly=sub.price_monthly,
            price_yearly=sub.price_yearly,
            features={
                "max_api_calls_per_month": sub.max_api_calls_per_month,
                "max_comparisons": sub.max_comparisons,
                "max_reports": sub.max_reports,
                "has_ads": sub.has_ads,
                "has_advanced_analytics": sub.has_advanced_analytics,
                "has_api_access": sub.has_api_access,
                "has_data_export": sub.has_data_export,
                "has_custom_reports": sub.has_custom_reports,
                "has_real_time_alerts": sub.has_real_time_alerts,
            },
        )
        for sub in subscriptions
    ]
