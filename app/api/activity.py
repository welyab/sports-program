from fastapi import APIRouter, Depends, HTTPException, Header, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.core.database import get_db
from app.models.activity import Activity, ActivityCreate, ActivityRead
from app.models.user import User, UserCreate
from app.api.user import create_user

router = APIRouter(tags=["Activity"])

@router.get("/activities", response_model=List[ActivityRead])
async def get_activities(
    db: AsyncSession = Depends(get_db),
    x_slack_user_id: str = Header(...),
):
    user_found = await get_user_by_slack_id(db, slack_id=x_slack_user_id)
    if not user_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this slack_id not found")
    stmt = select(Activity).where(Activity.user_id == user_found.id)
    result = await db.execute(stmt)
    activities = result.scalars().all()
    return activities


@router.get("/programs/{program_id}/activities", response_model=List[ActivityRead])
async def get_activities_by_program(
    db: AsyncSession = Depends(get_db),
    program_id: int = Path(..., title="ID Program", ge=1),
    x_slack_user_id: str = Header(...),
):
    user_found = await get_user_by_slack_id(db, slack_id=x_slack_user_id)
    if not user_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this slack_id not found")
    stmt = select(Activity).where(Activity.user_id == user_found.id, Activity.program_id == program_id)
    result = await db.execute(stmt)
    activities = result.scalars().all()
    return activities


@router.post("/programs/{program_id}/activities", response_model=ActivityRead)
async def create_activity_by_program(
    activity_create: ActivityCreate,
    program_id: int = Path(..., title="ID Program", ge=1),
    db: AsyncSession = Depends(get_db),
    x_slack_user_id: str = Header(...),
):
    user_id: int
    user_found = await get_user_by_slack_id(db, slack_id=x_slack_user_id)
    if user_found:
        user_id = user_found.id
    else:
        new_user = await create_user(UserCreate(slack_id=x_slack_user_id, display_name=x_slack_user_id), db)
        user_id = new_user.id

    activity_date = activity_create.performed_at.date()
    stmt = select(Activity).where(
        Activity.user_id == user_id,
        Activity.program_id == program_id,
        func.date(Activity.performed_at) == activity_date
    )
    result = await db.execute(stmt)
    existing_activity = result.scalars().first()
    if existing_activity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An activity is already registered for the user on this date ({activity_date})."
        )

    db_activity = Activity(
        user_id=user_id,
        program_id=program_id,
        description=activity_create.description,
        evidence_url=activity_create.evidence_url,
        performed_at=activity_create.performed_at
    )
    db.add(db_activity)
    try:
        await db.commit()
        await db.refresh(db_activity)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    return db_activity


async def get_user_by_slack_id(db: AsyncSession, slack_id: str):
    stmt = select(User).where(User.slack_id == slack_id)
    result = await db.execute(stmt)
    return result.scalars().first()