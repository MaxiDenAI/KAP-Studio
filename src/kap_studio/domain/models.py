
from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field

class JourneyAsset(BaseModel):
    position: int = Field(ge=1, le=7)
    type: str
    stage: str
    primary_message: str
    hero: str
    pattern: str
    goal: str
    hero_count: int = 1
    brand_footer: Literal["external_only"] = "external_only"

class Product(BaseModel):
    id: str
    name: str
    version: str
    manufacturer: str
    category: str
    archetype: str
    accent: str
    audience: str
    promise: str
    journey: List[JourneyAsset] = []

class BrandSettings(BaseModel):
    footer_mode: Literal["external_only"] = "external_only"
    safe_area_height_px: int = 280
    approved_asset_id: str | None = None

class KapProject(BaseModel):
    kap_version: str = "0.2.0"
    schema_version: str = "1.0"
    product: Product
    marketplace_profiles: List[str] = []
    brand: BrandSettings = BrandSettings()
    exported_at: str | None = None
