#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de integração com o Mercado Pago para pagamentos via PIX
para o Gerador de Jogos da Lotofácil
"""

import os
import json
import requests
import base64
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
import hashlib
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/pagamento.log',
    filemode='a'
)
logger = logging.getLogger('mercadopago_integration')

class MercadoPagoIntegration:
    """Classe para integração com a API do Mercado Pago para pagamentos via PIX"""
    
    def __init__(self, access_token=None):
        """Inicializa a integração com o Mercado Pago"""
        # Em produção, o token seria armazenado de forma segura e não hardcoded
        self.access_token = access_token or os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
        self.api_base_url = "https://api.mercadopago.com/v1"
        self.pix_key = "42f51e7f-7586-4f26-a5b2-837ef34a0bfb"  # Chave PIX fornecida pelo usuário
        
    def _make_request(self, method, endpoint, data=None, params=None):
        """Realiza uma requisição para a API do Mercado Pago"""
        url = f"{self.api_base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para {url}: {str(e)}")
            return {"error": str(e)}
    
    def create_payment(self, user_data, plan_type):
        """
        Cria um pagamento via PIX
        
        Args:
            user_data (dict): Dados do usuário (nome, email, etc.)
            plan_type (str): Tipo de plano ('basic' ou 'premium')
            
        Returns:
            dict: Dados do pagamento, incluindo QR Code e informações para pagamento
        """
        # Determinar valor com base no plano
        amount = 69.90 if plan_type == 'premium' else 39.90
        
        # Gerar ID de referência único
        reference_id = self._generate_reference_id(user_data['email'])
        
        # Em um ambiente real, faríamos uma chamada à API do Mercado Pago
        # Como estamos simulando, vamos criar os dados do pagamento manualmente
        
        # Simular resposta da API
        payment_data = {
            "id": reference_id,
            "status": "pending",
            "date_created": datetime.now().isoformat(),
            "date_expiration": (datetime.now() + timedelta(hours=24)).isoformat(),
            "transaction_amount": amount,
            "description": f"Assinatura {plan_type.capitalize()} - Gerador de Jogos da Lotofácil",
            "payer": {
                "email": user_data['email'],
                "first_name": user_data['name'].split()[0],
                "last_name": " ".join(user_data['name'].split()[1:]) if len(user_data['name'].split()) > 1 else ""
            },
            "point_of_interaction": {
                "transaction_data": {
                    "qr_code": self._generate_pix_qr_code(amount, reference_id, user_data),
                    "qr_code_base64": self._generate_qr_code_base64(amount, reference_id, user_data),
                    "ticket_url": f"https://www.mercadopago.com.br/payments/{reference_id}"
                }
            }
        }
        
        # Salvar dados do pagamento no banco de dados
        self._save_payment_data(payment_data, user_data, plan_type)
        
        return payment_data
    
    def _generate_reference_id(self, email):
        """Gera um ID de referência único para o pagamento"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_input = f"{email}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _generate_pix_qr_code(self, amount, reference_id, user_data):
        """
        Gera o código PIX para pagamento
        
        Em um ambiente real, isso seria feito pela API do Mercado Pago.
        Aqui estamos simulando o formato do PIX Copia e Cola.
        """
        # Simulação de um código PIX (em produção, seria gerado pela API)
        return f"00020126580014br.gov.bcb.pix0136{self.pix_key}5204000053039865802BR5923Gerador Jogos Lotofacil6009SAO PAULO62290525{reference_id}6304{self._calculate_crc16(amount, reference_id)}"
    
    def _generate_qr_code_base64(self, amount, reference_id, user_data):
        """Gera o QR Code em formato base64 para exibição"""
        pix_code = self._generate_pix_qr_code(amount, reference_id, user_data)
        
        # Gerar QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(pix_code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter para base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def _calculate_crc16(self, amount, reference_id):
        """
        Calcula o CRC16 para o código PIX
        
        Em um ambiente real, isso seria feito pela API do Mercado Pago.
        Aqui estamos apenas simulando um valor.
        """
        # Simulação de um CRC16 (em produção, seria calculado corretamente)
        return "A123"
    
    def _save_payment_data(self, payment_data, user_data, plan_type):
        """
        Salva os dados do pagamento no banco de dados
        
        Em um ambiente real, isso seria feito em um banco de dados.
        Aqui estamos salvando em um arquivo JSON para simulação.
        """
        # Criar diretório de dados se não existir
        os.makedirs('/home/ubuntu/lotofacil/data/pagamentos', exist_ok=True)
        
        # Dados a serem salvos
        data_to_save = {
            "payment_id": payment_data["id"],
            "user_email": user_data["email"],
            "user_name": user_data["name"],
            "plan_type": plan_type,
            "amount": payment_data["transaction_amount"],
            "status": payment_data["status"],
            "date_created": payment_data["date_created"],
            "date_expiration": payment_data["date_expiration"]
        }
        
        # Salvar em arquivo JSON
        file_path = f'/home/ubuntu/lotofacil/data/pagamentos/{payment_data["id"]}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Dados do pagamento {payment_data['id']} salvos com sucesso")
        
        return True
    
    def check_payment_status(self, payment_id):
        """
        Verifica o status de um pagamento
        
        Args:
            payment_id (str): ID do pagamento
            
        Returns:
            dict: Status do pagamento
        """
        # Em um ambiente real, faríamos uma chamada à API do Mercado Pago
        # Como estamos simulando, vamos verificar o arquivo JSON
        
        file_path = f'/home/ubuntu/lotofacil/data/pagamentos/{payment_id}.json'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                payment_data = json.load(f)
            
            # Simulação de verificação de status
            # Em um ambiente real, o status seria atualizado pela API do Mercado Pago
            # Aqui estamos simulando uma chance de 20% de o pagamento ter sido aprovado
            import random
            if random.random() < 0.2:
                payment_data["status"] = "approved"
                
                # Atualizar arquivo JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(payment_data, f, ensure_ascii=False, indent=4)
                
                # Se aprovado, criar credenciais de acesso
                if payment_data["status"] == "approved":
                    self._create_user_credentials(payment_data)
            
            return {
                "payment_id": payment_id,
                "status": payment_data["status"],
                "plan_type": payment_data["plan_type"],
                "user_email": payment_data["user_email"]
            }
        except FileNotFoundError:
            logger.error(f"Pagamento {payment_id} não encontrado")
            return {"error": "Pagamento não encontrado"}
        except Exception as e:
            logger.error(f"Erro ao verificar status do pagamento {payment_id}: {str(e)}")
            return {"error": str(e)}
    
    def _create_user_credentials(self, payment_data):
        """
        Cria credenciais de acesso para o usuário após pagamento aprovado
        
        Args:
            payment_data (dict): Dados do pagamento
            
        Returns:
            dict: Credenciais de acesso
        """
        # Gerar senha aleatória
        password = self._generate_random_password()
        
        # Dados do usuário
        user_data = {
            "email": payment_data["user_email"],
            "name": payment_data["user_name"],
            "password": password,  # Em produção, seria armazenado o hash da senha
            "plan_type": payment_data["plan_type"],
            "subscription_start": datetime.now().isoformat(),
            "subscription_end": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "active"
        }
        
        # Salvar dados do usuário
        os.makedirs('/home/ubuntu/lotofacil/data/usuarios', exist_ok=True)
        file_path = f'/home/ubuntu/lotofacil/data/usuarios/{payment_data["user_email"].replace("@", "_").replace(".", "_")}.json'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Credenciais criadas para o usuário {payment_data['user_email']}")
        
        # Enviar e-mail com credenciais
        self._send_credentials_email(user_data)
        
        return {
            "email": user_data["email"],
            "password": password
        }
    
    def _generate_random_password(self, length=10):
        """Gera uma senha aleatória"""
        import random
        import string
        
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))
    
    def _send_credentials_email(self, user_data):
        """
        Envia e-mail com credenciais de acesso
        
        Em um ambiente real, isso seria feito por um serviço de e-mail.
        Aqui estamos apenas simulando o envio.
        """
        # Simular envio de e-mail
        email_content = f"""
        Olá {user_data['name']},
        
        Obrigado por assinar o Gerador de Jogos da Lotofácil!
        
        Suas credenciais de acesso:
        E-mail: {user_data['email']}
        Senha: {user_data['password']}
        
        Plano: {user_data['plan_type'].capitalize()}
        Validade: {user_data['subscription_end']}
        
        Acesse agora mesmo: https://gerador-lotofacil.com.br/login
        
        Atenciosamente,
        Equipe Gerador de Jogos da Lotofácil
        """
        
        # Salvar e-mail em arquivo para simulação
        os.makedirs('/home/ubuntu/lotofacil/data/emails', exist_ok=True)
        file_path = f'/home/ubuntu/lotofacil/data/emails/{user_data["email"].replace("@", "_").replace(".", "_")}.txt'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(email_content)
        
        logger.info(f"E-mail com credenciais enviado para {user_data['email']}")
        
        return True


# Função para testar a integração
def test_integration():
    """Testa a integração com o Mercado Pago"""
    mp = MercadoPagoIntegration()
    
    # Dados de teste
    user_data = {
        "name": "Usuário Teste",
        "email": "usuario@teste.com",
        "phone": "11999999999"
    }
    
    # Criar pagamento
    payment_data = mp.create_payment(user_data, "premium")
    print(f"Pagamento criado: {payment_data['id']}")
    
    # Verificar status
    status = mp.check_payment_status(payment_data['id'])
    print(f"Status do pagamento: {status['status']}")
    
    return payment_data


if __name__ == "__main__":
    # Criar diretórios necessários
    os.makedirs('/home/ubuntu/lotofacil/logs', exist_ok=True)
    os.makedirs('/home/ubuntu/lotofacil/data/pagamentos', exist_ok=True)
    os.makedirs('/home/ubuntu/lotofacil/data/usuarios', exist_ok=True)
    os.makedirs('/home/ubuntu/lotofacil/data/emails', exist_ok=True)
    
    # Testar integração
    test_integration()
