# src/maquina_config.py

import uuid
import psutil as p
import platform
import socket
import subprocess
import os
from utils.Database import Fazer_consulta_banco
from src.log_evento import registrar_log_evento

ID_USUARIO_SISTEMA = 1 

def _obter_mac_address() -> str:
    """ Calcula o MAC Address. """
    mac_int = uuid.getnode()
    return ':'.join(("%012X" % mac_int)[i:i+2] for i in range(0, 12, 2))



ID_USUARIO_SISTEMA = 1 

# Função auxiliar para rodar comandos PowerShell
def _rodar_powershell(comando: str) -> str:
    """ Roda um comando no PowerShell e retorna a saída limpa. """
    try:
        modelo_raw_bytes = subprocess.check_output(
            ['powershell', '-Command', comando],
            shell=True,
            stderr=subprocess.DEVNULL
        )
        # Decodifica e limpa a saída
        return modelo_raw_bytes.decode('utf-8', errors='ignore').strip()
    except Exception:
        return ""


def _obter_dados_atuais_do_sistema() -> dict:
    """ Coleta dados dinâmicos do SO (Host, IP, SO, Modelo e Fabricante). """
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    sistema_operacional = platform.system()
    
    # NOVAS VARIÁVEIS PARA OBTENÇÃO DETALHADA
    fabricante = ""
    modelo_base = "Modelo N/A"
    
    try:
        if sistema_operacional == "Windows":
            # 1. Obter FABRICANTE
            comando_fabricante = "Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object -ExpandProperty Manufacturer"
            fabricante = _rodar_powershell(comando_fabricante)
            
            # 2. Obter MODELO
            comando_modelo = "Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object -ExpandProperty Model"
            modelo_base = _rodar_powershell(comando_modelo)
            
        elif sistema_operacional == "Linux":
            # No Linux, o 'product_name' é geralmente a melhor combinação Fabricante + Modelo
            try:
                with open('/sys/class/dmi/id/product_name', 'r') as f:
                    modelo_base = f.read().strip()
                # Tenta obter o fabricante separadamente (opcional)
                with open('/sys/class/dmi/id/sys_vendor', 'r') as f:
                    fabricante = f.read().strip()
            except FileNotFoundError:
                # Fallback para dmidecode
                modelo_raw = subprocess.check_output(
                    ['dmidecode', '-s', 'system-product-name'], 
                    universal_newlines=True, 
                    stderr=subprocess.DEVNULL
                )
                modelo_base = modelo_raw.strip()

        elif sistema_operacional == "Darwin":
            modelo_base = subprocess.check_output(['sysctl', '-n', 'hw.model'], universal_newlines=True, stderr=subprocess.DEVNULL)
            modelo_base = modelo_base.strip()
            fabricante = "Apple"

    except Exception as e:
         registrar_log_evento(
             f"Falha ao obter modelo/fabricante: {e}", 
             registrar_bd=False
         )
         
    # Formata o modelo para ser amigável (Ex: Samsung 550XDA)
    if modelo_base and modelo_base != "Modelo N/A" and modelo_base != fabricante:
        modelo_final = f"{fabricante.strip()} {modelo_base.strip()}"
    else:
        modelo_final = modelo_base
         
    return {
        'hostname': hostname,
        'ip': ip,
        'modelo': modelo_final[:100] if modelo_final else "Modelo Desconhecido", 
        'sistemaOperacional': sistema_operacional,
    }
def _obter_dados_atuais_de_hardware() -> dict:
    """ Coleta dados de hardware estáticos (capacidade) usando psutil. """
    return {
        'CPU': p.cpu_count(logical=False), 
        'RAM': round(p.virtual_memory().total / (1024 ** 3), 2), 
        'DISCO': round(p.disk_usage('/').total / (1024 ** 3), 2)
    }

# --- FUNÇÃO DE UPDATE DE COMPONENTES ---

