from typing import Optional, List
from fastapi import Query, Request, Depends
from sqlalchemy import select, desc, asc, func
from sqlalchemy.orm import Session

from database import get_db
from taskboard.schemas import TaskOut


def paginate_query(query, page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size)

class Paginator:
    def __init__(self, db: Session, request: Request):
        self.db = db
        self.request = request

    def paginate(self, query, order_by: Optional[str] = None, page: int = 1, page_size: int = 10):
        total_records = self.db.execute(select(func.count()).select_from(query.subquery())).scalar()
        if order_by:
            if order_by.startswith("-"):
                field = order_by[1:]
                query = query.order_by(desc(field))
            else:
                field = order_by
                query = query.order_by(asc(field))

            if not field in query.columns:
                raise ValueError(f"Invalid field for ordering: {field}")

        query = paginate_query(query, page, page_size)
        result = self.db.execute(query).scalars().all()

        return result, total_records


def get_paginator(
    request: Request,
    db: Session = Depends(get_db)
) -> Paginator:
    return Paginator(db=db, request=request)
