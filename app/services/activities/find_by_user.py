from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.exceptions.business import EntityNotFoundError
from app.core.database import get_db
from app.models.activity import Activity
from app.services.users.find_by_slack_id import FindBySlackId


class FindByUser:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        user_find_by_slack_id: FindBySlackId = Depends()
    ):
        self.db = db
        self.user_find_by_slack_id = user_find_by_slack_id

    async def execute(self, slack_id: str):
        user_found = await self.user_find_by_slack_id.execute(slack_id)
        if not user_found:
            raise EntityNotFoundError("User", slack_id)
        stmt = select(Activity).where(Activity.user_id == user_found.id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
