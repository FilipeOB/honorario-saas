from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from .config import settings
from .api.v1 import honorarios_router

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=settings.BACKEND_CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME, "version": settings.APP_VERSION}

@app.get("/", include_in_schema=False)
async def frontend():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({"nome": settings.APP_NAME, "docs": "/api/docs"})

app.include_router(honorarios_router, prefix=settings.API_V1_STR)

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})
