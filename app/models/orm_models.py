import datetime
from sqlalchemy import (
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.database.connect import Base


class BaseClass:
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())


class SearchResult(BaseClass, Base):
    url: Mapped[str]
    name: Mapped[str]
