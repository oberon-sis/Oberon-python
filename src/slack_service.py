# src/slack_service.py
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from src.log_evento import registrar_log_evento 

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

slack_client = None
if SLACK_BOT_TOKEN:
    slack_client = WebClient(token=SLACK_BOT_TOKEN)
    print(" [SLACK SERVICE] Cliente Slack inicializado com sucesso.")
else:
    print(" [SLACK SERVICE] AVISO: Variável de ambiente SLACK_BOT_TOKEN não encontrada. O envio de alertas está desativado.")
# --------------------------------------


def formatar_mensagem_alerta(tipo: str, nivel: str, valor: float, limite: float, descricao: str) -> list:
    """ 
    Array blocks para formatação
    """
    
    emoji_map = {'CRITICO': '🚨', 'AVISO': '⚠️', 'INFO': '⚠️'}
    emoji = emoji_map.get(nivel.upper(), '⚠️')
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} ALERTA DE MONITORAMENTO ({nivel.upper()}) {emoji}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{descricao}*"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                { "type": "mrkdwn", "text": f"*Nível de Alerta:*\n{nivel.upper()}" },
                { "type": "mrkdwn", "text": f"*Limite Estabelecido:*\n{limite:.2f}%" },
                { "type": "mrkdwn", "text": f"*Tipo Monitorado:*\n{tipo}" },
                { "type": "mrkdwn", "text": f"*Valor Atual:*\n{valor:.2f}%" }
            ]
        }
    ]
    
    footer_text = f"Monitore o status do sistema para o cliente."
    if nivel.upper() == 'CRITICO':
        footer_text = "🚨 AÇÃO IMEDIATA NECESSÁRIA! 🚨 " + footer_text
        
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "plain_text",
                "text": footer_text
            }
        ]
    })
    
    return blocks


def enviar_notificacao_slack(channel_id: str, tipo: str, nivel: str, valor: float, limite: float, descricao: str):
    """ Envia notificação real para o Slack usando a chave 'blocks'. """
    
    if not slack_client:
        print("[SLACK] AVISO: O cliente Slack não está inicializado. Notificação ignorada.")
        return

    if not channel_id:
        registrar_log_evento(f"ERRO SLACK: Tentativa de envio sem 'channel_id'. Alerta: {descricao[:50]}...", False, None, 'ERRO SLACK')
        return

    blocks_payload = formatar_mensagem_alerta(tipo, nivel, valor, limite, descricao)
    
    text_fallback = f"ALERTA {nivel.upper()} para {tipo}: {descricao} (Valor: {valor:.2f}%)"

    try:
        response = slack_client.chat_postMessage(
            channel=channel_id,
            text=text_fallback,        
            blocks=blocks_payload     
        )
        print(f"[SLACK] Notificação enviada com sucesso para o canal {channel_id}.")
        
    except SlackApiError as e:
        error_msg = f"Falha ao enviar notificação Slack para o canal {channel_id}: {e.response.get('error', str(e))}"
        print(f"[SLACK] ERRO: {error_msg}")
        registrar_log_evento(error_msg, True, None, 'ERRO SLACK')
    except Exception as e:
        error_msg = f"Erro inesperado ao enviar notificação Slack: {str(e)}"
        print(f"[SLACK] ERRO: {error_msg}")
        registrar_log_evento(error_msg, True, None, 'ERRO SLACK')