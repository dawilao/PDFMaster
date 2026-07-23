import io
import shutil
import os
import glob
import time
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

            # Abre a imagem apenas para obter as dimensões
            # (reportlab reabre o arquivo por conta própria via img_path)
            with Image.open(img_path) as img:
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


def reduzir_tamanho_pdf(input_pdf, output_pdf, qualidade_imagem=30, nivel_compressao=7,
                         max_dimensao_imagem=1080, callback=None):
    """
    Reduz o tamanho de um arquivo PDF comprimindo conteúdo e imagens.

    Args:
        input_pdf (str): Caminho do arquivo PDF de entrada
        output_pdf (str): Caminho do arquivo PDF de saída
        qualidade_imagem (int): Qualidade JPEG das imagens (1-100, padrão: 30)
        nivel_compressao (int): Nível de compressão zlib dos content streams (1-9, padrão: 7)
        max_dimensao_imagem (int): Dimensão máxima das imagens em pixels (0 = sem limite, padrão: 1080)

    Returns:
        tuple[bool, float]: (sucesso, tempo_em_segundos)
    """
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

        # Rastreia objetos de imagem já processados pelo indirect_reference.
        # PDFs frequentemente compartilham o mesmo XObject de imagem entre páginas
        # (ex: logotipo, fundo). Sem este controle, a mesma imagem seria re-codificada
        # em JPEG com perda a cada página que a referenciar, acumulando degradação.
        imagens_processadas: set = set()

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

                # Comprime streams de conteúdo (texto, vetores)
                try:
                    writer_page.compress_content_streams(level=nivel_compressao)
                except Exception as e:
                    handle_error("reduzir_tamanho_pdf", f"Erro ao comprimir página {i+1}: {e}", None)

                # Comprime imagens da página (pulando as já processadas em outras páginas)
                try:
                    if hasattr(writer_page, 'images') and writer_page.images:
                        for img in writer_page.images:
                            try:
                                # Identificador único do objeto PDF no writer
                                ref = getattr(img, 'indirect_reference', None)
                                ref_key = (ref.idnum, ref.generation) if ref else None

                                if ref_key is not None and ref_key in imagens_processadas:
                                    continue  # Imagem compartilhada, já comprimida
                                if ref_key is not None:
                                    imagens_processadas.add(ref_key)

                                # Verificar tamanho dos dados brutos ANTES do decode (caro).
                                # O decode JPEG + re-encode custa ~0,1 s por imagem.
                                # Se a imagem já é pequena (≤ 25 KB) e não precisa de
                                # redimensionamento, o ganho de re-encodar é mínimo (~5 KB)
                                # e não justifica o custo.
                                dados_brutos = getattr(img, 'data', None)
                                tamanho_bruto = len(dados_brutos) if dados_brutos is not None else -1

                                if tamanho_bruto >= 0:
                                    # Dimensões via metadados do XObject — sem decode JPEG
                                    xobj = ref.get_object() if ref else None
                                    dim_w = int(xobj.get("/Width", 0)) if xobj else 0
                                    dim_h = int(xobj.get("/Height", 0)) if xobj else 0

                                    precisa_resize = (
                                        max_dimensao_imagem > 0
                                        and dim_w > 0 and dim_h > 0
                                        and max(dim_w, dim_h) > max_dimensao_imagem
                                    )

                                    # Pular apenas quando dimensões são conhecidas,
                                    # não há resize necessário, e imagem já é pequena
                                    if dim_w > 0 and dim_h > 0 and not precisa_resize and tamanho_bruto <= 50_000:
                                        continue

                                pil_img = img.image
                                img_w, img_h = pil_img.size

                                # Redimensiona imagens acima da resolução máxima.
                                # Fotos de relatórios ficam frequentemente em 3000-4000px,
                                # mas são exibidas em miniaturas no PDF. Reduzir a resolução
                                # tem impacto maior na compressão do que só reduzir a qualidade.
                                if max_dimensao_imagem > 0 and max(img_w, img_h) > max_dimensao_imagem:
                                    escala = max_dimensao_imagem / max(img_w, img_h)
                                    novo_w = max(1, int(img_w * escala))
                                    novo_h = max(1, int(img_h * escala))
                                    pil_img = pil_img.resize(
                                        (novo_w, novo_h),
                                        Image.Resampling.BILINEAR
                                    )

                                img.replace(pil_img, quality=qualidade_imagem)
                            except Exception as e:
                                handle_error("reduzir_tamanho_pdf", f"Erro ao processar imagem na página {i+1}: {e}", None)
                except Exception as e:
                    handle_error("reduzir_tamanho_pdf", f"Erro ao acessar imagens da página {i+1}: {e}", None)
                        
        # Aplica compressão adicional no writer
        try:
            writer.compress_identical_objects()
        except Exception as e:
            handle_error("reduzir_tamanho_pdf", f"Erro ao comprimir objetos idênticos: {e}", None)

        # Serializa em memória antes de abrir o arquivo de saída.
        # Isso é seguro mesmo quando input_pdf == output_pdf: o reader
        # já está fechado e todos os streams foram processados nas etapas acima.
        output_buffer = io.BytesIO()
        writer.write(output_buffer)

        with open(output_pdf, "wb") as output_file:
            output_file.write(output_buffer.getvalue())

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


