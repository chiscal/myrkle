from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud, models, schemas
from api import deps
from core import security
from core.config import settings
from core.security import get_password_hash
from utils import (
    generate_password_reset_token,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        db, browser_id=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{browser_id}", response_model=schemas.Msg)
def recover_password(browser_id: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    print("got here")
    user = crud.user.get_by_browser_id(db, browser_id=browser_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    db.delete(user)
    
    return {"msg": "Password recovery successful"}
