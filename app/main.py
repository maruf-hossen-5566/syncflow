from fastapi import Depends, FastAPI, HTTPException, Query, Header
from fastapi.requests import Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import app.models
from app.api import get_current_user, get_db, auth_router, account_router, document_router
from app.core.logging import setup_logger
from app.db.base import Base
from app.db.session import engine
from app.models import User

logger = setup_logger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates("templates")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(account_router, prefix="/me", tags=["Account"])
app.include_router(document_router, prefix="/documents", tags=["Document"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 303 and exc.headers and "Location" in exc.headers:
        return RedirectResponse(
            exc.headers["Location"],
            exc.status_code,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
        },
    )


@app.get("/")
def home(
    request: Request,
    hx_request: str | None = Header(default=None),
    size: int = Query(12, ge=1),
    page: int = Query(1, ge=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Parameters
    ----------
    request : Request
        FastAPI request object.
    hx_request : str | None
        Header parameter to check if the request is from HTMX.
    size : int
        Number of items per page.
    page : int
        Current Page number.
    user : User
        Current user dependency.
    db : Session
        Database session dependency.

    Returns
    -------
    TemplateResponse
    """
    return __home__(
        request,
        hx_request,
        size,
        page,
        user,
        db,
    )


from app.services.root import __home__
