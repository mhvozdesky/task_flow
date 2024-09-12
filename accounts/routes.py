import secrets
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .models import User, Role, UserRole, Token
from .schemas import UserCreate, TokenOut, LoginData
from database import get_db
from common.constants import RoleName


router = APIRouter()

# Initialize the context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = db.execute(select(Token).where(Token.token == token))
    db_token = result.scalars().first()

    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return db_token.user


@router.post("/register", response_model=TokenOut)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    statement = select(User).where(User.email == user.email)
    result = db.execute(statement)
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

    result = db.execute(select(Role).filter(Role.name == RoleName.USER))
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
    db.commit()
    db.refresh(new_token)

    return new_token


@router.post("/login")
async def login(login_data: LoginData, db: Session = Depends(get_db)):
    result = db.execute(select(User).filter(User.email == login_data.email))
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
    db.commit()

    return {"token": new_token.token}


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db),
            bearer_token: str = Depends(oauth2_scheme)
           ):
    statement = select(Token).where(
        Token.user_id == current_user.id,
        Token.token == bearer_token
    )
    token = db.execute(statement).scalars().first()

    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    db.delete(token)
    db.commit()

    return {"msg": "Logout successful"}
