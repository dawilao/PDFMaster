import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Toplevel, Button, Label
import customtkinter
import traceback

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