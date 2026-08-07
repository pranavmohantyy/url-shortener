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
    click_count = Column(Integer, default=0)
    expiration_date = Column(DateTime)

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/{slug}")
async def redirect_to_url(slug: str):
    db = SessionLocal()
    link = db.query(Link).filter(Link.slug == slug).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    link.click_count += 1
    db.commit()
    db.refresh(link)
    return {"redirect": link.original_url}
