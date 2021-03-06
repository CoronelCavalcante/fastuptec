import requests
import base64
import json
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from starlette.routing import Router
from ..config import settings
from ..database import get_db
from typing import List, Optional
from sqlalchemy import func
from .. import models,schemas, oauth2, main
from sqlalchemy.orm import Session, query
from sqlalchemy.exc import IntegrityError



router = APIRouter(
    prefix="/OS",
    tags=['OS']
)

##OrdemServico.py lida com todos os request de ordem de servico.



#variavel host e token sao usadas em todas as chamdas para a API da IXC. sendo assim essa API serve como middleware

host = 'https://abn.redeip.com.br/'
token = settings.ixc_token.encode('utf-8')


#get_cliente, get_login, get_assunto, get_contrato tem que ser chamado varias vezes, cada um delas é chamado 1 
# vez para cada ordem de servico normalmente isso seria uma consulta com JOINS num banco de dados mas a API da IXC nao permite isso, 
# eu tentei contactar a IXC para ao menos poder fazer uma unica colsulta com varios IPs de clientes 
# mas falaram que é impossivel tem que ser um a um
#esse é o motivo pelo qual pode demorar de 10 a 30 segundos para receber as informações

def get_cliente(id_cliente): 
   
    url = "https://abn.redeip.com.br/webservice/v1/cliente".format(host)

    payload = json.dumps({
        'qtype': 'cliente.id',
        'query': id_cliente,
        'oper': '=',
        'page': '1',
        'rp': '100',
        'sortname': 'cliente.id',
        'sortorder': 'asc'
    })

    headers = {
        'ixcsoft': 'listar',
        'Authorization': 'Basic {}'.format(base64.b64encode(token).decode('utf-8')),
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=payload, headers=headers)
    resjson = response.json()
    registros = resjson.get('registros')
    return registros

def get_login(id_login):
    url = "https://abn.redeip.com.br/webservice/v1/radusuarios".format(host)
    payload = json.dumps({
    'qtype': 'radusuarios.id',
    'query':  id_login,
    'oper': '=',
    'page': '1',
    'rp': '20',
    'sortname': 'radusuarios.id',
    'sortorder': 'asc'
})

    headers = {
        'ixcsoft': 'listar',
        'Authorization': 'Basic {}'.format(base64.b64encode(token).decode('utf-8')),
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=payload, headers=headers)
    resjson = response.json()
    registros = resjson.get('registros')
    return registros #login volta como registros ao inves de registros[0] pra verificar se é ou nao None. pois cliente podem justamente ter a ordem de serviço pra colocar 

def get_one_assunto(id):
    url = "https://abn.redeip.com.br/webservice/v1/su_oss_assunto".format(host)

    payload = json.dumps({
        'qtype': 'su_oss_assunto.id',
        'query': id,
        'oper': '=',
        'page': '1',
        'rp': '100',
        'sortname': 'su_oss_assunto.id',
        'sortorder': 'asc'
    })

    headers = {
        'ixcsoft': 'listar',
        'Authorization': 'Basic {}'.format(base64.b64encode(token).decode('utf-8')),
        'Content-Type': 'application/json'
    }





    
    response = requests.post(url, data=payload, headers=headers)
    resjson = response.json()
    registros = resjson.get('registros')
   
    return registros[0]



def get_one_contrato(id):
    url = "https://abn.redeip.com.br/webservice/v1/cliente_contrato".format(host)

    payload = json.dumps({
        'qtype': 'cliente_contrato.id',
        'query': id,
        'oper': '=',
        'page': '1',
        'rp': '100',
        'sortname': 'cliente_contrato.id',
        'sortorder': 'asc'
    })

    headers = {
        'ixcsoft': 'listar',
        'Authorization': 'Basic {}'.format(base64.b64encode(token).decode('utf-8')),
        'Content-Type': 'application/json'
    }





    
    response = requests.post(url, data=payload, headers=headers)
    resjson = response.json()
    registros = resjson.get('registros')
   
    return registros[0]






#get ordems abertas faz uma unica consulta que retorna todas as ordens de servico que estejam marcadas como abertas no banco
def get_ordem_abertas():
    url = "https://abn.redeip.com.br/webservice/v1/su_oss_chamado".format(host)
    

    payload = json.dumps({
        'qtype': 'su_oss_chamado.status',
        'query': 'A',
        'oper': '=',
        'page': '1',
        'rp': '100',
        'sortname': 'su_oss_chamado.id',
        'sortorder': 'asc'
    })

    headers = {
        'ixcsoft': 'listar',
        'Authorization': 'Basic {}'.format(base64.b64encode(token).decode('utf-8')),
        'Content-Type': 'application/json'
    }





    response = requests.post(url, data=payload, headers=headers)
    resjson = response.json()
    registros = resjson.get('registros')
    if not registros:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'ordens abertas nao foram encontradas')
    
    return registros


