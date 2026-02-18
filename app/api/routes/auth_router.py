"""Router para autenticación y gestión de sesiones."""
from fastapi import APIRouter, HTTPException, status
from app.schemas.auth_schema import LoginRequest, LoginResponse

# En el futuro importarás tu session de base de datos aquí
# from app.adapters.database import get_db
# from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Endpoint para iniciar sesión.
    Actualmente usa credenciales hardcodeadas.
    Próximamente conectará con PostgreSQL vía SQLAlchemy.
    """

    # --- ZONA DE SIMULACIÓN DE BASE DE DATOS ---

    # 1. HARDCODED (LO QUE USAMOS HOY)
    # Simulamos que buscamos en la BD y encontramos esto:
    admin_user = "admin"
    admin_pass = "admin"  # En BD real esto estaría hasheado (bcrypt)

    if credentials.username == admin_user and credentials.password == admin_pass:
        # Login Exitoso
        return LoginResponse(
            access_token="fake-jwt-token-para-pruebas",  # Mañana generarás un JWT real
            token_type="bearer",
            user_role="admin"
        )

    # 2. SQLALCHEMY (LO QUE HARÁS MAÑANA)
    # user = db.query(UserModel).filter(UserModel.username == credentials.username).first()
    # if not user or not verify_password(credentials.password, user.password):
    #     raise HTTPException(...)

    # --- FIN ZONA DE SIMULACIÓN ---

    # Si no coincide:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales incorrectas",
        headers={"WWW-Authenticate": "Bearer"},
    )