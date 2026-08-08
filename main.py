from fastapi import FastAPI, HTTPException, Body, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sqlalchemy import create_engine, Column, String, Integer, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
import string
import httpx
from slowapi import Limiter
from slowapi.util import get_remote_address

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(HTTPSRedirectMiddleware)

limiter = Limiter(key_func=get_remote_address)

class URLShortener(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_slug = Column(String, unique=True, nullable=False)
    expiration_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

@app.post("/shorten")
async def shorten_url(url: str = Body(...), slug: str = Body(None), expiration: str = Body(None)):
    db = SessionLocal()
    if slug is None:
        slug = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    expiration_date = datetime.fromisoformat(expiration) if expiration else None
    new_url = URLShortener(original_url=url, short_slug=slug, expiration_date=expiration_date)
    db.add(new_url)
    db.commit()
    return {"shortened_url": f"http://localhost:8000/r/{slug}"}

@app.get("/r/{slug}")
async def redirect_to_url(slug: str):
    db = SessionLocal()
    url = db.query(URLShortener).filter(URLShortener.short_slug == slug).first()
    if url:
        if url.expiration_date and url.expiration_date < datetime.utcnow():
            raise HTTPException(status_code=404, detail="URL expired")
        return {"url": url.original_url}
    raise HTTPException(status_code=404, detail="URL not found")

@app.get("/analytics/{slug}")
async def get_analytics(slug: str):
    db = SessionLocal()
    url = db.query(URLShortener).filter(URLShortener.short_slug == slug).first()
    if url:
        return {"original_url": url.original_url, "created_at": url.created_at}
    raise HTTPException(status_code=404, detail="URL not found")
