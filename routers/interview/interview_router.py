from azure.cosmos import PartitionKey, exceptions
from fastapi import APIRouter, Request, exceptions, Depends
from fastapi.encoders import jsonable_encoder

from .requests import *
from ..authentication.jwt_service import get_current_user

router = APIRouter()


async def get_or_create_interview_container(app):
    container_name = "interview"
    try:
        app.interview_items_container = app.database.get_container_client(container_name)
        return await app.interview_items_container.read()
    except exceptions.CosmosResourceNotFoundError:
        print("Creating container with id as partition key")
        return await app.database.create_container(id=container_name, partition_key=PartitionKey(path="/id"))
    except exceptions.CosmosHttpResponseError:
        raise

@router.post("/interview/schedule")
async def schedule_interview(req: Request, schedule_req: ScheduleReq, user: dict = Depends(get_current_user)):
    interview = jsonable_encoder(schedule_req)
    new_interview = await req.app.interview_items_container.create_item(interview, enable_automatic_id_generation=True)
    return new_interview


@router.post("/interview/load/{id}")
async def load_interview(req: Request,id :str,user: dict = Depends(get_current_user)):
    print(id)
    for item in req.app.interview_items_container.query_items(
            query=f'SELECT * FROM interview r WHERE r.id={id}',
            enable_cross_partition_query=True):
            return item



