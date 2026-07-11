from fastapi import APIRouter, Depends, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.logging import setup_logger
from app.models.auth import User
from app.services.auth import (
    __register_page__,
    __register_user__,
    __login_page__,
    __login_user__,
    __logout_page__, __logout_user__,
)

logger = setup_logger(__name__)

router = APIRouter()

templates = Jinja2Templates("templates")


@router.get("/register")
def register_page(
    request: Request,
):
    """Account registration page for a new user"""
    return __register_page__(request)


@router.post("/register")
def register_user(
    request: Request,
    db: Session = Depends(get_db),
    email: str | None = Form(None),
    password: str | None = Form(None),
):
    """
    Parameters
    ----------
    request : Request
        FastAPI request object.
    db : Session
        Database session dependency.
    email : str | None
        User email address.
    password  : str | None
        User password.

    Returns
    -------
    RedirectResponse
        Redirect to the login page after successful registration.
    """
    return __register_user__(request, db, email, password)


@router.get("/login")
def login_page(
    request: Request,
):
    """Log in page for the user."""
    return __login_page__(request)


@router.post("/login")
def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Parameters
    ----------
    request : Request
        FastAPI request object.
    form_data : OAuth2PasswordRequestForm
        0Auth form for authentication credentials.
    db : Session
        Database session dependency.

    Returns
    -------
    RedirectResponse
        Redirect to the home page.
    """
    return __login_user__(request, form_data, db)


@router.get("/logout")
def logout_page(
    request: Request,
    user: User = Depends(get_current_user),
):
    """Log out confirmation page for current user."""
    return __logout_page__(request, user)


@router.post("/logout")
def logout_user(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log out the current user."""
    return __logout_user__(request, user, db)
