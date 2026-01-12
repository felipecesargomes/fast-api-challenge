# FastAPI Async Banking API

API RESTful assíncrona desenvolvida com FastAPI, PostgreSQL e SQLAlchemy para gerenciamento de contas bancárias e operações financeiras, implementando autenticação JWT, validação de saldo, limites diários e testes completos.

## Tecnologias

- **FastAPI** - Framework web moderno e de alta performance
- **SQLAlchemy 2.0** - ORM assíncrono para PostgreSQL
- **asyncpg** - Driver PostgreSQL assíncrono
- **JWT** - Autenticação baseada em tokens
- **Poetry** - Gerenciamento de dependências
- **Docker** - Containerização da aplicação
- **pytest-asyncio** - Testes assíncronos

## Funcionalidades

- Autenticação JWT com tokens Bearer
- Gestão de contas bancárias (criação, listagem, desativação)
- Operações bancárias (depósito e saque)
- Validação de saldo e limites diários
- Extrato bancário com paginação
- Tipos de conta (corrente e poupança)
- Histórico completo de transações
- Operações assíncronas end-to-end
- Arquitetura modular e escalável
- Documentação automática (Swagger/OpenAPI)
- Testes automatizados com pytest

## Configuração

### Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/app
JWT_SECRET=sua-chave-secreta-aqui
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Rodando com Docker

```bash
docker-compose up --build
```

A API estará disponível em `http://localhost:8000`

- **Documentação Swagger**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Rodando localmente

```bash
# Instalar dependências
poetry install

# Iniciar servidor de desenvolvimento
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Autenticação

**POST** `/auth/login`

Gera um token de acesso JWT.

```json
{
  "username": "tester"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Contas Bancárias (Protegido)

**POST** `/accounts`

Cria uma nova conta bancária.

```bash
Authorization: Bearer <token>
```

```json
{
  "user_id": 1,
  "account_type": "checking",
  "initial_balance": 100.00,
  "daily_limit": 1000.00
}
```

**GET** `/accounts`

Lista todas as contas bancárias (com filtros opcionais).

**GET** `/accounts/{account_id}`

Busca uma conta específica.

**PATCH** `/accounts/{account_id}/deactivate`

Desativa uma conta bancária.

### Operações Bancárias (Protegido)

**POST** `/operations/deposit`

Realiza um depósito.

```json
{
  "account_id": 1,
  "operation_type": "deposit",
  "amount": 500.00,
  "description": "Depósito inicial"
}
```

**POST** `/operations/withdraw`

Realiza um saque (valida saldo e limite diário).

```json
{
  "account_id": 1,
  "operation_type": "withdrawal",
  "amount": 200.00,
  "description": "Saque"
}
```

**GET** `/operations/{account_id}/statement`

Retorna o extrato da conta com paginação.

**GET** `/operations`

Lista operações com filtros opcionais.

### Items (Protegido)

**POST** `/items`

Cria um novo item (requer autenticação).

```bash
Authorization: Bearer <token>
```

```json
{
  "name": "Item A"
}
```

**GET** `/items?limit=10&offset=0`

Lista itens com paginação (requer autenticação).

```bash
Authorization: Bearer <token>
```

## Testes

Execute a suíte de testes:

```bash
poetry run pytest
```

Para testes com cobertura:

```bash
poetry run pytest --cov=src
```

## Estrutura do Projeto

```
├── src/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── accounts.py    # Endpoints de contas bancárias
│   │   │   ├── operations.py  # Endpoints de operações
│   │   │   ├── auth.py        # Endpoints de autenticação
│   │   │   └── items.py       # Endpoints de items
│   │   ├── deps.py            # Dependências (DB, auth)
│   │   ├── routes.py          # Registro de rotas
│   │   └── schemas.py         # Schemas Pydantic
│   ├── core/
│   │   ├── config.py          # Configurações
│   │   └── security.py        # JWT e segurança
│   ├── db.py                  # Configuração do banco
│   ├── models.py              # Modelos SQLAlchemy
│   └── main.py                # Aplicação FastAPI
├── tests/
│   ├── conftest.py            # Fixtures pytest
│   ├── test_banking.py        # Testes bancários
│   └── test_items.py          # Testes de items
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Requisitos

- Python 3.11+
- PostgreSQL 14+
- Poetry
- Docker & Docker Compose (opcional)
#
