import datetime
import os
def createlog(arquivo):
        logfile=open(arquivo,'w')
        hoje=datetime.date.today()
        logfile.writelines('Inicializando Aplicacao em ' + str(hoje)+'\n')
        logfile.close
        
def lognow(arquivo, info):
    if(os.path.isfile(arquivo)):
        agora = datetime.datetime.now() 
        logfile=open(arquivo,'a+',-1, "utf-8")
        logfile.writelines((str(agora)+": "+str(info))+'\n')
        logfile.close()
        return(0)
    else:
        return("Arquivo não encontrado")