#usada para pegar um ordem qualquer por id dela. to usado quando se faz alguma consulta de ordem fechada
def get_one_by_id(id):
    url = "https://abn.redeip.com.br/webservice/v1/su_oss_chamado".format(host)

    payload = json.dumps({
        'qtype': 'su_oss_chamado.id',
        'query': id,
        'oper': '=',
        'page': '1',
        'rp': '100',
        'sortname': 'su_oss_chamado.id',
        'sortorder': 'asc'
    })

    headers = {
        'ixcsoft': 'listar',
        'Authorization': 'Basic {}'.format(base64.b64encode(token).decode('utf-8')),
        'Content-Type': 'application/json'
    }





    response = requests.post(url, data=payload, headers=headers)
    resjson = response.json()
    registros = resjson.get('registros')
    if not registros:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'ordem {id} nao existe')
    return registros[0]



#Essa rota é usada unicamente por gerentes para que o front end so precise fazer uma unica chamada para essa api
#ela carrega todas as infos de ordens de servicos abertas, distribuidas e do proprio gerente
@router.get("/Manager")
def all_manager(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.manager == False:        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Você não é manager')
    distribuidas = db.query(models.OrdemDistribuida).all()
    if not distribuidas:        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não ha ordens distribuidas no banco de dados')
    ordemDistCompleta = []
    for ordem in distribuidas:
        minhaordem = get_one_by_id(str(ordem.id_ordem_servico))
        cliente = get_cliente(minhaordem.get('id_cliente'))
        if cliente !=None:
            cliente = cliente[0]
        login = get_login(minhaordem.get('id_login'))
        if login != None:
            login = login[0] 
        contrato = get_one_contrato(minhaordem.get('id_contrato'))
        assunto = get_one_assunto(minhaordem.get('id_assunto'))     
        poster = db.query(models.Employee.id,models.Employee.email,models.Employee.created_at,models.Employee.manager).filter(models.Employee.id == ordem.id_poster).first()
        employee = db.query(models.Employee.id,models.Employee.email,models.Employee.created_at,models.Employee.manager).filter(models.Employee.id == ordem.id_employee).first()
        associar = {'ordem_servico': minhaordem,'cliente': cliente, 'login': login, 'distribuida': ordem, 'poster': poster, 'employee': employee, 'contrato': contrato, 'assunto': assunto }
        ordemDistCompleta.append(associar)
    minhasOrdens = []
    ordensDB= db.query(models.OrdemDistribuida).filter(models.OrdemDistribuida.id_employee == current_user.id).all()
    if ordensDB:
        for ordem in ordensDB:
            minhaordem = get_one_by_id(str(ordem.id_ordem_servico))
            cliente = get_cliente(minhaordem.get('id_cliente'))
            login = get_login(minhaordem.get('id_login'))
            if login != None:
                login = login[0] 
            contrato = get_one_contrato(minhaordem.get('id_contrato'))
            assunto = get_one_assunto(minhaordem.get('id_assunto'))     
            posterquery = db.query(models.Employee).filter(models.Employee.id == ordem.id_poster).first()
            poster = posterquery.email
            associar = {'ordem_servico': minhaordem,'cliente': cliente, 'login': login, 'completed': ordem.completed, 'created_at': ordem.created_at, 'givem_by': poster, 'contrato': contrato, 'assunto': assunto  }
            minhasOrdens.append(associar)
    managercompleto = {'ordens_abertas': main.ordemMemoria, 'minhas_ordens': minhasOrdens,'ordens_dist':ordemDistCompleta}
    return (managercompleto)

#para melhorar um pouco o desempenho eu coloquei para o servidor manter em memoria as ordens de servicos abertas
#essa rota pede a lista de ordens abertas completas(com cliente contrato login)
@router.get("/Abertas")
def get_os(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.manager == False:        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Você não é autorizado a ver todas as Ordens de Servicos abertas')
    

    return (main.ordemMemoria)


#rota para distribuir uma Os para um funcionario criando uma nova entrada no banco de dados
@router.post("/Dist", status_code=status.HTTP_201_CREATED)
def dist_os(dist: schemas.DistCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.manager == False:        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Você não é autorizado a Distruibuir uma OS')
    employee= db.query(models.Employee).filter(models.Employee.id == dist.id_employee).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Funcionario com id {dist.id_employee} não existe")
    ordems_abertas = main.ordemMemoria
    for ordem in ordems_abertas:
        if str(ordem.get("ordem_servico").get('id')) == str(dist.id_ordem_servico):
            nova_ordem = models.OrdemDistribuida(id_employee = employee.id,  id_ordem_servico = int(ordem.get("ordem_servico").get('id')), id_poster = current_user.id, completed = dist.completed) 
            db.add(nova_ordem)
            try:                
                db.commit()
                return{"message": "Ordem Distribuida com sucesso"}
            except IntegrityError:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"A Ordem de Servico: {ordem.get('ordem_servico').get('id')} Ja foi dada ao Funcionario: {employee.email}")   
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ordem de Servico nao encontrada na lista de Abertas")
            
#rota para perdi a lista de ordens distribuidas ela nao fica em memoria do servidor pois pode ficar muito longa com o passar do tempo

@router.get("/Dist")
def get_os_distribuida(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.manager == False:        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Voce nao e autorizado a ver todas as Ordens de Servicos abertas')
    distribuidas = db.query(models.OrdemDistribuida).all()
    if not distribuidas:        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não ha ordens distribuidas no banco de dados')
    ordemDistCompleta = []
    for ordem in distribuidas:
        minhaordem = get_one_by_id(str(ordem.id_ordem_servico))
        cliente = get_cliente(minhaordem.get('id_cliente'))
        if cliente !=None:
            cliente = cliente[0]
        login = get_login(minhaordem.get('id_login'))
        if login != None:
            login = login[0] 
        contrato = get_one_contrato(minhaordem.get('id_contrato'))
        assunto = get_one_assunto(minhaordem.get('id_assunto'))     
        poster = db.query(models.Employee.id,models.Employee.email,models.Employee.created_at,models.Employee.manager).filter(models.Employee.id == ordem.id_poster).first()
        employee = db.query(models.Employee.id,models.Employee.email,models.Employee.created_at,models.Employee.manager).filter(models.Employee.id == ordem.id_employee).first()
        associar = {'ordem_servico': minhaordem,'cliente': cliente, 'login': login, 'distribuida': ordem, 'poster': poster, 'employee': employee, 'contrato': contrato, 'assunto': assunto }
        ordemDistCompleta.append(associar)



    return (ordemDistCompleta)


#rota usada para funcionarios receberem as suas ordens de servicos especificas
@router.get("/My")
def get_my_os(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    minhasOrdens = []
    ordensDB= db.query(models.OrdemDistribuida).filter(models.OrdemDistribuida.id_employee == current_user.id).all()
    if not ordensDB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não ha ordens distribuidas no banco de dados')
    for ordem in ordensDB:
        minhaordem = get_one_by_id(str(ordem.id_ordem_servico))
        cliente = get_cliente(minhaordem.get('id_cliente'))
        login = get_login(minhaordem.get('id_login'))
        if login != None:
            login = login[0] 
        contrato = get_one_contrato(minhaordem.get('id_contrato'))
        assunto = get_one_assunto(minhaordem.get('id_assunto'))     
        posterquery = db.query(models.Employee).filter(models.Employee.id == ordem.id_poster).first()
        poster = posterquery.email
        associar = {'ordem_servico': minhaordem,'cliente': cliente, 'login': login, 'completed': ordem.completed, 'created_at': ordem.created_at, 'givem_by': poster, 'contrato': contrato, 'assunto': assunto  }
        minhasOrdens.append(associar)

    return (minhasOrdens)



#rota usada para gerentes receberem todas as ordens de servicos que ja foram distribuidaspara um funcionario especifico
@router.get("/emp/{id}")

def get_emp_os(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.manager == False:        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Voce nao e autorizado a ver todas as Ordens de Servicos abertas')
    Ordens = []
    ordensDB= db.query(models.OrdemDistribuida).filter(models.OrdemDistribuida.id_employee == id).all()
    if not ordensDB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não ha ordens distribuidas para esse funcionario no banco de dados')
    for ordem in ordensDB:
        minhaordem = get_one_by_id(str(ordem.id_ordem_servico))
        cliente = get_cliente(minhaordem.get('id_cliente'))
        if cliente != None:
            cliente = cliente[0]
        login = get_login(minhaordem.get('id_login'))
        if login != None:
            login = login[0] 
        contrato = get_one_contrato(minhaordem.get('id_contrato'))
        assunto = get_one_assunto(minhaordem.get('id_assunto'))         
        posterquery = db.query(models.Employee).filter(models.Employee.id == ordem.id_poster).first()
        poster = posterquery.email
        associar = {'ordem_servico': minhaordem,'cliente': cliente, 'login': login, 'completed': ordem.completed, 'created_at': ordem.created_at, 'givem_by': poster, 'contrato': contrato, 'assunto': assunto  }
        Ordens.append(associar)

    return (Ordens)






#rota usada para receber uma ordem especifca por ID.
@router.get("/{id}")
def get_one(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.manager == False:        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Nao autorizado')
    
    minhaordem = get_one_by_id(str(id))
    
    cliente = get_cliente(minhaordem.get('id_cliente'))
    login = get_login(minhaordem.get('id_login'))
    if login != None:
        login = login[0]
    contrato = get_one_contrato(minhaordem.get('id_contrato'))
    assunto = get_one_assunto(minhaordem.get('id_assunto'))    
    minhaordem = {'ordem_servico': minhaordem,'cliente': cliente, 'login': login, 'contrato': contrato, 'assunto': assunto }
    

    return (minhaordem)