from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import utils
from .. import database, schemas, models, oauth2


router = APIRouter(tags=['Autentication'])

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.Employee).filter(models.Employee.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    

    #create a token
    #return token

    access_token = oauth2.create_acess_token(data={"user_id": user.id})
    return {"acess_token": access_token, "token_type": "bearer"}