"""Schémas Pydantic de l'API."""

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    """Données d'entrée de l'endpoint /predict."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "surface": 45.0,
                "nombre_pieces": 2,
                "code_postal": "94270",
                "annee": 2025,
            }
        }
    )

    surface: float = Field(..., gt=9, le=500, description="Surface en m²")
    nombre_pieces: int = Field(..., ge=1, le=10, description="Nombre de pièces")
    code_postal: str = Field(..., pattern=r"^\d{5}$", description="Code postal")
    annee: int = Field(..., ge=2014, le=2100, description="Année de la vente")


class PredictionResponse(BaseModel):
    """Réponse de l'endpoint /predict."""

    prix_m2: float
    prix_estime: float


class HealthResponse(BaseModel):
    """Réponse de l'endpoint /health."""

    status: str
    model_loaded: bool
