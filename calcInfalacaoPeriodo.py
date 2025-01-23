import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL do site com a tabela
url = 'https://legacy.debit.com.br/tabelas/tabela-completa-pdf.php?indice=inpc'

# Obter o conteúdo da página
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Encontrar todas as tabelas
tabelas = soup.find_all('table')

# Selecionar a segunda tabela
table = tabelas[1]  # Índice 1 para a segunda tabela

# Converter a tabela HTML para um DataFrame
df = pd.read_html(str(table))[0]

# Exibir a tabela
print(df)

# Função para calcular inflação acumulada
def calcular_inflacao_acumulada(mes_inicio, ano_inicio, mes_fim, ano_fim, df):
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Localizar os índices das linhas
    inicio = df[(df['Ano'] == ano_inicio) & (df[mes_inicio] != '-')].iloc[0]
    fim = df[(df['Ano'] == ano_fim) & (df[mes_fim] != '-')].iloc[0]
    
    # Extrair os valores de inflação para o cálculo
    if not inicio.empty and not fim.empty:
        inflacao_inicio = float(inicio[mes_inicio].replace(',', '.'))  # Convertendo para float
        inflacao_fim = float(fim[mes_fim].replace(',', '.'))  # Convertendo para float
        inflacao_acumulada = (inflacao_fim - inflacao_inicio)
        return inflacao_acumulada
    else:
        return "Dados não encontrados."

# Solicitar ao usuário o período
mes_inicio = input("Digite o mês inicial (exemplo: Jan): ")
ano_inicio = int(input("Digite o ano inicial: "))
mes_fim = input("Digite o mês final (exemplo: Dez): ")
ano_fim = int(input("Digite o ano final: "))

# Calcular e exibir a inflação acumulada
inflacao = calcular_inflacao_acumulada(mes_inicio, ano_inicio, mes_fim, ano_fim, df)
print(f"A inflação acumulada de {mes_inicio}/{ano_inicio} até {mes_fim}/{ano_fim} é: {inflacao:.2f}")
