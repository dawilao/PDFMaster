import shutil
import os
import glob
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfStreamError
from tkinter import filedialog, messagebox
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

try:
    from .utils import handle_error, exportar_log_tempo
except ImportError:
    from utils import handle_error, exportar_log_tempo

def convert_to_pdf(pasta_imagens, output_pdf):
    """
    Converte todas as imagens de uma pasta em um único arquivo PDF
    
    Args:
        pasta_imagens (str): Caminho da pasta contendo as imagens
        output_pdf (str): Caminho do arquivo PDF de saída
    """
    try:
        # Extensões de imagem suportadas
        extensoes_imagem = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.gif']
        
        # Lista para armazenar as imagens
        imagens = []
        
        # Busca por imagens na pasta
        for extensao in extensoes_imagem:
            imagens.extend(glob.glob(os.path.join(pasta_imagens, extensao)))
            imagens.extend(glob.glob(os.path.join(pasta_imagens, extensao.upper())))
        
        if not imagens:
            messagebox.showinfo("Aviso", "Não há arquivos válidos para inclusão no PDF.")
            return
        
        # Verifica se o arquivo PDF já existe
        if os.path.exists(output_pdf):
            messagebox.showinfo("Aviso", "Arquivo já existente.")
            return
        
        # Remove duplicatas
        imagens = list(set(imagens))

        # Ordena as imagens por nome
        imagens.sort()
        
        # Cria um novo documento PDF usando reportlab para melhor controle de layout
        c = canvas.Canvas(output_pdf, pagesize=A4)
        page_width, page_height = A4
        
        for img_path in imagens:
            print("Convertendo:", img_path)
            
            # Abre a imagem
            img = Image.open(img_path)
            
            # Converte para RGB se necessário (para garantir compatibilidade com PDF)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calcula as dimensões da imagem para caber na página com proporção correta
            img_width, img_height = img.size
            
            # Calcula o redimensionamento mantendo a proporção
            if img_width > img_height:
                # Imagem em formato paisagem
                scaled_width = page_width - 40  # Margem de 20 pontos de cada lado
                scaled_height = (scaled_width / img_width) * img_height
                
                # Se a altura ainda for maior que a página, redimensiona pela altura
                if scaled_height > page_height - 40:
                    scaled_height = page_height - 40
                    scaled_width = (scaled_height / img_height) * img_width
            else:
                # Imagem em formato retrato
                scaled_height = page_height - 40  # Margem de 20 pontos de cada lado
                scaled_width = (scaled_height / img_height) * img_width
                
                # Se a largura ainda for maior que a página, redimensiona pela largura
                if scaled_width > page_width - 40:
                    scaled_width = page_width - 40
                    scaled_height = (scaled_width / img_width) * img_height
            
            # Centraliza a imagem na página
            x_pos = (page_width - scaled_width) / 2
            y_pos = (page_height - scaled_height) / 2
            
            # Adiciona a imagem ao PDF centralizada na página
            c.drawImage(img_path, x_pos, y_pos, width=scaled_width, height=scaled_height)
            c.showPage()  # Adiciona uma nova página para a próxima imagem
        
        # Salva o documento PDF
        c.save()
        messagebox.showinfo("Sucesso", f"PDF criado com sucesso: {output_pdf}")
        
    except Exception as e:
        handle_error("convert_to_pdf", f"Erro ao converter imagens para PDF: {str(e)}", None)


