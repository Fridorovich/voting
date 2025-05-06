import logging
from sqlalchemy.orm import Session
from app.database.models import User
from passlib.context import CryptContext
from jose import jwt
from datetime import timedelta, datetime, UTC
from app.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(
        db: Session, email: str,
        password: str,
        role: str = "admin"
):
    logger.info(f"Creating user: email={email}, role={role}")
    hashed_password = pwd_context.hash(password)
    new_user = User(
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User created successfully: id={new_user.id}")
    return new_user


async def authenticate_user(db: Session, email: str, password: str):
    logger.info(f"Authenticating user: email={email}")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"Authentication failed: user not found for email={email}")
        return None
    if not pwd_context.verify(password, user.hashed_password):
        logger.warning(f"Authentication failed: wrong password for email={email}")
        return None
    logger.info(f"User authenticated: id={user.id}")
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    logger.info("Creating access token")
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    logger.info("Access token created")
    return encoded_jwt


def decode_access_token(token: str):
    logger.info("Decoding access token")
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        logger.info("Token decoded successfully")
        return payload
    except jwt.JWTError as e:
        logger.error(f"Failed to decode token: {e}")
        return None


def create_refresh_token(
        data: dict,
        expires_delta:
        timedelta = None
):
    logger.info("Creating refresh token")
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    logger.info("Refresh token created")
    return encoded_jwt
