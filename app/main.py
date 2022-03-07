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
from .routers.ordemServico import get_ordem_abertas, get_cliente, get_one_contrato, get_login, get_one_assunto


SQLALCHEMY_DATABASE_URL = "mysql+pymysql://{0}:{1}@{2}/{3}".format(settings.database_username, settings.database_password, settings.database_hostname,settings.database_name)

sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)
ordemMemoria = []

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
    print("limpando ordemmemoria")
    ordemMemoria.clear
    print("indo para o get ordem abertas")
    abertas = get_ordem_abertas()
    print("indo para o for tamano total das abertas ",len(abertas))
    for ordem in abertas:
        print("id da ordem a ser tratada ", ordem.get('id'), " id do cliente.", ordem.get('id_cliente'), "id contrato: ", ordem.get('id_contrato'), " ordem.get('id_assunto'): ", ordem.get('id_assunto') )
        print("indo para o get cliente")
        cliente = get_cliente(ordem.get('id_cliente'))
        if cliente != None:
            cliente = cliente[0]
        print("indo para o get login")
        login = get_login(ordem.get('id_login'))
        if login != None:
            login = login[0]
        print("indo para o get contrato")
        contrato = get_one_contrato(ordem.get('id_contrato'))
        print("indo para o get assunto")
        assunto = get_one_assunto(ordem.get('id_assunto'))
        associar = {'ordem_servico': ordem,'cliente': cliente, 'login': login, 'assunto': assunto, 'contrato': contrato}
        ordemMemoria.append(associar)
    print("ordem memoria carregada")
    
    with sessionmaker.context_session() as db:
        distribuidas = db.query(models.OrdemDistribuida).all()
        
        if distribuidas:   
                     
            A_abertas = []
            for o in abertas:
                aberta = int(o.get("id"))
                A_abertas.append(aberta)            
           
            amudar = db.query(models.OrdemDistribuida).filter(models.OrdemDistribuida.id_ordem_servico.notin_(A_abertas))
            amudar.update({"completed" : True})
            db.commit()
            

                    

            
    


