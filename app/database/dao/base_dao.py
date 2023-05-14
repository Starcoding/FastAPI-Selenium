import datetime
from abc import ABC
from typing import TypeVar, Type, Optional, Any, Iterable

from pydantic import BaseModel
from sqlalchemy import select, delete, insert, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from sqlalchemy.sql.functions import count

from app.database.connect import Base
from app.logger import get_logger

logger = get_logger("sqlalchemy", "./logs/sqlalchemy.log")

Model = TypeVar("Model", bound="Base")
BM = TypeVar("BM", bound=BaseModel)


class BaseDAO(ABC):
    model: Type[Base] = Base
    TKwargs = Optional[Any]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.trans = self.session.begin()

    async def __aenter__(self):
        await self.trans.__aenter__()
        return self  # type: ignore

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        await self.trans.__aexit__(exc_type, exc_val, exc_tb)
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def get_list(self, **kwargs: TKwargs) -> list[Model] | Any:
        query = self._construct_query(select(self.model), **kwargs)
        q = await self.session.execute(query)
        results = q.scalars().all()
        return results

    async def get_selected_list(
        self, select_: Iterable, **kwargs: TKwargs
    ) -> list[Model] | Any:
        query = self._construct_query(select(*select_), **kwargs)
        q = await self.session.execute(query)
        results = q.scalars().all()
        return results

    async def get_item_by_id(self, item_id: int, **kwargs: TKwargs) -> Optional[Model]:
        query = self._construct_query(select(self.model), **kwargs)
        try:
            q = await self.session.execute(query.where(self.model.id == item_id))
        except SQLAlchemyError as exc:
            logger.error(exc.args)
            raise
        else:
            item: Optional[Model] = q.scalar_one_or_none()
        return item

    async def delete_item(self, item_id: int) -> bool:
        item = await self.get_item_by_id(item_id)
        if not item:
            return False
        try:
            await self.session.execute(
                delete(self.model).where(self.model.id == item_id)
            )
            await self.session.flush()
        except SQLAlchemyError as exc:
            logger.error(exc.args)
            raise
        return True

    async def create_item(self, item: BM, **kwargs: TKwargs) -> Optional[Model]:
        try:
            q = await self.session.execute(
                insert(self.model).values(**item.dict()).returning(self.model.id)
            )
            item_id = q.scalar_one()
            await self.session.flush()
        except SQLAlchemyError as exc:
            logger.error(exc.args)
            raise
        return await self.get_item_by_id(item_id, **kwargs)

    async def update_item(
        self, item_id: int, item: BM, **kwargs: TKwargs
    ) -> Optional[Model]:
        try:
            await self.session.execute(
                update(self.model)
                .where(self.model.id == item_id)
                .values(**item.dict(exclude_none=True))
            )
            await self.session.flush()
        except SQLAlchemyError as exc:
            logger.error(exc.args)
            raise
        return await self.get_item_by_id(item_id, **kwargs)

    async def check_ids_exists(self, ids: list[int]) -> bool:
        q = await self.session.execute(select(count()).where(self.model.id.in_(ids)))  # type: ignore
        cnt: int = q.scalar_one()
        return len(ids) == cnt

    def _construct_query(
        self,
        query: Select,
        where: Optional[Iterable] = None,
        select_in_load: Optional[Iterable] = None,
        order_by: Optional[Iterable] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Select:
        if where:
            query = query.where(*where)
        if select_in_load:
            for option in select_in_load:
                query = query.options(selectinload(option))
        if order_by:
            query = query.order_by(*order_by)
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        return query
