# Wallet Transaction System

## Installation
- Git Clone :

    ```git clone https://github.com/hariharaselvam/wallet.git```

- Create Virtual Environment:

    ```python3 -m venv wenv```

- Activate Virtual Environment:

    ```source wenv/bin/activate```

- Install requirements:
    ```
    cd wallet
    pip install -r requirements.txt
    ```

- Run Uvicorn

    ```uvicorn main:app --reload```

## Application Access
- Home page : http://127.0.0.1:8000/
- Swagger UI : http://127.0.0.1:8000/docs

## Demo
![Home page](images/Screenshot%202024-04-23%20at%203.04.12%E2%80%AFPM.png)

![API page](images/Screenshot%202024-04-23%20at%203.04.43%E2%80%AFPM.png)

## API documentation
### Open APIs

#### Create User
    method: POST
    url: http://127.0.0.1:8000/api/user/create/
    parameters: username, password
    response: user created reference

#### Create Wallet
    method: POST
    url: http://127.0.0.1:8000/api/wallet/create/
    parameters: wallet
    response: wallet created reference

#### Create Token
    method: POST
    url: http://127.0.0.1:8000/api/token/
    parameters: username, password
    response: bearer token


### Secure APIs

#### Create Account
    method: POST
    url: http://127.0.0.1:8000/api/account/create/
    parameters: wallet name, minimum balance, maximum transaction limit
    response: user wallet created reference
    authentication: brearer token

#### Credit to wallet
    method: POST
    url: http://127.0.0.1:8000/api/account/{{wallet}}/credit/
    parameters: wallet name, amount to deposit, transaction mode
    response: transaction reference
    authentication: brearer token

#### Debit from wallet
    method: POST
    url: http://127.0.0.1:8000/api/account/{{wallet}}/debit/
    parameters: wallet name, amount to debit, recipient
    response: transaction reference
    authentication: brearer token

#### Wallet Balance
    method: GET
    url: http://127.0.0.1:8000/api/account/{{wallet}}/balance/
    parameters: wallet name
    response: wallet balance
    authentication: brearer token

#### Wallet Transactions
    method: GET
    url: http://127.0.0.1:8000/api/account/{{wallet}}/transactions/
    parameters: wallet name
    response: transaction list
    authentication: brearer token