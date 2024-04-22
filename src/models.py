from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLAlchemy models
SQLALCHEMY_DATABASE_URL = "sqlite:///./wallets.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database definitions
class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class WalletModel(Base):
    __tablename__ = "wallet"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AccountModel(Base):
    __tablename__ = "account"
    id = Column(String, primary_key=True, index=True)
    wallet_id = Column(String)
    user_id = Column(String)
    balance = Column(Integer, default=0)
    min_amount = Column(Integer, default=0)
    max_transaction = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)


class TransactionModel(Base):
    __tablename__ = "transaction"
    id = Column(String, primary_key=True, index=True)
    from_account = Column(String)
    to_account = Column(String)
    amount = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    """Get DB session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
