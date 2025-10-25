# src/incidente.py

from utils.Database import Fazer_consulta_banco
from src.log_evento import registrar_log_evento
import secrets
import string

ID_FUNCIONARIO_PADRAO = 1 

def _gerar_chave_jira(tipo: str) -> str:
    """ Gera uma chave simulada para o JIRA com ATÉ 20 caracteres. """
    TIPO_PREFIXO = tipo.upper()[:8] 
    caracteres = string.ascii_uppercase + string.digits
    token_unico = ''.join(secrets.choice(caracteres) for _ in range(10))
    return f"{TIPO_PREFIXO}-{token_unico}"
    
def registrar_incidente(
    fk_log_detalhe_evento: int,
    titulo: str, 
    descricao: str, 
    categoria: str, 
    severidade: str,
    fkLogSistema: int
) -> int:
    """ Insere um registro na tabela 'Incidente'. """
    
    chave_jira = _gerar_chave_jira("INCIDENTE")
    status_padrao = 'Aberto'

    try:
        id_inserido = Fazer_consulta_banco({
            "query": """
                INSERT INTO Incidente (chaveJira, titulo, descricao, categoria, status, severidade, 
                fkLogDetalheEvento) VALUES (%s, %s, %s, %s, %s, %s, %s);
            """,
            "params": (chave_jira, titulo, descricao, categoria, status_padrao, severidade, fk_log_detalhe_evento),
        })

        if id_inserido > 0:
            registrar_log_evento(f"[DB] Incidente registrado. ID: {id_inserido}, Chave Jira: {chave_jira}", True, fkLogSistema, 'LOG INCIDENTE')
        return id_inserido
        
    except RuntimeError as e:
        registrar_log_evento(f"ERRO CRÍTICO ao registrar Incidente: {str(e)}", True, fkLogSistema, 'ERRO INCIDENTE')
        return -1