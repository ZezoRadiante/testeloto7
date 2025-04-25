#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Flask para o sistema de autenticação de usuários
"""

import os
import json
from flask import Flask, request, jsonify, render_template, make_response
import logging
from datetime import datetime

# Importar o sistema de autenticação
from scripts.auth.auth_system import AuthSystem

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/auth_api.log',
    filemode='a'
)
logger = logging.getLogger('auth_api')

class AuthAPI:
    """Classe para API do sistema de autenticação"""
    
    def __init__(self):
        """Inicializa a API"""
        # Criar diretórios necessários
import os

# Define um caminho relativo para a pasta logs
log_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_dir, exist_ok=True)
        
        # Inicializar sistema de autenticação
        self.auth = AuthSystem()
    
    def register(self, user_data):
        """
        Registra um novo usuário
        
        Args:
            user_data (dict): Dados do usuário
            
        Returns:
            dict: Resultado do registro
        """
        try:
            logger.info(f"Registrando usuário via API: {user_data.get('email')}")
            
            # Validar dados
            required_fields = ['email', 'name', 'password', 'plan_type']
            for field in required_fields:
                if field not in user_data:
                    return {
                        'success': False,
                        'message': f'Campo obrigatório ausente: {field}'
                    }
            
            # Registrar usuário
            registered_user = self.auth.register_user(user_data)
            
            if not registered_user:
                return {
                    'success': False,
                    'message': 'Falha ao registrar usuário. E-mail já existe ou dados inválidos.'
                }
            
            return {
                'success': True,
                'user': registered_user
            }
        except Exception as e:
            logger.error(f"Erro ao registrar usuário: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao registrar usuário: {str(e)}'
            }
    
    def login(self, email, password):
        """
        Realiza login do usuário
        
        Args:
            email (str): E-mail do usuário
            password (str): Senha do usuário
            
        Returns:
            dict: Resultado do login
        """
        try:
            logger.info(f"Tentativa de login via API: {email}")
            
            # Realizar login
            login_result = self.auth.login(email, password)
            
            if not login_result:
                return {
                    'success': False,
                    'message': 'Credenciais inválidas'
                }
            
            return {
                'success': True,
                'token': login_result['token'],
                'user': login_result['user']
            }
        except Exception as e:
            logger.error(f"Erro ao realizar login: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao realizar login: {str(e)}'
            }
    
    def verify_token(self, token, required_plan=None):
        """
        Verifica se um token é válido
        
        Args:
            token (str): Token JWT
            required_plan (str): Plano necessário para acesso (opcional)
            
        Returns:
            dict: Resultado da verificação
        """
        try:
            logger.info("Verificando token via API")
            
            # Verificar token
            payload = self.auth.verify_access(token, required_plan)
            
            if not payload:
                return {
                    'success': False,
                    'message': 'Token inválido ou acesso negado'
                }
            
            return {
                'success': True,
                'user': payload
            }
        except Exception as e:
            logger.error(f"Erro ao verificar token: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao verificar token: {str(e)}'
            }
    
    def get_user(self, email):
        """
        Obtém dados de um usuário
        
        Args:
            email (str): E-mail do usuário
            
        Returns:
            dict: Resultado da consulta
        """
        try:
            logger.info(f"Obtendo dados do usuário via API: {email}")
            
            # Obter dados do usuário
            user_data = self.auth.get_user(email)
            
            if not user_data:
                return {
                    'success': False,
                    'message': 'Usuário não encontrado'
                }
            
            return {
                'success': True,
                'user': user_data
            }
        except Exception as e:
            logger.error(f"Erro ao obter dados do usuário: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao obter dados do usuário: {str(e)}'
            }
    
    def update_user(self, email, update_data):
        """
        Atualiza dados de um usuário
        
        Args:
            email (str): E-mail do usuário
            update_data (dict): Dados a serem atualizados
            
        Returns:
            dict: Resultado da atualização
        """
        try:
            logger.info(f"Atualizando dados do usuário via API: {email}")
            
            # Atualizar dados do usuário
            updated_user = self.auth.update_user(email, update_data)
            
            if not updated_user:
                return {
                    'success': False,
                    'message': 'Falha ao atualizar usuário. Usuário não encontrado ou dados inválidos.'
                }
            
            return {
                'success': True,
                'user': updated_user
            }
        except Exception as e:
            logger.error(f"Erro ao atualizar dados do usuário: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao atualizar dados do usuário: {str(e)}'
            }
    
    def list_users(self):
        """
        Lista todos os usuários
        
        Returns:
            dict: Resultado da consulta
        """
        try:
            logger.info("Listando usuários via API")
            
            # Listar usuários
            users = self.auth.list_users()
            
            return {
                'success': True,
                'users': users
            }
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao listar usuários: {str(e)}'
            }

# Inicializar Flask
app = Flask(__name__, 
            template_folder='/home/ubuntu/lotofacil/templates',
            static_folder='/home/ubuntu/lotofacil/static')

# Inicializar API
auth_api = AuthAPI()

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Registra um novo usuário
    
    Espera um JSON com os seguintes campos:
    - email: E-mail do usuário
    - name: Nome do usuário
    - password: Senha do usuário
    - plan_type: Tipo de plano ('basic' ou 'premium')
    
    Retorna um JSON com o resultado do registro
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados ausentes'
            }), 400
        
        result = auth_api.register(data)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao registrar usuário: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao registrar usuário: {str(e)}'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Realiza login do usuário
    
    Espera um JSON com os seguintes campos:
    - email: E-mail do usuário
    - password: Senha do usuário
    
    Retorna um JSON com o resultado do login
    """
    try:
        data = request.json
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'message': 'Dados ausentes'
            }), 400
        
        result = auth_api.login(data['email'], data['password'])
        
        if not result['success']:
            return jsonify(result), 401
        
        # Criar resposta com cookie
        response = make_response(jsonify(result))
        
        # Definir cookie com token
        response.set_cookie(
            'auth_token',
            result['token'],
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=24 * 60 * 60  # 24 horas
        )
        
        return response
    except Exception as e:
        logger.error(f"Erro ao realizar login: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao realizar login: {str(e)}'
        }), 500

