from dotenv import load_dotenv
from mysql.connector import connect, Error
import psutil as p
import os
import datetime

load_dotenv()

def inserir_metricas(idComponente, valor):
  config = {
    'user': os.getenv("USER_DB"),
    'password': os.getenv("PASSWORD_DB"),
    'host': os.getenv("HOST_DB"),
    'database': os.getenv("DATABASE_DB")
    }
  
  try:
    db = connect(**config)
    if (db.is_connected):
      with db.cursor() as cursor:
        query = f"INSERT INTO captura (idComponente, valor, dtCaptura) VALUES ({idComponente}, {valor}, now());"
        cursor.execute(query)

        db.commit()
      
      cursor.close()
      db.close()

  except Error as e:
    print(f"Error to connect with MySQL - {e}")

for i in range(20):
  porcentagem_cpu = p.cpu_percent(interval=1, percpu=False)
  porcentagem_ram = p.virtual_memory().percent
  porcentagem_disco = p.disk_usage("/").percent
  mac_address = p.net_if_addrs().get('wlo1')[1][1]
  hora_registro = datetime.datetime.now().strftime("%H:%M:%S")

  print()
  print("Registro inserido com sucesso!")
  print(f"Hora do registro: {hora_registro}")
  print(f"-="*20)
  print(f"Porcentagem de uso da CPU: {porcentagem_cpu}%")
  print(f"Porcentagem de uso da RAM: {porcentagem_ram}%")
  print(f"Porcentagem de uso do DISCO: {porcentagem_disco}%")
  print(f"Mac adress: {mac_address}")
  print(f"-="*20)

  inserir_metricas(1, porcentagem_cpu)
  inserir_metricas(2, porcentagem_ram)
  inserir_metricas(3, porcentagem_disco)
