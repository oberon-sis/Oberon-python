import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

CANAL_MOCK_MAP = {
    "santander-alertas": "C09R5ASRL6P",  
}


if not SLACK_BOT_TOKEN:
    print("Verificar .env")
    client = None
else:
    client = WebClient(token=SLACK_BOT_TOKEN)
    print(" Cliente Slack WebClient inicializado.")



def buscar_id_canal_mock(nome_canal):
    nome_canal_limpo = nome_canal.lstrip('#').lower()
    
    id_canal = CANAL_MOCK_MAP.get(nome_canal_limpo)

    if id_canal:
        print(f"id (mocado): '{nome_canal}' -> '{id_canal}'")
        return id_canal
    else:
        print(f" Canal '{nome_canal}' não encontrado no dicionário Mock.")
        return None

def enviar_mensagem(nome_canal, texto_mensagem):
    if not client:
        print("Não é possível enviar a mensagem: Cliente Slack não está inicializado devido à falta do Token.")
        return

    id_canal = buscar_id_canal_mock(nome_canal)
    
    if not id_canal:
        print(" Não é possível enviar a mensagem: ID do canal não encontrado.")
        return

    print(f" Tentando postar no canal com ID: {id_canal}")
    try:
        response = client.chat_postMessage(
            channel=id_canal, 
            text=texto_mensagem,
            as_user=True 
        )
        print("---")
        print(f" SUCESSO! Mensagem enviada para '{nome_canal}'.")
        print(f" ID da Mensagem (TS): {response['ts']}")
        print("---")

    except SlackApiError as e:
        # Captura e trata erros específicos da API do Slack
        print("---")
        print(f"ERRO ao enviar mensagem para '{nome_canal}':")
        print(f"Código do erro: {e.response['error']}")
        
        # O erro mais comum é 'not_in_channel' (Bot não é membro)
        if e.response['error'] == "not_in_channel":
            print("O bot não encontrou o canal")
        
        print("---")
    except Exception as e:
        print(f"🛑 ERRO inesperado: {e}")

if __name__ == "__main__":
    CANAL_ALVO_1 = "santander-alertas"
    MENSAGEM_1 = "Atenção: Uso de CPU 90% "
    print("\n##### TESTE : Canal de Alerta #####")
    enviar_mensagem(CANAL_ALVO_1, MENSAGEM_1)
