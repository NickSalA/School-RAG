"""Tests básicos para los endpoints de autenticación usando pytest y TestClient."""

import pytest
import bcrypt
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.factory import create
from app.core.database import get_session
from app.models.user_model import User

# Configurar base de datos en memoria para las pruebas
sqlite_url = "sqlite://"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def get_session_override():
    with Session(engine) as session:
        yield session

app = create()
app.dependency_overrides[get_session] = get_session_override

@pytest.fixture(name="client")
def client_fixture():
    # Asegurar que las tablas existan antes de cada prueba
    SQLModel.metadata.create_all(engine)
    client = TestClient(app)
    yield client
    # Limpiar base de datos después de la prueba
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture():
    with Session(engine) as session:
        yield session

def test_register_user(client: TestClient):
    """1. Test de registro (crear un usuario inicial)"""
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "password": "testpassword", "role": "admin"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_login_success(client: TestClient, session: Session):
    """2. Test de login exitoso (que devuelva el token JWT)"""
    # Usando bcrypt directamente para cumplir el requirement
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(b"mypassword", salt).decode("utf-8")
    user = User(username="loginuser", password_hash=hashed, role="admin")
    session.add(user)
    session.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "loginuser", "password": "mypassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failed(client: TestClient, session: Session):
    """3. Test de login fallido (contraseña o usuario incorrecto)"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(b"mypassword", salt).decode("utf-8")
    user = User(username="failuser", password_hash=hashed, role="admin")
    session.add(user)
    session.commit()
    
    # Intentar con mala contraseña
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "failuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    
    # Intentar con usuario inexistente
    response2 = client.post(
        "/api/v1/auth/login",
        json={"username": "notfound", "password": "mypassword"}
    )
    assert response2.status_code == 401

def test_protected_route(client: TestClient, session: Session):
    """4. Test de ruta protegida (intentar acceder a un endpoint con y sin el token)"""
    # Crear cuenta de usuario
    client.post(
        "/api/v1/auth/register",
        json={"username": "protecteduser", "password": "testpassword", "role": "admin"}
    )
    
    # Test CON token
    response_login = client.post(
        "/api/v1/auth/login",
        json={"username": "protecteduser", "password": "testpassword"}
    )
    token = response_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response_with_token = client.get("/api/v1/auth/me", headers=headers)
    assert response_with_token.status_code == 200
    assert response_with_token.json()["username"] == "protecteduser"

    # Test SIN token
    response_without_token = client.get("/api/v1/auth/me")
    assert response_without_token.status_code == 401
