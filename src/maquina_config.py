from utils.Database import Fazer_consulta_banco
import uuid



def procurar_mac_address():
    mac_int = uuid.getnode()
    mac_hex = ':'.join(("%012X" % mac_int)[i:i+2] for i in range(0, 12, 2))
    print("╔════════════════════════════════════════════════════╗")
    print(f"       O SEU MAC ADRESS É: {mac_hex}")
    print("╚════════════════════════════════════════════════════╝")

    return mac_hex

def validar_dados_maquina(mac_adress):
    resultado = Fazer_consulta_banco({
        "query": "select * from viewDadosMaquina WHERE macAddress = %s",
        "params": (mac_adress)
    })

    if resultado:

        informacoes_maquina = {
            'idMaquina': resultado[0][0],
            'nome': resultado[0][1],
            'hostname': resultado[0][2],
            'modelo': resultado[0][3],
            'macAddress': mac_adress,
            'ip': resultado[0][4],
            'sitemaOperacional': resultado[0][5],
            'razaoSocial': resultado[0][6],
        }
        print('╔════════════════════════════════════════════════════╗')
        print(f"   🔹 Monitoramento iniciado com sucesso! 🔹\n"
            f" 💻   NOME DA EMPRESA: {informacoes_maquina['razaoSocial']}\n"
            f" 🏷️   NOME DA MÁQUINA: {informacoes_maquina['nome']}\n"
            f" 🔗   HOSTNAME: {informacoes_maquina['hostname']}\n"
            f" ⚙️   MODELO: {informacoes_maquina['modelo']}\n"
            f" 🐧   SISTEMA OPERACIONAL: {informacoes_maquina['sitemaOperacional']}\n"
            f" 🆔   MAC ADRESS : {informacoes_maquina['macAddress']}\n"
            f" 🌍   IP ADRESS: {informacoes_maquina['ip']}\n"
            f" 🚀   Seja bem-vindo(a)! ao sistema de monitoramento da OBERON ✨\n")
        print('╚════════════════════════════════════════════════════╝')

        return informacoes_maquina
    else:
        print(f"\n❌ Este Maquina {mac_adress} não foi encontrado no sistema. ❌\n")
        return None


LIMITES_OBERON = {
    'cpu porcentagem': 90.0,   
    'ram porcentagem': 95.0,   
    'disco porcentagem': 85.0, 
    'rede taxa': 50.0,   
}

def procura_parametros(dados: dict):
    global LIMITES_OBERON
    resultado = Fazer_consulta_banco({
        "query": """
            SELECT idMaquinaComponente, tipo, unidade, origemParametro, limite_base_db
            FROM ViewParametrosMaquina 
            WHERE idMaquina = %s;
        """,
        "params": (dados.get('idMaquina'),)
    })
    
    configuracoes = {}
    
    for idMaquinaComponente, tipo, unidade, origemParametro, limite_base_db in resultado:
        
        limite_final = None
        
        if limite_base_db is not None:
            limite_final = float(limite_base_db)
            print(f"  Limite encontrado no DB ({origemParametro}): {limite_final} para {tipo}")
            
        elif origemParametro.upper() == 'OBERON' or limite_base_db is None:
            limite_oberon = LIMITES_OBERON.get(tipo)
            if limite_oberon is not None:
                limite_final = limite_oberon
                print(f"  Usando limite OBERON ({origemParametro}): {limite_final} para {tipo}")
            else:
                print(f"  Erro: Limite OBERON não definido para o tipo {tipo}. Componente ignorado.")
        
        if limite_final is not None:
            if tipo not in configuracoes:
                configuracoes[tipo] = []
                
            configuracoes[tipo].append({
                'idMaquinaComponente': idMaquinaComponente,
                'unidade': unidade,
                'limite': limite_final 
            })

    return configuracoes