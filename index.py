import numpy as np
import pandas as pd
import csv
import re
from validate_docbr import CPF, CNPJ
from thefuzz import fuzz

cpfValid = CPF()
cnpjValid = CNPJ()

# função validação de string


def stateValid(stateValue):
    per = 70
    stateCorrectly = re.sub(r"[^A-Za-z0–9]", "", stateValue).upper()
    if (fuzz.ratio("MINAS GERAIS", stateCorrectly)) > per:
        newValue = 'MG'
    elif (fuzz.ratio("RIO DE JANEIRO", stateCorrectly)) > per:
        newValue = 'RJ'
    elif (fuzz.ratio("SÃO PAULO", stateCorrectly)) > per:
        newValue = 'SP'
    elif (fuzz.ratio("DISTRITO FEDERAL", stateCorrectly)) > per:
        newValue = 'DF'
    else:
        newValue = stateValue
    return newValue


# lendo arquivo origem
with open("./dados_cadastrais_fake.csv", encoding="utf8") as file:
    csvreader = csv.reader(file, delimiter=';')
    # pulando header
    next(csvreader)
    linhas = []
    linha = []
    for row in csvreader:

        # deixando somente números
        cpf = re.sub(r"[^0-9]", "", row[4])
        cnpj = re.sub(r"[^0-9]", "", row[5])

        linhas.append(row[0])  # nomes
        linhas.append(row[1])  # idade
        linhas.append(re.sub(r"[^A-Za-z0–9]", "", row[2]))  # cidade
        linhas.append(stateValid(row[3]))  # estado
        linhas.append(cpf)  # cpf
        linhas.append(cnpj)  # cnpj
        linhas.append(cpfValid.validate(cpf))  # cpfStatus
        linhas.append(cnpjValid.validate(cnpj))  # cnpjStatus

        linha.append(linhas)

        linhas = []

# lendo arquivo tratado e populando
with open('dados_cadastrais_tratados.csv', 'w', newline='', encoding='utf-8') as newcsv:
    writer = csv.writer(newcsv, delimiter=';')
    cabecalho = ['nomes', 'idade', 'cidade', 'estado',
                 'cpf', 'cnpj', 'cpfStatus', 'cnpjStatus']
    writer.writerow(cabecalho)
    for row in linha:
        writer.writerow(row)

cabecalho = ['nomes', 'idade', 'cidade', 'estado',
             'cpf', 'cnpj', 'cpfStatus', 'cnpjStatus']
df = pd.read_csv('./dados_cadastrais_tratados.csv', header=0, delimiter=';')

stateIndex = np.array([df['estado'].value_counts().values, ])

stateValues = df['estado'].value_counts().index

df1 = pd.DataFrame(df, columns=cabecalho)

df2 = pd.DataFrame(stateIndex, columns=stateValues)

# body do report
text = f'''
<html>
    <title>report</title>
    <!-- CSS only -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">
    <body>
        <h1><center>Report</center></h1>
        <h5>Métricas:</h5>
        <h6>Quantidade de Clientes: <span class="badge bg-secondary">''' + str(df['nomes'].count()) + '''</span></h6>
        <h6>Média de Idade dos Clientes: <span class="badge bg-secondary">''' + str(df['idade'].mean()) + '''</span></h6>
        <h6>Quantidade de Clientes por Estado: ''' + df2.to_html(classes='table table-striped text-center', justify='center') + '''</h6>
        <h6>Quantidade de Clientes CPF Válido: <span class="badge bg-secondary">''' + str(df[df['cpfStatus'] == True]['cpfStatus'].count()) + '''</span></h6>
        <h6>Quantidade de Clientes CPF Inválido: <span class="badge bg-secondary">''' + str(df[df['cpfStatus'] == False]['cpfStatus'].count()) + '''</span></h6>
        <h6>Quantidade de Clientes CNPJ Válido: <span class="badge bg-secondary">''' + str(df[df['cnpjStatus'] == True]['cnpjStatus'].count()) + '''</span></h6>
        <h6>Quantidade de Clientes CNPJ Inválido: <span class="badge bg-secondary">''' + str(df[df['cnpjStatus'] == False]['cnpjStatus'].count()) + '''</span></h6>
        <br><h5>dados_cadastrais_tratados.csv</h5>
        ''' + df1.to_html(classes='table table-striped text-center', justify='center') + '''
    </body>
</html>
'''
# salvando o report
file = open("report.html", "w")
file.write(text)
file.close()
