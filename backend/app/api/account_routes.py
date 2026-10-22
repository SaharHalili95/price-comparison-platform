from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.grocery import PriceAlert, SavedBasket
from app.models.user import User

router = APIRouter(prefix="/api", tags=["account"])


class AlertRequest(BaseModel):
    barcode: str
    target_price: Decimal | None = Field(default=None, gt=0)


class BasketBody(BaseModel):
    barcodes: list[str] = Field(max_length=100)


@router.get("/alerts")
def list_alerts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        text(
            "SELECT a.id, a.barcode, i.name, a.target_price, (SELECT min(price) FROM current_prices c WHERE c.barcode = a.barcode) "
            "AS current_min_price FROM price_alerts a JOIN items i ON i.barcode = a.barcode WHERE a.user_id = :u ORDER BY a.id"
        ),
        {"u": user.id},
    ).mappings()
    return [
        {**r, "target_price": float(r["target_price"]) if r["target_price"] is not None else None,
         "current_min_price": float(r["current_min_price"]) if r["current_min_price"] is not None else None}
        for r in rows
    ]


@router.post("/alerts", status_code=201)
def create_alert(body: AlertRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.execute(text("SELECT 1 FROM items WHERE barcode = :b"), {"b": body.barcode}).first() is None:
        raise HTTPException(status_code=404, detail="Item not found")
    alert = db.query(PriceAlert).filter_by(user_id=user.id, barcode=body.barcode).first() or PriceAlert(user_id=user.id, barcode=body.barcode)
    alert.target_price = body.target_price
    db.add(alert)
    db.commit()
    return {"id": alert.id}


@router.delete("/alerts/{alert_id}", status_code=204)
def delete_alert(alert_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Scoped to the signed-in user, so one user cannot delete another's alert by guessing its id.
    db.query(PriceAlert).filter_by(id=alert_id, user_id=user.id).delete()
    db.commit()
    return Response(status_code=204)


@router.get("/basket")
def get_basket(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    basket = db.get(SavedBasket, user.id)
    return {"barcodes": basket.barcodes if basket else []}


@router.put("/basket")
def save_basket(body: BasketBody, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    basket = db.get(SavedBasket, user.id) or SavedBasket(user_id=user.id)
    basket.barcodes = list(dict.fromkeys(body.barcodes))
    db.add(basket)
    db.commit()
    return {"barcodes": basket.barcodes}
