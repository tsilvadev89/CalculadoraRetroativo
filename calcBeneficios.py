import pdfplumber
import pandas as pd
import re
from tkinter import Tk, filedialog, messagebox, simpledialog
from datetime import datetime

# Função para simular a inflação mensal (exemplo: 0,5% ao mês)
def calcular_correcao_monetaria(valor, competencia, taxa_mensal=0.005):
    hoje = datetime.today()
    competencia_data = datetime.strptime(competencia, "%m/%Y")
    meses = (hoje.year - competencia_data.year) * 12 + (hoje.month - competencia_data.month)
    correcao = valor * ((1 + taxa_mensal) ** meses)
    percentual = (correcao / valor - 1) * 100
    return round(correcao, 2), round(percentual, 2)

# Função para extrair texto do PDF
def extrair_dados_pdf(arquivo_pdf):
    with pdfplumber.open(arquivo_pdf) as pdf:
        texto = ""
        for pagina in pdf.pages:
            texto += pagina.extract_text() + "\n"
    return texto

# Função para organizar os dados em tabela
def organizar_dados_em_tabela(texto):
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
    tetos = [2112.00, 2826.65, 3751.05, 4664.68]
    aliquotas = [0, 0.075, 0.15, 0.225, 0.275]
    deducoes = [0, 158.40, 370.40, 651.73, 884.96]

    for i in range(len(tetos)):
        if remuneracao <= tetos[i]:
            return round(remuneracao * aliquotas[i] - deducoes[i], 2)
    
    return round(remuneracao * aliquotas[-1] - deducoes[-1], 2)

# Função principal para processar o PDF
def processar_pdf(arquivo_pdf, inicio, termino):
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
    tabela["Periculosidade Corrigida"] = tabela["Adicional Periculosidade"] - tabela["Diferença INSS"] - tabela["Diferença IRPF"]

    tabela["Valor Corrigido"], tabela["Percentual Correção"] = zip(*tabela.apply(
        lambda row: calcular_correcao_monetaria(row["Periculosidade Corrigida"], row["Competência"].strftime("%m/%Y")),
        axis=1
    ))

    tabela = tabela.sort_values(by="Competência")
    tabela["Competência"] = tabela["Competência"].dt.strftime("%m/%Y")

    return tabela

# Função para selecionar o arquivo
def selecionar_arquivo():
    Tk().withdraw()
    arquivo_pdf = filedialog.askopenfilename(
        title="Selecione o arquivo CNIS em PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    if arquivo_pdf:
        try:
            inicio = simpledialog.askstring("Período Retroativo", "Informe o início (mm/aaaa):")
            termino = simpledialog.askstring("Período Retroativo", "Informe o término (mm/aaaa):")
            
            if not inicio or not termino:
                messagebox.showwarning("Atenção", "Você deve informar o período retroativo!")
                return
            
            tabela_final = processar_pdf(arquivo_pdf, inicio, termino)
            caminho_saida = filedialog.asksaveasfilename(
                title="Salvar resultados como",
                defaultextension=".xlsx",
                filetypes=[("Arquivos Excel", "*.xlsx")]
            )
            if caminho_saida:
                with pd.ExcelWriter(caminho_saida, engine="openpyxl") as writer:
                    tabela_final.to_excel(writer, index=False, sheet_name="Cálculos")
                    # Adicionar tabelas de dedução como outra aba
                    deducoes = pd.DataFrame({
                        "Faixa": ["Até R$1.320", "R$1.320,01 a R$2.571,29", "R$2.571,30 a R$3.856,94", "Acima de R$7.507,49"],
                        "Alíquota": ["7,5%", "9%", "12%", "14%"]
                    })
                    deducoes.to_excel(writer, index=False, sheet_name="Deduções INSS e IRPF")
                
                messagebox.showinfo("Sucesso", "Os resultados foram salvos com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao processar o arquivo: {e}")
    else:
        messagebox.showwarning("Atenção", "Nenhum arquivo selecionado!")

if __name__ == "__main__":
    selecionar_arquivo()
