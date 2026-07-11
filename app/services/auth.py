from datetime import timezone, timedelta, datetime

from fastapi import Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.logging import setup_logger
from app.core.security import hash_password
from app.core.security import verify_password
from app.models import User, Session as AuthSession
from app.utils.url import normalize_params
from app.utils.validators import validate_email, validate_password

logger = setup_logger(__name__)

templates = Jinja2Templates("templates")


def __register_page__(
    request: Request,
):
    return templates.TemplateResponse(request, "pages/register.html")


def __register_user__(
    request: Request,
    db: Session,
    email: str,
    password: str,
):
    try:
        validate_email(email)
        validate_password(password)
    except ValueError as error:
        return RedirectResponse(
            f"{request.url}/?error_message={normalize_params(str(error))}",
            status.HTTP_303_SEE_OTHER,
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return RedirectResponse(
            f"{request.url}/?error_message={normalize_params('Account already exists with this email.')}",
            status.HTTP_303_SEE_OTHER,
        )

    new_user = User(
        email=email,
        hashed_password=hash_password(password),
    )

    try:
        db.add(new_user)
        db.commit()
    except Exception as error:
        logger.error(f"Failed to create user <{email}>: {error}")
        return RedirectResponse(
            f"{request.url}/?error_message={normalize_params('Something went wrong, please try again later.')}",
            status.HTTP_303_SEE_OTHER,
        )

    return RedirectResponse(
        f"{request.base_url}auth/login/?success_message={normalize_params('🎉 Account created successfully, now you can log in.')}",
        status.HTTP_303_SEE_OTHER,
    )


def __login_page__(request: Request):
    return templates.TemplateResponse(
        request,
        "pages/login.html",
    )


def __login_user__(request: Request, form_data: OAuth2PasswordRequestForm, db: Session):
    email = form_data.username
    password = form_data.password

    try:
        validate_email(email)
        validate_password(password)
    except ValueError as error:
        return RedirectResponse(
            f"{request.url}/?error_message={normalize_params(str(error))}",
            status.HTTP_303_SEE_OTHER,
        )

    user = db.query(User).filter(User.email == email).first()

    if not user:
        logger.error(f"Account does not exit with this email <{email}>")
        return RedirectResponse(
            f"{request.url}/?error_message={normalize_params('Account does not exit with this email.')}",
            status.HTTP_303_SEE_OTHER,
        )

    if not verify_password(password, user.hashed_password):
        logger.error(f"Failed to login user <{email}>: Invalid credentials!")
        return RedirectResponse(
            f"{request.url}/?error_message={normalize_params('Invalid credentials!')}",
            status.HTTP_303_SEE_OTHER,
        )

    session = AuthSession(
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    try:
        db.add(session)
        db.commit()
    except Exception as error:
        logger.error(f"Failed to create session: {error}")
        return RedirectResponse(
            f"{request.url}/?error_message={normalize_params('Failed to create session, please tray again later')}",
            status.HTTP_303_SEE_OTHER,
        )
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="session-id",
        value=str(session.id),
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return response


def __logout_page__(
    request: Request,
    user: User,
):
    return templates.TemplateResponse(
        request,
        "pages/confirm_page.html",
        context={
            "user": user,
            "confirm_message": "Are you sure, You want to logout?",
            "confirm_url": "/auth/logout",
            "cancel_url": "/",
        },
    )


def __logout_user__(
    request: Request,
    user: User,
    db: Session,
):
    session_id = request.cookies.get("session-id")

    session = db.query(AuthSession).filter(AuthSession.id == session_id).first()

    try:
        db.delete(session)
        db.commit()
    except Exception as error:
        logger.error(f"Failed to delete session <{session_id}>: {error}")
        return RedirectResponse(
            f"{request.url}/?error_message={normalize_params(str(error))}",
            status.HTTP_303_SEE_OTHER,
        )

    res = RedirectResponse(
        f"login/?success_message=Logout+was+successful.",
        status.HTTP_303_SEE_OTHER,
    )
    res.delete_cookie("session-id")

    return res