def dividir_pdf_1(diretorio):
    """
    Divide um PDF em páginas individuais
    
    Args:
        diretorio (str): Caminho do arquivo PDF a ser dividido
    """
    try:
        nome_arquivo = os.path.splitext(os.path.basename(diretorio))[0]
        pasta_saida = os.path.dirname(diretorio)  # Obtém o diretório do arquivo original
        pdf = PdfReader(diretorio)
        
        if len(pdf.pages) == 0:
            messagebox.showinfo("Aviso", "O PDF não contém páginas para dividir.")
            return
        elif len(pdf.pages) == 1:
            messagebox.showinfo("Aviso", "O PDF contém apenas uma página. Nenhuma divisão necessária.")
            return
        else:
            # Para cada página do PDF, cria um novo arquivo PDF com a página única
            for pagina in range(len(pdf.pages)):
                escreve_pdf = PdfWriter()
                escreve_pdf.add_page(pdf.pages[pagina])

                nome_arquivo_saida = '{}_{}.pdf'.format(nome_arquivo, pagina)
                nome_completo_saida = os.path.join(pasta_saida, nome_arquivo_saida)
                
                with open(nome_completo_saida, 'wb') as saida:
                    escreve_pdf.write(saida)
                
                print('Criado: {}'.format(nome_arquivo_saida))
            
            messagebox.showinfo("Sucesso", "Divisão de PDF concluída.")
            
    except PdfStreamError:
        msg_erro = "O arquivo selecionado não é um PDF válido ou está corrompido.\nPor favor, verifique o arquivo e tente novamente."
        handle_error("Dividir PDF", msg_erro, None)
        return
    except PermissionError:
        msg_erro = "O arquivo PDF está sendo utilizado por outro programa.\nFeche o arquivo e tente novamente."
        handle_error("Dividir PDF", msg_erro, None)
        return
    except FileNotFoundError:
        msg_erro = "O arquivo selecionado não foi encontrado.\nVerifique se o arquivo ainda existe no local especificado."
        handle_error("Dividir PDF", msg_erro, None)
        return
    except Exception as e:
        handle_error("Dividir PDF", f": {str(e)}", None)
        return


def reduzir_tamanho_pdf(input_pdf, output_pdf, qualidade_imagem=30, nivel_compressao=7, callback=None, tempo_total=None):
    """
    Reduz o tamanho de um arquivo PDF comprimindo conteúdo e imagens.
    
    Args:
        input_pdf (str): Caminho do arquivo PDF de entrada
        output_pdf (str): Caminho do arquivo PDF de saída
        qualidade_imagem (int): Qualidade das imagens (1-100, padrão: 40)
        nivel_compressao (int): Nível de compressão (1-9, padrão: 9)
    
    Returns:
        bool: True se bem-sucedido, False caso contrário
    """
    import time

    tempo_total = 0

    def log(msg):
        if callback:
            callback(msg)
        else:
            print(msg)

    tempo_inicio = time.time()
    
    try:
        # Cria o writer e clona do reader
        writer = PdfWriter()
        
        # Abre e lê o PDF original
        with open(input_pdf, "rb") as input_file:
            reader = PdfReader(input_file)
            total_pages = len(reader.pages)
            
            # Processa cada página
            for i, page in enumerate(reader.pages):
                log(f"    - Compactando página {i+1}/{total_pages}...")

                # Adiciona a página ao writer PRIMEIRO
                writer.add_page(page)
                
                # Agora processa a página que pertence ao writer
                writer_page = writer.pages[i]

                # Comprime streams de conteúdo
                try:
                    writer_page.compress_content_streams(level=nivel_compressao)
                except Exception as e:
                    handle_error("reduzir_tamanho_pdf", f"Erro ao comprimir página {i+1}: {e}", None)
                
                # Processa imagens na página
                try:
                    if hasattr(writer_page, 'images') and writer_page.images:
                        for img in writer_page.images:
                            try:
                                img.replace(img.image, quality=qualidade_imagem)
                                # Sucesso ao processar imagem, não precisa logar
                            except Exception as e:
                                handle_error("reduzir_tamanho_pdf", f"Erro ao processar imagem na página {i+1}: {e}", None)
                except Exception as e:
                    handle_error("reduzir_tamanho_pdf", f"Erro ao acessar imagens da página {i+1}: {e}", None)
                        
        # Aplica compressão adicional no writer
        try:
            writer.compress_identical_objects()
        except Exception as e:
            handle_error("reduzir_tamanho_pdf", f"Erro ao comprimir objetos idênticos: {e}", None)

        # Salva o arquivo
        with open(output_pdf, "wb") as output_file:
            writer.write(output_file)

        tempo_total = time.time() - tempo_inicio  # Calcula o tempo total
        log(f"- Compactação finalizada.\nTempo de execução: {tempo_total:.2f} segundos")
        # PDF reduzido salvo com sucesso
        return True, tempo_total
        
    except FileNotFoundError:
        msg_erro = f"Arquivo não encontrado: {input_pdf}\nVerifique se o arquivo ainda existe no local especificado."
        log(f"• Erro: {msg_erro}")
        handle_error("Compactar PDF", msg_erro, None)
        return False, 0
    except PdfStreamError:
        msg_erro = "O arquivo selecionado não é um PDF válido ou está corrompido.\nPor favor, verifique o arquivo e tente novamente."
        handle_error("Compactar PDF", msg_erro, None)
        return False, 0
    except PermissionError:
        msg_erro = "O arquivo PDF está sendo utilizado por outro programa.\nFeche o arquivo e tente novamente."
        handle_error("Compactar PDF", msg_erro, None)
        return False, 0
    except Exception as e:
        log(f"• Erro ao compactar o PDF: {e}")
        handle_error("Compactar PDF", f": {e}", None)
        return False, 0


