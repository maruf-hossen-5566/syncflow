from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.logging import setup_logger
from app.models.auth import User
from app.services.account import (
    __account_page__,
    __update_account_info__,
    __account_delete_confirm__,
    __account_delete__
)

logger = setup_logger(__name__)

router = APIRouter()

templates = Jinja2Templates("templates")


@router.get("")
def account_page(
    request: Request,
    user: User = Depends(get_current_user),
):
    return __account_page__(request, user)


@router.post("")
def update_account_info(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    name: str | None = Form(None),
):
    return __update_account_info__(request, user, db, name)


@router.get("/account-delete")
def account_delete_confirm(
    request: Request,
    user: User = Depends(get_current_user),
):
    return __account_delete_confirm__(request, user)


@router.post("/account-delete")
def account_delete(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return __account_delete__(request, user, db)
