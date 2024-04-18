# o código abaixo vai ser responsável pela extração de AFD.
# ele vai realizar a busca duas vezes entre um determinado tempo.
# vai comparar os dados e adicionar qualquer dado faltante.

# Importar funções control id
from controlidAPI import *

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
        hora = linha[18:22]
        pis = linha[23:34]

        valores = (registro,data,hora,pis)
        print('Valores: '+registro,data,hora,pis)

        lista_primeira_busca.append(valores)

# Agora partimos para a segunda busca

sleep(120)

lista_segunda_busca = [] # Declaramos a lista para comparar

# Executamos a função

texto = busca_dados_afd()

print('Iniciando tratativa de texto')
for linha in texto:
    if linha != '':
        registro = linha[0:10]
        data = linha[10:18]
        hora = linha[18:22]
        pis = linha[23:34]

        valores = (registro,data,hora,pis)

        lista_segunda_busca.append(valores)

# Agora, após obter as duas bibliotecas vamos comparar as chaves e adicionar as faltantes!

conjunto1 = set(lista_primeira_busca)
conjunto2 = set(lista_segunda_busca)

elementos_adicionais = list(conjunto2 - conjunto1)

print('Digitais não baixadas na primeira busca!')
print(elementos_adicionais)

for linha in elementos_adicionais:

    lista_primeira_busca.append(linha)

with open('saida.txt', 'a') as arquivo:
    for linha in lista_primeira_busca:
        arquivo.write(str(linha)+'\n')