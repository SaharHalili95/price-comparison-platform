from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SourceEnum(str, Enum):
    """Available price sources - Israeli stores"""
    KSP = "KSP"
    BUG = "Bug"
    ZAP = "Zap"


class PriceInfo(BaseModel):
    """Price information from a specific source"""
    source: SourceEnum
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    currency: str = Field(default="₪", max_length=3)
    availability: bool = Field(default=True)
    url: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return round(v, 2)

    class Config:
        json_schema_extra = {
            "example": {
                "source": "KSP",
                "price": 299.90,
                "currency": "₪",
                "availability": True,
                "url": "https://ksp.co.il/web/item/12345",
                "last_updated": "2026-01-12T10:30:00"
            }
        }


class ProductBase(BaseModel):
    """Base product schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    pass


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductWithPrices(ProductResponse):
    """Product with price comparison from multiple sources"""
    prices: List[PriceInfo]
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    average_price: Optional[float] = None

    @validator('lowest_price', 'highest_price', 'average_price')
    def round_prices(cls, v):
        return round(v, 2) if v is not None else None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Samsung Galaxy S24 Ultra",
                "description": "סמארטפון דגל עם מסך 6.8 אינץ'",
                "category": "אלקטרוניקה",
                "created_at": "2026-01-12T10:00:00",
                "updated_at": "2026-01-12T10:00:00",
                "prices": [
                    {
                        "source": "KSP",
                        "price": 3999.0,
                        "currency": "₪",
                        "availability": True,
                        "url": "https://ksp.co.il/web/item/12345"
                    }
                ],
                "lowest_price": 3799.0,
                "highest_price": 4199.0,
                "average_price": 3999.0
            }
        }


class SearchResponse(BaseModel):
    """Search response with products"""
    query: str
    total_results: int
    products: List[ProductWithPrices]

    class Config:
        json_schema_extra = {
            "example": {
                "query": "wireless mouse",
                "total_results": 5,
                "products": []
            }
        }
