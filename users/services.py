from users.models import UserModel
from fastapi.exceptions import HTTPException
from core.security import get_password_hash


async def create_user_account(data, db):
    user = db.query(UserModel).filter(UserModel.email == data.email).first()

    if user:
        raise HTTPException(status_code=422, details="Email is already registered with us.")

    new_user = UserModel(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password=get_password_hash(data.password),
        is_active=False,
        is_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
