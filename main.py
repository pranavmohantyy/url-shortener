from fastapi import FastAPI, HTTPException, Body, Depends
from sqlalchemy import create_engine, Column, String, Integer, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
import string
import httpx

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    url = Column(String)
    expiration = Column(DateTime)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class URLSchema:
    url: str

    @classmethod
    def validate(cls, value):
        if not value.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid URL scheme.")
        try:
            response = httpx.head(value, timeout=5)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="URL not reachable.")
        except httpx.RequestError:
            raise HTTPException(status_code=400, detail="URL not reachable.")
        return value

@app.post("/shorten")
async def create_link(url_schema: URLSchema = Body(...)):
    url = URLSchema.validate(url_schema.url)
    slug = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    new_link = Link(slug=slug, url=url, expiration=datetime.utcnow() + timedelta(days=30))
    db = SessionLocal()
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return {"slug": new_link.slug, "url": new_link.url}