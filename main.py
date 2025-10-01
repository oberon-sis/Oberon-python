import time
from utils.Database import Fazer_consulta_banco
from src.captura import capturar_dado
from src.maquina_config import procurar_mac_address, validar_dados_maquina, procura_parametros
from src.alertas import horario_atual, inserir_registro, processar_leitura_com_alerta
from src.exportacao import exportar_para_csv 
informacoes_maquina = {} 

logo = """
║════════════════════════════════════════════════════════════════════════════════════════╣
║     ███████     ███████████   ██████████  ███████████       ███████     ██████   █████ ║
║   ███▒▒▒▒▒███  ▒▒███▒▒▒▒▒███ ▒▒███▒▒▒▒▒█ ▒▒███▒▒▒▒▒███    ███▒▒▒▒▒███  ▒▒██████ ▒▒███  ║ 
║  ███     ▒▒███  ▒███    ▒███  ▒███  █ ▒   ▒███    ▒███   ███     ▒▒███  ▒███▒███ ▒███  ║
║ ▒███      ▒███  ▒██████████   ▒██████     ▒██████████   ▒███      ▒███  ▒███▒▒███▒███  ║
║ ▒███      ▒███  ▒███▒▒▒▒▒███  ▒███▒▒█     ▒███▒▒▒▒▒███  ▒███      ▒███  ▒███ ▒▒██████  ║
║ ▒▒███     ███   ▒███    ▒███  ▒███ ▒   █  ▒███    ▒███  ▒▒███     ███   ▒███  ▒▒█████  ║
║ ▒▒▒███████▒    ███████████   ██████████  █████   █████  ▒▒▒███████▒    █████  ▒▒█████  ║
║  ▒▒▒▒▒▒▒     ▒▒▒▒▒▒▒▒▒▒▒   ▒▒▒▒▒▒▒▒▒▒  ▒▒▒▒▒   ▒▒▒▒▒     ▒▒▒▒▒▒▒     ▒▒▒▒▒    ▒▒▒▒▒    ║  
║════════════════════════════════════════════════════════════════════════════════════════╣
║                      SISTEMA DE MONITORAMENTO DA UPFINITY                              ║
║════════════════════════════════════════════════════════════════════════════════════════╣
    Iniciando Monitoramento ....
╚════════════════════════════════════════════════════════════════════════════════════════╝
    """
menu_resumido = """
    """
saida = """
    ╔════════════════════════════════════════════════════╗
    ║             Encerrando a OBERON System             ║
    ║════════════════════════════════════════════════════╣
    ║  Sessão finalizada com sucesso.                    ║
    ║  Todos os serviços foram encerrados.               ║
    ║  Até a próxima utilização.                         ║
    ╚════════════════════════════════════════════════════╝
    """
continuar_loop = True
def formatar_palavra(palavra):
    print(f"""
    ╔════════════════════════════════════════════════════╗
    ║  {palavra}
    ╚════════════════════════════════════════════════════╝
    """)

def main():
    global informacoes_maquina
    global continuar_loop
    print(logo)
    while continuar_loop:
        try:
            iniciar_monitoramento()
        except KeyboardInterrupt:
            print("\n Monitoramento Interrompido! ")
            print(saida)
            break


    if informacoes_maquina and informacoes_maquina.get('idMaquina'):
        id_maquina = informacoes_maquina.get('idMaquina')
        Fazer_consulta_banco({
            "query": "UPDATE Maquina SET status = 'Inativo' WHERE idMaquina = %s",
            "params": (id_maquina,)
        })
        formatar_palavra(" Status Maquina atualizado para INATIVO")
        horario = horario_atual()
        Fazer_consulta_banco({
            "query": """
                         INSERT INTO Alerta (fkMaquina, descricao, nivel, horarioInicio)
                         VALUES (%s, %s, %s, %s)
                    """,
            "params": (id_maquina, 'Máquina está off-line', 'critico', horario)
        })
        formatar_palavra("Alerta Maquina off-line gerado")


