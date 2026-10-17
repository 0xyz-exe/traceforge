from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid
from ..database import get_db
from ..models import User, Workspace
from ..schemas.base import UserRegister, UserLogin, Token, UserResponse
from ..utils.auth import hash_password, verify_password, create_access_token
from ..config import settings

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create workspace
    workspace_slug = user_data.workspace_name.lower().replace(" ", "-")[:100]
    workspace = Workspace(
        name=user_data.workspace_name,
        slug=workspace_slug
    )
    db.add(workspace)
    db.flush()
    
    # Create user
    user = User(
        workspace_id=workspace.id,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "workspace_id": user.workspace_id,
        "workspace": workspace,
    }

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "workspace_id": str(user.workspace_id)}
    )
    
    return Token(
        access_token=access_token,
        expires_in=settings.jwt_expiry_hours * 3600
    )
