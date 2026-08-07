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
    original_url = Column(String, nullable=False)
    short_url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    __table_args__ = (UniqueConstraint('short_url'),)

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/shorten/")
async def create_link(original_url: str = Body(...), expires_in_days: int = Body(0)):
    db = SessionLocal()
    short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days) if expires_in_days > 0 else None
    new_link = Link(original_url=original_url, short_url=short_url, expires_at=expires_at)
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return {"short_url": new_link.short_url}

@app.get("/{short_url}/")
async def redirect_link(short_url: str):
    db = SessionLocal()
    link = db.query(Link).filter(Link.short_url == short_url).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    if link.expires_at and link.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Link expired")
    return {"original_url": link.original_url}
