from fastapi import Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.logging import setup_logger
from app.models import User

logger = setup_logger(__name__)

templates = Jinja2Templates("templates")


def __account_page__(request: Request, user: User):
    return templates.TemplateResponse(
        request,
        "pages/account.html",
        {"user": user},
    )


def __update_account_info__(
    request: Request,
    user: User,
    db: Session,
    name: str | None,
):
    if name and name.strip():
        user.name = name
    else:
        return templates.TemplateResponse(
            request,
            "components/account_info_card.html",
            {"user": user, "errors": ["Name cannot be empty."]},
        )

    try:
        db.commit()
        db.refresh(user)
    except Exception as error:
        logger.error(f"Failed to update account info for <{user.email}>: {error}")
        return templates.TemplateResponse(
            request,
            "components/account_info_card.html",
            {
                "user": user,
                "errors": ["Failed to update account info, please try again later."],
            },
        )

    return templates.TemplateResponse(
        request,
        "components/account_info_card.html",
        {"user": user},
    )


def __account_delete_confirm__(
    request: Request,
    user: User,
):
    return templates.TemplateResponse(
        request,
        "pages/confirm_page.html",
        {
            "user": user,
            "confirm_message": "Are you sure, You want to delete your account?",
            "confirm_url": "/me/account-delete",
            "cancel_url": "/me",
        },
    )


def __account_delete__(
    request: Request,
    user: User,
    db: Session,
):
    try:
        db.delete(user)
        db.commit()
    except Exception as error:
        logger.error(f"Failed to delete account <{user.id}>: {error}")
        return templates.TemplateResponse(
            request,
            "pages/confirm_page.html",
            {
                "user": user,
                "confirm_message": "Are you sure, You want to delete your account?",
                "confirm_url": "/me/account-delete",
                "cancel_url": "/me",
                "errors": ["Account delete failed, please try again later."],
            },
        )

    res = RedirectResponse(
        "/auth/login?success_message=Account+deleted+successfully.",
        status.HTTP_303_SEE_OTHER,
    )
    res.delete_cookie("session-id")
    return res
