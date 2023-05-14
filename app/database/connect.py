from typing import Any

import inflection
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import as_declarative, declared_attr

metadata = MetaData()


@as_declarative()
class Base:
    id: Any
    __name__: str

    @declared_attr  # type: ignore
    def __tablename__(self) -> str:
        return inflection.underscore(self.__name__)
