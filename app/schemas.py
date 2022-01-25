from subprocess import CompletedProcess
from xmlrpc.client import Boolean
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional




class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    manager: bool = False


class UserOut(BaseModel):
    id: int
    email: EmailStr
    manager: bool = False
    created_at: datetime
    class Config:
        orm_mode=True


class Token(BaseModel):
    access_token: str
    token_type: str
    manager: Boolean

class TokenData(BaseModel):
    id: Optional[str] = None


class DistCreate(BaseModel):
    id_employee: int
    id_ordem_servico: int
    completed: Boolean = False
    
