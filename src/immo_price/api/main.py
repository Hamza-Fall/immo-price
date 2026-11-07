"""Application FastAPI : /health et /predict."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request

from immo_price.api.schemas import (
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
)
from immo_price.api.security import verify_api_key
from immo_price.config import get_settings
from immo_price.logging_config import setup_logging
from immo_price.predict import load_model, predict_price

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Charge le modèle au démarrage de l'application."""
    settings = get_settings()
    setup_logging(settings.log_level)
    try:
        app.state.model = load_model(settings.model_path)
        logger.info("Modèle chargé depuis %s", settings.model_path)
    except FileNotFoundError:
        logger.error("Modèle absent : lancez immo-train")
        app.state.model = None
    yield


app = FastAPI(
    title="Immo Price API",
    description="Estimation du prix d'un appartement à partir des données DVF.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    """Indique l'état du service et si le modèle est chargé."""
    loaded = getattr(request.app.state, "model", None) is not None
    return HealthResponse(status="ok", model_loaded=loaded)


@app.post(
    "/predict",
    response_model=PredictionResponse,
    dependencies=[Depends(verify_api_key)],
)
def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
    """Estime le prix d'un appartement (clé API requise)."""
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(503, "Modèle non chargé")
    result = predict_price(model, **payload.model_dump())
    logger.info("Prédiction effectuée pour le code postal %s", payload.code_postal)
    return PredictionResponse(**result)


def run() -> None:
    """Lance le serveur uvicorn en local."""
    uvicorn.run("immo_price.api.main:app", host="127.0.0.1", port=8000)
