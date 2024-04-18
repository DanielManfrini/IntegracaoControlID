#Tipo: Python3
#Realiza o sincronismo dos REPs
#Criado em 03/09/2022
#Criado por Mauricio Ferrari
#Revisão para operar no xaxim por: Daniel Lopes Manfrini.
#Dependências: controlidAPI.py (manipuladores da API dos REPs)

import asyncio
import datetime
import pathlib
from queue import PriorityQueue
import controlidAPI
import time
import urllib3
from controlidAPI import user_encode
import logger
#import syncDB


#urllib3.disable_warnings()
# Resolve o caminho atual
whereiam=pathlib.Path().resolve()

# Cria caminho de log
wherelog=str(whereiam)+'\log_'+ str(datetime.datetime.now().strftime("%d%m%Y_%H%M")) +'.txt'
print(wherelog)

# Chama a função para caregar as credenciais
cred=controlidAPI.credLoad()

# Inicailiza log
logger.createlog(wherelog) 
logger.lognow(wherelog, 'Inicializando Sincronismo de usuários')
logger.lognow(wherelog, 'Verificando REP Mestre')

# Lista para armazenar os relógios SLAVE.
slave=[]

# Contadores para os relógios MASTER.
cnt_master_xaxim=0
cnt_master_capao=0

# Vamos ler os objetos dentro da biblioteca json
for each in cred:
    tipo=cred[each]['mestre']

    # Se o tipo for 2 é o rep do capão do qual pegamos oa dados dos novos funcionários.
    if tipo == 2:
        mestre_capao=str(each)
        logger.lognow(wherelog, 'REP Capão: ' + mestre_capao)
        cnt_master_capao+=1

    # Se o tipo for 1 é o MASTER localizado no xaxim que realizará o append dos dados.
    elif tipo == 1:
        mestre_xaxim=str(each)
        logger.lognow(wherelog, 'REP Xaxim: ' + mestre_xaxim)
        cnt_master_xaxim+=1

    # Se o tipo for 0 é apenas slave.
    elif tipo == 0:
        slave.append(each)

# Vamos verificar os mestres.
if cnt_master_capao != 1 or cnt_master_xaxim != 1: 
    logger.lognow(wherelog, 'ERRO! Quantidade de REPs Mestre diferente de 1')
    exit()

# Partimos para a coleta dos dados do equipamento mestre localizado no capão raso
logger.lognow(wherelog, 'Iniciando coleta de usuários do REP Mestre Capão: '+ str(mestre_capao))

# Chamando a função de login.
session_capao=controlidAPI.loginCID(mestre_capao,cred)
if session_capao == 1:
    logger.lognow(wherelog, 'Falha ao conectar em ' + mestre_capao + '. Não é possível prosseguir! Encerrando')
    quit()
logger.lognow(wherelog, 'Iniciado sessão '+ session_capao + ' em ' + mestre_capao)
logger.lognow(wherelog, 'Sessão ativa:  ' + str(controlidAPI.is_valid(mestre_capao,cred,session_capao)))

# Chamando a função de contagem de usuarios.
qnt_mestre_capao=controlidAPI.counter(mestre_capao,cred,session_capao)
logger.lognow(wherelog, 'Contagem de usuários no REP Mestre Capão: ' + str(qnt_mestre_capao) )

# Chamando a função de carregar usuários.
usr_mestre_capao=controlidAPI.load_users(mestre_capao,cred,session_capao)

# Chamando função de logoff.
controlidAPI.logoffCID(mestre_capao,cred,session_capao)
logger.lognow(wherelog, 'Encerrando sessão '+ session_capao + ' em ' + mestre_capao)
logger.lognow(wherelog, 'Leitura de usuários do REP Mestre concluída!')
logger.lognow(wherelog, 'Iniciando sincronismo com REP Xaxim')

# Partimos agora para coletar os dados do MASTER do xaxim, e realizar um append nos dados.
logger.lognow(wherelog, 'Iniciando coleta de usuários do REP Mestre Xaxim: '+ str(mestre_xaxim))

# Chamando a função de login.
session_xaxim=controlidAPI.loginCID(mestre_xaxim,cred)
if session_xaxim == 1:
    logger.lognow(wherelog, 'Falha ao conectar em ' + mestre_xaxim + '. Não é possível prosseguir! Encerrando')
    quit()
logger.lognow(wherelog, 'Iniciado sessão '+ session_xaxim + ' em ' + mestre_xaxim)
logger.lognow(wherelog, 'Sessão ativa:  ' + str(controlidAPI.is_valid(mestre_xaxim,cred,session_xaxim)))

