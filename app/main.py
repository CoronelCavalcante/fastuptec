from fastapi import FastAPI, Depends
from .routers import ordemServico, user, auth
from . import models,schemas,utils, oauth2
from .database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from sqlalchemy.orm import Session, query
from sqlalchemy.exc import IntegrityError
from fastapi_utils.session import FastAPISessionMaker
from .config import settings
from typing import List
from .routers.ordemServico import get_ordem_abertas


SQLALCHEMY_DATABASE_URL = "mysql+pymysql://{0}:{1}@{2}/{3}".format(settings.database_username, settings.database_password, settings.database_hostname,settings.database_name)

sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)


models.Base.metadata.create_all(bind=engine)


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(ordemServico.router)
app.include_router(user.router)
app.include_router(auth.router)



@app.get("/")
def root():
    return {"message": f"Hello World!!!"}

#Esse codigo ta exelente nao sei como melhorar mais
@app.on_event("startup")
@repeat_every(seconds=60 * 10)
def update_ordem_dist():
    with sessionmaker.context_session() as db:
        distribuidas = db.query(models.OrdemDistribuida).all()
        if distribuidas:   
                     
            abertas = get_ordem_abertas()
            A_abertas = []
            for o in abertas:
                aberta = int(o.get("id"))
                A_abertas.append(aberta)            
           
            amudar = db.query(models.OrdemDistribuida).filter(models.OrdemDistribuida.id_ordem_servico.notin_(A_abertas))
            amudar.update({"completed" : True})
            db.commit()
            

                    

            
    


