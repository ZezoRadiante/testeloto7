#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Flask para o sistema de pagamento com Stripe do Gerador de Jogos da Lotofácil
"""

import os
import json
from flask import Flask, request, jsonify, render_template, send_file, redirect
from datetime import datetime
import logging
from stripe_integration import StripeIntegration

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/api.log',
    filemode='a'
)
logger = logging.getLogger('payment_api_stripe')

# Inicializar Flask
app = Flask(__name__, 
            template_folder='/home/ubuntu/lotofacil/templates',
            static_folder='/home/ubuntu/lotofacil/static')

# Inicializar integração com Stripe
stripe_integration = StripeIntegration()

# Criar diretórios necessários
os.makedirs('/home/ubuntu/lotofacil/logs', exist_ok=True)
os.makedirs('/home/ubuntu/lotofacil/data/assinaturas', exist_ok=True)
os.makedirs('/home/ubuntu/lotofacil/data/usuarios', exist_ok=True)
os.makedirs('/home/ubuntu/lotofacil/data/emails', exist_ok=True)

@app.route('/')
def index():
    """Rota para a página inicial"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Rota para a página de login"""
    return render_template('login.html')

@app.route('/pagamento')
def pagamento():
    """Rota para a página de pagamento"""
    return render_template('pagamento.html')

@app.route('/dashboard')
def dashboard():
    """Rota para o dashboard do usuário"""
    return render_template('dashboard.html')

@app.route('/pagamento/sucesso')
def pagamento_sucesso():
    """Rota para página de sucesso após pagamento"""
    session_id = request.args.get('session_id', '')
    return render_template('pagamento_sucesso.html', session_id=session_id)

@app.route('/pagamento/cancelado')
def pagamento_cancelado():
    """Rota para página de cancelamento de pagamento"""
    return render_template('pagamento_cancelado.html')

@app.route('/api/assinatura/criar', methods=['POST'])
def criar_assinatura():
    """
    Cria uma nova assinatura
    
    Espera um JSON com os seguintes campos:
    - name: Nome do usuário
    - email: E-mail do usuário
    - phone: Telefone do usuário (opcional)
    - plan_type: Tipo de plano ('basic' ou 'premium')
    
    Retorna um JSON com os dados da assinatura, incluindo URL de pagamento
    """
    try:
        data = request.json
        
        # Validar dados
        if not data or 'name' not in data or 'email' not in data or 'plan_type' not in data:
            return jsonify({"error": "Dados incompletos"}), 400
        
        # Criar assinatura
        subscription_data = stripe_integration.create_subscription(data, data['plan_type'])
        
        return jsonify({
            "success": True,
            "subscription_id": subscription_data['id'],
            "payment_url": subscription_data['payment_url']
        })
    except Exception as e:
        logger.error(f"Erro ao criar assinatura: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/assinatura/status/<subscription_id>', methods=['GET'])
def verificar_status(subscription_id):
    """
    Verifica o status de uma assinatura
    
    Args:
        subscription_id (str): ID da assinatura
        
    Retorna um JSON com o status da assinatura
    """
    try:
        status = stripe_integration.check_subscription_status(subscription_id)
        return jsonify(status)
    except Exception as e:
        logger.error(f"Erro ao verificar status da assinatura {subscription_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/usuario/login', methods=['POST'])
def login_usuario():
    """
    Realiza login do usuário
    
    Espera um JSON com os seguintes campos:
    - email: E-mail do usuário
    - password: Senha do usuário
    
    Retorna um JSON com os dados do usuário em caso de sucesso
    """
    try:
        data = request.json
        
        # Validar dados
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Dados incompletos"}), 400
        
        # Verificar credenciais
        email = data['email']
        password = data['password']
        
        # Em um ambiente real, isso seria feito em um banco de dados
        # Aqui estamos verificando o arquivo JSON
        file_path = f'/home/ubuntu/lotofacil/data/usuarios/{email.replace("@", "_").replace(".", "_")}.json'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            # Verificar senha
            if user_data['password'] == password:
                # Remover senha do retorno
                user_data.pop('password', None)
                
                # Verificar validade da assinatura
                subscription_end = datetime.fromisoformat(user_data['subscription_end'])
                if subscription_end < datetime.now():
                    user_data['status'] = 'expired'
                
                return jsonify({
                    "success": True,
                    "user": user_data
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Credenciais inválidas"
                }), 401
        except FileNotFoundError:
            return jsonify({
                "success": False,
                "error": "Usuário não encontrado"
            }), 404
    except Exception as e:
        logger.error(f"Erro ao realizar login: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/usuario/verificar-email', methods=['POST'])
def verificar_email():
    """
    Verifica se um e-mail já está cadastrado
    
    Espera um JSON com o seguinte campo:
    - email: E-mail a ser verificado
    
    Retorna um JSON indicando se o e-mail já está cadastrado
    """
    try:
        data = request.json
        
        # Validar dados
        if not data or 'email' not in data:
            return jsonify({"error": "Dados incompletos"}), 400
        
        email = data['email']
        file_path = f'/home/ubuntu/lotofacil/data/usuarios/{email.replace("@", "_").replace(".", "_")}.json'
        
        exists = os.path.exists(file_path)
        
        return jsonify({
            "exists": exists
        })
    except Exception as e:
        logger.error(f"Erro ao verificar e-mail: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webhook/stripe', methods=['POST'])
def webhook_stripe():
    """
    Webhook para receber notificações do Stripe
    """
    try:
        payload = request.data.decode('utf-8')
        sig_header = request.headers.get('Stripe-Signature')
        
        # Processar evento
        result = stripe_integration.handle_webhook_event(payload, sig_header)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=True)
