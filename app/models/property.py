from enum import Enum
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PropertyType(str, Enum):
    APARTMENT = "APARTMENT"
    VILLA = "VILLA"
    HOUSE = "HOUSE"
    PLOT = "PLOT"
    COMMERCIAL = "COMMERCIAL"
    LAND = "LAND"

class PropertyStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    SOLD = "SOLD"
    RENTED = "RENTED"
    PENDING = "PENDING"

class Property(BaseModel):
    property_id: Optional[int] = None
    user_id: int
    title: str
    description: str
    price: float
    location: str
    property_type: PropertyType
    status: PropertyStatus = PropertyStatus.AVAILABLE
    images: List[str] = []
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    year_built: Optional[int] = None
    amenities: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_featured: bool = False
    views: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    city: str
    state: str
    country: str
    zip_code: Optional[str] = None
    is_active: bool = True

    class Config:
        orm_mode = True
        use_enum_values = True 