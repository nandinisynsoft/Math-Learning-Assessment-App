from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def register(self, db: Session, payload: RegisterRequest) -> User:
        exists = db.query(User).filter(User.email == payload.email).first()
        if exists:
            raise ValueError("Email already exists")

        user = User(
            id=str(uuid4()),
            email=payload.email,
            full_name=payload.full_name,
            role=payload.role,
            hashed_password=hash_password(payload.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def login(self, db: Session, payload: LoginRequest) -> str:
        user = db.query(User).filter(User.email == payload.email).first()
        if not user or not verify_password(payload.password, user.hashed_password):
            raise ValueError("Invalid credentials")
        return create_access_token(user.id)


auth_service = AuthService()
