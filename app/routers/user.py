from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models,schemas,utils, oauth2
from sqlalchemy.orm import Session, query
from ..database import get_db
from sqlalchemy.exc import IntegrityError



router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.manager == False:        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Você não é autorizado a criar novos usuarios')
    
    hashed_password=utils.hash(user.password)
    user.password = hashed_password
    new_user = models.Employee(**user.dict())
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Email ja registrado")



@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db) ):
    user = db.query(models.Employee).filter(models.Employee.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} was not found")
    
    return user


# @router.post("/adm", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
# def create_first_user(db: Session = Depends(get_db)):
#     hashed_password=utils.hash("adm123")
    
#     new_user = models.Employee(email="adm@gmail.com", password = hashed_password, manager = True)
#     db.add(new_user)
#     try:
#         db.commit()
#         db.refresh(new_user)
#         return new_user
#     except IntegrityError:
#                 db.rollback()
#                 raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Email ja registrado")



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #cursor.execute("""DELETE FROM posts WHERE id= %s RETURNING *""", (str(id),))
   # deleted_post = cursor.fetchone()
   # conn.commit()
    if current_user.manager == False:        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Você não é autorizado a criar novos usuarios')
    
    emp_query = db.query(models.Employee).filter(models.Employee.id == id)
    empDel = emp_query.first()
    if empDel == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Employee with id: {id} does not exist')
    if empDel.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Not Authorized to perform request action")
    emp_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)