from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, Token, UserResponse
from app.utils.security import verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.email == req.user_id_or_email) | (User.user_id == req.user_id_or_email)
    ).first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/user ID or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    access_token = create_access_token(data={"sub": user.user_id, "role": user.role.value})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/quick-switch/{role}", response_model=Token)
def quick_switch_demo_role(role: str, db: Session = Depends(get_db)):
    """Demo feature to quickly switch roles (ADMIN, OFFICER, REVIEWER, VIEWER) for testing."""
    role_upper = role.upper()
    user = db.query(User).filter(User.role == role_upper).first()
    if not user:
        raise HTTPException(404, f"No demo user found for role {role_upper}")
    
    access_token = create_access_token(data={"sub": user.user_id, "role": user.role.value})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
