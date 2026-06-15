"""
Endpoints de autenticação:
  POST /api/v1/auth/login          → retorna JWT
  GET  /api/v1/auth/me             → dados do usuário logado
  POST /api/v1/auth/create-user    → admin cria conta pós-pagamento
"""
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext
from ....database import get_db
from ....models.user import User, UserSettings
from ....schemas.auth import (
    LoginRequest, TokenResponse, CreateUserRequest, UserOut
)
from ....config import settings

router = APIRouter(prefix="/auth", tags=["Autenticação"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Helpers JWT ──────────────────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: str, email: str) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": user_id, "email": email, "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> User:
    """Dependency: extrai e valida JWT do header Authorization: Bearer <token>"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer":
            raise credentials_exception
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise credentials_exception
    return user


# ─── Endpoints ───────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Login com e-mail e senha → retorna JWT (validade: 7 dias)"""
    user = db.query(User).filter(User.email == body.email.lower().strip()).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta inativa. Entre em contato com o suporte.",
        )
    user.last_login = datetime.utcnow()
    db.commit()
    token = create_token(user.id, user.email)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        email=user.email,
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    """Retorna dados do usuário autenticado"""
    return current_user


@router.post("/create-user", response_model=UserOut, status_code=201)
def create_user(
    body: CreateUserRequest,
    x_admin_secret: str = Header(..., alias="x-admin-secret"),
    db: Session = Depends(get_db),
):
    """
    Cria uma conta de usuário. Requer header x-admin-secret.
    Pode ser chamado manualmente ou por webhook de pagamento.
    """
    admin_secret = os.environ.get("ADMIN_SECRET_KEY", "")
    if not admin_secret or x_admin_secret != admin_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado",
        )
    email = body.email.lower().strip()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado",
        )
    user = User(
        email=email,
        password_hash=hash_password(body.password),
        name=body.name,
        plan=body.plan,
        must_change_password=body.must_change_password,
    )
    db.add(user)
    db.flush()
    # Criar configurações padrão para o usuário
    db.add(UserSettings(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


@router.post("/setup", response_model=UserOut, status_code=201)
def setup_first_user(body: CreateUserRequest, db: Session = Depends(get_db)):
    """
    Cria o primeiro usuario administrador.
    BLOQUEADO automaticamente assim que qualquer usuario existir no banco.
    Use apenas na primeira inicializacao do sistema.
    """
    total = db.query(User).count()
    if total > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Setup ja realizado. Use /create-user com x-admin-secret.",
        )
    email = body.email.lower().strip()
    user = User(
        email=email,
        password_hash=hash_password(body.password),
        name=body.name,
        plan=body.plan or "admin",
        must_change_password=False,
    )
    db.add(user)
    db.flush()
    db.add(UserSettings(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user