def _atualizar_capacidades_componentes(id_maquina, dados_hardware):
    """
    Executa a lógica de atualização da tabela Componente usando os IDs da view.
    """
    COMPONENTES_MAP = {'CPU': 'nucleosThreads', 'RAM': 'capacidadeGb', 'DISCO': 'capacidadeGb'}

    # 1. Obter IDs dos componentes usando a view (vw_ComponentesParaAtualizar)
    try:
        componentes_db = Fazer_consulta_banco({
            "query": "SELECT idComponente, tipoComponente FROM vw_ComponentesParaAtualizar WHERE fkMaquina = %s",
            "params": (id_maquina,)
        })
    except RuntimeError as e:
        registrar_log_evento(f"[DB] ERRO ao consultar componentes para atualização: {e}", False)
        return

    # 2. Iterar e atualizar
    for id_componente, tipo_comp in componentes_db:
        campo_bd = COMPONENTES_MAP.get(tipo_comp)
        valor = dados_hardware.get(tipo_comp)

        if campo_bd and valor is not None and valor > 0:
            try:
                Fazer_consulta_banco({
                    "query": f"UPDATE Componente SET {campo_bd} = %s, fkEditadoPor = 1 WHERE idComponente = %s",
                    "params": (valor, id_componente)
                })
                registrar_log_evento(f"[DB] Componente {tipo_comp} (ID:{id_componente}) atualizado com {campo_bd} = {valor}", False)
            except RuntimeError as e:
                registrar_log_evento(f"[DB] ERRO CRÍTICO ao atualizar Componente {tipo_comp}: {e}", False)


# --- FUNÇÃO PRINCIPAL DE VALIDAÇÃO ---

def buscar_e_validar_maquina():
    """ Localiza, valida e atualiza os dados da máquina no DB. """
    mac_adress = _obter_mac_address()
    registrar_log_evento(f"O MAC ADRESS É: {mac_adress}", False)
    
    # 1. Validação
    try:
        resultado = Fazer_consulta_banco({"query": "SELECT idMaquina FROM vw_DadosMaquina WHERE macAddress = %s", "params": (mac_adress,)})
    except RuntimeError as e:
        registrar_log_evento(f"ERRO BD CRÍTICO ao buscar máquina: {str(e)}", False)
        return None

    if not resultado:
        registrar_log_evento("Falha crítica: Máquina não encontrada no sistema.", False)
        return None

    id_maquina = resultado[0][0]
    dados_sistema = _obter_dados_atuais_do_sistema()
    
    # 2. Atualiza a tabela Maquina
    try:
        Fazer_consulta_banco({
            "query": "UPDATE Maquina SET hostname = %s, modelo = %s, ip = %s, sistemaOperacional = %s, fkEditadoPor = 1 WHERE idMaquina = %s",
            "params": (dados_sistema['hostname'], dados_sistema['modelo'], dados_sistema['ip'], dados_sistema['sistemaOperacional'], id_maquina)
        })
        registrar_log_evento(f"[DB] Dados da Máquina atualizados (ID: {id_maquina})", False)
    except RuntimeError as e:
        registrar_log_evento(f"[DB] ERRO ao atualizar Maquina: {str(e)}", False)
        
    # 3. Atualiza Componentes (Lógica completa)
    try:
        dados_hardware = _obter_dados_atuais_de_hardware()
        _atualizar_capacidades_componentes(id_maquina, dados_hardware) # <--- Chama a atualização real
        registrar_log_evento(f"[DB] Componentes de Hardware coletados/atualizados.", False)
    except Exception as e:
        registrar_log_evento(f"[DB] ERRO ao coletar/atualizar hardware: {e}", False)
        
    return {'idMaquina': id_maquina, 'macAddress': mac_adress}

def obter_parametros_monitoramento(id_maquina):
    """ Consulta a view vw_ParametrosComponente para obter todos os limites. """
    try:
        resultado = Fazer_consulta_banco({
            "query": """
                     SELECT idComponente, funcaoMonitorar, unidadeMedida, identificador, limite
                     FROM vw_ParametrosComponente
                     WHERE idMaquina = %s;
            """,
            "params": (id_maquina,)
        })
        
        configuracoes = {}
        if resultado:
            for fkComponente, tipo, unidade, nivel, limite in resultado:
                if tipo not in configuracoes:
                    configuracoes[tipo] = []
                configuracoes[tipo].append({
                    'idParametro': fkComponente, # Usamos fkComponente como ID do Parâmetro da View
                    'fkComponente': fkComponente, # Usamos fkComponente como ID do Componente
                    'limite': float(limite),
                    'nivel': nivel,
                    'unidade': unidade
                })
        return configuracoes
    except RuntimeError as e:
        registrar_log_evento(f"ERRO CRÍTICO ao obter parâmetros do DB: {str(e)}", False)
        return None