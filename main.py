from fastapi import FastAPI, HTTPException, Body
from sqlalchemy import create_engine, Column, String, Integer, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import random
import string

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, index=True)
    custom_slug = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/shorten")
async def shorten_url(original_url: str, custom_slug: str = Body(None)):
    db = SessionLocal()
    if custom_slug:
        existing_link = db.query(Link).filter(Link.custom_slug == custom_slug).first()
        if existing_link:
            raise HTTPException(status_code=400, detail="Custom slug already in use")
    else:
        custom_slug = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    new_link = Link(original_url=original_url, custom_slug=custom_slug)
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return {"shortened_url": f"/shorten/{new_link.custom_slug}"}