from bcb import sgs
from datetime import datetime

def obter_inflacao_acumulada(mes_inicio, ano_inicio, mes_fim, ano_fim):
    # Formatar as datas para o formato AAAA-MM
    data_inicio = f"{ano_inicio}-{mes_inicio:02d}-01"
    data_fim = f"{ano_fim}-{mes_fim:02d}-01"

    # Obter o índice do IPCA (código 433) para o período desejado
    ipca = sgs.get(('IPCA', 433), start_date=data_inicio, end_date=data_fim)

    if not ipca.empty:
        # Calcular a inflação acumulada usando o valor do IPCA no início e no fim do período
        ipca_inicio = ipca.iloc[0]['IPCA']
        ipca_fim = ipca.iloc[-1]['IPCA']
        inflacao_acumulada = (ipca_fim / ipca_inicio - 1) * 100
        return inflacao_acumulada
    else:
        return None

def main():
    # Solicitar as entradas do usuário
    mes_inicio = int(input("Digite o mês inicial (1-12): "))
    ano_inicio = int(input("Digite o ano inicial: "))
    mes_fim = int(input("Digite o mês final (1-12): "))
    ano_fim = int(input("Digite o ano final: "))

    # Validar as datas
    try:
        # Verificar se a data fornecida é válida
        datetime(ano_inicio, mes_inicio, 1)
        datetime(ano_fim, mes_fim, 1)
    except ValueError:
        print("Data inválida!")
        return

    # Calcular a inflação acumulada
    inflacao = obter_inflacao_acumulada(mes_inicio, ano_inicio, mes_fim, ano_fim)

    if inflacao is not None:
        print(f"A inflação acumulada de {mes_inicio}/{ano_inicio} a {mes_fim}/{ano_fim} foi de {inflacao:.2f}%")
    else:
        print("Não foi possível calcular a inflação acumulada. Verifique se as datas são válidas.")

if __name__ == "__main__":
    main()
