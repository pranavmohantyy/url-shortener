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

limiter = Limiter(key_func=get_remote_address)

class Link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    slug = Column(String, index=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(HTTPSRedirectMiddleware)

@app.post("/shorten")
@limiter.limit("10/minute")
async def shorten_url(url: str = Body(...), slug: str = None, expires_in: int = None, request: Request):
    db = SessionLocal()
    if slug:
        existing_link = db.query(Link).filter(Link.slug == slug).first()
        if existing_link:
            raise HTTPException(status_code=400, detail="Slug already taken")
    else:
        slug = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=expires_in) if expires_in else None
    new_link = Link(url=url, slug=slug, expires_at=expires_at)
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    db.close()
    return {"slug": new_link.slug, "url": new_link.url}
