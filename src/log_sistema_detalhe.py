# src/log_sistema_detalhe.py

from utils.Database import Fazer_consulta_banco
from src.log_evento import registrar_log_evento

def iniciar_sessao_log_sistema(fk_maquina: int) -> int:
    """ Insere em LogSistema e retorna o ID. """
    try:
        id_inserido = Fazer_consulta_banco({
            "query": "INSERT INTO LogSistema (fkMaquina, tipoAcesso) VALUES (%s, 'AgentePython');",
            "params": (fk_maquina,),
        })
        if id_inserido > 0:
            registrar_log_evento(f"[DB] Sessão de monitoramento (LogSistema) iniciada. ID: {id_inserido}", False)
        return id_inserido
    
    except RuntimeError as e:
        registrar_log_evento(f"ERRO CRÍTICO ao iniciar LogSistema: {str(e)}", False)
        return -1

def finalizar_sessao_log_sistema(id_log_sistema: int) -> bool:
    """ Atualiza o registro na tabela 'LogSistema' para marcar o horário de finalização. """
    
    try:
        linhas_afetadas = Fazer_consulta_banco({
            "query": "UPDATE LogSistema SET horarioFinal = NOW() WHERE idLogSistema = %s AND horarioFinal IS NULL", 
            "params": (id_log_sistema,),
        })

        if linhas_afetadas > 0:
            registrar_log_evento(f"[DB] Log de Sistema (Sessão) ID {id_log_sistema} finalizado.", False)
            return True
        return False

    except RuntimeError as e:
        registrar_log_evento(f"ERRO CRÍTICO ao finalizar LogSistema ID {id_log_sistema}: {str(e)}", False)
        return False

def inserir_detalhe_de_evento(fk_log_sistema: int, evento_captura: str, descricao: str) -> int:
    """ Insere um evento detalhado na tabela 'LogDetalheEvento'. """
    
    try:
        id_inserido = Fazer_consulta_banco({
            "query": "INSERT INTO LogDetalheEvento (fkLogSistema, eventoCaptura, descricao) VALUES (%s, %s, %s);",
            "params": (fk_log_sistema, evento_captura, descricao),
        })
        if id_inserido > 0:
            registrar_log_evento(f"[DB] Log Detalhe de Evento inserido (Evento: {evento_captura}). ID: {id_inserido}", False)
        return id_inserido

    except RuntimeError as e:
        registrar_log_evento(f"ERRO CRÍTICO ao inserir LogDetalheEvento: {str(e)}", False)
        return -1