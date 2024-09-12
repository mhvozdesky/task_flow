import secrets
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from .models import User, Role, UserRole, Token
from .schemas import UserCreate, TokenOut, LoginData
from database import get_db
from common.constants import RoleName


router = APIRouter()

# Initialize the context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/register", response_model=TokenOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)

    new_user = User(
        email=user.email,
        password=hashed_password,
        phone=user.phone,
        first_name=user.first_name,
        last_name=user.last_name
    )

    result = await db.execute(select(Role).filter(Role.name == RoleName.USER))
    default_role = result.scalars().first()
    if not default_role:
        default_role = Role(name=RoleName.USER)
        db.add(default_role)

    user_role = UserRole(user=new_user, role=default_role)

    # Generate a token for the user
    new_token = Token(
        token=secrets.token_hex(16),
        user=new_user,
        issued_at=datetime.utcnow()
    )

    db.add(new_user)
    db.add(user_role)
    db.add(new_token)
    await db.commit()
    await db.refresh(new_token)

    return new_token


@router.post("/login")
async def login(login_data: LoginData, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == login_data.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    new_token = Token(
        token=secrets.token_hex(16),
        user=user,
        issued_at=datetime.utcnow()
    )

    db.add(new_token)
    await db.commit()

    return {"token": new_token.token}
