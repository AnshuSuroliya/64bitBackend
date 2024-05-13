from fastapi import FastAPI, HTTPException, Depends, APIRouter
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt
from azure.cosmos import CosmosClient, exceptions
from .userModels import *
router = APIRouter()

ENDPOINT = "https://64bit.documents.azure.com:443/"
KEY = "Jt52zG1yfldaWoluTcWTgZHuH2yw4PDOtrRqMWV0dpoZLMvQPNwVIo0JsS81bkhA9cpGyI58cQPoACDbtNhKzQ=="

client = CosmosClient(ENDPOINT, KEY)
database = client.get_database_client("64bit")
container = database.get_container_client("Users")

SECRET_KEY = "5367566B59703373367639792F423F4528482B4D6251655468576D5A71347437"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
@router.post("/signup/")
async def signup(user: User):
    print(user)
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
        print(login)
        query = f"SELECT * FROM c WHERE c.email = '{login.email}'"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        print(items)
        if not items:
           login_res=loginRes()
           login_res.message="Invalid Email"
           login_res.success=False
           login_res.jwt=None
           return login_res
        stored_user = items[0]

        if not verify_password(login.password, stored_user["password"]):
            login_res = loginRes()
            login_res.message = "Wrong Password"
            login_res.success = False
            login_res.jwt = None
            return login_res

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": login.email}, expires_delta=access_token_expires)
        login_res=loginRes()
        login_res.message="Login Successfull"
        login_res.success=True
        login_res.jwt=access_token
        return login_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
