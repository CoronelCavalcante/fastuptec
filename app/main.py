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

#arquivo usado para incializar o banco de dados caso nao exista e estabelecer conecção com o memsmo
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://{0}:{1}@{2}/{3}".format(settings.database_username, settings.database_password, settings.database_hostname,settings.database_name)

sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)
ordemMemoria = []

models.Base.metadata.create_all(bind=engine)

#criar a API e o middle ware para receber pedidos de qualquer IP
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


#rota para teste ping
@app.get("/")
def root():
    return {"message": f"Hello World!!!"}

#rotina de manutemção usada para acessar o Banco da IXC e receber as informações de todas as OS abertas e seus detalhes
#assim ao menos é mais rapido para uma das funções do APP
@app.on_event("startup")
@repeat_every(seconds=60 * 10)
def update_ordem_dist():
   
    ordemMemoria.clear()
    abertas = get_ordem_abertas()
    for ordem in abertas:
        cliente = get_cliente(ordem.get('id_cliente'))
        if cliente != None:
            cliente = cliente[0]
        login = get_login(ordem.get('id_login'))
        if login != None:
            login = login[0]
        contrato = get_one_contrato(ordem.get('id_contrato'))
        assunto = get_one_assunto(ordem.get('id_assunto'))
        associar = {'ordem_servico': ordem,'cliente': cliente, 'login': login, 'assunto': assunto, 'contrato': contrato}
        ordemMemoria.append(associar)
    
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
            

                    

            
    


