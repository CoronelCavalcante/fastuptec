from subprocess import CompletedProcess
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
    created_at: datetime
    class Config:
        orm_mode=True


class Token(BaseModel):
    acess_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None


class DistCreate(BaseModel):
    id_employee: int
    id_ordem_servico: int
