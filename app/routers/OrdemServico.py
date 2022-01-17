import requests
import base64
import json
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from starlette.routing import Router
from ..config import settings

rounter = APIRouter(
    prefix="/OS",
    tags=['OS']
)
#deixei so url como variavel em função pq ela muda sempre
host = 'https://abn.redeip.com.br/'
token = settings.ixc_token.encode('utf-8')

def get_cliente(ordem): 
   
    url = "https://abn.redeip.com.br/webservice/v1/cliente".format(host)

    payload = json.dumps({
        'qtype': 'cliente.id',
        'query': ordem.get('id_cliente'),
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

def get_login(ordem):
    url = "https://abn.redeip.com.br/webservice/v1/radusuarios".format(host)
    payload = json.dumps({
    'qtype': 'radusuarios.id',
    'query':  ordem.get('id_login'),
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



@rounter.get("/Abertas")
def get_os():
    ordemCompleta = []
    ordems_abertas = get_ordem_abertas()
    for ordem in ordems_abertas:
        cliente = get_cliente(ordem)
        login = get_login(ordem)
        if login != None:
            login = login[0] 
             

        associar = {'ordem_servico': ordem,'cliente': cliente, 'login': login}
        ordemCompleta.append(associar)    



    return (ordemCompleta)

