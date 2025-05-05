from fastapi import Depends, HTTPException, status, Request
from app.modules.admin.schemas import TokenParam
from app.modules.auth.services import decode_access_token

async def get_current_user(token_param: TokenParam = Depends()):
    """Проверка JWT-токена из параметра запроса"""
    token = token_param.token
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    email = payload.get("sub")
    role = payload.get("role")
    if not email or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return {"email": email, "role": role}

async def get_current_admin(user=Depends(get_current_user)):
    """Проверка, является ли пользователь администратором"""
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user