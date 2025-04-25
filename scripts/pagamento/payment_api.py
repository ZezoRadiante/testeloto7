#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Flask para o sistema de pagamento do Gerador de Jogos da Lotofácil
"""

import os
import json
from flask import Flask, request, jsonify, render_template, send_file
from datetime import datetime
import logging
from mercadopago_integration import MercadoPagoIntegration

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/api.log',
    filemode='a'
)
logger = logging.getLogger('payment_api')

# Inicializar Flask
app = Flask(__name__, 
            template_folder='/home/ubuntu/lotofacil/templates',
            static_folder='/home/ubuntu/lotofacil/static')

# Inicializar integração com Mercado Pago
mp_integration = MercadoPagoIntegration()

# Criar diretórios necessários
os.makedirs('/home/ubuntu/lotofacil/logs', exist_ok=True)
os.makedirs('/home/ubuntu/lotofacil/data/pagamentos', exist_ok=True)
os.makedirs('/home/ubuntu/lotofacil/data/usuarios', exist_ok=True)
os.makedirs('/home/ubuntu/lotofacil/data/emails', exist_ok=True)
os.makedirs('/home/ubuntu/lotofacil/static/images/qrcodes', exist_ok=True)

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

@app.route('/api/pagamento/criar', methods=['POST'])
def criar_pagamento():
    """
    Cria um novo pagamento
    
    Espera um JSON com os seguintes campos:
    - name: Nome do usuário
    - email: E-mail do usuário
    - phone: Telefone do usuário (opcional)
    - plan_type: Tipo de plano ('basic' ou 'premium')
    
    Retorna um JSON com os dados do pagamento, incluindo QR Code
    """
    try:
        data = request.json
        
        # Validar dados
        if not data or 'name' not in data or 'email' not in data or 'plan_type' not in data:
            return jsonify({"error": "Dados incompletos"}), 400
        
        # Criar pagamento
        payment_data = mp_integration.create_payment(data, data['plan_type'])
        
        # Salvar QR Code como imagem
        qr_code_path = f"/home/ubuntu/lotofacil/static/images/qrcodes/{payment_data['id']}.png"
        import base64
        from PIL import Image
        import io
        
        # Decodificar base64 e salvar como imagem
        img_data = base64.b64decode(payment_data['point_of_interaction']['transaction_data']['qr_code_base64'])
        img = Image.open(io.BytesIO(img_data))
        img.save(qr_code_path)
        
        # Adicionar URL da imagem ao retorno
        payment_data['qr_code_url'] = f"/static/images/qrcodes/{payment_data['id']}.png"
        
        return jsonify(payment_data)
    except Exception as e:
        logger.error(f"Erro ao criar pagamento: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/pagamento/status/<payment_id>', methods=['GET'])
def verificar_status(payment_id):
    """
    Verifica o status de um pagamento
    
    Args:
        payment_id (str): ID do pagamento
        
    Retorna um JSON com o status do pagamento
    """
    try:
        status = mp_integration.check_payment_status(payment_id)
        return jsonify(status)
    except Exception as e:
        logger.error(f"Erro ao verificar status do pagamento {payment_id}: {str(e)}")
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

@app.route('/api/webhook/mercadopago', methods=['POST'])
def webhook_mercadopago():
    """
    Webhook para receber notificações do Mercado Pago
    
    Em um ambiente real, isso seria configurado no Mercado Pago
    para receber notificações de pagamentos
    """
    try:
        data = request.json
        
        # Validar dados
        if not data or 'data' not in data or 'id' not in data['data']:
            return jsonify({"error": "Dados incompletos"}), 400
        
        payment_id = data['data']['id']
        
        # Verificar status do pagamento
        status = mp_integration.check_payment_status(payment_id)
        
        # Registrar notificação
        logger.info(f"Notificação recebida para pagamento {payment_id}: {status}")
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/qrcode/<payment_id>', methods=['GET'])
def get_qrcode(payment_id):
    """
    Retorna a imagem do QR Code para um pagamento
    
    Args:
        payment_id (str): ID do pagamento
    """
    try:
        qr_code_path = f"/home/ubuntu/lotofacil/static/images/qrcodes/{payment_id}.png"
        
        if os.path.exists(qr_code_path):
            return send_file(qr_code_path, mimetype='image/png')
        else:
            return jsonify({"error": "QR Code não encontrado"}), 404
    except Exception as e:
        logger.error(f"Erro ao obter QR Code: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=True)
