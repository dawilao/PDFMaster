"""
Módulo responsável por operações de banco de dados.

Inclui funções para:
- Conexão com banco de dados SQLite;
- Validação de credenciais de login;
- Alteração de senhas de usuários.
"""

import sqlite3
from typing import Optional, Tuple


class DatabaseManager:
    """Gerenciador de operações do banco de dados."""
    
    def __init__(self):
        self.db_paths = [
            r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\login.db',
            r'app\bd\login.db'
        ]
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Estabelece conexão com o banco de dados.
        
        Returns:
            sqlite3.Connection: Conexão com o banco de dados.
            
        Raises:
            sqlite3.Error: Se não conseguir conectar a nenhum dos caminhos.
        """
        for db_path in self.db_paths:
            try:
                return sqlite3.connect(db_path)
            except sqlite3.Error:
                continue
        
        raise sqlite3.Error("Não foi possível conectar ao banco de dados em nenhum dos caminhos.")
    
    def validar_credenciais(self, usuario: str, senha: str) -> Optional[Tuple[str, str]]:
        """
        Valida as credenciais do usuário no banco de dados.
        
        Args:
            usuario (str): Nome de usuário.
            senha (str): Senha do usuário.
            
        Returns:
            Optional[Tuple[str, str]]: Tupla com (nome_completo, abas) se válido, None caso contrário.
            
        Raises:
            sqlite3.Error: Se houver erro na operação do banco de dados.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = (
                "SELECT senha, nome_completo, abas "
                "FROM dados_login "
                "WHERE LOWER(nome_usuario) = ?"
            )
            cursor.execute(query, (usuario.lower(),))
            resultado = cursor.fetchone()
            
            if resultado and resultado[0] == senha:
                return (resultado[1], resultado[2])
            return None
            
        finally:
            conn.close()
    
    def verificar_senha_atual(self, usuario: str) -> Optional[str]:
        """
        Verifica e retorna a senha atual do usuário.
        
        Args:
            usuario (str): Nome de usuário.
            
        Returns:
            Optional[str]: Senha atual se o usuário existir, None caso contrário.
            
        Raises:
            sqlite3.Error: Se houver erro na operação do banco de dados.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT senha FROM dados_login WHERE LOWER(nome_usuario) = ?",
                (usuario.lower(),)
            )
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
            
        finally:
            conn.close()
    
    def alterar_senha(self, usuario: str, nova_senha: str) -> bool:
        """
        Altera a senha do usuário no banco de dados.
        
        Args:
            usuario (str): Nome de usuário.
            nova_senha (str): Nova senha.
            
        Returns:
            bool: True se a alteração foi bem-sucedida, False caso contrário.
            
        Raises:
            sqlite3.Error: Se houver erro na operação do banco de dados.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE dados_login SET senha = ? WHERE LOWER(nome_usuario) = ?",
                (nova_senha, usuario.lower())
            )
            conn.commit()
            return cursor.rowcount > 0
            
        finally:
            conn.close()