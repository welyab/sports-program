from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.exceptions.business import BusinessRuleViolationError, EntityNotFoundError, DatabaseError
from app.core.database import get_db
from app.schemas.activity import ActivityCreate
from app.models.activity import Activity
from app.schemas.user import UserCreate
from app.services.users.find_by_slack_id import FindBySlackId
from app.services.users.create import Create
from app.services.activities.check_activity_same_day import CheckActivitySameDay
from app.services.programs.find_by_id import FindById


class Create:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        user_find_by_slack_id: FindBySlackId = Depends(),
        user_create: Create = Depends(),
        check_activity_same_day: CheckActivitySameDay = Depends(),
        program_find_by_id: FindById = Depends()
    ):
        self.db = db
        self.user_find_by_slack_id = user_find_by_slack_id
        self.user_create = user_create
        self.check_activity_same_day = check_activity_same_day
        self.program_find_by_id = program_find_by_id

    async def execute(
        self,
        activity_create: ActivityCreate,
        program_id: int,
        slack_id: str,
    ):
        user_id = await self.validate_user(slack_id)
        performed_at = activity_create.performed_at or datetime.now()
        await self.validate_program(program_id, performed_at)
        await self.check_activity_same_day.execute(
            program_id,
            user_id,
            performed_at
        )

        db_activity = Activity(
            user_id=user_id,
            program_id=program_id,
            description=activity_create.description,
            evidence_url=activity_create.evidence_url,
            performed_at=performed_at
        )
        self.db.add(db_activity)
        try:
            await self.db.commit()
            await self.db.refresh(db_activity)
        except Exception:
            await self.db.rollback()
            raise DatabaseError()

        return db_activity

    async def validate_user(self, slack_id):
        user_found = await self.user_find_by_slack_id.execute(slack_id)
        if user_found:
            return user_found.id
        else:
            new_user = await self.user_create.execute(UserCreate(slack_id=slack_id, display_name=slack_id))
            return new_user.id

    async def validate_program(self, program_id, performed_at):
        program_found = await self.program_find_by_id.execute(program_id)
        if not program_found:
            raise EntityNotFoundError("Program", program_id)

        if performed_at < program_found.start_date:
            raise BusinessRuleViolationError(
                "Activity date is outside the program date range")

        if program_found.end_date and performed_at > program_found.end_date:
            raise BusinessRuleViolationError(
                "Activity date is outside the program date range")
