from fastapi import APIRouter, Depends, Header, Path, Query
from typing import List, Annotated

from app.schemas.activity import ActivityCreate, ActivityResponse
from app.services.activities.create import Create
from app.services.activities.find_by_user import FindByUser
from app.services.activities.find_by_user_and_program import FindByUserAndProgram

router = APIRouter(tags=["Activity"])

CreateServiceDep = Annotated[Create, Depends()]
FindByUserServiceDep = Annotated[FindByUser, Depends()]
FindByUserAndProgramServiceDep = Annotated[FindByUserAndProgram, Depends()]


@router.get("/activities", response_model=List[ActivityResponse])
async def get_activities_by_user(
    service: FindByUserServiceDep,
    x_slack_user_id: str = Header(..., title="ID Slack User"),
    reference_date: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
):
    return await service.execute(x_slack_user_id, reference_date)


@router.get("/programs/{slack_channel}/activities", response_model=List[ActivityResponse])
async def get_activities_by_user_and_program(
    service: FindByUserAndProgramServiceDep,
    slack_channel: str = Path(..., title="Program Slack Channel"),
    x_slack_user_id: str = Header(..., title="ID Slack User"),
    reference_date: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
):
    return await service.execute(slack_channel, x_slack_user_id, reference_date)


@router.post("/programs/{slack_channel}/activities", response_model=ActivityResponse)
async def create_activity(
    service: CreateServiceDep,
    activity_create: ActivityCreate,
    slack_channel: str = Path(..., title="Program Slack Channel"),
    x_slack_user_id: str = Header(..., title="ID Slack User"),
):
    return await service.execute(activity_create, slack_channel, x_slack_user_id)
