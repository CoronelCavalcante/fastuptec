from pydantic import BaseModel
from pydantic import BaseModel, EmailStr
from datetime import datetime



class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        orm_mode=True


class Token(BaseModel):
    acess_token: str
    token_type: str
