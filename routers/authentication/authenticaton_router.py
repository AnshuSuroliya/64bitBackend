from fastapi import FastAPI, HTTPException, Depends, APIRouter, Query,Request
from passlib.context import CryptContext
from datetime import datetime, timedelta

from azure.cosmos import CosmosClient, exceptions

from .jwt_service import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user
from .userModels import *
router = APIRouter()

ENDPOINT = "https://64bit.documents.azure.com:443/"
KEY = "Jt52zG1yfldaWoluTcWTgZHuH2yw4PDOtrRqMWV0dpoZLMvQPNwVIo0JsS81bkhA9cpGyI58cQPoACDbtNhKzQ=="

client = CosmosClient(ENDPOINT, KEY)
database = client.get_database_client("64bit")
container = database.get_container_client("Users")




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/signup/")
async def signup(user: User):
    try:
        query = f"SELECT * FROM c WHERE c.email = '{user.email}'"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        if items:
            signup_res = signupRes()
            signup_res.message = "User Already registered"
            signup_res.success = False
            return signup_res
        hashed_password = hash_password(user.password)
        user_doc = {"firstName":user.firstName,"lastName":user.lastName,"email": user.email, "password": hashed_password}
        print(user_doc)
        container.create_item(user_doc,enable_automatic_id_generation=True)
        signup_res=signupRes()
        signup_res.message="User Registered Successfully"
        signup_res.success=True
        return signup_res
    except exceptions.CosmosResourceExistsError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login/")
async def login(login : loginReq):
    try:
        query = f"SELECT * FROM c WHERE c.email = '{login.email}'"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        if not items:
           login_res=loginRes()
           login_res.message="Invalid Email"
           login_res.success=False
           login_res.jwt=None
           login.email=None
           return login_res
        stored_user = items[0]
        if not verify_password(login.password, stored_user["password"]):
            login_res = loginRes()
            login_res.message = "Wrong Password"
            login_res.success = False
            login_res.jwt = None
            login.email=None
            return login_res
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": login.email}, expires_delta=access_token_expires)
        login_res=loginRes()
        login_res.message="Login Successfull"
        login_res.success=True
        login_res.jwt=access_token
        login_res.email=login.email
        return login_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/getUserData/")
async def getUserData(email: EmailReq,user: dict = Depends(get_current_user)):

    try:
        print(email)
        query = f"SELECT * FROM Users u WHERE u.email='{email.email}'"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        if not items:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = items[0]
        return UserResponse(firstName=user_data["firstName"], lastName=user_data["lastName"], email=user_data["email"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
