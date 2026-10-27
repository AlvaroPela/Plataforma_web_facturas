"""Punto de entrada de la API."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import auth

app = FastAPI(title="Plataforma de Facturas - API", version="0.1.0")

# Permite que React (otro puerto/dominio) consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origenes,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def manejar_validacion(request: Request, exc: RequestValidationError):
    """Devuelve el mensaje en español de la HU en vez del error técnico de Pydantic."""
    mensaje = "Error en los campos ingresados"
    for error in exc.errors():
        if error.get("type") == "value_error":
            mensaje = str(error.get("ctx", {}).get("error", mensaje))
            break
    return JSONResponse(status_code=422, content={"detail": mensaje})


app.include_router(auth.router)


@app.get("/salud", tags=["Sistema"])
def salud():
    return {"estado": "ok"}
