"""Which alerts a run triggered, and the message that carries each one to the notifier."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class AlertEvent:
    alert_id: int
    email: str
    barcode: str
    name: str
    price: float
    previous_price: float
    chain: str
    store: str

    def to_json(self) -> bytes:
        return json.dumps(asdict(self), ensure_ascii=False).encode()

    @classmethod
    def from_json(cls, data: bytes) -> "AlertEvent":
        return cls(**json.loads(data))


_TRIGGERED = """
WITH drops AS (
    -- Prices that changed in this run, with the price the same store had before.
    SELECT h.store_pk, h.barcode, h.price,
           (SELECT p.price FROM price_history p WHERE p.store_pk = h.store_pk AND p.barcode = h.barcode
            AND p.observed_at < h.observed_at ORDER BY p.observed_at DESC LIMIT 1) AS previous_price
    FROM price_history h
    WHERE h.observed_at = :observed_at
),
best AS (
    SELECT DISTINCT ON (d.barcode) d.* FROM drops d
    WHERE d.previous_price IS NOT NULL AND d.price < d.previous_price
    ORDER BY d.barcode, d.price
)
SELECT a.id AS alert_id, u.email, b.barcode, i.name, b.price, b.previous_price, ch.name AS chain, s.name AS store
FROM price_alerts a
JOIN users u ON u.id = a.user_id
JOIN best b ON b.barcode = a.barcode
JOIN items i ON i.barcode = b.barcode
JOIN stores s ON s.id = b.store_pk
JOIN chains ch ON ch.id = s.chain_id
WHERE (a.target_price IS NULL OR b.price <= a.target_price)
  AND (a.last_notified_at IS NULL OR a.last_notified_at < :observed_at)
ORDER BY a.id
"""


def find_triggered_alerts(session: Session, observed_at: datetime) -> list[AlertEvent]:
    """An alert fires when a store's price dropped in this run, and reached the target if one is set."""
    rows = session.execute(text(_TRIGGERED), {"observed_at": observed_at}).mappings()
    return [AlertEvent(**{**r, "price": float(r["price"]), "previous_price": float(r["previous_price"])}) for r in rows]


def mark_notified(session: Session, alert_ids: list[int], when: datetime) -> None:
    if alert_ids:
        session.execute(text("UPDATE price_alerts SET last_notified_at = :w WHERE id = ANY(:ids)"), {"w": when, "ids": alert_ids})
        session.commit()
