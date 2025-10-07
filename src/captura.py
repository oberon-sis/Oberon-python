import psutil as p
import time

ACOES_METRICAS = {
    "cpu porcentagem": lambda: p.cpu_percent(),
    "ram porcentagem": lambda: p.virtual_memory().percent,
    "disco porcentagem": lambda: p.disk_usage('/').percent,


    "CPU_frequencia": lambda: round(p.cpu_freq().current / 1000, 1),
    "RAM_disponivel": lambda: round(p.virtual_memory().available / (1024 ** 3), 2),
    "DISK_disponivel": lambda: round(p.disk_usage('/').free / (1024 ** 3), 2),

    
    "REDE_recebida": lambda: round(p.net_io_counters().packets_recv / (1024 * 1024), 2),
    "REDE_enviada": lambda: round(p.net_io_counters().packets_sent / (1024 * 1024), 2),
    "PROCESSOS_ativos": lambda: sum(1 for proc in p.process_iter(['status']) if proc.info['status'] == 'running'),
    "PROCESSOS_desativado": lambda: sum(1 for proc in p.process_iter(['status']) if proc.info['status'] != 'running'),
}

def capturar_dado(tipo: str):
    try:
        funcao = ACOES_METRICAS.get(tipo)
        return funcao() if funcao else None
    
    except Exception as e:
        print(f"⚠️ Erro ao coletar valor para {tipo}: {e}")
        return None