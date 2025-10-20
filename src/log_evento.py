# src/log_evento.py

import os
from utils.display_utils import obter_horario_atual, formatar_palavra
from utils.Database import Fazer_consulta_banco 

class GerenciadorDeLogGeral:
    """
    Gerencia o registro de logs de auditoria no terminal, em arquivo TXT e 
    no banco de dados (tabela LogDetalheEvento).
    """

    def __init__(self, db_connector):
        self.consultar_banco = db_connector

    def _imprimir_e_salvar_txt(self, log_texto: str) -> bool:
        """ Imprime no terminal (formatado) e salva no arquivo TXT. """
        mensagem_terminal = f"REGISTRO DE EVENTO GERAL: {log_texto}"
        formatar_palavra(mensagem_terminal)

        try:
            nome_arquivo = "log_eventos_do_sistema.txt"
            with open(nome_arquivo, 'a', encoding='utf-8') as f:
                f.write(log_texto + "\n")
            return True
        except Exception as e:
            print(f"⚠️ Erro ao escrever no arquivo de log TXT: {e}") 
            return False

    def _registrar_no_banco(self, mensagem: str, fkLogSistema: int, eventoCaptura: str) -> int:
        """ 
        Insere o registro na tabela 'LogDetalheEvento'.
        """
        id_inserido = -1
        
        try:
            id_inserido = self.consultar_banco({
                "query": """
                    INSERT INTO LogDetalheEvento (fkLogSistema, eventoCaptura, descricao) 
                    VALUES (%s, %s, %s);
                """,
                "params": (fkLogSistema, eventoCaptura, mensagem) 
            })
            
        except RuntimeError as e:
            self._imprimir_e_salvar_txt(f"ERRO BD: Falha ao inserir Log Detalhe Evento ({eventoCaptura}). Detalhes: {str(e)}")
            
        return id_inserido
    
    def registrar_log_evento(self, mensagem: str, registrar_bd: bool = False, fkLogSistema: int = None, eventoCaptura: str = 'LOG GERAL'):
        """
        Função principal que orquestra o registro de logs (Terminal/TXT obrigatório).
        Se registrar_bd for True, insere no banco, REQUERINDO o fkLogSistema.
        """
        horario = obter_horario_atual()
        log_texto_completo = f"[{horario}] {mensagem}"
        
        self._imprimir_e_salvar_txt(log_texto_completo)
        
        if registrar_bd:
            if fkLogSistema is None:
                self._imprimir_e_salvar_txt("ERRO: Tentativa de registrar no BD falhou. fkLogSistema não fornecido.")
                return
                
            id_bd = self._registrar_no_banco(mensagem, fkLogSistema, eventoCaptura)
            if id_bd is not None and id_bd != -1:
                self._imprimir_e_salvar_txt(f"[DB] Log Detalhe Evento ({eventoCaptura}) inserido com ID: {id_bd}")