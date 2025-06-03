import customtkinter
import os
import webbrowser
import traceback
import threading
import re

try:
    from .utils import config_btn, switch_altera_modo_dark_light, print_dimensao, validar_caminho_ou_selecionar, criar_pastas, handle_error
    from .pdf_utils import convert_to_pdf, dividir_pdf_1, dividir_pdf_por_tamanho, selecionar_arquivo_pdf
except ImportError:
    from utils import config_btn, switch_altera_modo_dark_light, print_dimensao, validar_caminho_ou_selecionar, criar_pastas, handle_error
    from pdf_utils import convert_to_pdf, dividir_pdf_1, dividir_pdf_por_tamanho, selecionar_arquivo_pdf

class PDFMasterApp:
    __author__ = "Dawison Nascimento"
    __license__ = "MIT License"
    __version__ = "1.2.0"

    def __init__(self, nome_usuario=None):
        # Inicialização das variáveis globais como atributos da classe
        self.nome_usuario = nome_usuario.title()
        self.entry_caminho_pasta = None
        self.entry_nome_do_arquivo_pdf = None
        self.btn_versao = None
        self.btn_contato_programador = None
        self.btn_sair = None
        self.btn_ajuda_e_suporte = None
        self.switch_dark_light_mode = None
        self.frame_contatos_sair_centralizado = None
        self.frame_contatos_sair_esquerda = None
        self.entry_caminho_pasta_dividir_por_tamanho = None
        self.entry_caminho_dividir_pdf_1 = None
        self.btn_abrir_pasta_dividir_pdf_por_tamanho = None
        self.tab_janela = None
        self.frame_contatos_sair = None
        self.frame_switch = None
        self.label_switch = None
        self.espaco_centralizar_switch = 0
        self.tamanho_janela = "540x420"
        self.debug_frame = None
        self.debug_textbox = None
        self.debug_expanded = False
        self.icon_path = r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\PDFMaster\app\PDFMaster_icon.ico'
        
        # Configurar modo de aparência
        customtkinter.set_appearance_mode("system")
        
        # Criar e configurar a janela principal
        self.setup_main_window()
        
    def setup_main_window(self):
        """Configura a janela principal e todos os seus componentes"""
        # Configuração da interface gráfica principal, com título e tamanho da janela
        self.janela = customtkinter.CTk()
        self.janela.title("PDFMaster")
        
        self.janela.geometry(self.tamanho_janela)
        self.janela.resizable(False, False)
        
        try:
            self.janela.iconbitmap(self.icon_path)
        except Exception as e:
            print(f"Não foi possível carregar o ícone: {e}")

        # Título da janela com o nome do usuário
        titulo = customtkinter.CTkLabel(master=self.janela, text=f"Bem-vindo, {self.nome_usuario}!", font=("Segoe UI", 16, "bold"))
        titulo.pack(pady=(10, 5))
     
        self.tab_janela = customtkinter.CTkTabview(master=self.janela, border_width=2, height=35, width=520)
        self.tab_janela.pack(pady=(0,5))  # Ajusta o padding e expande para preencher o espaço

        # Criar todas as abas
        self.create_aba_imagem_pdf()
        self.create_aba_dividir_pdf()
        self.create_aba_dividir_pdf_por_tamanho()
        self.create_frame_inferior()
        
        # Executar funções que precisam de delay
        self.janela.after(100, self.centraliza_switch)
        self.janela.after(2000, self.print_dimensao)

    def create_debug_console(self):
        """Cria o campo de debug expandível/minimizável"""
        self.debug_frame = customtkinter.CTkFrame(master=self.janela, fg_color="transparent")
        self.debug_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.btn_toggle_debug = customtkinter.CTkButton(
            master=self.debug_frame,
            text="Mostrar passo a passo",
            command=self.toggle_debug_console,
            width=180
        )
        self.btn_toggle_debug.pack(side="left", padx=(0, 10))

        self.debug_textbox = customtkinter.CTkTextbox(
            master=self.debug_frame,
            height=80,
            width=400,
            state="disabled",
            font=("Roboto", 10),
        )
        self.debug_textbox.pack(side="left", fill="x", expand=True)
        self.debug_textbox.pack_forget()  # Inicialmente oculto

    def show_debug_console(self):
        """Exibe o campo de debug na tela"""
        if not self.debug_frame:
            self.create_debug_console()
        else:
            self.debug_frame.pack(fill="x", padx=10, pady=(0, 5))
            self.btn_toggle_debug.pack(side="left", padx=(0, 10))
        self.debug_expanded = False
        self.debug_textbox.pack_forget()
        self.btn_toggle_debug.configure(text="Mostrar passo a passo")

    def hide_debug_console(self):
        """Oculta o campo de debug da tela"""
        if self.debug_frame:
            self.debug_frame.pack_forget()

    def toggle_debug_console(self):
        """Expande ou minimiza o campo de debug"""
        if self.debug_expanded:
            self.debug_textbox.pack_forget()
            self.btn_toggle_debug.configure(text="Mostrar passo a passo")
        else:
            self.debug_textbox.pack(side="left", fill="x", expand=True)
            self.btn_toggle_debug.configure(text="Ocultar passo a passo")
        self.debug_expanded = not self.debug_expanded

    def append_debug(self, msg):
        """Adiciona mensagem ao campo de debug"""
        self.debug_textbox.configure(state="normal")
        
        # Se for mensagem de progresso de página, sobrescreve a última linha
        if (
            "Compactando página" in msg
            or "Dividindo página" in msg
        ):
            # Remove a última linha antes de inserir a nova
            self.debug_textbox.delete("end-2l", "end-1l")
            self.debug_textbox.insert("end-1l", msg + "\n")
        else:
            self.debug_textbox.insert("end", msg + "\n")
            self.debug_textbox.see("end")
        
        self.debug_textbox.configure(state="disabled")

    def create_aba_imagem_pdf(self):
        """Cria a aba 'Imagem para PDF'"""
        # Adicionar uma aba
        aba_imagem_pdf = self.tab_janela.add("Imagem para PDF")

        # Frame para separação dos botões
        frame_aba_imagem_pdf = customtkinter.CTkFrame(master=aba_imagem_pdf, border_width=0, width=400)
        frame_aba_imagem_pdf.pack(padx=0, fill="x")

        # Cria um rótulo (label) para o campo de entrada do caminho (pasta) para localização das fotos
        label_caminho_pasta = customtkinter.CTkLabel(master=frame_aba_imagem_pdf, text="Caminho:", anchor="w", width=400)
        label_caminho_pasta.pack(pady=(5,0), padx=0)

        # Cria um campo de entrada (Entry) para o usuário digitar o caminho (pasta) para localização das fotos
        self.entry_caminho_pasta = customtkinter.CTkEntry(master=frame_aba_imagem_pdf, 
                                                     placeholder_text="Insira o caminho",
                                                     width=400,
                                                     border_width=1)
        self.entry_caminho_pasta.pack(pady=0)

        # Cria um rótulo (label) para o campo de entrada do nome do arquivo PDF
        label_nome_arquivo_pdf = customtkinter.CTkLabel(master=frame_aba_imagem_pdf,
                                                       text="Nome do arquivo PDF:", 
                                                       anchor="w", 
                                                       width=400)
        label_nome_arquivo_pdf.pack(pady=(5,0), padx=0)
        
        # Cria um campo de entrada (Entry) para o usuário digitar o nome do arquivo PDF
        self.entry_nome_do_arquivo_pdf = customtkinter.CTkEntry(master=frame_aba_imagem_pdf,
                                                     placeholder_text="Insira o nome para o PDF. Deixe em branco para usar 'EXECUÇÃO'",
                                                     width=400,
                                                     border_width=1)
        self.entry_nome_do_arquivo_pdf.pack(pady=(5, 10))

        # Botão para converter imagens em PDF
        btn_converter = customtkinter.CTkButton(master=frame_aba_imagem_pdf,
                                                text="Converter Imagens para PDF",
                                                command=self.converter_imagens)
        btn_converter.pack(pady=15)
        config_btn(btn_converter)

        # Botão para criar pastas padrão
        btn_criar_pastas = customtkinter.CTkButton(master=frame_aba_imagem_pdf,
                                                   text="Criar Pastas Padrão",
                                                   command=self.criar_pastas_interface)
        btn_criar_pastas.pack(pady=(0,10))
        config_btn(btn_criar_pastas)

    def create_aba_dividir_pdf(self):
        """Cria a aba 'Dividir PDF'"""
        # Adicionar uma aba
        aba_dividir_pdf = self.tab_janela.add("Dividir PDF")

        # Frame para separação dos botões
        frame_aba_dividir_pdf_1 = customtkinter.CTkFrame(master=aba_dividir_pdf, border_width=0)
        frame_aba_dividir_pdf_1.pack(padx=0, fill="x")

        # Cria um rótulo (label) para o campo de entrada do caminho (pasta) para localização das fotos
        label_caminho_pasta_aba_dividir_pdf_1 = customtkinter.CTkLabel(master=frame_aba_dividir_pdf_1, text="Caminho:", pady=5, anchor="w", width=350)
        label_caminho_pasta_aba_dividir_pdf_1.pack(pady=(5,0), padx=0)

        self.entry_caminho_dividir_pdf_1 = customtkinter.CTkEntry(master=frame_aba_dividir_pdf_1,
                                                             placeholder_text="Insira o caminho",
                                                             width=350,
                                                             border_width=1)
        self.entry_caminho_dividir_pdf_1.pack(pady=(0,5))

        # Botão para dividir um PDF em páginas individuais
        btn_dividir_pdf = customtkinter.CTkButton(master=frame_aba_dividir_pdf_1, 
                                                  text="Dividir PDF", 
                                                  command=self.dividir_pdf_1_interface)
        btn_dividir_pdf.pack(pady=10)
        config_btn(btn_dividir_pdf)

    def create_aba_dividir_pdf_por_tamanho(self):
        """Cria a aba 'Dividir PDF por Tamanho'"""
        # Adicionar uma aba
        aba_dividir_pdf_por_tamanho = self.tab_janela.add("Dividir PDF por Tamanho")

        # Frame para separação dos botões
        frame_aba_dividir_pdf_por_tamanho = customtkinter.CTkFrame(master=aba_dividir_pdf_por_tamanho, border_width=0)
        frame_aba_dividir_pdf_por_tamanho.pack(padx=0, fill="x")

        # Cria um rótulo (label) para o campo de entrada do caminho (pasta) para localização das fotos
        label_caminho_pasta_aba_dividir_pdf_por_tamanho = customtkinter.CTkLabel(master=frame_aba_dividir_pdf_por_tamanho,
                                                                       text="Caminho:",
                                                                       pady=5,
                                                                       anchor="w",
                                                                       width=350)
        label_caminho_pasta_aba_dividir_pdf_por_tamanho.pack(pady=(5,0), padx=0)

        # Cria um campo de entrada (Entry) para o usuário digitar o caminho (pasta) para localização do PDF
        self.entry_caminho_pasta_dividir_por_tamanho = customtkinter.CTkEntry(master=frame_aba_dividir_pdf_por_tamanho, 
                                                     placeholder_text="Insira o caminho",
                                                     width=350,
                                                     border_width=1)
        self.entry_caminho_pasta_dividir_por_tamanho.pack(pady=(0,5))

        # Botão para abrir o caminho especificado
        self.btn_abrir_pasta_dividir_pdf_por_tamanho = customtkinter.CTkButton(master=frame_aba_dividir_pdf_por_tamanho, 
                                                  text="Converter PDF por Tamanho: até 5 MB", 
                                                  command=self.dividir_pdf_por_tamanho_interface)
        self.btn_abrir_pasta_dividir_pdf_por_tamanho.pack(pady=10)
        config_btn(self.btn_abrir_pasta_dividir_pdf_por_tamanho)

    def create_frame_inferior(self):
        """Cria o frame inferior com botões de ajuda, suporte e sair"""
        # Adiciona um frame fixado na parte de baixo da janela
        self.frame_contatos_sair = customtkinter.CTkFrame(master=self.janela)
        self.frame_contatos_sair.pack(side='bottom', fill='x', padx=0)

        # Configura o layout do frame para usar grid com pesos proporcionais
        self.frame_contatos_sair.grid_columnconfigure(0, weight=1)  # Espaço flexível à esquerda
        self.frame_contatos_sair.grid_columnconfigure(1, weight=2)  # Switch
        self.frame_contatos_sair.grid_columnconfigure(2, weight=2)  # Botões centrais
        self.frame_contatos_sair.grid_columnconfigure(3, weight=2)  # Botões à direita
        self.frame_contatos_sair.grid_columnconfigure(4, weight=1)  # Espaço flexível à direita

        self.create_switch_section()
        self.create_central_buttons()
        self.create_left_buttons()

    def create_switch_section(self):
        """Cria a seção do switch para alterar tema"""
        # Cria um frame adicional para o switch e o label
        self.frame_switch = customtkinter.CTkFrame(master=self.frame_contatos_sair,
                                              fg_color="transparent",
                                              border_width=0)
        self.frame_switch.grid(row=0, column=1, sticky="nsew")
        self.frame_switch.grid_columnconfigure(0, weight=1)

        # Cria um label para o texto acima do switch
        self.label_switch = customtkinter.CTkLabel(
            master=self.frame_switch, 
            text=" Alterar tema"
        )
        self.label_switch.grid(row=0, column=0, pady=(10, 2))

        # Variável para armazenar o estado do switch
        switch_dark_light_mode_var = customtkinter.StringVar(value="on")

        # Cria um switch para alterar o modo escuro e claro
        self.switch_dark_light_mode = customtkinter.CTkSwitch(
            master=self.frame_switch,
            command=lambda: switch_altera_modo_dark_light(self.switch_dark_light_mode), 
            text="",
            variable=switch_dark_light_mode_var,
            onvalue="on",
            offvalue="off"
        )

    def create_central_buttons(self):
        """Cria os botões centrais (Ajuda e Suporte, Sair)"""
        # Cria um frame adicional para os botões de "Ajuda e Suporte" e "Sair"
        self.frame_contatos_sair_centralizado = customtkinter.CTkFrame(master=self.frame_contatos_sair,
                                                                  fg_color="transparent",
                                                                  border_width=0,
                                                                  height=76)
        self.frame_contatos_sair_centralizado.grid(row=0, column=2, sticky="nsew")
        self.frame_contatos_sair_centralizado.grid_columnconfigure(0, weight=1)

        # Cria o botão de suporte
        self.btn_ajuda_e_suporte = customtkinter.CTkButton(master=self.frame_contatos_sair_centralizado,
                                            text="Ajuda e Suporte",
                                            fg_color="#035397",
                                            text_color="white",
                                            corner_radius=52,
                                            command=self.toggle_ajuda,
                                            width=160)
        self.btn_ajuda_e_suporte.grid(row=0, column=0, pady=(5,0))

        # Botão para fechar o programa
        self.btn_sair = customtkinter.CTkButton(
            master=self.frame_contatos_sair_centralizado,
            text="Sair",
            fg_color="#B31312",
            hover_color="Dark red",
            text_color=("white"),
            corner_radius=52,
            command=self.janela.destroy,
            width=160)
        self.btn_sair.grid(row=1, column=0, pady=(10, 5))

    def create_left_buttons(self):
        """Cria os botões à esquerda (Sobre, Contato)"""
        # Cria um frame adicional para os botões "Sobre o Programa" e "Contate o Programador"
        self.frame_contatos_sair_esquerda = customtkinter.CTkFrame(master=self.frame_contatos_sair,
                                                              fg_color="transparent",
                                                              border_width=0,
                                                              height=76,
                                                              width=170)
        self.frame_contatos_sair_esquerda.grid(row=0, column=3, sticky="nsew")
        self.frame_contatos_sair_esquerda.grid_columnconfigure(0, weight=1)

        # Cria os botões, mas não os exibe inicialmente
        self.btn_versao = customtkinter.CTkButton(master=self.frame_contatos_sair_esquerda, 
                                             text="Sobre o programa",
                                             width=160,
                                             fg_color="#035397",
                                             text_color="white",
                                             corner_radius=52,
                                             command=self.versao)

        self.btn_contato_programador = customtkinter.CTkButton(master=self.frame_contatos_sair_esquerda,
                                          text="Contate o programador",
                                          width=160,
                                          fg_color="#035397",
                                          text_color="white",
                                          corner_radius=52,
                                          command=lambda: webbrowser.open("https://wa.me/447979217469"))

    def centraliza_switch(self):
        """Centraliza o switch automaticamente baseado no tamanho do frame"""
        tamanho_do_frame = self.frame_switch.winfo_width()
        tamanho_do_texto = self.label_switch.winfo_width()
        tamanho_do_switch = 100
        espaco_entre_texto = (tamanho_do_frame - tamanho_do_texto) / 2
        espaco_entre_switch = (tamanho_do_frame - tamanho_do_switch) / 2
        self.espaco_centralizar_switch = (espaco_entre_texto - espaco_entre_switch) + ((tamanho_do_texto / 2) + 11)
        
        print(tamanho_do_frame, tamanho_do_texto, tamanho_do_switch)
        print(espaco_entre_texto, espaco_entre_switch, self.espaco_centralizar_switch)

        # Grid do switch
        self.switch_dark_light_mode.grid(row=1, column=0, padx=(self.espaco_centralizar_switch, 0), pady=(0, 10))

    def print_dimensao(self):
        """Imprime dimensões dos componentes da interface"""
        lista = [self.tab_janela, self.frame_contatos_sair, self.frame_switch, 
                self.frame_contatos_sair_centralizado, self.frame_contatos_sair_esquerda, 
                self.switch_dark_light_mode, self.label_switch]
        # print_dimensao(lista)

    # Métodos de comando dos botões - integrados com utils e pdf_utils
    def converter_imagens(self):
        """Converte imagens para PDF"""
        caminho = self.entry_caminho_pasta.get()
        caminho_validado = validar_caminho_ou_selecionar(caminho)

        nome_arquivo = self.entry_nome_do_arquivo_pdf.get().upper().strip()
        caracteres_invalidos = r'[<>:"/\\|?*]'  # Lista de caracteres inválidos em nomes de arquivo
        nome_arquivo = re.sub(caracteres_invalidos, '_', nome_arquivo)

        if not nome_arquivo:
            nome_arquivo = "EXECUÇÃO"

        if caminho_validado:
            # Atualiza o campo de entrada com o caminho validado
            self.entry_caminho_pasta.delete(0, 'end')
            self.entry_caminho_pasta.insert(0, caminho_validado)
            
            # Converte as imagens
            import os
            output_pdf = os.path.join(caminho_validado, nome_arquivo + ".pdf")
            convert_to_pdf(caminho_validado, output_pdf)
        
        self.janela.focus()

    def criar_pastas_interface(self):
        """Cria pastas padrão"""
        caminho = self.entry_caminho_pasta.get()
        caminho_validado = validar_caminho_ou_selecionar(caminho)
        
        if caminho_validado:
            # Atualiza o campo de entrada com o caminho validado
            self.entry_caminho_pasta.delete(0, 'end')
            self.entry_caminho_pasta.insert(0, caminho_validado)
            
            # Cria as pastas
            criar_pastas(caminho_validado)

    def dividir_pdf_1_interface(self):
        """Divide PDF em páginas individuais"""
        caminho_inicial = self.entry_caminho_dividir_pdf_1.get()
        
        # Verifica por easter egg
        if caminho_inicial.lower() == "jesus":
            from tkinter import messagebox
            messagebox.askquestion("Amém", "Será que você vai para o céu?")

        # Seleciona o arquivo PDF
        arquivo = selecionar_arquivo_pdf(caminho_inicial)
        
        if arquivo:
            dividir_pdf_1(arquivo)

    def dividir_pdf_por_tamanho_interface(self):
        """Divide PDF por tamanho"""
        caminho_inicial = self.entry_caminho_pasta_dividir_por_tamanho.get()

        # Verifica por easter egg
        if caminho_inicial.lower() == "jesus":
            from tkinter import messagebox
            messagebox.askquestion("Amém", "Será que você vai para o céu?")

        # Seleciona o arquivo PDF
        arquivo = selecionar_arquivo_pdf(caminho_inicial)

        # Só continua se o usuário selecionou um arquivo
        if not arquivo:
            return

        # Obtém o diretório de saída
        pasta_saida = os.path.dirname(arquivo)

        if arquivo:
            self.show_debug_console()  # Mostra o campo de debug
            # Executa em thread separada
            threading.Thread(
                target=self._dividir_pdf_por_tamanho_thread,
                args=(arquivo, pasta_saida),
                daemon=True
            ).start()

    def _dividir_pdf_por_tamanho_thread(self, arquivo, pasta_saida):
        try:
            self.clear_debug()
            self.append_debug("Iniciando divisão do PDF...")
            dividir_pdf_por_tamanho(arquivo, pasta_saida, nome_usuario=self.nome_usuario, callback=self.append_debug)
            self.append_debug("Divisão concluída!")
        except Exception as e:
            self.append_debug(f"Erro: {e}")
        finally:
            # Aguarda um pequeno tempo para o usuário ver a mensagem final, se quiser
            self.janela.after(5000, self.hide_debug_console)

    def clear_debug(self):
        """Limpa o campo de debug"""
        self.debug_textbox.configure(state="normal")
        self.debug_textbox.delete("1.0", "end")
        self.debug_textbox.configure(state="disabled")

    def toggle_ajuda(self):
        """Toggle para mostrar/esconder ajuda"""
        try:
            is_visible = self.btn_versao.winfo_ismapped()
            if is_visible:
                self._esconder_ajuda()
            else:
                self._mostrar_ajuda()
            self._ajustar_janela()
        except Exception as e:
            handle_error("toggle_ajuda", e, self.janela)

    def _esconder_ajuda(self):
        """Esconde os botões de ajuda"""
        self.btn_versao.grid_forget()
        self.btn_contato_programador.grid_forget()

    def _mostrar_ajuda(self):
        """Mostra os botões de ajuda"""
        self.btn_versao.grid(row=0, column=0, pady=(5, 0))
        self.btn_contato_programador.grid(row=1, column=0, pady=(10, 5))

    def _ajustar_janela(self):
        """Ajusta o tamanho da janela ao conteúdo"""
        self.janela.update_idletasks()
        self.janela.geometry(self.tamanho_janela)

    def versao(self):
        """Mostra informações sobre a versão"""
        try:
            instrucoes = self._get_instrucoes()
            info_versao = self._get_info_versao()
            mensagem = f"{instrucoes}\n\n{info_versao}"
            from tkinter import messagebox
            messagebox.showinfo("Sobre o Programa", mensagem)
        except Exception as e:
            handle_error("versao", e, self.janela)

    def _get_instrucoes(self):
        """Retorna as instruções do programa"""
        return (
            "Bem-vindo ao PDFMaster.\n\n"
            "O PDFMaster facilita a criação e manipulação de arquivos PDF.\n\n"
            "Funções disponíveis:\n"
            "• Imagem para PDF: Converte imagens JPG em PDF\n"
            "• Dividir PDF: Separa páginas em arquivos individuais\n"
            "• Dividir por Tamanho: Divide PDFs em arquivos ≤ 5MB"
        )

    def _get_info_versao(self):
        """Retorna informações de versão"""
        return (
            f"Criado por: {self.__author__}\n"
            f"Licença: {self.__license__}\n"
            f"Versão: {self.__version__}\n"
        )

    def run(self):
        """Inicia o loop principal da aplicação"""
        self.janela.mainloop()

def janela(nome_usuario):
    """Função para iniciar a aplicação PDFMaster com o nome do usuário"""
    app = PDFMasterApp(nome_usuario)
    app.run()

if __name__ == "__main__":
    # Teste rápido da aplicação
    janela("Usuário Teste")