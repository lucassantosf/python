"""
conftest.py — Fixtures compartilhadas entre todos os testes.

Estratégia:
- Banco SQLite in-memory separado por sessão de teste (sem tocar o app.db).
- Override da dependência `get_db` do FastAPI para injetar a sessão de teste.
- JWT real gerado via JWTProvider para testar rotas protegidas.
- Uma tabela `users` mínima é criada para satisfazer a FK de posts.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.main import create_app
from src.infrastructure.database.base import Base
from src.infrastructure.database.session import get_db
from src.infrastructure.security.jwt import JWTProvider

# Importa todos os models para o Base os enxergar ao criar tabelas
from src.infrastructure.database.models import post_model  # noqa: F401
from src.infrastructure.database.models import user_model  # noqa: F401


# ---------------------------------------------------------------------------
# Engine in-memory (uma por sessão pytest — isolada & descartável)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Cria todas as tabelas no banco in-memory antes de qualquer teste."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session():
    """
    Fornece uma sessão de banco limpa por teste.
    Faz rollback ao final para isolar cada caso de teste.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """
    TestClient do FastAPI com a dependência de banco substituída
    pelo db_session de teste.
    """
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture()
def test_user(db_session):
    """
    Insere um usuário de teste diretamente no banco in-memory
    e retorna seus dados. Usado para satisfazer a FK author_id de posts.
    """
    db_session.execute(
        text(
            "INSERT INTO users (email, password_hash, role) "
            "VALUES (:email, :password_hash, :role)"
        ),
        {
            "email": "test@example.com",
            "password_hash": "hashed_pw",
            "role": "user",
        },
    )
    db_session.commit()
    row = db_session.execute(
        text("SELECT id FROM users WHERE email = 'test@example.com'")
    ).fetchone()
    return {"id": row[0], "email": "test@example.com"}



@pytest.fixture()
def auth_token(test_user):
    """JWT válido para o usuário de teste."""
    return JWTProvider.create_access_token(data={"sub": str(test_user["id"])})


@pytest.fixture()
def auth_headers(auth_token):
    """Header Authorization pronto para usar nas requisições autenticadas."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture()
def created_post(client, auth_headers):
    """Cria um post via API e retorna o payload de resposta."""
    response = client.post(
        "/api/v1/posts/",
        json={"title": "Post Fixture", "content": "Conteúdo fixture"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()
