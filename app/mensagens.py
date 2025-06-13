import random
from datetime import datetime

class MensagemInterativa:
    def __init__(self, nome_usuario):
        self.nome_usuario = nome_usuario.split(" ")[0].capitalize()
        self.mensagens_usadas = []
        
        # Cores do CustomTkinter
        self.cores = {
            'sexta': "#00D4AA",      # Verde CustomTkinter (animado)
            'sexta13': "#8B0000",    # Vermelho sangue
            'segunda': "#FF6B35",    # Laranja energético  
            'especial': "#1E88E5",   # Azul destaque
            'natal': "#FF1744",      # Vermelho Natal
            'ano_novo': "#FFD700",   # Dourado Ano Novo
            'halloween': "#FF8F00",  # Laranja Halloween
            'domingo': "#9C27B0",    # Roxo relaxante
            'motivacional': "#4CAF50", # Verde motivação
            'engracada': "#FF5722",  # Laranja vibrante (divertido)
            'normal': None           # Cor padrão do tema
        }
    
    def obter_saudacao_periodo(self):
        """Retorna saudação baseada no período do dia"""
        hora = datetime.now().hour
        
        if 5 <= hora < 12:
            return "Bom dia"
        elif 12 <= hora < 18:
            return "Boa tarde"
        else:
            return "Boa noite"
    
    def obter_dia_semana(self):
        """Retorna o dia da semana atual"""
        dias = {
            0: "segunda-feira",
            1: "terça-feira", 
            2: "quarta-feira",
            3: "quinta-feira",
            4: "sexta-feira",
            5: "sábado",
            6: "domingo"
        }
        return dias[datetime.now().weekday()]
    
    def obter_mensagens_variadas(self):
        """Lista de mensagens variadas para o PDFMaster"""
        mensagens = [
            f"Bem-vindo de volta ao PDFMaster, {self.nome_usuario}!",
            f"Opa {self.nome_usuario}! Vamos trabalhar com PDFs hoje?",
            f"Opa {self.nome_usuario}! O PDFMaster está pronto para você!",
            f"Seja bem-vindo, {self.nome_usuario}! Que tal começarmos?",
            f"Ótimo te ver aqui, {self.nome_usuario}!",
            f"Vamos dominar os PDFs juntos, {self.nome_usuario}!",
            f"Preparado para mais produtividade, {self.nome_usuario}?",
            f"Seus PDFs estão esperando por você, {self.nome_usuario}!",
            f"Hora de organizar documentos, {self.nome_usuario}!",
            f"O mestre dos PDFs chegou! Oi, {self.nome_usuario}!"
        ]
        return mensagens
    
    def obter_mensagens_especiais(self):
        """Mensagens para ocasiões especiais com cores específicas"""
        hoje = datetime.now()
        dia_mes = hoje.day
        mes = hoje.month
        ano = hoje.year

        # Mensagens especiais para datas fixas
        if mes == 1 and dia_mes == 1:
            return f"Feliz Ano Novo, {self.nome_usuario}! Que {ano} seja produtivo!", 'ano_novo'
        elif mes == 12 and dia_mes == 25:
            return f"🎄 Feliz Natal, {self.nome_usuario}! Ho ho ho!", 'natal'
        elif mes == 10 and dia_mes == 31:
            return f"🎃 Feliz Halloween, {self.nome_usuario}! Boo!", 'halloween'
        elif hoje.weekday() == 4 and dia_mes == 13:
            mensagens_sexta = [
                f"Sexta 13, {self.nome_usuario}? O terror aqui é PDF gigante. Relaxa, eu resolvo!",
                f"Sexta-feira 13, {self.nome_usuario}? PDF pesado dá azar. Eu cuido disso!",
                f"Olá, {self.nome_usuario}! PDF pesado na sexta 13? Isso sim é um filme de terror!",
                f"PDF não compactado na Sexta 13, {self.nome_usuario}? Que azar o seu, hein...",
                f"Entre Jason e um PDF não compactado… eu fujo do PDF!\nE você, {self.nome_usuario}?",
                f"Prezado {self.nome_usuario}, evite PDFs assustadores hoje.",
            ]
            return random.choice(mensagens_sexta), 'sexta13'

        # Mensagens especiais para dias da semana (com variações)
        elif hoje.weekday() == 4:  # Sexta-feira
            mensagens_sexta = [
                f"🎉 Sextou, {self.nome_usuario}! Vamos finalizar a semana!",
                f"Finalmente sexta, {self.nome_usuario}! Última jornada da semana!",
                f"⭐ Sexta-feira chegou, {self.nome_usuario}! Bora terminar com chave de ouro!",
                f"🚀 Sexta produtiva, {self.nome_usuario}! Vamos fechar a semana bem!",
                f"😎 É sexta, {self.nome_usuario}! Que tal organizarmos uns PDFs?",
                f"Sextou, {self.nome_usuario}! Bem-vindo ao PDFMaster!",
            ]
            return random.choice(mensagens_sexta), 'sexta'

        elif hoje.weekday() == 0:  # Segunda-feira
            mensagens_segunda = [
                f"🌟 Segunda-feira, {self.nome_usuario}! Vamos começar bem a semana!",
                f"⚡ Nova semana, {self.nome_usuario}! Cheio de energia para começar!",
                f"Segunda chegou, {self.nome_usuario}! Bem-vindo ao PDFMaster!",
                f"☕ Segundou, {self.nome_usuario}! Café e produtividade!",
                f"🚀 Olá, {self.nome_usuario}! Semana nova, novos PDFs para organizar!",
                f"Segundou, {self.nome_usuario}! Bem-vindo ao PDFMaster!",
            ]
            return random.choice(mensagens_segunda), 'segunda'
        
        elif hoje.weekday() == 6:  # Domingo
            mensagens_domingo = [
                f"😊 Domingo relaxante, {self.nome_usuario}! Que tal organizar uns PDFs?",
                f"🏠 Domingo em casa, {self.nome_usuario}! Momento perfeito para organizar!",
                f"Domingo tranquilo, {self.nome_usuario}! Vamos ser produtivos?",
                f"Domingo de organização, {self.nome_usuario}! PDFs esperando por você!",
            ]
            return random.choice(mensagens_domingo), 'domingo'
        
        return None, None
    
    def gerar_mensagem(self):
        """Gera mensagem e retorna a mensagem e cor apropriada"""
        # Primeiro verifica se há mensagem especial
        msg_especial, cor_especial = self.obter_mensagens_especiais()
        if msg_especial:
            return msg_especial, cor_especial
        
        # Se não há mensagem especial, gera uma normal
        saudacao = self.obter_saudacao_periodo()
        dia_semana = self.obter_dia_semana()
        
        # Escolhe o tipo de mensagem aleatoriamente
        tipo_msg = random.choice([
            "periodo_dia",
            "dia_semana", 
            "variada",
            "motivacional",
            "engraçada"
        ])
        
        if tipo_msg == "periodo_dia":
            mensagens = [
                f"{saudacao}, {self.nome_usuario}! Bem-vindo ao PDFMaster!",
                f"{saudacao}, {self.nome_usuario}! O Mestre dos PDFs saúda você!",
                f"{saudacao}, {self.nome_usuario}! Que tal encarar uns PDFs?",
                f"{saudacao}, {self.nome_usuario}! Bora ser produtivo?!",
                f"{saudacao}, {self.nome_usuario}! O PDFMaster está pronto!",
            ]
            cor = 'normal'
        elif tipo_msg == "dia_semana":
            mensagens = [
                f"Boa {dia_semana}, {self.nome_usuario}! Vamos trabalhar?",
                f"Olá {self.nome_usuario}! Boa {dia_semana}!",
                f"Boa {dia_semana}, {self.nome_usuario}! Pronto para o PDFMaster?",
                f"Boa {dia_semana}, {self.nome_usuario}! Vamos começar?",
                f"Boa {dia_semana}, {self.nome_usuario}! Qual missão de hoje?",
                f"E aí, {self.nome_usuario}! {dia_semana} chegou, bora agir!",
                f"Olá, {self.nome_usuario}. Pronto para encarar a {dia_semana} com eficiência?",
            ]
            cor = 'normal'
        elif tipo_msg == "motivacional":
            frases_motivacao = [
                "Vamos ser produtivos hoje!",
                "Que tal organizarmos alguns documentos?",
                "Preparado para dominar os PDFs?",
                "Vamos fazer acontecer!",
                "Mais um dia, mais PDFs!",
                "Cada clique é um passo na produtividade!",
                "PDF em ordem, mente em paz!",
                "Produtividade em alta!",
                "Com PDFMaster e café, nenhum PDF resiste!",
            ]
            frase = random.choice(frases_motivacao)
            mensagens = [f"{saudacao}, {self.nome_usuario}! {frase}"]
            cor = 'motivacional'
        elif tipo_msg == "engracada":
            mensagens = [
                f"Opa {self.nome_usuario}, sabe que horas são? Hora de organizar seus PDFs!",
                f"E aí {self.nome_usuario}! Vim resolver seus B.O.s... de arquivos, claro.",
                f"E aí {self.nome_usuario}! Compactando mais PDFs que café na segunda-feira.",
                f"Saudações, {self.nome_usuario}! O Mestre dos PDFs saúda você!",
                f"E aí, {self.nome_usuario}? Os PDFs não vão se compactar sozinhos!",
            ]
            cor = 'engracada'
        else:  # variada
            mensagens = self.obter_mensagens_variadas()
            cor = 'normal'
        
        # Evita repetir a mesma mensagem seguidas vezes
        mensagens_disponiveis = [m for m in mensagens if m not in self.mensagens_usadas]
        if not mensagens_disponiveis:
            self.mensagens_usadas = []
            mensagens_disponiveis = mensagens
        
        mensagem_escolhida = random.choice(mensagens_disponiveis)
        self.mensagens_usadas.append(mensagem_escolhida)
        
        # Mantém apenas as últimas 5 mensagens no histórico
        if len(self.mensagens_usadas) > 5:
            self.mensagens_usadas = self.mensagens_usadas[-5:]
        
        return mensagem_escolhida, cor
    
    def obter_cor(self, tipo_cor):
        """Retorna a cor hexadecimal para o tipo especificado"""
        return self.cores.get(tipo_cor, None)
