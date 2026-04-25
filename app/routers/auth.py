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
from app.core.rate_limit import limiter

# ===== СХЕМЫ ДЛЯ СБРОСА ПАРОЛЯ =====
from pydantic import BaseModel, EmailStr


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


router = APIRouter(prefix="/auth", tags=["authentication"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/hour")
async def register(
    request: Request,
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
        print(f"🔵 DEBUG: About to send welcome email to user {user.id}")

        await auth_service.send_welcome_email(user.id)
        print(f"🟢 DEBUG: Welcome email sent")

        return user

        # Отправляем приветственное письмо

    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/token", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        access_token, refresh_token = await auth_service.login_user(
            form_data.username, form_data.password
        )

        response = JSONResponse(
            content={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        )

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
@limiter.limit("20/minute")
async def refresh_access_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        access_token = await auth_service.refresh_access_token(
            refresh_data.refresh_token
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except (InvalidRefreshTokenError, ExpiredRefreshTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
@limiter.limit("20/minute")
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
    request: Request,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.logout_all_devices(current_user.id)
    return {"message": "Logged out from all devices"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user_optional_cookie)):
    return current_user


# ===== ЭНДПОИНТЫ =====
@router.post("/forgot-password")
@limiter.limit("3/hour")
async def forgot_password(
    request: Request,
    data: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Запрос на сброс пароля"""
    token = await auth_service.request_password_reset(data.email)
    await auth_service.send_password_reset_email(data.email, token)
    # Отправляем письмо со ссылкой для сброса

    return {"message": "If email exists, reset link sent"}


@router.post("/reset-password")
@limiter.limit("3/hour")
async def reset_password(
    request: Request,
    data: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Подтверждение сброса пароля"""
    success = await auth_service.reset_password(data.token, data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Password reset successfully"}


@router.post("/change-password")
async def change_password(
    request: Request,
    data: PasswordChangeRequest,
    current_user: User = Depends(
        get_current_user_optional_cookie
    ),  # ← Поддерживает и cookie, и Bearer
    auth_service: AuthService = Depends(get_auth_service),
):
    # Проверяем CSRF только для cookie-аутентификации
    if request.cookies.get("access_token"):
        from app.core.csrf import verify_csrf_token

        verify_csrf_token(request)

    success = await auth_service.change_password(
        current_user.id, data.old_password, data.new_password
    )
    if not success:
        raise HTTPException(status_code=400, detail="Incorrect old password")

    # После смены пароля удаляем старые токены
    response = JSONResponse(content={"message": "Password changed successfully"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

@router.get("/whoami")
async def whoami(current_user: User = Depends(get_current_user_optional_cookie)):
    if not current_user:
        return {"authenticated": False}
    return {
        "authenticated": True, 
        "id": current_user.id,
        "username": current_user.username, 
        "role": current_user.role.value
    }
