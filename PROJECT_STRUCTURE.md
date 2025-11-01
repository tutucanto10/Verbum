# Estrutura e Organização do Projeto — Backend (FastAPI + Supabase)

Este documento explica como o projeto está organizado e qual é a função de cada pasta e arquivo.
Serve para que toda a equipe mantenha o mesmo padrão de desenvolvimento e facilite a colaboração.

---

## Estrutura de Pastas

├── backend/ # Pasta principal do backend (FastAPI)
│ ├── app/ # Código-fonte da aplicação FastAPI
│ │ ├── api/ # Rotas (endpoints da API)
│ │ ├── core/ # Configurações centrais (ex: variáveis, segurança)
│ │ ├── schemas/ # Schemas Pydantic (validação de entrada/saída)
│ │ ├── services/ # Lógica de negócio e integrações (Supabase, GPT)
│ │ ├── tests/ # Testes automatizados
│ │ ├── utils/ # Funções auxiliares e genéricas
│ │ ├── main.py # Ponto de entrada da aplicação FastAPI
│ │ └── init.py
│ │
│ ├── requirements.txt # Dependências do backend
│ └── init.py
│
├── frontend/ # Pasta para o projeto do frontend #adicionaremos a estrutura de pastas quando formos comecar o frontend
│
├── .env # Variáveis de ambiente (NÃO deve ser versionado)
├── .env.example # Modelo das variáveis de ambiente (pode ser versionado)
├── .gitignore # Arquivos/pastas ignoradas pelo Git
├── PROJECT_STRUCTURE.md # (este documento)
└── README.md # Descrição geral do projeto

---

## Estrutura Detalhada — Backend (`backend/app`)

### `api/`
- Define as **rotas** (endpoints HTTP) da aplicação FastAPI.
- Cada arquivo representa um conjunto de rotas (ex: `auth.py`, `chat.py`, `users.py`).
- Pode conter subpastas versionadas (`v1`, `v2`) caso a API evolua.

Exemplo:
```python
@router.post("/login")
def login(data: LoginRequest):
    return auth_service.login(data) 
```
### `core/`

- Centraliza configurações do projeto (env, CORS, segurança, middlewares).
- Normalmente contém config.py (carrega .env) e, se necessário, security.py, middleware.py.

Exemplo (config.py):

```PYTHON
from dotenv import load_dotenv
import os

load_dotenv()  # carrega .env da raiz do repo

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APP_NAME = os.getenv("APP_NAME", "Chat API")
```

### schemas/

-Define os modelos Pydantic usados para validação de entrada e formatação de saída.
-Serve como “contrato” entre o backend e o frontend.
-Pode conter validadores simples (@field_validator) e defaults, mas nunca lógica de negócio.

Exemplo:

```python
# chat.py
from pydantic import BaseModel, field_validator

class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v):
        if not (0 <= v <= 2):
            raise ValueError("Temperature deve estar entre 0 e 2")
        return v

class ChatResponse(BaseModel):
    answer: str
```

### services/

-Camada que contém a lógica de negócio da aplicação.
-É aqui que ficam as integrações externas (Supabase, GPT, email, etc.).
-Rotas chamam apenas funções dos services — isso mantém as rotas finas e limpas.
-Pode haver um arquivo por domínio: chat_service.py, auth_service.py, supabase_service.py.

Exemplo:

```python
# chat_service.py
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.supabase_service import supabase
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_gpt_response(user_id: str, payload: ChatRequest) -> ChatResponse:
    supabase.table("messages").insert({
        "user_id": user_id, "role": "user", "content": payload.message
    }).execute()

    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente útil."},
            {"role": "user", "content": payload.message},
        ],
        temperature=payload.temperature
    )
    answer = result.choices[0].message.content

    supabase.table("messages").insert({
        "user_id": user_id, "role": "assistant", "content": answer
    }).execute()

    return ChatResponse(answer=answer)
```

### utils/

-Contém funções auxiliares e genéricas, que podem ser usadas em qualquer parte do projeto.
-Não devem depender de FastAPI, banco de dados ou APIs externas.
-Exemplo: funções de formatação, segurança, hashing, manipulação de strings, etc.

Exemplo:

```python
# security.py
import hashlib, hmac

def sha256_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()

def safe_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)
```

### dependencies/ (opcional)

-Define dependências usadas com Depends() no FastAPI.
-Usado para autenticação, injeção de usuários logados, ou conexão com serviços.
-Deve retornar objetos ou dados que as rotas precisem.

Exemplo:

```python
# auth.py
from fastapi import Header, HTTPException
from app.services.supabase_service import supabase

async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido.")
    token = authorization.split(" ", 1)[1]
    supabase.auth.set_auth(token)
    user = supabase.auth.get_user().user
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não autenticado.")
    return user
```

### tests/

-Contém testes automatizados (geralmente com pytest).
-Testes unitários e de integração ficam aqui.
-Útil para garantir que cada parte do sistema continua funcionando conforme esperado.

Exemplo:

```python
# test_health.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

### main.py

-É o ponto de entrada da aplicação FastAPI.
-Cria a instância principal do app e registra as rotas.
-Pode também aplicar middlewares e configurações globais.

Exemplo:

```python
# main.py
from fastapi import FastAPI
from app.api.v1.routes import router as api_router

app = FastAPI(title="Chat API")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def health():
    return {"status": "ok"}
```