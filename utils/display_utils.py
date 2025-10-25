# utils/display_utils.py

from datetime import datetime

def obter_horario_atual() -> str:
    """
    Retorna a hora atual formatada no padrão do banco de dados (YYYY-MM-DD HH:MM:SS).
    """
    agora = datetime.now()
    return agora.strftime("%Y-%m-%d %H:%M:%S")

def formatar_palavra(palavra: str):
    """
    Formata uma string para ser exibida no terminal em uma caixa que se adapta 
    dinamicamente à largura da palavra.
    """
    palavra_str = str(palavra)
    
    # Cálculo para garantir que a linha de borda tenha a mesma largura do conteúdo.
    largura_borda = '═' * (len(palavra_str) + 4)
    
    print(f"""
╔{largura_borda}╗
║  {palavra_str}  ║
╚{largura_borda}╝
    """)