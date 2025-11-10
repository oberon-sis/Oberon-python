import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv() 

SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')


def send_slack_message(message):
    if not SLACK_WEBHOOK_URL:
        print("Verificar .env")
        
    payload = {'text': message}
    headers = {'Content-type': 'application/json'}

    print(f"Tentando enviar mensagem: '{message}'")
    
    response = None 
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, headers=headers)
        
        response.raise_for_status() 
        
        print("Mensagem enviada com sucesso!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f" Erro ao enviar a mensagem: {e}")
        if response is not None and response.text:
            print(f"Detalhes da Resposta do Slack: {response.text}")
        return False



def main():

    print("Digite a mensagem que deseja enviar ao Slack (pressione Enter para enviar):")
        
    message = input("Digite a mensagem")

    send_slack_message(message)
main()