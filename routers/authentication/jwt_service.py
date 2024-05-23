from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import Header, FastAPI, Depends, HTTPException,Request
#from jose import JWTError

SECRET_KEY = "5367566B59703373367639792F423F4528482B4D6251655468576D5A71347437"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
async def get_current_user(request: Request, authorization: str = Header(...)) -> dict:
    #try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme. Must be Bearer.")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    #except (ValueError, JWTError):
    #    raise HTTPException(status_code=401, detail="Invalid or missing token")

