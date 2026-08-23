import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import Base, engine
from app.limiter import limiter
from app.routers import auth, categories, summary, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite Database tables (Users, Categories, Transactions)
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Finanças Pessoais",
    description="Aplicativo de Finanças Pessoais Responsivo com Tema Escuro, SQLite e Autenticação",
    version="2.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# API Routers
app.include_router(auth.router)
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