@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    """
    Verifica se um token é válido
    
    Parâmetros de consulta:
    - plan: Plano necessário para acesso (opcional)
    
    Retorna um JSON com o resultado da verificação
    """
    try:
        # Obter token do cabeçalho Authorization ou do cookie
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = request.cookies.get('auth_token')
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token ausente'
            }), 401
        
        # Obter plano necessário
        required_plan = request.args.get('plan')
        
        result = auth_api.verify_token(token, required_plan)
        
        if not result['success']:
            return jsonify(result), 401
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao verificar token: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao verificar token: {str(e)}'
        }), 500

@app.route('/api/auth/user/<email>', methods=['GET'])
def get_user(email):
    """
    Obtém dados de um usuário
    
    Args:
        email (str): E-mail do usuário
        
    Retorna um JSON com o resultado da consulta
    """
    try:
        result = auth_api.get_user(email)
        
        if not result['success']:
            return jsonify(result), 404
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao obter dados do usuário: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao obter dados do usuário: {str(e)}'
        }), 500

@app.route('/api/auth/user/<email>', methods=['PUT'])
def update_user(email):
    """
    Atualiza dados de um usuário
    
    Args:
        email (str): E-mail do usuário
        
    Espera um JSON com os dados a serem atualizados
    
    Retorna um JSON com o resultado da atualização
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados ausentes'
            }), 400
        
        result = auth_api.update_user(email, data)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao atualizar dados do usuário: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar dados do usuário: {str(e)}'
        }), 500

@app.route('/api/auth/users', methods=['GET'])
def list_users():
    """
    Lista todos os usuários
    
    Retorna um JSON com o resultado da consulta
    """
    try:
        result = auth_api.list_users()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao listar usuários: {str(e)}'
        }), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """
    Realiza logout do usuário
    
    Retorna um JSON com o resultado do logout
    """
    try:
        # Criar resposta
        response = make_response(jsonify({
            'success': True,
            'message': 'Logout realizado com sucesso'
        }))
        
        # Remover cookie
        response.delete_cookie('auth_token')
        
        return response
    except Exception as e:
        logger.error(f"Erro ao realizar logout: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao realizar logout: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=5003, debug=True)
