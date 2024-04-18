from urllib3 import Retry
from ast import Break
import json
from time import sleep
import time
from turtle import goto
from numpy import append
import requests
import math
import urllib3
import sys
import os
from datetime import datetime

urllib3.disable_warnings()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def credLoad():  # vai carregar as credenciais do aparelho control ID do objeto em config.json onde a chave é o Hostname
    arquivo_cred = resource_path('config.json')
    fcred = open(arquivo_cred, 'r')
    credenciais = json.load(fcred)
    return(credenciais)


def loginCID(dev, jcred):  # Faz login no CID com as credenciais recebidas
    payload = {
        "login": ""+jcred[dev]["usuario"]+"",
        "password": ""+jcred[dev]["senha"]+""
    }
    tokenadd = ("https://"+jcred[dev]["ip"] + "/login.fcgi")
    retorno = 1
    for attempt in range(10):  # tenta logar 10 vezes

        if attempt == 10:
            print("Impossível conectar a " + dev)
            continue

        try:
            r = requests.post(tokenadd, json=payload, verify=False, timeout=3)
        except:
            time.sleep(10)
            print("Tentar nova conexão após 10seg - 401")
        else:
            data = r.json()
            retorno = data["session"]
            break
    return(retorno)


def logoffCID(dev, jcred, session):  # Faz login no CID com as credenciais recebidas
    payload = {}
    tokenadd = ("https://"+jcred[dev]["ip"] +
                "/logout.fcgi?session=" + session)
    for attempt in range(10):
        if attempt == 10:
            print("Impossível conectar a " + dev)
            exit()
        try:
            r = requests.post(tokenadd, json=payload, verify=False, timeout=10)
        except:
            time.sleep(10)
            print("Tentar nova conexão após 10seg - 402")
        else:
            break
        print("logoff")
    data = r.json()
    return(data)


def is_valid(dev, jcred, session):  # Verifica validade da Sessão
    tokenadd = ("https://"+jcred[dev]["ip"] +
                "/session_is_valid.fcgi?session=" + session)
    for attempt in range(10):
        try:
            r = requests.post(tokenadd, verify=False, timeout=10)
        except:
            print("Impossível verificar o Token, tentando novemente...")
            time.sleep(30)
        else:
            break
        print("isvalid")
    data = r.json()
    return(data["session_is_valid"])


def counter(dev, jcred, session):  # conta a quantidade de usuarios no relógio master
    tokenadd = ("https://"+jcred[dev]["ip"] +
                "/count_users.fcgi?session=" + session)
    for attempt in range(10):
        if attempt == 10:
            print("Impossível conectar a " + dev)
            exit()
        try:
            r = requests.post(tokenadd, verify=False, timeout=15)
        except:
            time.sleep(10)
            print("Tentar nova conexão após 10seg - 403")
        else:
            break
        print("counter")
    data = r.json()
    print(data['count'])
    return(data['count'])


def load_users(dev, jcred, session):  # le os usuarios do CID
    total = counter(dev, jcred, session)
    rounds = math.ceil(total/100)
    runnings = 0
    retry = 0
    users = dict
    base = dict()
    while runnings < rounds:
        print("Execução atual: " + str(runnings))
        print("Offset atual: " + str(100*runnings))

        tokenadd = ("https://"+jcred[dev]["ip"] +
                    "/load_users.fcgi?session=" + session)
        payload = {
            "templates": True,
            "limit": 100,
            "offset": int(100*runnings)
        }
        runnings += 1

        for attempt in range(10):
            if attempt == 10:
                print("Impossível conectar a " + dev)
                return(1)
            try:
                r = requests.post(tokenadd, json=payload,
                                  verify=False, timeout=20)
            except:
                time.sleep(10)
                print("Tentar nova conexão após 10seg - 404")
            else:
                break
            print("loadusers")

        data = r.json()
        users = data['users']
        for each in users:
            base[each['pis']] = each
        if is_valid(dev, jcred, session) == False:
            print("Renovando sessão")
            session = loginCID(dev, jcred)
        else:
            print("Sessão OK")
    return(base)


def remove_user(dev, jcred, session, user):  # Verifica validade da Sessão
    tokenadd = ("https://"+jcred[dev]["ip"] +
                "/remove_users.fcgi?session=" + session)
    payload = {
        "users": [int(user)]
    }
    for attempt in range(10):
        try:
            r = requests.post(tokenadd, json=payload, verify=False, timeout=3)
        except:
            print("Impossível conectar, tentando novemente...")
            time.sleep(30)
        else:
            data = r.json()
            break
    if data == {}:
        print("Exclusão executada com sucesso!")
    else:
        print(data)


def insert_user(dev, jcred, session, user_json):  # Verifica validade da Sessão
    tokenadd = ("https://"+jcred[dev]["ip"] +
                "/add_users.fcgi?session=" + session)
    payload = user_json
    user_json = user_json['users'][0]
    for attempt in range(10):
        try:
            r = requests.post(tokenadd, json=payload, verify=False, timeout=3)
        except:
            print("Impossível conectar, tentando novemente...")
            time.sleep(30)
        else:
            data = r.json()
            break
    if data == {}:
        print("Usuário cadastrado com sucesso: " + str(user_json['pis']) + " " + str(
            user_json['registration']) + " " + user_json['name'])
    elif data['code'] == 400:
        print(data['error'] + " - " + user_json['name'])


def user_encode(user):
    templates = []
    for template in user['templates']:
        templates.append(template)

    usr_json = {
        'users': [{
            'pis': int(user['pis']),
            'name': str(user['name']),
            'registration': int(user['code']),
            'admin': bool(user['admin']),
            'bars': str(user['bars']),
            'code': int(user['code']),
            'rfid': int(user['rfid']),
            'templates': templates
        }]
    }
    return(usr_json)


def baixa_adf(dev, jcred, session):

    hoje = datetime.now()

    dia = hoje.day
    mes = hoje.month
    ano = hoje.year

    print('buscando od dados do dia: '+str(hoje))
    tokenadd = ("https://"+jcred[dev]["ip"] +
                "/get_afd.fcgi?session=" + session)

    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        'initial_date': {
            'day': dia,
            'month': mes,
            'year': ano
        }
    }

    try:
        r = requests.post(tokenadd, json=payload,  headers=headers, verify=False)
        if r.status_code == 200:
            try:

                data = r.text

            except ValueError as e:
                print("Erro ao fazer o parsing da resposta JSON:", e)
                data = None
        else:
            print("Erro na solicitação:", r.status_code)
            data = None

    except requests.exceptions.RequestException as e:
        print("Erro durante a solicitação:", e)
        data = None

    return data
