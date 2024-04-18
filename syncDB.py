import os
import pathlib
import csv
import time

def sisfin_ler():
    whereiam=pathlib.Path().resolve() #resolve o caminho atual
    cmd="powershell.exe "+ str(whereiam) + "\Cmd\sisfin_export.ps1"
    os.system(cmd)
    db_sisfin_demitidos=dict()
    time.sleep(10)
    retorno=1
    try:
        csv_file=open('funcionario.csv','r')
    except:
        print("Falha ao abrir arquivo")
    else:
        line_count = 0
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            db_sisfin_demitidos[row['PIS']]={
                'MATRICULA':row['CDMATRFUNCIONARIO'],
                'NOME':row['NMFUNCIONARIO'],
                'SITUACAO': row['SITAFA']}
            line_count += 1
        retorno=db_sisfin_demitidos
        csv_file.close()
        print(retorno)
    return(retorno)