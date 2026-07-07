from fastapi import APIRouter, HTTPException, Request, Response
from itsdangerous import BadSignature, TimestampSigner
from pydantic import BaseModel

COOKIE_NAME = "prodev_session"
MAX_AGE = 60 * 60 * 24  # сутки

router = APIRouter(prefix="/api/auth")


class LoginBody(BaseModel):
    password: str


def _signer(request: Request) -> TimestampSigner:
    return TimestampSigner(request.app.state.secret_key)


def require_admin(request: Request) -> None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Требуется вход")
    try:
        _signer(request).unsign(token, max_age=MAX_AGE)
    except BadSignature:
        raise HTTPException(status_code=401, detail="Сессия недействительна")


@router.post("/login")
def login(body: LoginBody, request: Request, response: Response):
    if body.password != request.app.state.admin_password:
        raise HTTPException(status_code=401, detail="Неверный пароль")
    token = _signer(request).sign("admin").decode()
    response.set_cookie(
        COOKIE_NAME, token, max_age=MAX_AGE, httponly=True, samesite="lax"
    )
    return {"ok": True}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@router.get("/me")
def me(request: Request):
    require_admin(request)
    return {"ok": True}
