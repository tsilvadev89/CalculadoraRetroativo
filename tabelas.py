import pdfplumber
import pandas as pd
import requests

# Mapeamento dos meses abreviados para números
MESES_MAP = {
    'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
    'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
}

def baixar_pdf(url: str, caminho_arquivo: str) -> None:
    """Baixa o arquivo PDF da URL fornecida e salva no caminho especificado."""
    response = requests.get(url)
    with open(caminho_arquivo, 'wb') as f:
        f.write(response.content)
    print(f"PDF baixado para {caminho_arquivo}")


def extrair_dados_pdf(pdf_path: str) -> list:
    """Extrai os dados do PDF e retorna uma lista de dados formatados."""
    dados = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, pagina in enumerate(pdf.pages):
            print(f"Processando página {page_number + 1}")
            tabelas = pagina.extract_tables()
            for tabela in tabelas:
                if len(tabela) > 2:
                    anos = tabela[0][1:] 
                    for linha in tabela[1:]:
                        mes = linha[0].lower()
                        valores = linha[1:]
                        for ano, valor in zip(anos, valores):
                            if mes in MESES_MAP:
                                mes_ano = f"{MESES_MAP[mes]}/{ano}"
                                dados.append([mes_ano, valor])
    print(f"Dados extraídos de {len(dados)} entradas.")
    return dados


def criar_dataframe(dados: list) -> pd.DataFrame:
    """Cria um DataFrame com os dados extraídos e ordena pela data."""
    df = pd.DataFrame(dados, columns=['Data', 'Valor'])
    df['Data'] = pd.to_datetime(df['Data'], format='%m/%Y')
    df = df.sort_values(by='Data')
    return df


def exportar_para_excel(df: pd.DataFrame, nome_arquivo: str) -> None:
    """Exporta o DataFrame para um arquivo Excel."""
    df.to_excel(nome_arquivo, index=False)
    print(f"Tabela exportada para o arquivo Excel: {nome_arquivo}")


def main():
    # URL do PDF
    url = 'https://legacy.debit.com.br/tabelas/tabela-completa-pdf.php?indice=inpc'
    pdf_path = 'tabela_inpc.pdf'
    
    # Baixar o PDF
    baixar_pdf(url, pdf_path)
    
    # Extrair os dados do PDF
    dados = extrair_dados_pdf(pdf_path)
    
    # Criar o DataFrame
    df = criar_dataframe(dados)
    
    # Exportar para Excel
    excel_filename = 'tabela_inpc_ordenada.xlsx'
    exportar_para_excel(df, excel_filename)


if __name__ == "__main__":
    main()
