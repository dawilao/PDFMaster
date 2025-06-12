#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para manipulação de arquivos PDF e JPG.
- Converte imagens JPG em um PDF.
- Cria pastas padrão para organização de arquivos.
- Divide um arquivo PDF em várias páginas individuais.
- Divide um arquivo PDF em outros, limitando o tamanho a 5Mb

Interface gráfica desenvolvida usando o customtkinter.
<https://medium.com/@fareedkhandev/modern-gui-using-tkinter-12da0b983e22>
"""
__author__ = "Dawison Nascimento"
__status__ = "Stable"
__license__ = "MIT license"
__copyright__ = "Copyright (c) 2025 Dawison Nascimento"
__maintainer__ = "Dawison Nascimento"
__email__ = "daw_afk@tutamail.com"
__url__ = "https://github.com/dawilao/PDFMaster"

from app.tela_login import janela_login

if __name__ == "__main__":
    janela_login()