def dividir_pdf_por_tamanho(caminho, caminho_saida, tamanho_mb_maximo=4.4, nome_usuario=None, callback=None):
    """
    Divide um PDF em partes menores baseado no tamanho máximo especificado
    
    Args:
        arquivo_pdf (str): Caminho do arquivo PDF a ser dividido
        tamanho_max_mb (int): Tamanho máximo em MB para cada parte
    """
    import time

    lista_tempo_total = []
    tempo_total = 0
    
    def log(msg):
        if callback:
            callback(msg)
        else:
            print(msg)
    
    try:
        mensagem_final = []
        log_tempo = []  # Lista para armazenar dados de tempo

        # Determinar o caminho da pasta temporária na pasta Documentos
        temp_folder = os.path.join(os.path.expanduser('~'), 'Documents', 'temp_folder')
        
        # Verifica se a pasta definida na temp_folder existe. Se existir, apaga a mesma antes de seguir com a função
        if os.path.exists(temp_folder):
            # Excluir a pasta temporária
            shutil.rmtree(temp_folder)

        os.makedirs(temp_folder, exist_ok=True)

        # Copiar o arquivo selecionado para a pasta temporária
        caminho_temp = os.path.join(temp_folder, os.path.basename(caminho))
        shutil.copy(caminho, caminho_temp)

        tamanho_sem_compactar = round(os.path.getsize(caminho_temp) / 1048576, 2) # Converte para MB

        # Compactar o arquivo PDF antes de dividir
        log("- Compactando PDF antes de dividir...")
        sucesso_compactacao, tempo_total_compactacao = reduzir_tamanho_pdf(caminho_temp, caminho_temp, callback=log)

        lista_tempo_total.append(tempo_total_compactacao)

        if not sucesso_compactacao:
            # Excluir a pasta temporária criada
            if os.path.exists(temp_folder):
                shutil.rmtree(temp_folder)
                log("• Erro ao compactar o PDF. A pasta temporária foi excluída.")
                print("Erro", "Não foi possível compactar o PDF. Verifique o arquivo e tente novamente.")
            return

        tamanho_compactado = round(os.path.getsize(caminho_temp) / 1048576, 2)  # Converte para MB

        log("- Iniciando divisão do PDF...")

        if tamanho_compactado > 4.9:
            # Atualizar o caminho para o arquivo temporário copiado
            leitor_pdf = PdfReader(caminho_temp)
            total_pages = len(leitor_pdf.pages)

            num_contagem = 1
            current_writer = PdfWriter()
            temp_caminho = os.path.join(temp_folder, "temp.pdf")

            def save_current_part():
                nonlocal num_contagem, current_writer, temp_caminho

                if len(current_writer.pages) > 0:
                    nome_arquivo_base = os.path.splitext(os.path.basename(caminho))[0]
                    output_file_name = f"PT{num_contagem:02} {nome_arquivo_base}.pdf"
                    output_caminho = os.path.join(temp_folder, output_file_name)
                    
                    # Escrever diretamente no arquivo final ao invés de usar arquivo temporário
                    with open(output_caminho, "wb") as output_file:
                        current_writer.write(output_file)
                    
                    current_size_mb = os.path.getsize(output_caminho) / 1048576
                    log(f"    - {output_file_name} criado com {len(current_writer.pages)} páginas, tamanho: {current_size_mb:.2f} MB")
                    mensagem_final.append(f"{output_file_name} criado com {len(current_writer.pages)} páginas, tamanho: {current_size_mb:.2f} MB\n")
                    
                    num_contagem += 1
                    current_writer = PdfWriter()
            
            tempo_inicio_pdf = time.time()  # Início do processamento da página

            for i in range(total_pages):
                log(f"    - Dividindo página {i+1}/{total_pages}...")
                current_writer.add_page(leitor_pdf.pages[i])

                # Salva a parte atual temporariamente e verifica o tamanho do arquivo
                if len(current_writer.pages) >= 1:
                    current_writer.write(temp_caminho)
                    current_size_mb = os.path.getsize(temp_caminho) / 1048576
                    if current_size_mb >= tamanho_mb_maximo:
                        log(f"    - Tamanho excedido: {current_size_mb:.2f} MB, salvando parte {num_contagem}")
                        save_current_part()

                        tempo_pdf = time.time() - tempo_inicio_pdf  # Tempo gasto para processar o arquivo PDF
                        lista_tempo_total.append(tempo_pdf)
                
                        log_msg = f"    - PDF {num_contagem-1}: {tempo_pdf:.2f} segundos"
                        log(log_msg)
                        log_tempo.append(log_msg)

                        tempo_inicio_pdf = time.time()  # reinicia contagem para próxima parte

            # Salva a última parte, se houver páginas restantes
            if len(current_writer.pages) > 0:
                tempo_inicio_pdf = time.time()  # Início do processamento da página
                log(f"    - Salvando última parte {num_contagem} com {len(current_writer.pages)} páginas")
                save_current_part()
                tempo_pdf = time.time() - tempo_inicio_pdf  # Tempo gasto para processar o arquivo PDF
                lista_tempo_total.append(tempo_pdf)

                tempo_total = 0
                for tempo in lista_tempo_total:
                    tempo_total += tempo

                print(f"Tempo total = {tempo_total}")

                log_msg = f"    - PDF {num_contagem-1}: {tempo_pdf:.2f} segundos"
                log(log_msg)
                log_tempo.append(log_msg)

            log(f"- Tempo total gasto para dividir o PDF: {tempo_total:.2f} segundos")

            # Mover os arquivos gerados de volta para a pasta original
            for file_name in os.listdir(temp_folder):
                if file_name.startswith("PT"):
                    log(f"- Movendo arquivo {file_name} para {caminho_saida}")
                    shutil.move(os.path.join(temp_folder, file_name), caminho_saida)

            # Excluir a pasta temporária
            log("- Excluindo pasta temporária: " + temp_folder)
            shutil.rmtree(temp_folder)

            TEMPO_MINIMO_LOG = 120
            # Após processar todas as partes
            if log_tempo and tempo_total >= TEMPO_MINIMO_LOG:  # Se houve operações de tempo registradas
                log_tempo.append(f"Tempo total: {tempo_total:.2f} segundos")
                log_tempo.append(f"Arquivo original: {os.path.basename(caminho)}")
                log_tempo.append(f"Quantidade de páginas: {total_pages}")
                log_tempo.append(f"Tamanho original: {tamanho_sem_compactar:.2f} MB")
                log_tempo.append(f"Tamanho após compactação: {tamanho_compactado:.2f} MB")
                
                # Exporta o log
                log_path = exportar_log_tempo(nome_usuario, log_tempo)
                if log_path:
                    mensagem_final.append(f"Log de tempo salvo em:\n{log_path}")

            # Calculando a redução de tamanho em KB e em porcentagem
            reducao_tamanho_mb = (tamanho_sem_compactar - tamanho_compactado)
            percentual_reducao = ((tamanho_sem_compactar - tamanho_compactado) / tamanho_sem_compactar) * 100

            # Organizando a mensagem
            informacao_compactacao = [
                "Informações sobre a compactação do arquivo:",
                f"Tamanho original: {tamanho_sem_compactar:.2f} MB",
                f"Tamanho após compactação: {tamanho_compactado:.2f} MB",
                f"Redução de tamanho: {reducao_tamanho_mb:.2f} MB ({percentual_reducao:.2f}%)"
                f"\nTempo total para dividir o PDF: {tempo_total:.2f} segundos"
            ]

            messagebox.showinfo("Sucesso", f"Compactação e divisão de PDF concluída.\n\n{'\n'.join(mensagem_final)}\n\n{'\n'.join(informacao_compactacao)}")

        else:
            if os.path.exists(caminho):
                os.remove(caminho)

            # Mover os arquivos gerados de volta para a pasta original
            for file_name in os.listdir(temp_folder):
                shutil.move(os.path.join(temp_folder, file_name), caminho_saida)

            # Excluir a pasta temporária
            shutil.rmtree(temp_folder)

            # Calculando a redução de tamanho em KB e em porcentagem
            reducao_tamanho_mb = (tamanho_sem_compactar - tamanho_compactado)
            percentual_reducao = ((tamanho_sem_compactar - tamanho_compactado) / tamanho_sem_compactar) * 100

            # Organizando a mensagem
            mensagem_final = [
                f"Tamanho original: {tamanho_sem_compactar:.2f} MB",
                f"Tamanho após compactação: {tamanho_compactado:.2f} MB",
                f"Redução de tamanho: {reducao_tamanho_mb:.2f} MB ({percentual_reducao:.2f}%)"
            ]

            messagebox.showinfo("Sucesso", f"Compressão de PDF concluída.\n\n{'\n'.join(mensagem_final)}")
    
    except PdfStreamError:
        msg_erro = "O arquivo selecionado não é um PDF válido ou está corrompido.\nPor favor, verifique o arquivo e tente novamente."
        handle_error("Dividir PDF por Tamanho", msg_erro, None)
        return
    except PermissionError:
        msg_erro = "O arquivo PDF está sendo utilizado por outro programa.\nFeche o arquivo e tente novamente."
        handle_error("Dividir PDF por Tamanho", msg_erro, None)
        return
    except FileNotFoundError:
        msg_erro = "O arquivo selecionado não foi encontrado.\nVerifique se o arquivo ainda existe no local especificado."
        handle_error("Dividir PDF por Tamanho", msg_erro, None)
        return
    except Exception as e:
        handle_error("Dividir PDF por Tamanho", f": {str(e)}", None)
        return


def selecionar_arquivo_pdf(caminho_inicial: str = ""):
    """
    Abre um diálogo para selecionar um arquivo PDF
    
    Args:
        caminho_inicial (str): Diretório inicial para o diálogo
    
    Returns:
        str: Caminho do arquivo selecionado ou None se cancelado
    """
    arquivo = filedialog.askopenfilename(
        title="Selecione o arquivo PDF", 
        initialdir=caminho_inicial, 
        filetypes=[("PDF files", "*.pdf")]
    )
    return arquivo if arquivo else None