# Chamando a função de contagem de usuarios.
qnt_mestre_xaxim=controlidAPI.counter(mestre_xaxim,cred,session_xaxim)
logger.lognow(wherelog, 'Contagem de usuários no REP Mestre Xaxim: ' + str(qnt_mestre_xaxim) )

# Chamando a função de carregar usuários.
usr_mestre_xaxim=controlidAPI.load_users(mestre_xaxim,cred,session_xaxim)

# Verificaremos chave por chave se elas existem, se não irá criar o usuário. (Admissões)
for any in usr_mestre_capao.keys():
    try:
        usr_mestre_xaxim[int(any)]
    except KeyError:
        controlidAPI.insert_user(mestre_xaxim,cred,session_xaxim,controlidAPI.user_encode(usr_mestre_capao[int(any)]))

# Após sincronizar vamos carregar novamente os dados.
usr_mestre_xaxim=controlidAPI.load_users(mestre_xaxim,cred,session_xaxim)

logger.lognow(wherelog, 'Finalizado o sincronismo do '+ mestre_xaxim + ' com ' + mestre_capao)

# Chamando função de logoff.
controlidAPI.logoffCID(mestre_xaxim,cred,session_xaxim)
logger.lognow(wherelog, 'Encerrando sessão '+ session_xaxim + ' em ' + mestre_xaxim)
logger.lognow(wherelog, 'Leitura de usuários do REP Mestre concluída!')
logger.lognow(wherelog, 'Iniciando sincronismo com REPs Slave')

# Agora vamos finalmente sincronizar com os slaves
# Loop para em ambos os relágios.
for each in slave:
    logger.lognow(wherelog, 'Iniciando coleta de usuários do REP Slave: '+ str(each))

    # Chamados a função de login.
    session=controlidAPI.loginCID(each,cred)
    if session == 1:
        logger.lognow(wherelog, 'Falha ao conectar em ' + each + '. Ignorando REP.')
        continue
    logger.lognow(wherelog, 'Iniciado sessão '+ session + ' em ' + each)
    logger.lognow(wherelog, 'Sessão ativa:  ' + str(controlidAPI.is_valid(each,cred,session)))

    # Chamamos a função de contagem de usuários.
    qnt_slave=controlidAPI.counter(each,cred,session)
    logger.lognow(wherelog, 'Contagem de usuários no REP Slave: ' + str(qnt_slave) )

    # Chamamos a função para carregar os usuários.
    uslave=controlidAPI.load_users(each,cred,session)
    logger.lognow(wherelog, 'Leitura de usuários do REP Slave concluída!')

    # Agora vamos sincronizar com os dados já sincronizados do relógio MASTER xaxim.
    # Verificaremos chave por chave se elas existem, se não irá criar o usuário.
    for any in usr_mestre_xaxim.keys():
        if usr_mestre_xaxim[any]['templates_count'] == 0:
            pass
        else:
            try:
                uslave[int(any)]
            except KeyError:
                controlidAPI.insert_user(each,cred,session,controlidAPI.user_encode(usr_mestre_xaxim[int(any)]))
            else:
                # Verificaremos alteração de chave, se houver, será excluido e criado um novo cadastro com os dados atuais.
                if (uslave[any]['templates']==usr_mestre_xaxim[any]['templates']) and (uslave[any]['rfid']==usr_mestre_xaxim[any]['rfid']) and (uslave[any]['admin']==usr_mestre_xaxim[any]['admin']):
                    print("OK")
                else:
                    logger.lognow(wherelog, 'Atualizar ' + str(any) + 'em ' + str(each))
                    controlidAPI.remove_user(each,cred,session,any)
                    controlidAPI.insert_user(each,cred,session,controlidAPI.user_encode(usr_mestre_xaxim[int(any)]))

    # Verificaremos se há usuários que não estão localizados no MASTER xaxim, se sim irá excluir!              
    for one in uslave.keys():
        try:
            usr_mestre_xaxim[int(one)]
        except KeyError:
            logger.lognow(wherelog, str(one) + ":Não encontrado em master. De: " +  each + ". REMOVENDO!")
            controlidAPI.remove_user(each,cred,session,one)
    logger.lognow(wherelog, 'Finalizado o sincronismo com '+ each)
    controlidAPI.logoffCID(each,cred,session)
    logger.lognow(wherelog, 'Encerrando sessão '+ session + ' em ' + each) 
                





