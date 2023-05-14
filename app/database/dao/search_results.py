from typing import Optional

from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError

from app.database.dao.base_dao import BaseDAO, Model, logger
from app.models.orm_models import SearchResult


class SearchResultDAO(BaseDAO):
    model = SearchResult

    async def create_items(
        self,
        items: list[model],
    ) -> Optional[list[model]]:
        result = []
        try:
            for item in items:
                q = await self.session.execute(
                    insert(self.model).values(**item.dict()).returning(self.model.id)
                )
                item_id = q.scalar_one()
                result.append(item_id)
            await self.session.flush()
        except SQLAlchemyError as exc:
            logger.error(exc.args)
            raise
        return result
