import telebot
import pdfplumber
import pandas as pd
import re
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

# Inicializa o bot do Telegram com o token
TOKEN = '7382518689:AAGlXEi9eQXSudulY9PjZPdeoe_6-TFCwQU'
bot = telebot.TeleBot(TOKEN)

# Mapeamento dos meses abreviados para números
MESES_MAP = {
    'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
    'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
}

# Dados INPC (Tupla fixa)
dados_inpc = (
    (1995, [1.44, 1.01, 1.62, 2.49, 2.10, 2.18, 2.46, 1.02, 1.17, 1.40, 1.51, 1.65]),
    (1996, [1.46, 0.71, 0.29, 0.93, 1.28, 1.33, 1.20, 0.50, 0.02, 0.38, 0.34, 0.33]),
    (1997, [0.81, 0.45, 0.68, 0.60, 0.11, 0.35, 0.18, -0.03, 0.10, 0.29, 0.15, 0.57]),
    (1998, [0.85, 0.54, 0.49, 0.45, 0.72, 0.15, -0.28, -0.49, -0.31, 0.11, -0.18, 0.42]),
    (1999, [0.65, 1.29, 1.28, 0.47, 0.05, 0.07, 0.74, 0.55, 0.39, 0.96, 0.94, 0.74]),
    (2000, [0.61, 0.05, 0.13, 0.09, -0.05, 0.30, 1.39, 1.21, 0.43, 0.16, 0.29, 0.55]),
    (2001, [0.77, 0.49, 0.48, 0.84, 0.57, 0.60, 1.11, 0.79, 0.44, 0.94, 1.29, 0.74]),
    (2002, [1.07, 0.31, 0.62, 0.68, 0.09, 0.61, 1.15, 0.86, 0.83, 1.57, 3.39, 2.70]),
    (2003, [2.47, 1.46, 1.37, 1.38, 0.99, -0.06, 0.04, 0.18, 0.82, 0.39, 0.37, 0.54]),
    (2004, [0.83, 0.39, 0.57, 0.41, 0.40, 0.50, 0.73, 0.50, 0.17, 0.17, 0.44, 0.86]),
    (2005, [0.57, 0.44, 0.73, 0.91, 0.70, -0.11, 0.03, 0.00, 0.15, 0.58, 0.54, 0.40]),
    (2006, [0.38, 0.23, 0.27, 0.12, 0.13, -0.07, 0.11, -0.02, 0.16, 0.43, 0.42, 0.62]),
    (2007, [0.49, 0.42, 0.44, 0.26, 0.26, 0.31, 0.32, 0.59, 0.25, 0.30, 0.43, 0.97]),
    (2008, [0.69, 0.48, 0.51, 0.64, 0.96, 0.91, 0.58, 0.21, 0.15, 0.50, 0.38, 0.29]),
    (2009, [0.64, 0.31, 0.20, 0.55, 0.60, 0.42, 0.23, 0.08, 0.16, 0.24, 0.37, 0.24]),
    (2010, [0.88, 0.70, 0.71, 0.73, 0.43, -0.11, -0.07, -0.07, 0.54, 0.92, 1.03, 0.60]),
    (2011, [0.94, 0.54, 0.66, 0.72, 0.57, 0.22, 0.00, 0.42, 0.45, 0.32, 0.57, 0.51]),
    (2012, [0.51, 0.39, 0.18, 0.64, 0.55, 0.26, 0.43, 0.45, 0.63, 0.71, 0.54, 0.74]),
    (2013, [0.92, 0.52, 0.60, 0.59, 0.35, 0.28, -0.13, 0.16, 0.27, 0.61, 0.54, 0.72]),
    (2014, [0.63, 0.64, 0.82, 0.78, 0.60, 0.26, 0.13, 0.18, 0.49, 0.38, 0.53, 0.62]),
    (2015, [1.48, 1.16, 1.51, 0.71, 0.99, 0.77, 0.58, 0.25, 0.51, 0.77, 1.11, 0.90]),
    (2016, [1.51, 0.95, 0.44, 0.64, 0.98, 0.47, 0.64, 0.31, 0.08, 0.17, 0.07, 0.14]),
    (2017, [0.42, 0.24, 0.32, 0.08, 0.36, -0.30, 0.17, -0.03, -0.02, 0.37, 0.18, 0.26]),
    (2018, [0.23, 0.18, 0.07, 0.21, 0.43, 1.43, 0.25, 0.00, 0.30, 0.40, -0.25, 0.14]),
    (2019, [0.36, 0.54, 0.77, 0.60, 0.15, 0.01, 0.10, 0.12, -0.05, 0.04, 0.54, 1.22]),
    (2020, [0.19, 0.17, 0.18, -0.23, -0.25, 0.30, 0.44, 0.36, 0.87, 0.89, 0.95, 1.46]),
    (2021, [0.27, 0.82, 0.86, 0.38, 0.96, 0.60, 1.02, 0.88, 1.20, 1.16, 0.84, 0.73]),
    (2022, [0.67, 1.00, 1.71, 1.04, 0.45, 0.62, -0.60, -0.31, -0.32, 0.47, 0.38, 0.69]),
    (2023, [0.46, 0.77, 0.64, 0.53, 0.36, -0.10, -0.09, 0.20, 0.11, 0.12, 0.10, 0.55]),
    (2024, [0.57, 0.81, 0.19, 0.37, 0.46, 0.25, 0.26, -0.14, 0.48, 0.61, 0.33, 0.48])
)


