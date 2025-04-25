#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para envio de e-mails com credenciais de acesso
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/email.log',
    filemode='a'
)
logger = logging.getLogger('email_sender')

class EmailSender:
    """Classe para envio de e-mails com credenciais de acesso"""
    
    def __init__(self, smtp_server=None, smtp_port=None, smtp_user=None, smtp_password=None):
        """Inicializa o serviço de e-mail"""
        # Em produção, essas informações seriam armazenadas de forma segura
        self.smtp_server = smtp_server or os.environ.get('SMTP_SERVER', 'smtp.example.com')
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', 587))
        self.smtp_user = smtp_user or os.environ.get('SMTP_USER', 'noreply@example.com')
        self.smtp_password = smtp_password or os.environ.get('SMTP_PASSWORD', 'password')
        self.sender_email = self.smtp_user
        self.sender_name = "Gerador de Jogos da Lotofácil"
    
    def send_credentials_email(self, user_data):
        """
        Envia e-mail com credenciais de acesso
        
        Args:
            user_data (dict): Dados do usuário
            
        Returns:
            bool: True se o e-mail foi enviado com sucesso, False caso contrário
        """
        try:
            # Destinatário
            recipient_email = user_data['email']
            recipient_name = user_data['name']
            
            # Assunto
            subject = "Suas credenciais de acesso - Gerador de Jogos da Lotofácil"
            
            # Corpo do e-mail
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #000; color: #33ff33; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .credentials {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-left: 4px solid #33ff33; }}
                    .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
                    .button {{ display: inline-block; background-color: #33ff33; color: #000; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Gerador de Jogos da Lotofácil</h1>
                    </div>
                    <div class="content">
                        <p>Olá <strong>{recipient_name}</strong>,</p>
                        
                        <p>Obrigado por assinar o Gerador de Jogos da Lotofácil! Seu pagamento foi confirmado com sucesso.</p>
                        
                        <p>Abaixo estão suas credenciais de acesso:</p>
                        
                        <div class="credentials">
                            <p><strong>E-mail:</strong> {user_data['email']}</p>
                            <p><strong>Senha:</strong> {user_data['password']}</p>
                            <p><strong>Plano:</strong> {user_data['plan_type'].capitalize()}</p>
                            <p><strong>Validade:</strong> {user_data['subscription_end'].split('T')[0]}</p>
                        </div>
                        
                        <p>Para acessar sua conta, clique no botão abaixo:</p>
                        
                        <p style="text-align: center;">
                            <a href="https://gerador-lotofacil.com.br/login" class="button">Acessar Minha Conta</a>
                        </p>
                        
                        <p>Se o botão acima não funcionar, copie e cole o seguinte link em seu navegador:</p>
                        <p>https://gerador-lotofacil.com.br/login</p>
                        
                        <p>Esperamos que você tenha uma excelente experiência com nossa plataforma e consiga aumentar suas chances de ganhar na Lotofácil!</p>
                        
                        <p>Atenciosamente,<br>Equipe Gerador de Jogos da Lotofácil</p>
                    </div>
                    <div class="footer">
                        <p>Este é um e-mail automático. Por favor, não responda.</p>
                        <p>© 2025 Gerador de Jogos da Lotofácil. Todos os direitos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Versão em texto simples
            text_content = f"""
            Olá {recipient_name},
            
            Obrigado por assinar o Gerador de Jogos da Lotofácil! Seu pagamento foi confirmado com sucesso.
            
            Abaixo estão suas credenciais de acesso:
            
            E-mail: {user_data['email']}
            Senha: {user_data['password']}
            Plano: {user_data['plan_type'].capitalize()}
            Validade: {user_data['subscription_end'].split('T')[0]}
            
            Para acessar sua conta, visite: https://gerador-lotofacil.com.br/login
            
            Esperamos que você tenha uma excelente experiência com nossa plataforma e consiga aumentar suas chances de ganhar na Lotofácil!
            
            Atenciosamente,
            Equipe Gerador de Jogos da Lotofácil
            
            Este é um e-mail automático. Por favor, não responda.
            © 2025 Gerador de Jogos da Lotofácil. Todos os direitos reservados.
            """
            
            # Em um ambiente real, enviaríamos o e-mail via SMTP
            # Aqui estamos simulando o envio
            
            # Criar diretório para e-mails simulados
            os.makedirs('/home/ubuntu/lotofacil/data/emails', exist_ok=True)
            
            # Salvar e-mail em arquivo para simulação
            email_data = {
                "to": recipient_email,
                "from": self.sender_email,
                "subject": subject,
                "html_content": html_content,
                "text_content": text_content,
                "sent_at": datetime.now().isoformat()
            }
            
            file_path = f'/home/ubuntu/lotofacil/data/emails/{recipient_email.replace("@", "_").replace(".", "_")}_credentials.json'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(email_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"E-mail com credenciais simulado para {recipient_email}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail para {user_data['email']}: {str(e)}")
            return False
    
    def send_payment_confirmation_email(self, user_data, payment_data):
        """
        Envia e-mail de confirmação de pagamento
        
        Args:
            user_data (dict): Dados do usuário
            payment_data (dict): Dados do pagamento
            
        Returns:
            bool: True se o e-mail foi enviado com sucesso, False caso contrário
        """
        try:
            # Destinatário
            recipient_email = user_data['email']
            recipient_name = user_data['name']
            
            # Assunto
            subject = "Confirmação de Pagamento - Gerador de Jogos da Lotofácil"
            
            # Corpo do e-mail
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #000; color: #33ff33; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .payment-info {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-left: 4px solid #33ff33; }}
                    .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Gerador de Jogos da Lotofácil</h1>
                    </div>
                    <div class="content">
                        <p>Olá <strong>{recipient_name}</strong>,</p>
                        
                        <p>Recebemos seu pagamento com sucesso! Obrigado por assinar o Gerador de Jogos da Lotofácil.</p>
                        
                        <div class="payment-info">
                            <p><strong>ID do Pagamento:</strong> {payment_data['id']}</p>
                            <p><strong>Valor:</strong> R$ {payment_data['transaction_amount']:.2f}</p>
                            <p><strong>Data:</strong> {payment_data['date_created'].split('T')[0]}</p>
                            <p><strong>Plano:</strong> {user_data['plan_type'].capitalize()}</p>
                        </div>
                        
                        <p>Em breve você receberá outro e-mail com suas credenciais de acesso à plataforma.</p>
                        
                        <p>Atenciosamente,<br>Equipe Gerador de Jogos da Lotofácil</p>
                    </div>
                    <div class="footer">
                        <p>Este é um e-mail automático. Por favor, não responda.</p>
                        <p>© 2025 Gerador de Jogos da Lotofácil. Todos os direitos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Versão em texto simples
            text_content = f"""
            Olá {recipient_name},
            
            Recebemos seu pagamento com sucesso! Obrigado por assinar o Gerador de Jogos da Lotofácil.
            
            ID do Pagamento: {payment_data['id']}
            Valor: R$ {payment_data['transaction_amount']:.2f}
            Data: {payment_data['date_created'].split('T')[0]}
            Plano: {user_data['plan_type'].capitalize()}
            
            Em breve você receberá outro e-mail com suas credenciais de acesso à plataforma.
            
            Atenciosamente,
            Equipe Gerador de Jogos da Lotofácil
            
            Este é um e-mail automático. Por favor, não responda.
            © 2025 Gerador de Jogos da Lotofácil. Todos os direitos reservados.
            """
            
            # Em um ambiente real, enviaríamos o e-mail via SMTP
            # Aqui estamos simulando o envio
            
            # Criar diretório para e-mails simulados
            os.makedirs('/home/ubuntu/lotofacil/data/emails', exist_ok=True)
            
            # Salvar e-mail em arquivo para simulação
            email_data = {
                "to": recipient_email,
                "from": self.sender_email,
                "subject": subject,
                "html_content": html_content,
                "text_content": text_content,
                "sent_at": datetime.now().isoformat()
            }
            
            file_path = f'/home/ubuntu/lotofacil/data/emails/{recipient_email.replace("@", "_").replace(".", "_")}_payment.json'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(email_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"E-mail de confirmação de pagamento simulado para {recipient_email}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail para {user_data['email']}: {str(e)}")
            return False

# Função para testar o envio de e-mails
def test_email_sender():
    """Testa o envio de e-mails"""
    # Criar diretórios necessários
    os.makedirs('/home/ubuntu/lotofacil/logs', exist_ok=True)
    os.makedirs('/home/ubuntu/lotofacil/data/emails', exist_ok=True)
    
    # Inicializar serviço de e-mail
    email_sender = EmailSender()
    
    # Dados de teste
    user_data = {
        "email": "usuario@teste.com",
        "name": "Usuário Teste",
        "password": "senha123",
        "plan_type": "premium",
        "subscription_start": datetime.now().isoformat(),
        "subscription_end": (datetime.now().replace(month=datetime.now().month + 1)).isoformat(),
        "status": "active"
    }
    
    payment_data = {
        "id": "test_payment_123",
        "status": "approved",
        "date_created": datetime.now().isoformat(),
        "transaction_amount": 69.90
    }
    
    # Enviar e-mail de confirmação de pagamento
    payment_email_sent = email_sender.send_payment_confirmation_email(user_data, payment_data)
    print(f"E-mail de confirmação de pagamento enviado: {payment_email_sent}")
    
    # Enviar e-mail com credenciais
    credentials_email_sent = email_sender.send_credentials_email(user_data)
    print(f"E-mail com credenciais enviado: {credentials_email_sent}")
    
    return payment_email_sent and credentials_email_sent

if __name__ == "__main__":
    test_email_sender()
