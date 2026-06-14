import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ....config import settings
from ....database import get_db
from ....models.user import User
from ....utils.email import send_credentials_email

router = APIRouter(prefix="/webhook", tags=["Webhook"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _generate_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%&"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _get_or_create_user(email: str, name: str, db: Session) -> tuple:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return existing, None
    password = _generate_password()
    user = User(
        email=email,
        name=name or "",
        hashed_password=pwd_context.hash(password),
        plan="pro",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, password


def _dispatch_email(email: str, name: str, password: str) -> None:
    send_credentials_email(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_user=settings.SMTP_USER,
        smtp_password=settings.SMTP_PASSWORD,
        smtp_from=settings.SMTP_FROM,
        smtp_from_name=settings.SMTP_FROM_NAME,
        app_url=settings.APP_URL,
        to_email=email,
        name=name,
        password=password,
    )


@router.post("/hotmart", summary="Webhook Hotmart")
async def webhook_hotmart(request: Request, db: Session = Depends(get_db)):
    if settings.HOTMART_HOTTOK:
        token = request.headers.get("X-Hotmart-Hottok", "")
        if token != settings.HOTMART_HOTTOK:
            raise HTTPException(status_code=401, detail="Token Hotmart invalido")
    body = await request.json()
    event = body.get("event", "PURCHASE_COMPLETE")
    if event not in ("PURCHASE_COMPLETE", "PURCHASE_APPROVED"):
        return {"ok": True, "skipped": True, "event": event}
    data = body.get("data", body)
    buyer = data.get("buyer", data.get("Buyer", {}))
    email = (buyer.get("email") or "").strip().lower()
    name = buyer.get("name") or buyer.get("full_name") or ""
    if not email:
        raise HTTPException(status_code=400, detail="Email do comprador nao encontrado")
    user, password = _get_or_create_user(email, name, db)
    if password:
        _dispatch_email(email, name, password)
    return {"ok": True, "user_id": str(user.id), "new_user": bool(password)}


@router.post("/kiwify", summary="Webhook Kiwify")
async def webhook_kiwify(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    order_status = body.get("order_status", "paid")
    if order_status != "paid":
        return {"ok": True, "skipped": True, "status": order_status}
    customer = body.get("Customer") or body.get("customer") or {}
    email = (customer.get("email") or "").strip().lower()
    name = customer.get("full_name") or customer.get("name") or ""
    if not email:
        raise HTTPException(status_code=400, detail="Email do comprador nao encontrado")
    user, password = _get_or_create_user(email, name, db)
    if password:
        _dispatch_email(email, name, password)
    return {"ok": True, "user_id": str(user.id), "new_user": bool(password)}
