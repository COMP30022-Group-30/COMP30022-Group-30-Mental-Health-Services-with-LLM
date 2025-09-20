# Results framing and types of LLM interactions/responses
# Written by Vishay Chotai

from pydantic import BaseModel, Field
from typing import List, Optional

class Location(BaseModel):
    suburb: Optional[str] = None
    state: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

class ExtractionResult(BaseModel):
    intent: str = Field(description="search|chat")
    specialisation: Optional[str] = None
    location: Optional[Location] = None
    radius_km: Optional[int] = 15
    flags: List[str] = []

class Provider(BaseModel):
    id: str
    name: str
    specialisations: List[str] = []
    address: Optional[str] = None
    suburb: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    telehealth: Optional[bool] = None
    score: Optional[float] = None
    geo: Optional[dict] = None
    meta: Optional[dict] = None

class SearchRequest(BaseModel):
    query: str
    specialisation: Optional[str] = None
    location: Optional[Location] = None
    radius_km: Optional[int] = 15
    limit: int = 20

class SearchResponse(BaseModel):
    took_ms: int
    inferred: dict
    results: List[Provider]
