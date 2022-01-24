import requests
import base64
import json
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from starlette.routing import Router
from ..config import settings
from ..database import get_db
from typing import List, Optional
from sqlalchemy import func
from .. import models,schemas, oauth2
from sqlalchemy.orm import Session, query
from sqlalchemy.exc import IntegrityError


router = APIRouter(
    prefix="/OS",
    tags=['OS']
)
#MELHOR TACAR TODAS AS FUNÇOES DA AIC EM OUTRO ARQUIVO
#deixei so url como variavel em função pq ela muda sempre
host = 'https://abn.redeip.com.br/'
token = settings.ixc_token.encode('utf-8')

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
    return registros[0]

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
    return registros


def get_my_ordem_aberta(id):
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
    return registros






@router.get("/Abertas")
def get_os(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.manager == False:        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Você não é autorizado a ver todas as Ordens de Servicos abertas')
    
    ordemCompleta = []
    ordems_abertas = get_ordem_abertas()
    if not ordems_abertas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Nao existem ordems abertas')
    for ordem in ordems_abertas:
        cliente = get_cliente(ordem.get('id_cliente'))
        login = get_login(ordem.get('id_login'))
        if login != None:
            login = login[0] 
             

        associar = {'ordem_servico': ordem,'cliente': cliente, 'login': login}
        ordemCompleta.append(associar)    



    return (ordemCompleta)


@router.post("/Dist", status_code=status.HTTP_201_CREATED)
def dist_os(dist: schemas.DistCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.manager == False:        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Você não é autorizado a Distruibuir uma OS')
    employee= db.query(models.Employee).filter(models.Employee.id == dist.id_employee).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Funcionario com id {dist.id_employee} não existe")
    ordems_abertas = get_ordem_abertas()
    print("dist.idOS: ", dist.id_ordem_servico)
    for ordem in ordems_abertas:
        print("ORDEM: ", ordem.get('id'))
        if ordem.get('id') == str(dist.id_ordem_servico):
            nova_ordem = models.OrdemDistribuida(id_employee = employee.id,  id_ordem_servico = int(ordem.get('id')), id_poster = current_user.id, completed = dist.completed) 
            db.add(nova_ordem)
            try:                
                db.commit()
                return{"message": "Ordem Distribuida com sucesso"}
            except IntegrityError:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"A Ordem de Servico: {ordem.get('id')} Ja foi dada ao Funcionario: {employee.email}")   
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ordem de Servico nao encontrada na lista de Abertas")
            


@router.get("/Dist")
def get_os_distribuida(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.manager == False:        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Voce nao e autorizado a ver todas as Ordens de Servicos abertas')
    distribuidas = db.query(models.OrdemDistribuida).all()
    if not distribuidas:        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não ha ordens distribuidas no banco de dados')
     



    return (distribuidas)



@router.get("/My")
def get_my_os(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    minhasOrdens = []
    ordensDB= db.query(models.OrdemDistribuida).filter(models.OrdemDistribuida.id_employee == current_user.id).all()
    if not ordensDB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não ha ordens distribuidas no banco de dados')
    for ordem in ordensDB:
        minhaordem = get_my_ordem_aberta(str(ordem.id_ordem_servico))
        cliente = get_cliente(minhaordem[0].get('id_cliente'))
        login = get_login(minhaordem[0].get('id_login'))
        if login != None:
            login = login[0] 
             
        posterquery = db.query(models.Employee).filter(models.Employee.id == ordem.id_poster).first()
        poster = posterquery.email
        associar = {'ordem_servico': minhaordem,'cliente': cliente, 'login': login, 'completed': ordem.completed, 'created_at': ordem.created_at, 'givem_by': poster }
        minhasOrdens.append(associar)

    return (minhasOrdens)
