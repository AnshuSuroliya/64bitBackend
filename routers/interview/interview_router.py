from azure.cosmos import PartitionKey, exceptions, container, CosmosClient
from fastapi import APIRouter, Request, exceptions, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from .requests import *
from .responses import IResponse
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

@router.get("/getinterviewdata/{interview_id}")
async def get_Interview_data(interview_id:str,user: dict = Depends(get_current_user)):
    ENDPOINT = "https://64bit.documents.azure.com:443/"
    KEY = "Jt52zG1yfldaWoluTcWTgZHuH2yw4PDOtrRqMWV0dpoZLMvQPNwVIo0JsS81bkhA9cpGyI58cQPoACDbtNhKzQ=="

    client = CosmosClient(ENDPOINT, KEY)
    database = client.get_database_client("64bit")
    container_current = database.get_container_client("interview")
    print(interview_id)
    try:
        query = f"SELECT * FROM interview r WHERE r.id='{interview_id}'"
        items = list(container_current.query_items(query, enable_cross_partition_query=True))
        print(items)
        if not items:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = items[0]
        return IResponse(candidate_name=user_data["candidate_name"],skill_name=user_data["skills"][0]["name"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


