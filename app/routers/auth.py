from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.csrf import generate_csrf_token, set_csrf_cookie
from app.core.csrf import verify_csrf_token
from app.auth import (
    get_current_active_user,
    get_current_user_from_cookie,
    get_current_user_optional_cookie,
)
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

        # Создаём ответ с токенами
        response = JSONResponse(
            content={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        )

        # Устанавливаем HttpOnly cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=1800,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=2592000,
        )

        # Устанавливаем CSRF токен
        csrf_token = generate_csrf_token()
        set_csrf_cookie(response, csrf_token)

        return response
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
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    verify_csrf_token(request)
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await auth_service.logout(refresh_token)

    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@router.post("/logout-all")
async def logout_all_devices(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.logout_all_devices(current_user.id)
    return {"message": "Logged out from all devices"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user_optional_cookie)):
    return current_user


@router.post("/change-password")
async def change_password(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
):
    # Проверяем CSRF токен
    from app.core.csrf import verify_csrf_token

    verify_csrf_token(request)

    # TODO: логика смены пароля
    return {"message": "Password changed (example)"}
