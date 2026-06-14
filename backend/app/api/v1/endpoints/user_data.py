"""
Endpoints de dados do usuário:
  GET  /api/v1/user/settings   → busca configurações salvas
  PUT  /api/v1/user/settings   → salva configurações
  GET  /api/v1/user/history    → lista histórico de cálculos
  POST /api/v1/user/history    → salva um cálculo no histórico
  DELETE /api/v1/user/history/{id} → remove um item do histórico
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ....database import get_db
from ....models.user import User, UserSettings, CalculationHistory
from ....schemas.auth import UserSettingsSchema, HistoryItemIn, HistoryItemOut
from .auth import get_current_user

router = APIRouter(prefix="/user", tags=["Usuário"])


# ─── Configurações ──────────────────────────────────────────────

@router.get("/settings", response_model=UserSettingsSchema)
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not s:
        s = UserSettings(user_id=current_user.id)
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


@router.put("/settings", response_model=UserSettingsSchema)
def save_settings(
    body: UserSettingsSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not s:
        s = UserSettings(user_id=current_user.id)
        db.add(s)

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(s, field, value)

    db.commit()
    db.refresh(s)
    return s


# ─── Histórico ───────────────────────────────────────────────

@router.get("/history", response_model=List[HistoryItemOut])
def get_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(CalculationHistory)
        .filter(CalculationHistory.user_id == current_user.id)
        .order_by(CalculationHistory.created_at.desc())
        .limit(limit)
        .all()
    )


@router.post("/history", response_model=HistoryItemOut, status_code=201)
def add_history(
    body: HistoryItemIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = CalculationHistory(
        user_id=current_user.id,
        **body.model_dump()
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/history/{item_id}", status_code=204)
def delete_history(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(CalculationHistory)
        .filter(
            CalculationHistory.id == item_id,
            CalculationHistory.user_id == current_user.id,
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(item)
    db.commit()
