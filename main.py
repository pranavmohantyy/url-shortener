from fastapi import FastAPI, HTTPException, Body
from sqlalchemy import create_engine, Column, String, Integer, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
import string

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    click_count = Column(Integer, default=0)
    recent_clicks = Column(String)  # Store timestamps as comma-separated string

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/{slug}/stats")
async def get_link_stats(slug: str):
    db = SessionLocal()
    link = db.query(Link).filter(Link.slug == slug).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    recent_clicks = link.recent_clicks.split(",") if link.recent_clicks else []
    return {
        "click_count": link.click_count,
        "created_at": link.created_at,
        "expires_at": link.expires_at,
        "recent_clicks": recent_clicks
    }