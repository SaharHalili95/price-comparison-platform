from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# price_history is a monthly-partitioned table created in migration 0002 and written with SQL in the
# loader, so it has no ORM class.


class Chain(Base):
    __tablename__ = "chains"

    id: Mapped[str] = mapped_column(String(13), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(Text)
    portal: Mapped[str] = mapped_column(String(20))


class Store(Base):
    __tablename__ = "stores"
    __table_args__ = (UniqueConstraint("chain_id", "sub_chain_id", "store_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chain_id: Mapped[str] = mapped_column(ForeignKey("chains.id"))
    sub_chain_id: Mapped[str] = mapped_column(String(10))
    store_id: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(Text)
    address: Mapped[str] = mapped_column(Text, default="")
    city: Mapped[str] = mapped_column(Text, default="", index=True)


class Item(Base):
    __tablename__ = "items"

    barcode: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    manufacturer: Mapped[str] = mapped_column(Text, default="")
    unit_of_measure: Mapped[str] = mapped_column(Text, default="")
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    is_weighted: Mapped[bool] = mapped_column(Boolean, default=False)


class CurrentPrice(Base):
    __tablename__ = "current_prices"

    store_pk: Mapped[int] = mapped_column(ForeignKey("stores.id"), primary_key=True)
    barcode: Mapped[str] = mapped_column(ForeignKey("items.barcode"), primary_key=True, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    price_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chain_id: Mapped[str] = mapped_column(ForeignKey("chains.id"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(10))
    newest_file_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    files_ok: Mapped[int] = mapped_column(Integer, default=0)
    files_failed: Mapped[int] = mapped_column(Integer, default=0)
    items: Mapped[int] = mapped_column(Integer, default=0)
    price_changes: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[list[dict[str, str]]] = mapped_column(JSONB, default=list)
