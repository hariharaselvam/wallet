from fastapi import FastAPI
from views import api

app = FastAPI(
    title='WTS',
    description='Wallet Transaction System APIs'
)

app.include_router(api, prefix='/api', tags=["api"])