# Função para calcular a correção monetária com base no INPC
def calcular_correcao_monetaria(valor, competencia):
    """Calcula a correção monetária com base no INPC da competência."""
    # Extrair o ano e mês da competência
    ano, mes = competencia.split('/')
    ano = int(ano)
    mes = int(mes) - 1  # Ajustar para 0-index (0 = jan, 1 = fev, ...)
    
    # Encontrar o valor do INPC para o ano e mês
    inpc = None
    for ano_inpc, inpcs in dados_inpc:
        if ano_inpc == ano:
            inpc = inpcs[mes]
            break
    
    if inpc is None:
        raise ValueError(f"Não foi encontrado INPC para o ano {ano} e mês {mes + 1}")

    # Calcular o valor corrigido
    correcao = valor * (1 + inpc / 100)
    percentual = inpc  # Percentual de correção
    return round(correcao, 2), round(percentual, 2)

# Função para extrair texto do PDF
def extrair_dados_pdf(arquivo_pdf):
    """Extrai texto de um arquivo PDF."""
    with pdfplumber.open(arquivo_pdf) as pdf:
        texto = ""
        for pagina in pdf.pages:
            texto += pagina.extract_text() + "\n"
    return texto

# Função para organizar os dados em tabela
def organizar_dados_em_tabela(texto):
    """Transforma o texto extraído em um DataFrame organizado."""
    linhas = texto.split("\n")
    dados = []
    for linha in linhas:
        match = re.findall(r"(\d{2}/\d{4})\s+([\d,.]+)", linha)
        if match:
            for competencia, remuneracao in match:
                remuneracao = float(remuneracao.replace('.', '').replace(',', '.'))
                dados.append([competencia, remuneracao])
    return pd.DataFrame(dados, columns=["Competência", "Remuneração"])

# Funções para calcular impostos
def calcular_inss(remuneracao):
    """Calcula o desconto do INSS com base na remuneração."""
    tetos = [1320.00, 2571.29, 3856.94, 7507.49]
    aliquotas = [0.075, 0.09, 0.12, 0.14]
    faixas = [0] + tetos
    inss = 0

    for i in range(1, len(faixas)):
        if remuneracao > faixas[i-1]:
            base = min(remuneracao, faixas[i]) - faixas[i-1]
            desconto = base * aliquotas[i-1]
            inss += desconto
    return round(inss, 2)

def calcular_irpf(remuneracao):
    """Calcula o desconto do IRPF com base na remuneração."""
    tetos = [2112.00, 2826.65, 3751.05, 4664.68]
    aliquotas = [0, 0.075, 0.15, 0.225, 0.275]
    deducoes = [0, 158.40, 370.40, 651.73, 884.96]

    for i in range(len(tetos)):
        if remuneracao <= tetos[i]:
            return round(remuneracao * aliquotas[i] - deducoes[i], 2)
    
    return round(remuneracao * aliquotas[-1] - deducoes[-1], 2)

