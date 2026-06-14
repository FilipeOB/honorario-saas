"""
Aplicacao principal FastAPI - Sistema SaaS de Honorarios Advocaticios
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from .config import settings
from .api.v1 import honorarios_router, auth_router, user_router
from .database import init_db

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema SaaS de calculo e precificacao de honorarios advocaticios",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Inicializa banco de dados na subida da aplicacao"""
    db_path = os.environ.get("DATABASE_PATH", "./honorarios.db")
    db_dir = os.path.dirname(db_path)
    if db_dir and db_dir != ".":
        os.makedirs(db_dir, exist_ok=True)
    init_db()


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/", include_in_schema=False)
async def frontend():
    """Serve a calculadora (frontend HTML estatico)"""
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({"nome": settings.APP_NAME, "documentacao": "/api/docs"})


app.include_router(honorarios_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(user_router, prefix=settings.API_V1_STR)


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
