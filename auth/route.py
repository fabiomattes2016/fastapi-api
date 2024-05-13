from fastapi import APIRouter, status, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from auth.services import get_token, get_refresh_token, verify_token
from users.responses import UserResponse


router = APIRouter(
    prefix="/auth",
    tags=["User"],
    responses={404: {'descripion': 'Not found'}},
)


@router.post("/token", status_code=status.HTTP_200_OK)
async def authenticate_user(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return await get_token(data, db)


@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def refresh_token(refresh_token: str = Header(), db: Session = Depends(get_db)):
    return await get_refresh_token(token=refresh_token, db=db)


@router.post("/verify", status_code=status.HTTP_200_OK)
async def verify(token: str = Header(), db: Session = Depends(get_db)):
    return await verify_token(token, db=db)
