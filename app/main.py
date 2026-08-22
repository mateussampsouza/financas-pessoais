import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import engine, Base, SessionLocal
from app.seed import seed_default_categories
from app.routers import categories, transactions, summary

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite Database tables
    Base.metadata.create_all(bind=engine)
    # Seed initial categories if empty
    db = SessionLocal()
    try:
        seed_default_categories(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="Finanças Pessoais",
    description="Aplicativo de Finanças Pessoais Responsivo com Tema Escuro e SQLite",
    version="1.0.0",
    lifespan=lifespan
)

# API Routers
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(summary.router)

# Mount Static Files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))
