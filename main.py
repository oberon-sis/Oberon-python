# main.py
import time
from utils.display_utils import formatar_palavra
from src.log_evento import registrar_log_evento
from src.log_sistema_detalhe import iniciar_sessao_log_sistema, finalizar_sessao_log_sistema, inserir_detalhe_de_evento
from src.maquina_config import buscar_e_validar_maquina, obter_parametros_monitoramento
from src.alertas import inserir_registro_de_metrica, processar_alerta_leitura
from src.captura import capturar_dado_da_metrica
from src.incidente import registrar_incidente


# Constantes de Configuração
INTERVALO_DE_COLETA_SEGUNDOS = 10 

# Variáveis de estado global (simples)
maquina_data = None
fkLogSistema = None

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
def main():
    """ Ponto de entrada principal com tratamento de interrupção. """
    global fkLogSistema
    global logo
    pausa_necessaria = False 
    try:
        print(logo)
        orquestrar_coleta()
        
    except KeyboardInterrupt:
        pausa_necessaria = True
        formatar_palavra("\nMonitoramento Interrompido pelo Usuário.")
    else: 
        if maquina_data is None:
             pausa_necessaria = True
    finally:
        # Lógica de encerramento
        if fkLogSistema is not None and fkLogSistema != -1:
            registrar_log_evento("Agente encerrado. Finalizando sessão LogSistema.", False, None, 'LOG FIM')
            
            # 1. Insere LogDetalheEvento para o desligamento
            id_log_detalhe = inserir_detalhe_de_evento(
                fkLogSistema, 'Desligamento', 'Agente encerrado por KeyboardInterrupt.'
            )
            
            # 2. Registra Incidente
            if id_log_detalhe != -1:
                 registrar_incidente(
                    id_log_detalhe, 'Máquina Desligou/Agente Encerrado', 'Encerramento inesperado.', 'Software', 'Critica', fkLogSistema
                )
            
            finalizar_sessao_log_sistema(fkLogSistema)
        if pausa_necessaria and fkLogSistema is None:
            print("\n ATENÇÃO: O AGENTE ENCERROU INESPERADAMENTE. VERIFIQUE OS LOGS ACIMA.")
            input("Pressione Enter para sair...")

def orquestrar_coleta():
    """ Orquestrador principal funcional. """
    global maquina_data
    global fkLogSistema
    
    # 1. VALIDAÇÃO E INÍCIO DE SESSÃO
    maquina_data = buscar_e_validar_maquina()
    
    if maquina_data is None:
        return

    fkLogSistema = iniciar_sessao_log_sistema(maquina_data['idMaquina'])
    if fkLogSistema == -1:
        registrar_log_evento("Falha crítica: Não foi possível iniciar a sessão LogSistema.", False, None, 'ERRO INICIAL')
        return

    registrar_log_evento(f"Monitoramento iniciado. Sessão: {fkLogSistema}", True, fkLogSistema, 'LOG INICIO')

    # 2. CARREGAR PARÂMETROS
    parametros = obter_parametros_monitoramento(maquina_data['idMaquina'])
    
    if not parametros:
        registrar_log_evento("Nenhum parâmetro configurado. Encerrando.", True, fkLogSistema, 'LOG GERAL')
        return

    # 3. LOOP DE COLETA
    while True:
        registrar_log_evento("Iniciando novo ciclo de coleta...", True, fkLogSistema, 'LOG COLETA')
        print('╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗')
        
        for tipo, lista_parametros in parametros.items():
            
            # Coleta o valor
            valor_dado = capturar_dado_da_metrica(tipo, fkLogSistema)

            if valor_dado is None:
                 continue
            
            fkComponente = lista_parametros[0]['fkComponente']

            # Insere Registro ÚNICO
            idRegistro = inserir_registro_de_metrica(valor_dado, fkComponente)
            
            if idRegistro != -1:
                # Processa os 3 níveis (ATENCAO, ALERTA, CRITICO)
                for medida in lista_parametros:
                    
                    print(f"   - Coleta: {tipo} ({medida['unidade']}) → Valor: {valor_dado:.2f} {medida['unidade']} → Limite Configurado ({medida['nivel']}): {medida['limite']}")
                    
                    processar_alerta_leitura(
                        idRegistro, medida['idParametro'], tipo, valor_dado, 
                        medida['limite'], medida['nivel'], fkLogSistema
                    )
        
        print('\n╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════╝')
        time.sleep(INTERVALO_DE_COLETA_SEGUNDOS)





if __name__ == '__main__':
    main()