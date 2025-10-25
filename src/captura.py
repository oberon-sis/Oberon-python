# src/captura.py

import psutil as p
from src.log_evento import registrar_log_evento

ACOES_METRICAS = {
    "cpu porcentagem": lambda: p.cpu_percent(),
    "ram porcentagem": lambda: p.virtual_memory().percent,
    "disco porcentagem": lambda: p.disk_usage('/').percent,
    "CPU_frequencia": lambda: round(p.cpu_freq().current / 1000, 1),
    "RAM_disponivel": lambda: round(p.virtual_memory().available / (1024 ** 3), 2),
    "DISK_disponivel": lambda: round(p.disk_usage('/').free / (1024 * 1024 * 1024), 2),
    "REDE_recebida": lambda: round(p.net_io_counters().bytes_recv / (1024 * 1024), 2),
    "REDE_enviada": lambda: round(p.net_io_counters().bytes_sent / (1024 * 1024), 2),
    "PROCESSOS_ativos": lambda: sum(1 for proc in p.process_iter(['status']) if proc.info['status'] == 'running'),
    "PROCESSOS_desativado": lambda: sum(1 for proc in p.process_iter(['status']) if proc.info['status'] != 'running'),
}

def capturar_dado_da_metrica(tipo_metrica: str, fkLogSistema: int) -> float | None:
    """ Captura o valor atual de uma métrica. """
    try:
        funcao = ACOES_METRICAS.get(tipo_metrica)
        if funcao:
            return float(funcao())
        return None
    
    except Exception as e:
        registrar_log_evento(f"⚠️ Erro ao coletar valor para {tipo_metrica}: {e}", True, fkLogSistema, 'ERRO COLETA')
        return None