"""Authentication API routes.

Defines all authentication endpoints for the ForkIt API.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.models.auth import (
    LoginRequest,
    LoginResponse,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    UserResponse,
)
from app.services.auth_service import (
    AuthError,
    AuthService,
    EmailNotVerifiedError,
)
from app.utils.rate_limiter import AUTH_RATE_LIMIT, VERIFICATION_RATE_LIMIT, limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_auth_service() -> AuthService:
    """Dependency to get auth service instance."""
    return AuthService()


def get_current_user(
    authorization: str | None = Header(None, alias="Authorization"),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Dependency to get current authenticated user.

    Args:
        authorization: Authorization header with Bearer token.
        auth_service: Auth service instance.

    Returns:
        Current user info.

    Raises:
        HTTPException: If not authenticated.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    user = auth_service.get_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return user


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
@limiter.limit(AUTH_RATE_LIMIT)
def register(
    request: Request,
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new user.

    Args:
        data: Registration request with user details.
        auth_service: Auth service instance.

    Returns:
        Created user info.

    Raises:
        HTTPException: If registration fails.
    """
    try:
        return auth_service.register(data)
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.post("/login", response_model=LoginResponse)
@limiter.limit(AUTH_RATE_LIMIT)
def login(
    request: Request,
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    """Log in a user.

    Args:
        data: Login request with credentials.
        auth_service: Auth service instance.

    Returns:
        Login response with tokens and user info.

    Raises:
        HTTPException: If login fails.
    """
    try:
        return auth_service.login(data)
    except EmailNotVerifiedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )


@router.post("/refresh", response_model=LoginResponse)
def refresh_token(
    data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    """Refresh access token.

    Args:
        data: Refresh token request.
        auth_service: Auth service instance.

    Returns:
        Login response with new tokens.

    Raises:
        HTTPException: If refresh fails.
    """
    try:
        return auth_service.refresh_token(data.refresh_token)
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(auth_service: AuthService = Depends(get_auth_service)) -> None:
    """Log out current user.

    Args:
        auth_service: Auth service instance.
    """
    auth_service.logout()


@router.post("/password-reset")
@limiter.limit(VERIFICATION_RATE_LIMIT)
def request_password_reset(
    request: Request,
    data: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Request password reset email.

    Always returns success to prevent email enumeration.

    Args:
        data: Password reset request with email.
        auth_service: Auth service instance.

    Returns:
        Success message.
    """
    auth_service.request_password_reset(data.email)
    msg = "If an account exists with this email, a reset link has been sent."
    return {"message": msg}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get current user info.

    Args:
        current_user: Current authenticated user.

    Returns:
        Current user info.
    """
    return current_user


@router.post("/resend-verification")
@limiter.limit(VERIFICATION_RATE_LIMIT)
def resend_verification(
    request: Request,
    data: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Resend verification email.

    Args:
        data: Request with email.
        auth_service: Auth service instance.

    Returns:
        Success message.
    """
    auth_service.resend_verification_email(data.email)
    msg = "If an account exists with this email, a verification link has been sent."
    return {"message": msg}
