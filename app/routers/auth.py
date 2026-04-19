from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_active_user
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    ExpiredRefreshTokenError,
)
from app.database import get_db
from app.models import User
from app.schemas import (
    Token,
    UserCreate,
    UserResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = await auth_service.register_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role,
        )
        return user
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        access_token, refresh_token = await auth_service.login_user(
            form_data.username, form_data.password
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        access_token = await auth_service.refresh_access_token(request.refresh_token)
        return {"access_token": access_token, "token_type": "bearer"}
    except (InvalidRefreshTokenError, ExpiredRefreshTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.logout(request.refresh_token)
    return {"message": "Logged out successfully"}


@router.post("/logout-all")
async def logout_all_devices(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.logout_all_devices(current_user.id)
    return {"message": "Logged out from all devices"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
