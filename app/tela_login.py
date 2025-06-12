"""
Módulo responsável pela autenticação de usuários no sistema.

Inclui funções para:
- Tela de login com validação de credenciais;
- Alteração de senha;
- Interface gráfica com CustomTkinter;
- Integração com banco de dados SQLite para verificação de dados de login.
"""

import sqlite3
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

from .componentes import CustomEntry
from bd.utils_bd import DatabaseManager
from .utils import handle_error, IconManager


class LoginManager:
    """Gerenciador do sistema de login."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.root_login = None
        self.janela_alterar = None
        self.icone = IconManager()
    
    def validacao_login(self, root_login: ctk.CTk, entry_usuario: CustomEntry, entry_senha: CustomEntry):
        """
        Valida os dados de login inseridos pelo usuário.

        Verifica se o nome de usuário e a senha correspondem aos registros do banco de dados.
        Em caso de sucesso, fecha a janela de login e abre a tela principal.
        Caso contrário, exibe uma notificação de erro.
        
        Args:
            root_login (ctk.CTk): Janela principal da tela de login.
            entry_usuario (CustomEntry): Campo de entrada do nome de usuário.
            entry_senha (CustomEntry): Campo de entrada da senha.
        """
        from .tela_principal import janela

        usuario = entry_usuario.get().strip()
        senha = entry_senha.get()

        try:
            resultado = self.db_manager.validar_credenciais(usuario, senha)
            
            if resultado:
                nome_completo_usuario, abas = resultado
                messagebox.showinfo("Login sucedido", f"Bem vindo, {nome_completo_usuario.title()}!")
                root_login.destroy()
                janela(nome_completo_usuario)
            else:
                messagebox.showerror("Erro de Login", "Usuário ou senha inválidos!")

        except sqlite3.Error as erro_conexao:
            e = (
                "Erro de conexão",
                "Não foi possível conectar ao banco de dados. "
                "Certifique-se de que o Drive está conectado e de que há conexão com a internet."
            )
            handle_error("erro_conexao", e, self.root_login)

    def _validar_nova_senha(self, nova_senha: str, senha_atual_banco: str) -> bool:
        """
        Valida os critérios da nova senha.
        
        Args:
            nova_senha (str): Nova senha a ser validada.
            senha_atual_banco (str): Senha atual do banco de dados.
            
        Returns:
            bool: True se a senha é válida, False caso contrário.
        """
        if nova_senha == senha_atual_banco:
            messagebox.showerror("Erro", "A nova senha não pode ser igual à senha atual!")
            return False

        if len(nova_senha) < 4:
            messagebox.showerror("Erro", "A nova senha deve ter no mínimo 4 caracteres!")
            return False

        if len(nova_senha) > 10:
            messagebox.showerror("Erro", "A nova senha deve ter no máximo 10 caracteres!")
            return False

        return True

    def _alterar_senha(self, entry_usuario_alt: CustomEntry, entry_senha_atual: CustomEntry, 
                      entry_nova_senha: CustomEntry):
        """
        Processa a alteração de senha do usuário.
        
        Args:
            entry_usuario_alt (CustomEntry): Campo de entrada do nome de usuário.
            entry_senha_atual (CustomEntry): Campo de entrada da senha atual.
            entry_nova_senha (CustomEntry): Campo de entrada da nova senha.
        """
        usuario = entry_usuario_alt.get().strip()
        senha_atual = entry_senha_atual.get()
        nova_senha = entry_nova_senha.get()

        # Verificar campos vazios
        campos_obrigatorios = [
            (usuario, "Usuário"),
            (senha_atual, "Senha atual"),
            (nova_senha, "Nova senha")
        ]
        
        campos_vazios = [nome for valor, nome in campos_obrigatorios if not valor]

        if campos_vazios:
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
            return

        try:
            # Verificar se a senha atual está correta
            senha_atual_banco = self.db_manager.verificar_senha_atual(usuario)
            
            if not senha_atual_banco or senha_atual_banco != senha_atual:
                messagebox.showerror("Erro", "Senha atual inválida ou usuário não encontrado!")
                return

            # Validar nova senha
            if not self._validar_nova_senha(nova_senha, senha_atual_banco):
                return

            # Alterar senha no banco de dados
            if self.db_manager.alterar_senha(usuario, nova_senha):
                messagebox.showinfo("Sucesso", "Sua senha foi alterada com sucesso!")
                self.janela_alterar.destroy()
                self.criar_janela_login()
            else:
                messagebox.showerror("Erro", "Não foi possível alterar a senha!")

        except sqlite3.Error as e_altera_senha:
            handle_error(
                e_altera_senha,
                "Erro ao alterar senha",
                "Não foi possível alterar a senha no banco de dados."
            )

    def _voltar_para_login(self):
        """Volta para a tela de login principal."""
        if self.janela_alterar:
            self.janela_alterar.destroy()
        self.criar_janela_login()

    def criar_janela_alterar_senha(self):
        """
        Cria e exibe a janela de alteração de senha para o usuário.

        Permite que o usuário insira seu nome de usuário, senha atual e uma nova senha.
        A função valida a senha atual com o banco de dados, verifica se a nova senha 
        atende aos critérios de segurança e, caso tudo esteja correto, atualiza a senha 
        no banco de dados.
        """
        if self.root_login:
            self.root_login.destroy()
        
        # Criar janela de alteração de senha
        self.janela_alterar = ctk.CTk()
        self.janela_alterar.title("PDFMaster - Alterar Senha")
        self.janela_alterar.geometry("300x400")
        ctk.set_default_color_theme("blue")

        self.icone.set_window_icon(self.janela_alterar)

        """# Título da janela
        titulo = ctk.CTkLabel(master=self.janela_alterar, text="PDFMaster\nAlterar senha", font=("Segoe UI", 32, "bold"))
        titulo.pack(pady=(20, 0))"""

        frame = ctk.CTkFrame(master=self.janela_alterar)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        # Substitua as linhas do título e subtítulo por:
        titulo = ctk.CTkLabel(
            master=frame, 
            text="PDFMaster", 
            font=("Segoe UI", 32, "bold")
        )
        titulo.grid(row=0, column=1, pady=(20, 0), padx=20)

        subtitulo = ctk.CTkLabel(
            master=frame, 
            text="Alterar senha", 
            font=("Segoe UI", 16, "bold")
        )
        subtitulo.grid(row=1, column=1, pady=(0, 0), padx=20)

        # Criação dos campos para usuário e senha
        label_usuario_alt = ctk.CTkLabel(master=frame, text="Usuário:", anchor="w")
        label_usuario_alt.grid(row=2, column=1, sticky="w", pady=(5, 0))

        entry_usuario_alt = CustomEntry(master=frame, placeholder_text="Insira o usuário")
        entry_usuario_alt.grid(row=3, column=1, sticky="ew")

        label_senha_atual = ctk.CTkLabel(master=frame, text="Senha Atual:", anchor="w")
        label_senha_atual.grid(row=4, column=1, sticky="w", pady=(10, 0))

        entry_senha_atual = CustomEntry(master=frame, show="*", placeholder_text="Insira a senha atual")
        entry_senha_atual.grid(row=5, column=1, sticky="ew")

        label_nova_senha = ctk.CTkLabel(master=frame, text="Nova Senha:", anchor="w")
        label_nova_senha.grid(row=6, column=1, sticky="w", pady=(10, 0))

        entry_nova_senha = CustomEntry(master=frame, show="*", placeholder_text="Insira a nova senha")
        entry_nova_senha.grid(row=7, column=1, sticky="ew")

        # Botão para alterar a senha
        botao_alterar_senha = ctk.CTkButton(
            master=frame, 
            text="Alterar Senha", 
            command=lambda: self._alterar_senha(entry_usuario_alt, entry_senha_atual, entry_nova_senha)
        )
        botao_alterar_senha.grid(row=8, column=1, sticky="ew", pady=(15, 0))

        self.janela_alterar.bind("<Return>", lambda enter: botao_alterar_senha.invoke())

        # Botão para voltar para a tela de login
        botao_voltar = ctk.CTkButton(
            master=frame,
            text="Voltar",
            fg_color="#B31312",
            hover_color="Dark red",
            command=self._voltar_para_login
        )
        botao_voltar.grid(row=9, column=1, sticky="ew", pady=(10, 5))

        self.janela_alterar.mainloop()

    def criar_janela_login(self):
        """
        Cria e exibe a interface gráfica de login do sistema.
        
        Permite que o usuário insira seu nome de usuário e senha,
        faça login, altere sua senha ou encerre o programa.
        
        Returns:
            tuple: Tupla contendo (root_login, entry_usuario, entry_senha)
        """
        self.root_login = ctk.CTk()
        self.root_login.title("PDFMaster - Login")
        self.root_login.geometry("300x380")
        ctk.set_default_color_theme("blue")

        self.icone.set_window_icon(self.root_login)

        # Título da janela
        titulo = ctk.CTkLabel(master=self.root_login, text="PDFMaster", font=("Segoe UI", 32, "bold"))
        titulo.pack(pady=(20, 0))

        # Cria um rótulo (label) para o campo de entrada do nome de usuário
        label_usuario = ctk.CTkLabel(master=self.root_login, text="Usuário:", anchor="w")
        label_usuario.pack(pady=(10,0), padx=80, fill="x")

        # Cria um campo de entrada (Entry) para o usuário digitar seu nome de usuário
        entry_usuario = CustomEntry(master=self.root_login, placeholder_text="Insira o usuário")
        entry_usuario.pack(pady=(0,15))

        # Cria um rótulo (label) para o campo de entrada da senha
        label_senha = ctk.CTkLabel(master=self.root_login, text="Senha:", anchor="w")
        label_senha.pack(pady=0, padx=80, fill="x")

        # Cria um campo de entrada (Entry) para o usuário digitar sua senha
        entry_senha = CustomEntry(master=self.root_login, show='*', placeholder_text="Insira a senha")
        entry_senha.pack(pady=(0,20))

        # Botão de login
        botao_login = ctk.CTkButton(
            master=self.root_login,
            text="Login",
            command=lambda: self.validacao_login(self.root_login, entry_usuario, entry_senha)
        )
        botao_login.pack(pady=(0,15))

        # Botão para sair
        botao_sair = ctk.CTkButton(
            master=self.root_login, 
            text="Sair", 
            fg_color="#B31312",
            hover_color="Dark red", 
            command=self.root_login.destroy
        )
        botao_sair.pack(pady=(0,15))

        # Botão para alterar senha
        botao_alterar_senha = ctk.CTkButton(
            master=self.root_login,
            text="Alterar Senha",
            command=self.criar_janela_alterar_senha
        )
        botao_alterar_senha.pack(pady=(0,15))

        self.root_login.bind("<Return>", lambda enter: botao_login.invoke())

        self.root_login.mainloop()

        return self.root_login, entry_usuario, entry_senha


# Função de conveniência para manter compatibilidade
def janela_login():
    """Função de conveniência para criar a janela de login."""
    login_manager = LoginManager()
    return login_manager.criar_janela_login()
