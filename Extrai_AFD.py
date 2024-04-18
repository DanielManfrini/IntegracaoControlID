# o código abaixo vai ser responsável pela extração de AFD.
# ele vai realizar a busca duas vezes entre um determinado tempo.
# vai comparar os dados e adicionar qualquer dado faltante.

# Importar funções control id
from controlidAPI import *
from datetime import datetime

hoje = datetime.today()
dia = hoje.date()

hoje = dia.strftime('%d/%m/%Y')

def busca_dados_afd(): # Declaramos a função para não reescrever.

    texto = [] # declaramos uma lista vazia, pois vamos preencher para retornar.

    # pegar as credenciais
    credenciais = credLoad()

    for dispositivo in credenciais:

        print('Logando no dispositivo: '+dispositivo)

        sessao = loginCID(dispositivo,credenciais)

        print('login iniciado: '+sessao)

        adf = baixa_adf(dispositivo,credenciais,sessao)

        print('Extraido arquivo!')

        logoffCID

        # após extrair os dados vamos tratar um a um.

        linhas_adf = adf.splitlines()

        for linha in linhas_adf:

            if linha.count('AFD') > 0:# se a linha conter ADF é o fim do arquivo então vamos pular

                pass

            elif len(linha) < 0: # aqui verifica se alinha está vazia e pula ela

                pass

            else: # Se não a gente junta.

                texto.append(linha)

    return texto

#Iniciamos a execução do código.

lista_primeira_busca = [] # Declaramos a lista para comparar

# Executamos a função

texto = busca_dados_afd()

print('Iniciando tratativa de texto')
for linha in texto:
    if linha != '':
    
        registro = linha[0:10]

        data = linha[10:18]
        dia = data[0:2]
        mes = data[2:4]
        ano = data[4:8]
        data = dia+'/'+mes+'/'+ano

        tempo = linha[18:22]
        hora = tempo[0:2]
        minuto = tempo[2:4]
        tempo_total = hora+':'+minuto

        pis = linha[23:34]

        valores = (registro,data,tempo_total,pis)

        lista_primeira_busca.append(valores)

# Agora partimos para a segunda busca

#sleep(120)

lista_segunda_busca = [] # Declaramos a lista para comparar

# Executamos a função

texto = busca_dados_afd()

print('Iniciando tratativa de texto')
for linha in texto:
    if linha != '':

        registro = linha[0:10]

        data = linha[10:18]
        dia = data[0:2]
        mes = data[2:4]
        ano = data[4:8]
        data = dia+'/'+mes+'/'+ano

        tempo = linha[18:22]
        hora = tempo[0:2]
        minuto = tempo[2:4]
        tempo_total = hora+':'+minuto

        pis = linha[23:34]

        valores = (registro,data,tempo_total,pis)

        lista_segunda_busca.append(valores)

# Agora, após obter as duas bibliotecas vamos comparar as chaves e adicionar as faltantes!

conjunto1 = set(lista_primeira_busca)
conjunto2 = set(lista_segunda_busca)

elementos_adicionais = list(conjunto2 - conjunto1)

for linha in elementos_adicionais:

    lista_primeira_busca.append(linha)


# Agora vamos buscar  e separar os pontos por digitais.
# Vamos criar uma lista nova, e abrir várias tuplas em cada laço
# o objetivo é que em cada linha do primeiro laço iniciamos um alço novo para buscar
# o pis correspondente e adicionar os horários na tupla.
# Assim criamos uma lista com o pis, o dia e as batidas de cada funcionário.
lista_final = []

for linha_inicial in lista_primeira_busca: # Laço para verificar cada linha.

    pis_inicial = linha_inicial[3]
    data_inicial = linha_inicial[1]

    tupla_laco = (pis_inicial,data_inicial,)

    for linha_laco in lista_primeira_busca: # Laço para buscar o pis correspondente na lista.

        pis_laco = linha_laco[3]
        data_laco = linha_laco[1]

        if pis_laco == pis_inicial and data_inicial == data_laco: # se o pis e a data forem iguais vai adicionar o horário a tupla.

            novo_horario = linha_laco[2]
            tupla_laco = tupla_laco + (novo_horario,)

    lista_final.append(tupla_laco) # no fim de cada laço vai adicionar a tupla na lista nova.

# Agora vamos escrever os dados para debug.
with open('saida.txt', 'a') as arquivo:
    for linha in lista_final:
        arquivo.write(str(linha)+'\n')