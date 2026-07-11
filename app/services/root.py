from math import ceil

from fastapi.requests import Request
from sqlalchemy.orm import Session

from app.models import User, Document
from app.schemas.auth import UserResponse
from app.schemas.document import DocPartialResponse


def __home__(
    request: Request,
    hx_request: str | None,
    size: int,
    page: int,
    user: User,
    db: Session,
):
    sort_by = request.query_params.get("sort")

    template_name = "pages/home.html"

    base_query = db.query(Document).filter(Document.members.any(id=user.id))

    if sort_by and sort_by == "by_me":
        docs_query = base_query.filter(Document.created_by == user.id)
    elif sort_by and sort_by == "not_by_me":
        docs_query = base_query.filter(Document.created_by != user.id)
    else:
        docs_query = base_query

    if hx_request:
        template_name = "components/docs_table.html"

    offset = (page - 1) * size
    paginated_docs = docs_query.order_by(Document.last_updated.desc()).offset(offset).limit(size).all()
    total_docs = len(docs_query.all())

    doc_response = [DocPartialResponse(
        id=doc.id,
        name=doc.name,
        created_at=doc.created_at,
        creator=UserResponse.model_validate(doc.creator.__dict__),
        last_updated=doc.last_updated,
        access_only_me=doc.access_only_me,
    ) for doc in paginated_docs]

    return templates.TemplateResponse(
        request,
        template_name,
        {
            "user": user,
            "docs": doc_response,
            "total_docs": total_docs,
            "size": size,
            "page": page,
            "pages": ceil(total_docs / size),
        },
    )



from app.main import templates