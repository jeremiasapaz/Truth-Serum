"""API endpoints for 'Who Represents Me' feature."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Leader

router = APIRouter(prefix="/api/representation", tags=["representation"])


@router.get("/location/{country}")
async def get_representatives_by_country(country: str, db: Session = Depends(get_db)):
    """Get all leaders representing a country."""
    leaders = db.query(Leader).filter(Leader.country == country).all()
    return {
        "country": country,
        "total": len(leaders),
        "leaders": [
            {
                "id": l.id,
                "name": l.name,
                "office": l.country,  # Will need to be updated with actual office
                "current": l.current,
                "political_affiliation": l.political_affiliation,
            }
            for l in leaders
        ]
    }


@router.get("/location/{country}/{region}")
async def get_representatives_by_region(country: str, region: str, db: Session = Depends(get_db)):
    """Get all leaders representing a country/region."""
    leaders = db.query(Leader).filter(
        Leader.country == country,
        Leader.region == region
    ).all()
    return {
        "country": country,
        "region": region,
        "total": len(leaders),
        "leaders": [
            {
                "id": l.id,
                "name": l.name,
                "office": l.country,
                "current": l.current,
                "political_affiliation": l.political_affiliation,
            }
            for l in leaders
        ]
    }


@router.get("/all")
async def get_all_representatives(db: Session = Depends(get_db)):
    """Get all leaders organized by country."""
    leaders = db.query(Leader).all()
    
    by_country = {}
    for l in leaders:
        if l.country not in by_country:
            by_country[l.country] = []
        by_country[l.country].append({
            "id": l.id,
            "name": l.name,
            "office": l.country,
            "current": l.current,
            "political_affiliation": l.political_affiliation,
        })
    
    return {
        "total_countries": len(by_country),
        "total_leaders": len(leaders),
        "countries": by_country
    }
