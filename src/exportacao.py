import csv
import os

def exportar_para_csv(dados: dict):
    nome_arquivo = f"coleta_maquina_{dados['idMaquina']}.csv"
    campos = [
        'idMaquina', 'hostname', 'macAddress', 
        'cpu porcentagem', 'ram porcentagem', 'disco duro porcentagem', 
        'horario'
    ]
    escrever_cabecalho = not os.path.exists(nome_arquivo)
    try:
        with open(nome_arquivo, 'a', newline='', encoding='utf-8') as arquivo_csv:
            writer = csv.DictWriter(arquivo_csv, fieldnames=campos, delimiter=';')
            if escrever_cabecalho:
                writer.writeheader() 
            writer.writerow(dados)
            print(f"  [CSV] Dados exportados com sucesso para {nome_arquivo}")
            
    except Exception as e:
        print(f"⚠️ Erro ao exportar dados para CSV: {e}")