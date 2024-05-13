from fastapi import Depends
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime, UTC
from jose import jwt, JWTError
from starlette.authentication import AuthCredentials, UnauthenticatedUser
from core.config import get_settings
from users.models import UserModel
from core.database import get_db


settings = get_settings()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_text_password, hashed_password):
    return pwd_context.verify(plain_text_password, hashed_password)


async def create_access_token(data, expiry: timedelta):
    payload = data.copy()
    expire_in = datetime.now(UTC) + expiry

    payload.update({'exp': expire_in})

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def create_refresh_token(data, access_token):
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM, access_token=access_token)


def get_token_payload(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM)
    except JWTError as error:
        return error

    return payload


def get_current_user(token: str = Depends(oauth2_scheme), db=None):
    payload = get_token_payload(token)
    if not payload or type(payload) is not dict:
        return None

    user_id = payload.get('id', None)
    if not user_id:
        return None

    if not db:
        db = next(get_db())

    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    return user


async def token_verify(token: str, db=None):
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM)

    if not payload or type(payload) is not dict:
        return False

    user_id = payload.get('id', None)
    if not user_id:
        return False

    if not db:
        db = next(get_db())

    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not user:
        return False

    return True


class JWTAuth:
    async def authenticate(self, conn):
        guest = AuthCredentials(['unauthenticated']), UnauthenticatedUser()

        if 'authorization' not in conn.headers:
            return guest

        token = conn.headers.get('authorization').split(' ')[1]

        if not token:
            return guest

        user = get_current_user(token)

        if not user:
            return guest

        return AuthCredentials('authenticated'), user
