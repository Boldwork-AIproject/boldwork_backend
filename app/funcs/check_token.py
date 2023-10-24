from fastapi import HTTPException, Request
from starlette import status
from datetime import timedelta
from typing import Dict
from jose import JWTError

from jwt_utils import verify_access_token


def get_current_user(request: Request) -> Dict[str, timedelta]:
    try:
        token = request.cookies.get("access_token")
        data = verify_access_token(token)
        return data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )