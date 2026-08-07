from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, String, Integer, DateTime
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
    slug = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/shorten")
async def shorten_url(original_url: str):
    slug = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    db = SessionLocal()
    db.add(Link(original_url=original_url, slug=slug))
    db.commit()
    db.refresh(link)
    return {"short_url": f"http://short.url/{slug}"}