import requests
import json
import sys
from packaging import version
import webbrowser
import os

# Versão atual do aplicativo
CURRENT_VERSION = "1.0.0"  # Atualize isso a cada lançamento

def get_version():
    """Recupera a versão atual do aplicativo do arquivo version.json."""
    try:
        # Caminho para o arquivo version.json na raiz do projeto
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'version.json')
        
        with open(json_path, 'r') as f:
            version_data = json.load(f)
            return version_data["version"]
    except Exception as e:
        # Versão fallback caso não consiga ler o arquivo
        return "1.0.0"

def check_for_updates():
    """Verifica se há uma versão mais recente disponível."""
    current_version = get_version()  # Obtém a versão atual
    try:
        # URL para um arquivo JSON que contém informações da versão mais recente
        # Pode ser um arquivo no GitHub ou em qualquer servidor web
        version_url = "https://raw.githubusercontent.com/dawilao/PDFMaster/main/version.json"
        
        response = requests.get(version_url, timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            latest_version = version_info["version"]
            download_url = version_info["download_url"]
            
            # Compara versões
            if version.parse(latest_version) > version.parse(current_version):
                show_update_dialog(latest_version, download_url, current_version)
                return False  # Versão desatualizada
            return True  # Versão atualizada
        else:
            # Se não conseguir verificar, permite o uso (mais amigável)
            print("Não foi possível verificar atualizações. Continuando...")
            return True
    except Exception as e:
        print(f"Erro ao verificar atualizações: {e}")
        # Em caso de erro, permite o uso
        return True

def show_update_dialog(latest_version, download_url, current_version):
    """Mostra diálogo de atualização e opções para o usuário."""
    print("\n" + "="*50)
    print(f"ATUALIZAÇÃO OBRIGATÓRIA DISPONÍVEL!")
    print(f"Sua versão: {current_version}")
    print(f"Nova versão: {latest_version}")
    print("\nVocê precisa atualizar para continuar usando o PDFMaster.")
    print("="*50)
    
    while True:
        choice = input("\nDeseja: [1] Baixar a nova versão agora, [2] Sair? ").strip()
        if choice == "1":
            print("Abrindo página de download...")
            webbrowser.open(download_url)
            sys.exit(0)
        elif choice == "2":
            print("Saindo do aplicativo. Por favor, atualize para usar novamente.")
            sys.exit(0)
