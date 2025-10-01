from utils.Database import Fazer_consulta_banco
from datetime import datetime, timedelta

def horario_atual():
    agora = datetime.now()
    return agora.strftime("%Y-%m-%d %H:%M:%S")

def inserir_registro(valor: float, fk_parametro: int):
    valor = float(valor)

    resultado = Fazer_consulta_banco({
        "query": "INSERT INTO Registro (valor, horario, fkMaquinaComponente) VALUES (%s, NOW(), %s);",
        "params": (valor, fk_parametro)
    })
    if resultado >= 0:
        print(resultado, "registro inserido")

def processar_leitura_com_alerta(fkMaquinaComponente: int, tipo: str, valor: float, limite: float):
    horario = horario_atual()
    valor = float(valor)

    nivel = None
    if valor >= limite * 1.2:
        nivel = "Critico"
    elif valor >= limite:
        nivel = "Alerta"
    elif valor >= limite * 0.9:
        nivel = "Atenção"
    
    alerta_aberto = Fazer_consulta_banco({
        "query": """
            SELECT idAlerta, nivel, horarioInicio
            FROM Alerta
            WHERE fkMaquinaComponente = %s AND descricao = %s AND horarioFinal IS NULL
            ORDER BY horarioInicio DESC
            LIMIT 1
        """,
        "params": (fkMaquinaComponente, tipo)
    })

    alerta_aberto = alerta_aberto[0] if alerta_aberto else None

    def alerta_expirado(data_hora_inicio):
        if isinstance(data_hora_inicio, datetime):
            return datetime.now() - data_hora_inicio > timedelta(minutes=5)
        return False

    if nivel: 
        if not alerta_aberto:
            Fazer_consulta_banco({
                "query": """
                    INSERT INTO Alerta (fkMaquinaComponente, descricao, nivel, valorInicial, horarioInicio)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                "params": (fkMaquinaComponente, tipo, nivel, valor, horario)
            })
            print(f"  Alerta ABERTO para {tipo} (nível: {nivel})")
        else:
            data_hora_inicio = alerta_aberto[2]
            if alerta_aberto[1] != nivel or alerta_expirado(data_hora_inicio):
                
                Fazer_consulta_banco({
                    "query": "UPDATE Alerta SET horarioFinal = %s, valorFinal = %s WHERE idAlerta = %s",
                    "params": (horario, valor, alerta_aberto[0])
                })
                
                Fazer_consulta_banco({
                    "query": """
                        INSERT INTO Alerta (fkMaquinaComponente, descricao, nivel, valorInicial, horarioInicio)
                        VALUES (%s, %s, %s, %s, %s)
                    """,
                    "params": (fkMaquinaComponente, tipo, nivel, valor, horario)
                })
                print(f"  Alerta atualizado: NOVO registro para {tipo} (nível: {nivel})")

    else: 
        if alerta_aberto:
            Fazer_consulta_banco({
                "query": "UPDATE Alerta SET horarioFinal = %s, valorFinal = %s WHERE idAlerta = %s",
                "params": (horario, valor, alerta_aberto[0])
            })
            print(f"  Alerta FECHADO para {tipo}")