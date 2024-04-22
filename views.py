from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel

from models import AccountModel
from models import get_db

from models import WalletModel

from models import UserModel
from helpers import generate_unique_id


# Secret key to sign JWT tokens
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

api = APIRouter()

class UserSession(BaseModel):
    username: str
    id: str

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

@api.post("/wallet/create/", response_model=None)
async def create_wallet(name: str = '', db: Session = Depends(get_db)):
    db_wallet = WalletModel(
        id=generate_unique_id(),
        name=name
    )
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    wallet_id = db_wallet.id
    return str(wallet_id)

@api.post("/account/create/", response_model=None)
async def create_account(wallet: str = '', db: Session = Depends(get_db), balance: int = 0,
                         min_balance: int = 0, max_transaction: int = 100,
                         current_user: UserSession = Depends(get_current_user)):
    user_id = current_user.get('id')

    wallet_obj = db.query(WalletModel).filter(WalletModel.name == wallet).first()
    if wallet_obj is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    wallet_id = wallet_obj.id

    existing_account = db.query(AccountModel).filter(AccountModel.user_id == user_id,
                                                     AccountModel.wallet_id == wallet_id).first()
    if existing_account:
        return HTTPException(status_code=400, detail="Wallet already exists for user")

    db_acc = AccountModel(
        id=generate_unique_id(),
        user_id=user_id,
        wallet_id=wallet_id,
        balance=balance,
        min_amount=min_balance,
        max_transaction=max_transaction,
    )
    db.add(db_acc)
    db.commit()
    db.refresh(db_acc)
    acc_id = db_acc.id
    return str(acc_id)

@api.get("/account/balance/", response_model=None)
async def create_account(wallet: str = '', db: Session = Depends(get_db),
                         current_user: UserSession = Depends(get_current_user)):
    user_id = current_user.get('id')

    wallet_obj = db.query(WalletModel).filter(WalletModel.name == wallet).first()
    if wallet_obj is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    wallet_id = wallet_obj.id

    account = db.query(AccountModel).filter(AccountModel.user_id == user_id,
                                                     AccountModel.wallet_id == wallet_id).first()
    if not account:
        return HTTPException(status_code=404, detail="Wallet not found for user")
    else:
        return HTTPException(status_code=200, detail=account.balance)
