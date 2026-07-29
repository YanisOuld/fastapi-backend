import jwt
from backend.app.core.config import settings
from backend.app.core.security import decode_access_token
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)

# Fixed user id returned for every request when BYPASS_AUTH=True (local dev only)
DEV_BYPASS_USER_ID = "00000000-0000-0000-0000-000000000000"

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or missing bearer token",
    headers={"WWW-Authenticate": "Bearer"},
)


def _decode_or_401(credentials: HTTPAuthorizationCredentials | None) -> dict:
    """Decode the bearer token or raise 401. Never bypasses — callers gate on
    BYPASS_AUTH before calling this."""
    if credentials is None:
        raise _UNAUTHORIZED
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError as exc:
        raise _UNAUTHORIZED from exc
    if not payload.get("sub"):
        raise _UNAUTHORIZED
    return payload


async def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    """Gate a route behind a valid token without needing the user id.

    Use it as a route-level dependency to privatize an endpoint:
        @router.get("/secret", dependencies=[Depends(verify_token)])

    When BYPASS_AUTH=True (local dev only) it lets every request through.
    """
    if settings.BYPASS_AUTH:
        return
    _decode_or_401(credentials)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """Like verify_token, but also returns the authenticated user id (`sub`).

    Under BYPASS_AUTH it returns a fixed dev user id so routes still get a value.
    """
    if settings.BYPASS_AUTH:
        return DEV_BYPASS_USER_ID
    return _decode_or_401(credentials)["sub"]