# Função principal para processar o PDF
def processar_pdf(arquivo_pdf, inicio, termino):
    """Processa o arquivo PDF e calcula os benefícios retroativos."""
    texto_pdf = extrair_dados_pdf(arquivo_pdf)
    tabela = organizar_dados_em_tabela(texto_pdf)

    tabela = tabela.groupby("Competência", as_index=False)["Remuneração"].sum()
    tabela["Competência"] = pd.to_datetime(tabela["Competência"], format="%m/%Y")
    
    periodo_inicio = pd.to_datetime(inicio, format="%m/%Y")
    periodo_termino = pd.to_datetime(termino, format="%m/%Y")
    tabela = tabela[(tabela["Competência"] >= periodo_inicio) & (tabela["Competência"] <= periodo_termino)]

    tabela["INSS"] = tabela["Remuneração"].apply(calcular_inss)
    tabela["IRPF"] = tabela["Remuneração"].apply(calcular_irpf)
    tabela["Adicional Periculosidade"] = tabela["Remuneração"] * 0.30
    tabela["Salário Reajustado"] = tabela["Remuneração"] + tabela["Adicional Periculosidade"]
    tabela["INSS Reajustado"] = tabela["Salário Reajustado"].apply(calcular_inss)
    tabela["IRPF Reajustado"] = tabela["Salário Reajustado"].apply(calcular_irpf)
    tabela["Diferença INSS"] = tabela["INSS Reajustado"] - tabela["INSS"]
    tabela["Diferença IRPF"] = tabela["IRPF Reajustado"] - tabela["IRPF"]
    
    tabela["Periculosidade Corrigida"] = (
        tabela["Adicional Periculosidade"] - tabela["Diferença INSS"] - tabela["Diferença IRPF"]
    )

    tabela["Valor Corrigido"], tabela["Percentual Correção"] = zip(*tabela.apply(
        lambda row: calcular_correcao_monetaria(
            row["Periculosidade Corrigida"],
            row["Competência"].strftime("%m/%Y")),
        axis=1
    ))

    tabela = tabela.sort_values(by="Competência")
    tabela["Competência"] = tabela["Competência"].dt.strftime("%m/%Y")

    return tabela

# Função para iniciar o bot
@bot.message_handler(commands=['start'])
def handle_start(message):
    """Envia uma mensagem de boas-vindas e instrui o usuário a enviar o PDF do CNIS."""
    bot.reply_to(message, "Olá! Envie seu arquivo CNIS em PDF para processarmos os cálculos.")

# Função para receber o arquivo do CNIS e pedir as datas
@bot.message_handler(content_types=['document'])
def handle_docs_photo(message):
    """Recebe o PDF do CNIS enviado pelo usuário e realiza os cálculos."""
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    arquivo_pdf = f"./{message.document.file_name}"

    with open(arquivo_pdf, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Solicitar ao usuário o período retroativo
    bot.send_message(message.chat.id, "Informe o início do período retroativo (mm/aaaa):")
    bot.register_next_step_handler(message, processar_periodo_inicio, arquivo_pdf)

def processar_periodo_inicio(message, arquivo_pdf):
    """Processa o início do período retroativo."""
    inicio = message.text
    bot.send_message(message.chat.id, "Agora, informe o término do período retroativo (mm/aaaa):")
    bot.register_next_step_handler(message, processar_periodo_termino, arquivo_pdf, inicio)

def processar_periodo_termino(message, arquivo_pdf, inicio):
    """Processa o término do período retroativo e executa o cálculo.""" 
    termino = message.text
    try:
        tabela_final = processar_pdf(arquivo_pdf, inicio, termino)
        
        # Salvar o resultado em Excel
        excel_filename = 'resultados_calculo.xlsx'
        tabela_final.to_excel(excel_filename, index=False)

        with open(excel_filename, 'rb') as arquivo:
            bot.send_document(message.chat.id, arquivo)
        
        bot.send_message(message.chat.id, "Cálculos realizados com sucesso e arquivo exportado!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ocorreu um erro: {e}")

# Iniciar o bot
if __name__ == "__main__":
    bot.polling()
