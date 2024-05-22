from pydantic import BaseModel


class User(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str

class signupRes(BaseModel):
    message:str | None=""
    success:bool | None=""
class loginReq(BaseModel):
    email:str | None
    password:str | None

class loginRes(BaseModel):
    message:str | None =""
    success:bool |None =""
    jwt:str |None =""
    email:str | None =""

class UserResponse(BaseModel):
    firstName: str
    lastName: str
    email: str
class EmailReq(BaseModel):
    email:str