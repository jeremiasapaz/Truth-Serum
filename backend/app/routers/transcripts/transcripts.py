"""API endpoints for speech transcripts."""
from datetime import UTC, datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Leader, SpeechTranscript

router = APIRouter(prefix="/api/transcripts", tags=["transcripts"])


# Pydantic models for request/response
class TranscriptCreate(BaseModel):
    leader_id: int
    platform: str
    video_url: str
    video_id: str | None = None
    title: str
    date: str | None = None
    location: str | None = None
    event: str | None = None
    transcript_text: str
    language: str = "en"
    submitted_by: str | None = None


class TranscriptResponse(BaseModel):
    id: int
    leader_id: int
    leader_name: str
    platform: str
    video_url: str
    video_id: str | None
    title: str
    date: str | None
    location: str | None
    event: str | None
    transcript_text: str
    language: str
    offense_categories: str | None
    flagged_quotes: str | None
    classification_confidence: float
    classified_by: str
    submitted_by: str | None
    verified: int
    created_at: str
    updated_at: str


@router.get("", response_model=List[TranscriptResponse])
def list_transcripts(
    leader_id: int | None = None,
    platform: str | None = None,
    verified_only: bool = False,
    db: Session = Depends(get_db),
):
    """List all speech transcripts with optional filters."""
    query = db.query(SpeechTranscript).join(Leader)
    
    if leader_id:
        query = query.filter(SpeechTranscript.leader_id == leader_id)
    if platform:
        query = query.filter(SpeechTranscript.platform == platform)
    if verified_only:
        query = query.filter(SpeechTranscript.verified == 1)
    
    transcripts = query.order_by(SpeechTranscript.created_at.desc()).all()
    
    return [
        TranscriptResponse(
            id=t.id,
            leader_id=t.leader_id,
            leader_name=t.leader.name,
            platform=t.platform,
            video_url=t.video_url,
            video_id=t.video_id,
            title=t.title,
            date=t.date.isoformat() if t.date else None,
            location=t.location,
            event=t.event,
            transcript_text=t.transcript_text,
            language=t.language,
            offense_categories=t.offense_categories,
            flagged_quotes=t.flagged_quotes,
            classification_confidence=t.classification_confidence,
            classified_by=t.classified_by,
            submitted_by=t.submitted_by,
            verified=t.verified,
            created_at=t.created_at.isoformat(),
            updated_at=t.updated_at.isoformat(),
        )
        for t in transcripts
    ]


@router.get("/{transcript_id}", response_model=TranscriptResponse)
def get_transcript(transcript_id: int, db: Session = Depends(get_db)):
    """Get a single transcript by ID."""
    transcript = db.query(SpeechTranscript).filter(SpeechTranscript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    return TranscriptResponse(
        id=transcript.id,
        leader_id=transcript.leader_id,
        leader_name=transcript.leader.name,
        platform=transcript.platform,
        video_url=transcript.video_url,
        video_id=transcript.video_id,
        title=transcript.title,
        date=transcript.date.isoformat() if transcript.date else None,
        location=transcript.location,
        event=transcript.event,
        transcript_text=transcript.transcript_text,
        language=transcript.language,
        offense_categories=transcript.offense_categories,
        flagged_quotes=transcript.flagged_quotes,
        classification_confidence=transcript.classification_confidence,
        classified_by=transcript.classified_by,
        submitted_by=transcript.submitted_by,
        verified=transcript.verified,
        created_at=transcript.created_at.isoformat(),
        updated_at=transcript.updated_at.isoformat(),
    )


@router.post("", response_model=TranscriptResponse)
def create_transcript(transcript: TranscriptCreate, db: Session = Depends(get_db)):
    """Create a new speech transcript (manual submission)."""
    # Verify leader exists
    leader = db.query(Leader).filter(Leader.id == transcript.leader_id).first()
    if not leader:
        raise HTTPException(status_code=404, detail="Leader not found")
    
    # Parse date if provided
    parsed_date = None
    if transcript.date:
        try:
            parsed_date = datetime.fromisoformat(transcript.date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    new_transcript = SpeechTranscript(
        leader_id=transcript.leader_id,
        platform=transcript.platform,
        video_url=transcript.video_url,
        video_id=transcript.video_id,
        title=transcript.title,
        date=parsed_date,
        location=transcript.location,
        event=transcript.event,
        transcript_text=transcript.transcript_text,
        language=transcript.language,
        submitted_by=transcript.submitted_by,
        classified_by="manual",
    )
    
    db.add(new_transcript)
    db.commit()
    db.refresh(new_transcript)
    
    return TranscriptResponse(
        id=new_transcript.id,
        leader_id=new_transcript.leader_id,
        leader_name=new_transcript.leader.name,
        platform=new_transcript.platform,
        video_url=new_transcript.video_url,
        video_id=new_transcript.video_id,
        title=new_transcript.title,
        date=new_transcript.date.isoformat() if new_transcript.date else None,
        location=new_transcript.location,
        event=new_transcript.event,
        transcript_text=new_transcript.transcript_text,
        language=new_transcript.language,
        offense_categories=new_transcript.offense_categories,
        flagged_quotes=new_transcript.flagged_quotes,
        classification_confidence=new_transcript.classification_confidence,
        classified_by=new_transcript.classified_by,
        submitted_by=new_transcript.submitted_by,
        verified=new_transcript.verified,
        created_at=new_transcript.created_at.isoformat(),
        updated_at=new_transcript.updated_at.isoformat(),
    )


@router.put("/{transcript_id}", response_model=TranscriptResponse)
def update_transcript(
    transcript_id: int,
    verified: int | None = None,
    db: Session = Depends(get_db),
):
    """Update a transcript (currently only verification status)."""
    transcript = db.query(SpeechTranscript).filter(SpeechTranscript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    if verified is not None:
        transcript.verified = verified
        transcript.updated_at = datetime.now(UTC)
    
    db.commit()
    db.refresh(transcript)
    
    return TranscriptResponse(
        id=transcript.id,
        leader_id=transcript.leader_id,
        leader_name=transcript.leader.name,
        platform=transcript.platform,
        video_url=transcript.video_url,
        video_id=transcript.video_id,
        title=transcript.title,
        date=transcript.date.isoformat() if transcript.date else None,
        location=transcript.location,
        event=transcript.event,
        transcript_text=transcript.transcript_text,
        language=transcript.language,
        offense_categories=transcript.offense_categories,
        flagged_quotes=transcript.flagged_quotes,
        classification_confidence=transcript.classification_confidence,
        classified_by=transcript.classified_by,
        submitted_by=transcript.submitted_by,
        verified=transcript.verified,
        created_at=transcript.created_at.isoformat(),
        updated_at=transcript.updated_at.isoformat(),
    )


@router.delete("/{transcript_id}")
def delete_transcript(transcript_id: int, db: Session = Depends(get_db)):
    """Delete a transcript."""
    transcript = db.query(SpeechTranscript).filter(SpeechTranscript.id == transcript_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    db.delete(transcript)
    db.commit()
    
    return {"message": "Transcript deleted"}
