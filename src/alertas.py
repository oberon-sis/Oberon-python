# src/alertas.py

from utils.Database import Fazer_consulta_banco
from src.log_evento import registrar_log_evento
from src.slack_service import enviar_notificacao_slack

def inserir_registro_de_metrica(valor: float, fkComponente: int) -> int:
    """ Insere o Registro e retorna o ID. """
    try:
        id_registro = Fazer_consulta_banco({
            "query": "INSERT INTO Registro (valor, fkComponente) VALUES (%s, %s);",
            "params": (valor, fkComponente),
        })
        if id_registro > 0:
            print(f"   [DB] Registro de métrica inserido com sucesso para componente {fkComponente}. ID: {id_registro}")
        return id_registro
    except RuntimeError as e:
        registrar_log_evento(f"ERRO BD CRÍTICO: Falha ao inserir Registro: {str(e)}", False)
        return -1

def processar_alerta_leitura(idRegistro: int, idParametro: int, tipo: str, valor: float, limite: float, nivel: str, fkLogSistema: int, slackInfo: dict):
    """ Processa o limite e insere o Alerta no DB. """
    
    alerta_ativo = valor >= limite
    
    if alerta_ativo:
        descricao = f"{tipo} atingiu o limite de {nivel} ({limite:.2f}%). Valor atual: {valor:.2f}%."
        
        try:
            id_alerta = Fazer_consulta_banco({
                "query": "INSERT INTO Alerta (fkRegistro, fkParametro, descricao, nivel) VALUES (%s, %s, %s, %s);",
                "params": (idRegistro, idParametro, descricao, nivel),
            })
            mandar_notificao_slack(slackInfo["ID_CANAL_SLACK"], tipo, nivel, valor, limite, descricao)
            
            if id_alerta > 0:
                print(f"   Alerta ABERTO para {tipo} (nível: {nivel}). ID Alerta: {id_alerta}")
                registrar_log_evento(f"Alerta ABERTO ({nivel}) para {tipo}. ID={id_alerta}", True, fkLogSistema, 'LOG ALERTA')
            else:
                registrar_log_evento(f"ERRO: Falha ao inserir Alerta para {tipo} no DB.", True, fkLogSistema, 'ERRO ALERTA')
        except RuntimeError as e:
            registrar_log_evento(f"ERRO BD CRÍTICO ao gerar alerta para {tipo}: {str(e)}", True, fkLogSistema, 'ERRO ALERTA')
def mandar_notificao_slack(channel_id: str, tipo: str, nivel: str, valor: float, limite: float, descricao: str):

    """ Simulação de envio de notificação (para implementação futura). """
    enviar_notificacao_slack(channel_id, tipo, nivel, valor, limite, descricao)