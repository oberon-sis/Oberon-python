# src/slack_service.py
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from src.log_evento import registrar_log_evento 
from utils.Database import Fazer_consulta_banco

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

slack_client = None
if SLACK_BOT_TOKEN:
    slack_client = WebClient(token=SLACK_BOT_TOKEN)
    print(" [SLACK SERVICE] Cliente Slack inicializado com sucesso.")
else:
    print(" [SLACK SERVICE] AVISO: Variável de ambiente SLACK_BOT_TOKEN não encontrada. O envio de alertas está desativado.")
# --------------------------------------

def procurar_informacoes_slack(idMaquina: int):
    """
    Recebe o idMaquina para identificação no banco de dados
    Retorna a o ID DO CANAL DO SLACK
    """
    IDENTIFICADOR = Fazer_consulta_banco({
        "query": """
                SELECT e.idEmpresa FROM Empresa AS e Join Maquina AS m on e.idEmpresa = m.fkEmpresa 
                WHERE m.idMaquina = %s;        
        """, 
        "params": (idMaquina, )
    })
    slackInfoRes = Fazer_consulta_banco({
        "query": """
                SELECT ID_CANAL_SLACK FROM vw_Dados_Slack WHERE IDENTIFICADOR_EMPRESA = %s;        
        """, 
        "params": (IDENTIFICADOR[0][0], )
    })

    return slackInfoRes[0][0]


LINK_PAINEL = "https://painel.monitoramento.com.br/ativos/"
LINK_HOME = "https://painel.monitoramento.com.br/ativos/"
def formatar_mensagem_alerta(idMaquina:int, alerta_descricao: dict, informacoes_maquina: dict,nomeMaquina:str,  informacoes_componentes:dict) -> list:
    """ 
    Array blocks para formatação
    """
    blocks_container = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": alerta_descricao["titulo"]
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": alerta_descricao["sub-titulo"]
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Contexto Técnico:*"
                },
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"* Nome/ID:*\n{nomeMaquina}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Sistema Operacional:*\n{informacoes_maquina["sistemaOperacional"]}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Modelo de Hardware:*\n{informacoes_maquina["modelo"]}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Endereço IP:*\n{informacoes_maquina["ip"]}"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "RESUMO DE RECURSOS"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*CPU (Processador):*\n{informacoes_componentes["CPU"]} núcleos"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Memória RAM:*\n{informacoes_componentes["RAM"]} GB"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*DISCO DURO:*\n{informacoes_componentes["DISCO"]} GB"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Acessar Paineis",
                        },
                        "style": "primary",
                        "url": f"{LINK_HOME}"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Ver Detalhes",
                        },
                        "style": "danger",
                        "url": f"{LINK_PAINEL}/{idMaquina}"
                    }
                ]
            }
        ]
    }
    
    return blocks_container["blocks"]


def enviar_notificacao_slack(ID_CNAAL_SLACK: str, alerta_descricao: dict, maquina_data:dict ):
    """ Envia notificação real para o Slack usando a chave 'blocks'. """
    
    if not slack_client:
        print("[SLACK] AVISO: O cliente Slack não está inicializado. Notificação ignorada.")
        return

    if not ID_CNAAL_SLACK:
        registrar_log_evento(f"ERRO SLACK: Tentativa de envio sem 'channel_id'. Alerta: {alerta_descricao["sub-titulo"]}...", False, None, 'ERRO SLACK')
        return

    blocks_payload = formatar_mensagem_alerta(
        maquina_data["idMaquina"], 
        alerta_descricao, 
        maquina_data["dados_sistema"],
        maquina_data["nomeMaquina"], 
        maquina_data["dados_hardware"]
        ) 
    
    text_fallback = alerta_descricao["sub-titulo"]

    try:
        response = slack_client.chat_postMessage(
            channel=ID_CNAAL_SLACK,
            text=text_fallback,        
            blocks=blocks_payload     
        )
        print(f"[SLACK] Notificação enviada com sucesso para o canal {ID_CNAAL_SLACK}.")
        
    except SlackApiError as e:
        error_msg = f"Falha ao enviar notificação Slack para o canal {ID_CNAAL_SLACK}: {e.response.get('error', str(e))}"
        print(f"[SLACK] ERRO: {error_msg}")
        registrar_log_evento(error_msg, True, None, 'ERRO SLACK')
    except Exception as e:
        error_msg = f"Erro inesperado ao enviar notificação Slack: {str(e)}"
        print(f"[SLACK] ERRO: {error_msg}")
        registrar_log_evento(error_msg, True, None, 'ERRO SLACK')