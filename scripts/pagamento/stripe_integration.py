#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de integração com o Stripe para assinaturas
para o Gerador de Jogos da Lotofácil
"""

import os
import json
import stripe
from datetime import datetime, timedelta
import logging
import hashlib
import uuid

# Configuração de logging
import os
# Criar diretório de logs se não existir
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join('logs', 'pagamento.log'),
    filemode='a'
)
logger = logging.getLogger('stripe_integration')

class StripeIntegration:
    """Classe para integração com a API do Stripe para assinaturas"""
    
    def __init__(self, api_key=None):
        """Inicializa a integração com o Stripe"""
        # Em produção, a chave seria armazenada de forma segura e não hardcoded
        self.api_key = api_key or os.environ.get('STRIPE_API_KEY', 'sk_test_51RAaFgCD34s5xyX8rSsSzWIJGgogtxumykcNuxOwsvNAd1Bvq93Zuw1du38Zb96sJmVstt3FWv2ARhRs16QPTYBm00ZjEg3FxN')
        stripe.api_key = self.api_key
        
        # Definição dos planos de assinatura
        self.plans = {
            'basic': {
                'name': 'Básico',
                'price_id': 'price_1OxZ0LKmJJGy8UzVabcdef123',  # ID do preço no Stripe
                'amount': 3990,  # em centavos
                'interval': 'month',
                'description': 'Plano Básico - Gerador de Jogos da Lotofácil'
            },
            'premium': {
                'name': 'Premium',
                'price_id': 'price_1OxZ0YKmJJGy8UzVxyzabc456',  # ID do preço no Stripe
                'amount': 6990,  # em centavos
                'interval': 'month',
                'description': 'Plano Premium - Gerador de Jogos da Lotofácil'
            }
        }
    
    def create_customer(self, user_data):
        """
        Cria um cliente no Stripe
        
        Args:
            user_data (dict): Dados do usuário (nome, email, etc.)
            
        Returns:
            dict: Dados do cliente criado
        """
        try:
            customer = stripe.Customer.create(
                email=user_data['email'],
                name=user_data['name'],
                phone=user_data.get('phone', ''),
                metadata={
                    'source': 'lotofacil_generator'
                }
            )
            
            logger.info(f"Cliente criado no Stripe: {customer.id}")
            return customer
        except Exception as e:
            logger.error(f"Erro ao criar cliente no Stripe: {str(e)}")
            raise
    
    def create_subscription(self, user_data, plan_type):
        """
        Cria uma assinatura no Stripe
        
        Args:
            user_data (dict): Dados do usuário (nome, email, etc.)
            plan_type (str): Tipo de plano ('basic' ou 'premium')
            
        Returns:
            dict: Dados da assinatura, incluindo link de pagamento
        """
        try:
            # Verificar se o plano existe
            if plan_type not in self.plans:
                raise ValueError(f"Plano não encontrado: {plan_type}")
            
            plan = self.plans[plan_type]
            
            # Criar cliente
            customer = self.create_customer(user_data)
            
            # Gerar ID de referência único
            reference_id = self._generate_reference_id(user_data['email'])
            
            # Criar sessão de checkout
            checkout_session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': plan['price_id'],
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url='https://gerador-lotofacil.com.br/pagamento/sucesso?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://gerador-lotofacil.com.br/pagamento/cancelado',
                metadata={
                    'reference_id': reference_id,
                    'plan_type': plan_type,
                    'user_email': user_data['email']
                }
            )
            
            # Preparar dados da assinatura
            subscription_data = {
                "id": reference_id,
                "checkout_session_id": checkout_session.id,
                "customer_id": customer.id,
                "status": "pending",
                "date_created": datetime.now().isoformat(),
                "plan_type": plan_type,
                "amount": plan['amount'] / 100,  # Converter de centavos para reais
                "description": plan['description'],
                "payment_url": checkout_session.url,
                "payer": {
                    "email": user_data['email'],
                    "name": user_data['name'],
                    "phone": user_data.get('phone', '')
                }
            }
            
            # Salvar dados da assinatura
            self._save_subscription_data(subscription_data, user_data, plan_type)
            
            return subscription_data
        except Exception as e:
            logger.error(f"Erro ao criar assinatura no Stripe: {str(e)}")
            raise
    
    def _generate_reference_id(self, email):
        """Gera um ID de referência único para a assinatura"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_input = f"{email}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _save_subscription_data(self, subscription_data, user_data, plan_type):
        """
        Salva os dados da assinatura no banco de dados
        
        Em um ambiente real, isso seria feito em um banco de dados.
        Aqui estamos salvando em um arquivo JSON para simulação.
        """
        # Criar diretório de dados se não existir
        os.makedirs(os.path.join('data', 'assinaturas'), exist_ok=True)
        
        # Dados a serem salvos
        data_to_save = {
            "subscription_id": subscription_data["id"],
            "checkout_session_id": subscription_data["checkout_session_id"],
            "customer_id": subscription_data["customer_id"],
            "user_email": user_data["email"],
            "user_name": user_data["name"],
            "plan_type": plan_type,
            "amount": subscription_data["amount"],
            "status": subscription_data["status"],
            "date_created": subscription_data["date_created"],
            "payment_url": subscription_data["payment_url"]
        }
        
        # Salvar em arquivo JSON
        file_path = os.path.join('data', 'assinaturas', f'{subscription_data["id"]}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Dados da assinatura {subscription_data['id']} salvos com sucesso")
        
        return True
    
    def check_subscription_status(self, subscription_id):
        """
        Verifica o status de uma assinatura
        
        Args:
            subscription_id (str): ID da assinatura
            
        Returns:
            dict: Status da assinatura
        """
        try:
            # Em um ambiente real, faríamos uma chamada à API do Stripe
            # para verificar o status da assinatura
            
            file_path = f'/home/ubuntu/lotofacil/data/assinaturas/{subscription_id}.json'
            
            with open(file_path, 'r', encoding='utf-8') as f:
                subscription_data = json.load(f)
            
            # Verificar status no Stripe
            try:
                checkout_session = stripe.checkout.Session.retrieve(
                    subscription_data['checkout_session_id']
                )
                
                # Atualizar status com base na sessão de checkout
                if checkout_session.payment_status == 'paid':
                    subscription_data['status'] = 'active'
                    
                    # Se a assinatura foi ativada, criar credenciais de acesso
                    if subscription_data['status'] == 'active':
                        self._create_user_credentials(subscription_data)
                    
                    # Atualizar arquivo JSON
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(subscription_data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                logger.error(f"Erro ao verificar status no Stripe: {str(e)}")
            
            return {
                "subscription_id": subscription_id,
                "status": subscription_data["status"],
                "plan_type": subscription_data["plan_type"],
                "user_email": subscription_data["user_email"]
            }
        except FileNotFoundError:
            logger.error(f"Assinatura {subscription_id} não encontrada")
            return {"error": "Assinatura não encontrada"}
        except Exception as e:
            logger.error(f"Erro ao verificar status da assinatura {subscription_id}: {str(e)}")
            return {"error": str(e)}
    
    def handle_webhook_event(self, payload, sig_header):
        """
        Processa eventos de webhook do Stripe
        
        Args:
            payload (str): Payload do evento
            sig_header (str): Assinatura do evento
            
        Returns:
            dict: Resultado do processamento
        """
        try:
            # Verificar assinatura do webhook
            endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_123456789abcdef')
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
            
            # Processar evento
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                
                # Obter dados da assinatura
                reference_id = session['metadata']['reference_id']
                
                # Atualizar status da assinatura
                file_path = f'/home/ubuntu/lotofacil/data/assinaturas/{reference_id}.json'
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        subscription_data = json.load(f)
                    
                    # Atualizar status
                    subscription_data['status'] = 'active'
                    
                    # Salvar dados atualizados
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(subscription_data, f, ensure_ascii=False, indent=4)
                    
                    # Criar credenciais de acesso
                    self._create_user_credentials(subscription_data)
                    
                    logger.info(f"Assinatura {reference_id} ativada com sucesso")
                except FileNotFoundError:
                    logger.error(f"Assinatura {reference_id} não encontrada")
                except Exception as e:
                    logger.error(f"Erro ao atualizar assinatura {reference_id}: {str(e)}")
            
            return {"success": True, "event_type": event['type']}
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return {"error": str(e)}
    
    def _create_user_credentials(self, subscription_data):
        """
        Cria credenciais de acesso para o usuário após assinatura ativada
        
        Args:
            subscription_data (dict): Dados da assinatura
            
        Returns:
            dict: Credenciais de acesso
        """
        # Gerar senha aleatória
        password = self._generate_random_password()
        
        # Dados do usuário
        user_data = {
            "email": subscription_data["user_email"],
            "name": subscription_data["user_name"],
            "password": password,  # Em produção, seria armazenado o hash da senha
            "plan_type": subscription_data["plan_type"],
            "subscription_start": datetime.now().isoformat(),
            "subscription_end": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "active"
        }
        
        # Salvar dados do usuário
        os.makedirs(os.path.join('data', 'usuarios'), exist_ok=True)
        file_path = os.path.join('data', 'usuarios', f'{subscription_data["user_email"].replace("@", "_").replace(".", "_")}.json')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Credenciais criadas para o usuário {subscription_data['user_email']}")
        
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
        os.makedirs(os.path.join('data', 'emails'), exist_ok=True)
        file_path = os.path.join('data', 'emails', f'{user_data["email"].replace("@", "_").replace(".", "_")}.txt')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(email_content)
        
        logger.info(f"E-mail com credenciais enviado para {user_data['email']}")
        
        return True

# Função para testar a integração
def test_integration():
    """Testa a integração com o Stripe"""
    stripe_integration = StripeIntegration()
    
    # Dados de teste
    user_data = {
        "name": "Usuário Teste",
        "email": "usuario@teste.com",
        "phone": "11999999999"
    }
    
    # Criar assinatura
    subscription_data = stripe_integration.create_subscription(user_data, "premium")
    print(f"Assinatura criada: {subscription_data['id']}")
    print(f"URL de pagamento: {subscription_data['payment_url']}")
    
    # Verificar status
    status = stripe_integration.check_subscription_status(subscription_data['id'])
    print(f"Status da assinatura: {status['status']}")
    
    return subscription_data


if __name__ == "__main__":
    # Criar diretórios necessários
    os.makedirs('logs', exist_ok=True)
    os.makedirs(os.path.join('data', 'assinaturas'), exist_ok=True)
    os.makedirs(os.path.join('data', 'usuarios'), exist_ok=True)
    os.makedirs(os.path.join('data', 'emails'), exist_ok=True)
    
    # Testar integração
    test_integration()
