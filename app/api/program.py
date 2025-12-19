from fastapi import APIRouter, Depends
from typing import List, Annotated

from app.schemas.program import ProgramCreate, ProgramResponse, ProgramUpdate
from app.services.programs.find_all import FindAll
from app.services.programs.create import Create
from app.services.programs.update import Update

router = APIRouter(tags=["Program"])

FindAllServiceDep = Annotated[FindAll, Depends()]
CreateServiceDep = Annotated[Create, Depends()]
UpdateServiceDep = Annotated[Update, Depends()]


@router.get("/programs", response_model=List[ProgramResponse])
async def get_programs(service: FindAllServiceDep):
    return await service.execute()


@router.post("/programs", response_model=ProgramResponse)
async def create_program(program: ProgramCreate, service: CreateServiceDep):
    return await service.execute(program)


@router.patch("/programs/{program_id}", response_model=ProgramResponse)
async def update_program(program_id: int, program: ProgramUpdate, service: UpdateServiceDep):
    return await service.execute(program_id, program)
