from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt

from models import get_db
from models import UserModel
from helpers import generate_unique_id


# Secret key to sign JWT tokens
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

api = APIRouter()

def create_jwt_token(data: dict):
    to_encode = data.copy()
    expires = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        id: str = payload.get("id")
        if username is None:
            raise credentials_exception
        token_data = {"username": username, "id": id}
    except JWTError:
        raise credentials_exception
    return token_data

@api.post("/user/create/", response_model=None)
async def create_user(username: str = '', password: str = '', db: Session = Depends(get_db)):
    db_user = UserModel(
        id=generate_unique_id(),
        username=username,
        password=password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    user_id = db_user.id
    return str(user_id)

@api.post("/token/", response_model=None)
async def login_for_access_token(username: str = '', password: str = '', db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if db_user and password == db_user.password:
        token_data = {"username": username, "id": db_user.id}
        return {"access_token": create_jwt_token(token_data), "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")