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


def procura_parametros(dados: dict):
    resultado = Fazer_consulta_banco({
        "query": """
            SELECT * FROM ViewParametrosMaquina WHERE idMaquina = %s;
        """,
        "params": (dados.get('idMaquina'),)
    })
    configuracoes = {}
    for idMaquinaComponente, tipo, unidade, limite,_, _,_,_ in resultado:
        if tipo not in configuracoes:
            configuracoes[tipo] = []
        configuracoes[tipo].append({
            'idMaquinaComponente': idMaquinaComponente,
            'unidade': unidade,
            'limite': limite
        })

    return configuracoes