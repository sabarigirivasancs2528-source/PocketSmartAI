from datetime import (
    datetime,
    timedelta,
    timezone
)

import jwt

from jwt.exceptions import InvalidTokenError

from pwdlib import PasswordHash

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status
)

from fastapi.security import (
    OAuth2PasswordBearer
)

from sqlalchemy.orm import Session

from .core import settings

from .db import db

from .models import User


s = settings()

password_hasher = PasswordHash.recommended()

bearer = OAuth2PasswordBearer(
    tokenUrl="/token",
    auto_error=False
)


def norm(value):

    return value.strip().lower()


def hash_pw(password):

    return password_hasher.hash(
        password
    )


def check_pw(password, hashed):

    return password_hasher.verify(
        password,
        hashed
    )


def token(user):

    expires = (
        datetime.now(timezone.utc)
        +
        timedelta(
            minutes=s.access_token_expire_minutes
        )
    )

    return jwt.encode(
        {
            "sub": str(user.id),
            "exp": expires
        },
        s.secret_key,
        algorithm="HS256"
    )


def current(
    request: Request,
    t: str | None = Depends(bearer),
    d: Session = Depends(db)
):

    try:

        if t:

            payload = jwt.decode(
                t,
                s.secret_key,
                algorithms=["HS256"]
            )

            user_id = int(
                payload["sub"]
            )

        else:

            user_id = int(
                request.session["user_id"]
            )

        user = d.get(
            User,
            user_id
        )

        if not user:
            raise ValueError()

        return user

    except (
        InvalidTokenError,
        KeyError,
        ValueError,
        TypeError
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )