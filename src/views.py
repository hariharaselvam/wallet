from datetime import datetime
from datetime import timedelta

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from jose import JWTError
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.helpers import generate_unique_id
from src.models import AccountModel
from src.models import TransactionModel
from src.models import UserModel
from src.models import WalletModel
from src.models import get_db

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


async def get_account(db: Session, user_id: str, wallet_name: str):
    wallet_obj = db.query(WalletModel).filter(WalletModel.name == wallet_name).first()
    print(wallet_obj)
    if wallet_obj is None:
        return None
    account_obj = db.query(AccountModel).filter(AccountModel.user_id == user_id,
                                                AccountModel.wallet_id == wallet_obj.id).first()
    if account_obj is None:
        return None
    print(account_obj)
    return account_obj


async def get_transactions(db: Session, account_id: str):
    transactions = db.query(TransactionModel).filter(or_(TransactionModel.from_account == account_id,
                                                         TransactionModel.to_account == account_id)).all()
    return transactions


@api.post("/user/create/", response_model=None)
async def create_user(username: str = '', password: str = '', db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if db_user:
        raise HTTPException(status_code=409, detail="Username already exists")

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
    db_wallet = db.query(WalletModel).filter(WalletModel.name == name).first()
    if db_wallet:
        raise HTTPException(status_code=409, detail="Wallet already exists")

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

    account = get_account(db, user_id, wallet)
    if account:
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
    return "Wallet (" + wallet + ") created for current user! Reference id : " + str(acc_id)


@api.get("/account/{wallet}/balance/", response_model=None)
async def account_balance(wallet: str = '', db: Session = Depends(get_db),
                          current_user: UserSession = Depends(get_current_user)):
    user_id = current_user.get('id')

    account = await get_account(db, user_id, wallet)
    if not account:
        return HTTPException(status_code=404, detail="Wallet not found for user")

    return "Wallet (" + wallet + ") balance is : " + str(account.balance) + " rs"


@api.post("/account/{wallet}/credit/", response_model=None)
async def credit_to_account(wallet: str = '', db: Session = Depends(get_db), amount: int = 0, mode: str = '',
                            current_user: UserSession = Depends(get_current_user)):
    user_id = current_user.get('id')

    account = await get_account(db, user_id, wallet)
    if not account:
        return HTTPException(status_code=404, detail="Wallet not found for user")

    transactions = await get_transactions(db, account.id)
    if len(transactions) == account.max_transaction:
        return HTTPException(status_code=403, detail="Transaction limit exceeded")

    account.balance = account.balance + amount
    db.commit()
    db.refresh(account)

    tr = TransactionModel(
        id=generate_unique_id(),
        from_account=mode,
        to_account=account.id,
        amount=amount
    )
    db.add(tr)
    db.commit()
    db.refresh(tr)
    return str(amount) + " credit to " + wallet + " from " + mode


@api.post("/account/{wallet}/debit/", response_model=None)
async def credit_to_account(wallet: str = '', db: Session = Depends(get_db), amount: int = 0, recipient: str = '',
                            current_user: UserSession = Depends(get_current_user)):
    user_id = current_user.get('id')

    account = await get_account(db, user_id, wallet)
    if not account:
        return HTTPException(status_code=404, detail="Wallet not found for user")
    new_balance = account.balance - amount

    if new_balance < account.min_amount:
        return HTTPException(status_code=200, detail="Insufficient balance")

    transactions = await get_transactions(db, account.id)
    if len(transactions) == account.max_transaction:
        return HTTPException(status_code=403, detail="Transaction limit exceeded")

    account.balance = new_balance
    db.commit()
    db.refresh(account)

    tr = TransactionModel(
        id=generate_unique_id(),
        from_account=account.id,
        to_account=recipient,
        amount=amount
    )
    db.add(tr)
    db.commit()
    db.refresh(tr)
    return str(amount) + " debited from " + wallet + " and send to " + recipient


@api.get("/account/{wallet}/transactions/", response_model=None)
async def account_balance(wallet: str = '', db: Session = Depends(get_db),
                          current_user: UserSession = Depends(get_current_user)):
    user_id = current_user.get('id')

    account = await get_account(db, user_id, wallet)
    if not account:
        return HTTPException(status_code=404, detail="Wallet not found for user")

    transactions = await get_transactions(db, account.id)
    return transactions
