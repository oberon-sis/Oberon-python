# Oberon - Coleta de Dados - Python

Repositório responsável pelo **agente em Python** que coleta métricas de hardware, do sistema de monitoramento da **Oberon**.
## 📌 Funcionalidades Chave

O sistema oferece uma solução completa de monitoramento e integração:

* **Coleta de Métricas:** Captura detalhada de recursos de hardware, incluindo **CPU**, **Memória**, **Disco** e **Temperatura**.
* **Identificação de Máquina:** Realiza a identificação da máquina através do **Nome**, **Modelo** e **MAC Address**.
* **Persistência de Dados:** Envio contínuo e armazenamento seguro de todas as métricas em **Banco de Dados**.

* **Visualização de Dados:** Integração com a plataforma **Web Data Viz** para exibição e análise gráfica das métricas coletadas.

## 📌 Funcionalidades em Desenvolvimento

* **Disparo de Alertas:** Integração com **API externa** para envio imediato de alertas críticos, garantindo resposta rápida a falhas.
* **Automação de Tickets:** Integração nativa com **Jira** para a criação automática de tickets de manutenção ou incidentes.


## 🚀 Tecnologias e Dependências

Este projeto foi desenvolvido utilizando as seguintes tecnologias e bibliotecas:

### Linguagens & Ambiente
* **Python 3.6**
* **SQL** MySql 

### Bibliotecas Python
* **psutil** (Para coleta de métricas do sistema)
* **requests** (Para integração com APIs externas de alerta)
* **jira** (Para comunicação e criação de tickets no Jira)

---

### 📂 Estrutura do Projeto

O projeto segue uma arquitetura modular, separando a lógica de negócio, utilidades e arquivos de configuração.

    .
    ├── src/
    │   ├── __pycache__/
    │   ├── alertas.py           # Lógica para disparo e tratamento de alertas.
    │   ├── captura.py           # Módulo para coleta das métricas de hardware (psutil).
    │   ├── exportacao.py        # Lógica para envio de métricas para o Banco de Dados.
    │   ├── maquina_config.py    # Módulo para coleta de informações de identificação da máquina.
    │   └── __init__.py
    ├── utils/
    │   ├── __pycache__/
    │   └── Database.py          # Classe de utilidade para gerenciar a conexão e operações com o Banco de Dados.
    ├── .env                     # Variáveis de ambiente e credenciais de acesso.
    ├── .gitignore               # Lista de arquivos e pastas ignorados pelo Git.
    ├── coleta_maquina_1.csv     # Exemplo de arquivo de dados coletados.
    ├── init.sh                  # Script de inicialização (instalação de dependências e execução).
    ├── main.py                  # Ponto de entrada do sistema e orquestrador principal da lógica.
    ├── README.md                # Documentação principal do projeto.
    └── requirements.txt         # Lista de dependências Python.

## 🛠️ Pré-requisitos

Para rodar este projeto, você precisa ter instalado:

* Python 3.6

---

## 💻 Como Rodar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/oberon-sis/Oberon-Coleta-Python.git
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure o Ambiente:**
    * Preencha o arquivo `.env` com as suas credenciais de banco de dados e API.

4.  **Execute o Script:**
    ```bash
    python main.py
    ```
    *ou utilize o script de inicialização:*
    ```bash
    ./init.sh
    ```

## 📖 Documentação
Mais detalhes sobre as métricas e requisitos estão na [documentação principal](../) disponivél nas pasta do one drive.

---
