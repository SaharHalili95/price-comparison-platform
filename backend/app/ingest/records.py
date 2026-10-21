from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class StoreRecord:
    chain_id: str
    sub_chain_id: str
    store_id: str
    name: str
    address: str
    city: str


@dataclass(frozen=True)
class PriceRecord:
    chain_id: str
    sub_chain_id: str
    store_id: str
    barcode: str
    name: str
    manufacturer: str
    unit_of_measure: str
    quantity: Decimal | None
    is_weighted: bool
    price: Decimal
    unit_price: Decimal | None
    price_updated_at: datetime | None
