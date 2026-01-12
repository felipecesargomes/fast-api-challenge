import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_bank_account(client: AsyncClient, access_token: str):
    """Testa criação de conta bancária"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = await client.post(
        "/accounts",
        json={
            "user_id": 1,
            "account_type": "checking",
            "initial_balance": 100.0,
            "daily_limit": 1000.0
        },
        headers=headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == 1
    assert data["balance"] == 100.0
    assert data["account_type"] == "checking"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_deposit_operation(client: AsyncClient, access_token: str):
    """Testa operação de depósito"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    account_response = await client.post(
        "/accounts",
        json={"user_id": 2, "account_type": "checking", "initial_balance": 0},
        headers=headers
    )
    account_id = account_response.json()["id"]
    
    deposit_response = await client.post(
        "/operations/deposit",
        json={
            "account_id": account_id,
            "operation_type": "deposit",
            "amount": 500.0,
            "description": "Teste de depósito"
        },
        headers=headers
    )
    
    assert deposit_response.status_code == 201
    data = deposit_response.json()
    assert data["operation_type"] == "deposit"
    assert data["amount"] == 500.0
    assert data["balance_after"] == 500.0


@pytest.mark.asyncio
async def test_withdraw_operation(client: AsyncClient, access_token: str):
    """Testa operação de saque"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    account_response = await client.post(
        "/accounts",
        json={"user_id": 3, "account_type": "checking", "initial_balance": 1000.0},
        headers=headers
    )
    account_id = account_response.json()["id"]
    
    withdraw_response = await client.post(
        "/operations/withdraw",
        json={
            "account_id": account_id,
            "operation_type": "withdrawal",
            "amount": 300.0,
            "description": "Teste de saque"
        },
        headers=headers
    )
    
    assert withdraw_response.status_code == 201
    data = withdraw_response.json()
    assert data["operation_type"] == "withdrawal"
    assert data["amount"] == 300.0
    assert data["balance_after"] == 700.0


@pytest.mark.asyncio
async def test_withdraw_insufficient_balance(client: AsyncClient, access_token: str):
    """Testa saque com saldo insuficiente"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    account_response = await client.post(
        "/accounts",
        json={"user_id": 4, "account_type": "checking", "initial_balance": 50.0},
        headers=headers
    )
    account_id = account_response.json()["id"]
    
    withdraw_response = await client.post(
        "/operations/withdraw",
        json={
            "account_id": account_id,
            "operation_type": "withdrawal",
            "amount": 100.0
        },
        headers=headers
    )
    
    assert withdraw_response.status_code == 400
    assert "Saldo insuficiente" in withdraw_response.json()["detail"]


@pytest.mark.asyncio
async def test_get_statement(client: AsyncClient, access_token: str):
    """Testa obtenção de extrato"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    account_response = await client.post(
        "/accounts",
        json={"user_id": 5, "account_type": "savings", "initial_balance": 200.0},
        headers=headers
    )
    account_id = account_response.json()["id"]
    
    await client.post(
        "/operations/deposit",
        json={"account_id": account_id, "operation_type": "deposit", "amount": 100.0},
        headers=headers
    )
    await client.post(
        "/operations/withdraw",
        json={"account_id": account_id, "operation_type": "withdrawal", "amount": 50.0},
        headers=headers
    )
    
    statement_response = await client.get(
        f"/operations/{account_id}/statement",
        headers=headers
    )
    
    assert statement_response.status_code == 200
    data = statement_response.json()
    assert data["account"]["id"] == account_id
    assert data["account"]["balance"] == 250.0
    assert data["total_operations"] == 2
    assert len(data["operations"]) == 2


@pytest.mark.asyncio
async def test_list_accounts(client: AsyncClient, access_token: str):
    """Testa listagem de contas"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    await client.post(
        "/accounts",
        json={"user_id": 10, "account_type": "checking"},
        headers=headers
    )
    await client.post(
        "/accounts",
        json={"user_id": 10, "account_type": "savings"},
        headers=headers
    )
    
    response = await client.get(
        "/accounts?user_id=10",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