def iniciar_monitoramento():
    global continuar_loop
    global informacoes_maquina
    
    mac_adrees = procurar_mac_address()
    
    informacoes_maquina_local = validar_dados_maquina(mac_adrees)

    if informacoes_maquina_local is None:
        return

    informacoes_maquina = informacoes_maquina_local

    informacao_parametros = procura_parametros(informacoes_maquina)


    if informacao_parametros is None or not informacao_parametros:
        print("Nenhum parâmetro de monitoramento configurado.")
        return

    id_maquina = informacoes_maquina.get('idMaquina')       

    Fazer_consulta_banco({
        "query": "UPDATE Maquina SET status = 'Ativo' WHERE idMaquina = %s",
        "params": (id_maquina,)
    })
    formatar_palavra(" Status Maquina atualizado para ATIVO ")

    verificar_alerta_Maquina = Fazer_consulta_banco({
        "query": """
            SELECT idAlerta 
            FROM Alerta
            WHERE fkMaquina = %s AND horarioFinal IS NULL
            ORDER BY horarioInicio DESC
            LIMIT 1
        """,
        "params": (id_maquina,)
    })

    if verificar_alerta_Maquina:
        horario = horario_atual()
        Fazer_consulta_banco({
            "query": "UPDATE Alerta SET horarioFinal = %s WHERE idAlerta = %s",
            "params": (horario, verificar_alerta_Maquina[0][0],)
        })
        formatar_palavra("Alerta de Maquina offline anterior FECHADO.")


    campos_obrigatorios_csv = ['cpu porcentagem', 'ram porcentagem', 'disco duro porcentagem']

    while True:

        print('╔═══════════════════════════════════════════════════════════════════════╗')
        
        horario_coleta = horario_atual()
        dados_capturados = {} 
        
        for tipo_componente in informacao_parametros.keys():
            valor_dado = capturar_dado(tipo_componente)
            if valor_dado is not None:
                dados_capturados[tipo_componente] = float(valor_dado)
        
        dados_csv = {
            'horario': horario_coleta,
            'idMaquina': informacoes_maquina_local.get('idMaquina'),
            'hostname': informacoes_maquina_local.get('hostname'),
            'macAddress': informacoes_maquina_local.get('macAddress')
        }
        
        for tipo_componente, lista_parametros in informacao_parametros.items():
            
            valor_dado = dados_capturados.get(tipo_componente)
            
            if valor_dado is None:
                continue 

            if tipo_componente == 'cpu porcentagem':
                dados_csv['cpu porcentagem'] = valor_dado
            elif tipo_componente == 'ram porcentagem':
                dados_csv['ram porcentagem'] = valor_dado
            elif tipo_componente == 'disco porcentagem':
                dados_csv['disco duro porcentagem'] = valor_dado
                
            
            for medida in lista_parametros:
                
                print(
                    f"\n   - Coleta: {tipo_componente} "
                    f"({medida['unidade']}) → Valor: {valor_dado:.2f} {medida['unidade']} "
                    f"→ Limite Configurado: {medida['limite']}"
                )

                inserir_registro(valor_dado, medida['idMaquinaComponente'])

                processar_leitura_com_alerta(
                    fkMaquinaComponente=int(medida['idMaquinaComponente']),
                    tipo=tipo_componente,
                    valor=float(valor_dado), 
                    limite=medida['limite']
                )
        
        if all(key in dados_csv for key in campos_obrigatorios_csv):
            exportar_para_csv(dados_csv) 
        else:
            formatar_palavra("⚠️ [CSV] Aviso: Nem todas as métricas necessárias para o CSV foram coletadas (CPU, RAM, DISK). Exportação ignorada neste ciclo.")
            
        print('\n╚═══════════════════════════════════════════════════════════════════════╝')

        time.sleep(10)


if __name__ == '__main__':
    main()