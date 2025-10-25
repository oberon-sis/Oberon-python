# src/log_evento.py

import os
from utils.display_utils import obter_horario_atual, formatar_palavra
from utils.Database import Fazer_consulta_banco 

LOG_FILE_PATH = "log_eventos_do_sistema.txt"

def _imprimir_e_salvar_txt(log_texto: str):
    """ Imprime no terminal e salva no arquivo TXT. """
    formatar_palavra(f"REGISTRO DE EVENTO GERAL: {log_texto}")
    try:
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(log_texto + "\n")
    except Exception as e:
        print(f"⚠️ Erro ao escrever no arquivo de log TXT: {e}") 

def registrar_log_evento(mensagem: str, registrar_bd: bool = False, fkLogSistema: int = None, eventoCaptura: str = 'LOG GERAL'):
    """
    Orquestra o log (terminal/TXT) e o registro no LogDetalheEvento (DB).
    """
    horario = obter_horario_atual()
    log_texto_completo = f"[{horario}] {mensagem}"
    
    _imprimir_e_salvar_txt(log_texto_completo)
    
    if registrar_bd:
        if fkLogSistema is None:
            _imprimir_e_salvar_txt("ERRO: Tentativa de registrar no BD falhou. fkLogSistema não fornecido.")
            return
            
        try:
            Fazer_consulta_banco({
                "query": "INSERT INTO LogDetalheEvento (fkLogSistema, eventoCaptura, descricao) VALUES (%s, %s, %s);",
                "params": (fkLogSistema, eventoCaptura, mensagem) 
            })
            _imprimir_e_salvar_txt(f"[DB] Log Detalhe Evento ({eventoCaptura}) inserido.")
        except RuntimeError as e:
            _imprimir_e_salvar_txt(f"ERRO BD: Falha ao inserir Log Detalhe Evento ({eventoCaptura}). Detalhes: {str(e)}")