from fastapi import FastAPI
from starlette.responses import HTMLResponse

from views import api

app = FastAPI(
    title='WTS',
    description='Wallet Transaction System APIs'
)

app.include_router(api, prefix='/api', tags=["api"])

@app.get("/", response_class=HTMLResponse)
async def root():
    welcome_message = """
        <html>
        <head>
            <title>Wallet Transaction System</title>
        </head>
        <body>
            <h1>Welcome to Wallet Transaction System</h1>
            <p></p>
            <p>To perform API operations, please navigate to the <a href="/docs">Swagger UI</a>.</p>
        </body>
        </html>
        """
    return welcome_message