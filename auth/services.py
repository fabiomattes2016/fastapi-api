from users.models import UserModel
from fastapi.exceptions import HTTPException
from core.security import verify_password, create_access_token, create_refresh_token, get_token_payload, token_verify
from core.config import get_settings
from datetime import timedelta
from auth.responses import TokenResponse


settings = get_settings()

async def get_token(data, db):
    user = db.query(UserModel).filter(UserModel.email == data.username).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials",
            headers={'WWW-Authenticate': 'Bearer'}
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials",
            headers={'WWW-Authenticate': 'Bearer'}
        )

    _verify_user_access(user=user)

    return await _get_user_token(user=user)


async def get_refresh_token(token, db):
    payload = get_token_payload(token=token)
    user_id = payload.get('id', None)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers={'WWW-Authenticate': 'Bearer'}
        )

    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return await _get_user_token(user=user, refresh_token=token)


def _verify_user_access(user: UserModel):
    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Account is inactive",
            headers={'WWW-Authenticate': 'Bearer'}
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=401,
            detail="Account is not verified",
            headers={'WWW-Authenticate': 'Bearer'}
        )


async def _get_user_token(user: UserModel, refresh_token = None):
    payload = {
        'id': user.id,
    }

    access_token_expiry = timedelta(minutes=settings.JWT_TOKEN_EXPIRE_MIN)

    access_token = await create_access_token(payload, access_token_expiry)

    if not refresh_token:
        refresh_token = await create_refresh_token(payload, access_token=access_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_token_expiry.seconds
    )


async def verify_token(token, db):
    if not token_verify(token):
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return True
