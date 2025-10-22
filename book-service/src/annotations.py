from src.core.db_core import get_db_session
from src.middlewares.auth_middleware import extract_user_context

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends, FastAPI, Query, Request

DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session)
]

UserContext = Annotated[
    object,
    Depends(extract_user_context)
]


def get_common_params(
    page_number: int = Query(1, ge=0),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query(None),
    sort_order: str = Query(None)
):
    return {
        "page_number": page_number,
        "page_size": page_size,
        "sort_by": sort_by,
        "sort_order": sort_order
    }

CommonParams = Annotated[
    dict,
    Depends(get_common_params)
]


