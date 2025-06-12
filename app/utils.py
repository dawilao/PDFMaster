import os
from os.path import exists
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Toplevel, Button, Label
import customtkinter
import traceback


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        # Verifica se o botão está desabilitado antes de mostrar
        if self.widget.cget("state") == "disabled":
            self.show_tooltip()

    def on_leave(self, event=None):
        self.hide_tooltip()

    def show_tooltip(self):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 50
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove a borda da janela
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=f" {self.text} ",
            background="#e3e3e3",
            foreground="black",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9)
        )
        label.pack()

    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class IconManager:
    """Gerencia o carregamento de ícones da aplicação."""
    
    def __init__(self):
        self.icon_paths = [
            r'app\assets\PDFMaster_icon.ico',
            r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\PDFMaster\app\PDFMaster_icon.ico',
        ]

    def set_window_icon(self, window):
        """Define o ícone da janela usando o primeiro caminho válido encontrado."""
        for path in self.icon_paths:
            if exists(path):
                try:
                    window.iconbitmap(path)
                    return  # Se conseguiu definir o ícone, encerra a função
                except Exception as e:
                    print(f"Erro ao carregar o ícone de {path}: {e}")
                    continue  # Tenta o próximo caminho se houver erro
        
        print("Não foi possível carregar o ícone de nenhum dos caminhos disponíveis")


def handle_error(funcao, erro, root):
    """Trata erros de forma centralizada com opção de expandir traceback"""
    tb = traceback.format_exc()

    def mostrar_traceback():
        win = Toplevel(root)
        win.title("Detalhes do erro")
        win.geometry("540x320")
        Label(win, text="Traceback completo:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Consolas", 9))
        txt.pack(expand=True, fill="both", padx=10, pady=10)
        txt.insert(tk.END, tb)
        txt.config(state="disabled")
        Button(win, text="Fechar", command=win.destroy).pack(pady=(0, 10))

    resposta = messagebox.askyesno(
        "Erro",
        f"Erro em {funcao}: {erro}\n\nDeseja ver detalhes do erro?",
        parent=root
    )
    if resposta:
        mostrar_traceback()


def selecionar_diretorio():
    """Abre um diálogo para selecionar um diretório e retorna o caminho selecionado."""
    diretorio = filedialog.askdirectory()
    return diretorio if diretorio else None


def config_btn(btn):
    """Configura o estilo padrão dos botões"""
    btn.configure(fg_color="#035397",
                  text_color=("white"),
                  corner_radius=52)


def switch_altera_modo_dark_light(switch):
    """Altera entre modo escuro e claro baseado no estado do switch"""
    modo = switch.get()
    
    if modo == "on":
        customtkinter.set_appearance_mode("dark")
    else:
        customtkinter.set_appearance_mode("light")


def print_dimensao(componentes_list):
    """Imprime as dimensões de uma lista de componentes da interface"""
    for item in componentes_list:
        largura = item.winfo_width()
        altura = item.winfo_height()
        print(f"{item}, largura = {largura} || Altura = {altura}")


def validar_caminho_ou_selecionar(caminho):
    """
    Valida se o caminho existe ou abre o seletor de diretório.
    Também verifica por easter eggs.
    """
    if caminho.lower() == "jesus":
        messagebox.askquestion("Amém", "Será que você vai para o céu?")
    
    if os.path.exists(caminho):
        return caminho
    else:
        return selecionar_diretorio()


def criar_pastas(diretorio):
    """Cria pastas padrão no diretório especificado"""
    if not os.path.exists(diretorio):
        messagebox.showerror("Erro", f"O diretório '{diretorio}' não existe.")
        return
    
    pastas = ["DOCUMENTOS", "LEVANTAMENTO"]
    pastas_criadas = []
    pastas_existentes = []
    
    for pasta in pastas:
        caminho_pasta = os.path.join(diretorio, pasta)
        
        if os.path.exists(caminho_pasta):
            pastas_existentes.append(pasta)
        else:
            try:
                os.makedirs(caminho_pasta)
                pastas_criadas.append(pasta)
            except PermissionError:
                messagebox.showerror("Erro", f"Sem permissão para criar a pasta '{pasta}'.")
                return
            except OSError as e:
                messagebox.showerror("Erro", f"Erro ao criar a pasta '{pasta}': {e}")
                return
    
    # Mensagens informativas
    if pastas_existentes:
        messagebox.showwarning("Aviso", f"Pasta(s) já existente(s): {', '.join(pastas_existentes)}")
    
    if pastas_criadas:
        messagebox.showinfo("Sucesso", f"Pasta(s) criada(s): {', '.join(pastas_criadas)}")
    
    if not pastas_criadas and not pastas_existentes:
        messagebox.showinfo("Info", "Nenhuma operação realizada.")


def exportar_log_tempo(nome_usuario, tempo_dados, pasta_destino=None):
    """
    Exporta os dados de tempo para um arquivo de log
    
    Args:
        nome_usuario (str): Nome do usuário que realizou a operação
        tempo_dados (list): Lista de strings com os dados de tempo
        pasta_destino (str): Caminho da pasta onde salvar o log. Se None, usa Documents/PDFMaster_Logs
    """
    import datetime
    
    try:
        # Se pasta_destino não foi especificada, cria pasta PDFMaster_Logs em Documents
        if not pasta_destino:
            try:
                pasta_destino = r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\PDFMaster\logs'
            except Exception:
                pasta_destino = r'logs'

        # Cria a pasta se não existir
        os.makedirs(pasta_destino, exist_ok=True)
        
        # Gera nome do arquivo com data/hora
        data_hora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"log_{nome_usuario}_{data_hora}.txt"
        caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
        
        # Escreve os dados no arquivo
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(f"Log de operação PDFMaster\n")
            f.write(f"Usuário: {nome_usuario}\n")
            f.write(f"Data/Hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("-" * 50 + "\n")
            for linha in tempo_dados:
                f.write(f"{linha}\n")
                
        print(f"Log salvo em: {caminho_arquivo}")
        return caminho_arquivo
        
    except Exception as e:
        handle_error("exportar_log_tempo", f"Erro ao exportar log: {str(e)}", None)
        return None