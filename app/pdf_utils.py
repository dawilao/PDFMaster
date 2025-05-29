import os
from tkinter import filedialog, messagebox
from PIL import Image
import glob


import os
import glob
from tkinter import messagebox
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

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
            messagebox.showerror("Erro", "Não há arquivos válidos para inclusão no PDF.")
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
        messagebox.showerror("Erro", f"Erro ao converter imagens para PDF: {str(e)}")


def dividir_pdf_1(arquivo_pdf):
    """
    Divide um PDF em páginas individuais
    
    Args:
        arquivo_pdf (str): Caminho do arquivo PDF a ser dividido
    """
    try:
        nome_arquivo = os.path.splitext(os.path.basename(diretorio))[0]
        pasta_saida = os.path.dirname(diretorio)  # Obtém o diretório do arquivo original
        pdf = PdfReader(diretorio)
        
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
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao dividir PDF: {str(e)}")


def reduzir_tamanho_pdf(input_pdf, output_pdf):
    writer = PdfWriter(clone_from=input_pdf)

    for page in writer.pages:
        page.compress_content_streams(level=7)

        for img in page.images:
            img.replace(img.image, quality=40)
            print("Imagem atual: ", img)

    with open(output_pdf, "wb") as f:
        writer.write(f)


def dividir_pdf_por_tamanho(arquivo_pdf, tamanho_max_mb=5):
    """
    Divide um PDF em partes menores baseado no tamanho máximo especificado
    
    Args:
        arquivo_pdf (str): Caminho do arquivo PDF a ser dividido
        tamanho_max_mb (int): Tamanho máximo em MB para cada parte
    """
    try:
        mensagem_final = []

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
        reduzir_tamanho_pdf(caminho_temp, caminho_temp)

        tamanho_compactado = round(os.path.getsize(caminho_temp) / 1048576, 2)  # Converte para MB

        if tamanho_compactado > 4.9:
            # Atualizar o caminho para o arquivo temporário copiado
            leitor_pdf = PdfReader(caminho_temp)
            total_pages = len(leitor_pdf.pages)

            num_contagem = 1
            current_writer = PdfWriter()
            temp_caminho = os.path.join(temp_folder, "temp.pdf")

            def save_current_part():
                nonlocal num_contagem, current_writer, temp_caminho

                nome_arquivo = os.path.basename(caminho)

                if len(current_writer.pages) > 0:
                    with open(temp_caminho, "wb") as temp_file:
                        current_writer.write(temp_file)
                    nome_arquivo_base = os.path.splitext(os.path.basename(caminho))[0]
                    current_size_mb = os.path.getsize(temp_caminho) / 1048576
                    output_file_name = f"PT{num_contagem:02} {nome_arquivo_base}.pdf"
                    output_caminho = os.path.join(temp_folder, output_file_name)
                    os.rename(temp_caminho, output_caminho)
                    print(f"{output_file_name} criado com {len(current_writer.pages)} páginas, tamanho: {current_size_mb:.2f} MB")
                    mensagem_final.append(f"{output_file_name} criado com {len(current_writer.pages)} páginas, tamanho: {current_size_mb:.2f} MB\n")
                    num_contagem += 1
                    current_writer = PdfWriter()

            for i in range(total_pages):
                current_writer.add_page(leitor_pdf.pages[i])

                # Salva a parte atual temporariamente e verifica o tamanho do arquivo
                if len(current_writer.pages) >= 1:
                    current_writer.write(temp_caminho)
                    current_size_mb = os.path.getsize(temp_caminho) / 1048576
                    if current_size_mb >= tamanho_mb_maximo:
                        save_current_part()

            # Salva a última parte, se houver páginas restantes
            if len(current_writer.pages) > 0:
                save_current_part()

            # Mover os arquivos gerados de volta para a pasta original
            for file_name in os.listdir(temp_folder):
                if file_name.startswith("PT"):
                    shutil.move(os.path.join(temp_folder, file_name), caminho_saida)

            # Excluir a pasta temporária
            shutil.rmtree(temp_folder)

            # Calculando a redução de tamanho em KB e em porcentagem
            reducao_tamanho_mb = (tamanho_sem_compactar - tamanho_compactado)
            percentual_reducao = ((tamanho_sem_compactar - tamanho_compactado) / tamanho_sem_compactar) * 100

            # Organizando a mensagem
            informacao_compactacao = [
                "Informações sobre a compactação do arquivo:",
                f"Tamanho original: {tamanho_sem_compactar:.2f} MB",
                f"Tamanho após compactação: {tamanho_compactado:.2f} MB",
                f"Redução de tamanho: {reducao_tamanho_mb:.2f} MB ({percentual_reducao:.2f}%)"
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
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao dividir PDF por tamanho: {str(e)}")


def selecionar_arquivo_pdf(caminho_inicial=""):
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