# utils/Database.py

from mysql.connector import connect, Error
from dotenv import load_dotenv
import os

load_dotenv()

def Fazer_consulta_banco(config):
    """
    Função de utilidade que centraliza a execução de consultas SQL.
    Lança RuntimeError em caso de falha no DB.

    Retorna:
    - Para SELECT: Lista de tuplas (resultado da consulta).
    - Para INSERT: O ID da linha inserida (cursor.lastrowid).
    - Para UPDATE/DELETE: O número de linhas afetadas (cursor.rowcount).
    """
    instrucaoSQL = config.get("query")
    valores = config.get("params", None)

    db_config = {
        'user': os.getenv("USER_DB"),
        'password': os.getenv("PASSWORD_DB"),
        'host': os.getenv("HOST_DB"),
        'database': os.getenv("DATABASE_DB")
    }

    try:
        conn = connect(**db_config)
        cursor = conn.cursor()

        if valores:
            cursor.execute(instrucaoSQL, valores if isinstance(valores, tuple) else (valores,))
        else:
            cursor.execute(instrucaoSQL)

        sql_tipo = instrucaoSQL.strip().lower()

        if sql_tipo.startswith("select"):
            resultado = cursor.fetchall()
            conn.close()
            return resultado
        else:
            conn.commit()
            
            if sql_tipo.startswith("insert"):
                id_inserido = cursor.lastrowid
                conn.close()
                return id_inserido
            else:
                linhas = cursor.rowcount
                conn.close()
                return linhas

    except Exception as e:
        error_message = f"Error to connect with MySQL - {e}"
        print(error_message)
        raise RuntimeError(error_message)