def dividir_pdf_por_tamanho(caminho, caminho_saida, tamanho_mb_maximo=14.7, nome_usuario=None, callback=None):
    """
    Divide um PDF em partes menores baseado no tamanho máximo especificado
    
    Args:
        arquivo_pdf (str): Caminho do arquivo PDF a ser dividido
        tamanho_max_mb (int): Tamanho máximo em MB para cada parte
    """
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

        if tamanho_compactado > 14.9:
            # Atualizar o caminho para o arquivo temporário copiado
            leitor_pdf = PdfReader(caminho_temp)
            total_pages = len(leitor_pdf.pages)

            num_contagem = 1
            current_writer = PdfWriter()
            # Buffer em memória reutilizável para medir o tamanho real a cada página.
            # A medição real por página garante que o split ocorra no momento exato
            # em que o limite é atingido, sem risco de excedê-lo por subestimativa.
            # O overhead de BytesIO (~1-2s para 500+ pág.) é negligenciável frente
            # ao tempo de compressão de imagens, então nenhuma heurística é necessária.
            _size_buf = io.BytesIO()

            def save_current_part():
                nonlocal num_contagem, current_writer

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
            
            # parte_inicio rastreia o índice (0-based) da primeira página da
            # parte atual no leitor_pdf. Usado para reconstruir o writer sem a
            # última página quando uma página sozinha causa overflow.
            parte_inicio = 0
            ultimo_tamanho_mb = 0.0   # último tamanho medido (pode ser stale)
            tempo_inicio_pdf = time.time()

            for i in range(total_pages):
                log(f"    - Dividindo página {i+1}/{total_pages}...")
                current_writer.add_page(leitor_pdf.pages[i])

                # Estratégia adaptativa de medição:
                #   - Abaixo de 80 % do limite → medir a cada 5 páginas (overhead menor)
                #   - Acima de 80 % → medir toda página (precisão para back-out exato)
                #   - Última página do arquivo → sempre medir
                pages_in_part = i - parte_inicio + 1
                near_limit = ultimo_tamanho_mb >= tamanho_mb_maximo * 0.80
                must_measure = near_limit or (pages_in_part % 5 == 0) or (i == total_pages - 1)

                if must_measure:
                    _size_buf.seek(0)
                    _size_buf.truncate()
                    current_writer.write(_size_buf)
                    ultimo_tamanho_mb = _size_buf.tell() / 1048576

                if ultimo_tamanho_mb >= tamanho_mb_maximo:
                    n_pages_now = len(current_writer.pages)

                    if n_pages_now > 1:
                        # Encontrar o corte correto varrendo de trás para frente.
                        # Em modo per-page (near_limit=True) resolve em 1 iteração.
                        # Em modo batch, o writer pode ter ultrapassado o limite há
                        # várias páginas — retroceder até encontrar o ponto correto.
                        cut_at = i

                        while cut_at > parte_inicio:
                            current_writer = PdfWriter()
                            for j in range(parte_inicio, cut_at):
                                current_writer.add_page(leitor_pdf.pages[j])

                            if cut_at == parte_inicio + 1:
                                break  # apenas 1 página restante — salvar assim mesmo

                            _size_buf.seek(0)
                            _size_buf.truncate()
                            current_writer.write(_size_buf)
                            rebuilt_size = _size_buf.tell() / 1048576

                            if rebuilt_size < tamanho_mb_maximo:
                                break  # corte correto encontrado

                            cut_at -= 1  # ainda acima do limite — remover mais uma

                        pages_moved = i - cut_at + 1
                        if pages_moved == 1:
                            log(f"    - Tamanho excedido: {ultimo_tamanho_mb:.2f} MB (página {cut_at + 1} movida à próxima parte), salvando parte {num_contagem}")
                        else:
                            log(f"    - Tamanho excedido: {ultimo_tamanho_mb:.2f} MB ({pages_moved} págs. movidas à próxima parte), salvando parte {num_contagem}")

                        save_current_part()  # salva current_writer e cria novo vazio

                        # Iniciar nova parte com as páginas movidas
                        for m in range(cut_at, i + 1):
                            current_writer.add_page(leitor_pdf.pages[m])
                        parte_inicio = cut_at
                        ultimo_tamanho_mb = 0.0
                    else:
                        # Página única já maior que o limite — salvar assim mesmo
                        log(f"    - Tamanho excedido: {ultimo_tamanho_mb:.2f} MB, salvando parte {num_contagem} (página única acima do limite)")
                        save_current_part()
                        parte_inicio = i + 1
                        ultimo_tamanho_mb = 0.0

                    tempo_pdf = time.time() - tempo_inicio_pdf
                    lista_tempo_total.append(tempo_pdf)
                    log_msg = f"    - PDF {num_contagem-1}: {tempo_pdf:.2f} segundos"
                    log(log_msg)
                    log_tempo.append(log_msg)
                    tempo_inicio_pdf = time.time()

            # Salva a última parte, se houver páginas restantes
            if len(current_writer.pages) > 0:
                log(f"    - Salvando última parte {num_contagem} com {len(current_writer.pages)} páginas")
                save_current_part()
                tempo_pdf = time.time() - tempo_inicio_pdf
                lista_tempo_total.append(tempo_pdf)
                log_msg = f"    - PDF {num_contagem-1}: {tempo_pdf:.2f} segundos"
                log(log_msg)
                log_tempo.append(log_msg)

            _size_buf.close()
            leitor_pdf.close()
            tempo_total = sum(lista_tempo_total)
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