#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Middleware para autenticação e controle de acesso
"""

import os
import json
from functools import wraps
from flask import request, jsonify, redirect, url_for
import logging

# Importar o sistema de autenticação
from auth_system import AuthSystem

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/auth_middleware.log',
    filemode='a'
)
logger = logging.getLogger('auth_middleware')

# Inicializar sistema de autenticação
auth = AuthSystem()

def token_required(f):
    """
    Decorator para verificar se o token é válido
    
    Args:
        f: Função a ser decorada
        
    Returns:
        function: Função decorada
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Obter token do cabeçalho Authorization ou do cookie
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = request.cookies.get('auth_token')
        
        if not token:
            logger.warning("Token ausente")
            return jsonify({
                'success': False,
                'message': 'Token ausente. Autenticação necessária.'
            }), 401
        
        # Verificar token
        payload = auth.verify_access(token)
        
        if not payload:
            logger.warning("Token inválido ou expirado")
            return jsonify({
                'success': False,
                'message': 'Token inválido ou expirado. Autenticação necessária.'
            }), 401
        
        # Adicionar dados do usuário ao request
        request.user = payload
        
        return f(*args, **kwargs)
    
    return decorated

def premium_required(f):
    """
    Decorator para verificar se o usuário tem plano premium
    
    Args:
        f: Função a ser decorada
        
    Returns:
        function: Função decorada
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Verificar se o usuário está autenticado
        if not hasattr(request, 'user'):
            logger.warning("Usuário não autenticado")
            return jsonify({
                'success': False,
                'message': 'Autenticação necessária.'
            }), 401
        
        # Verificar plano
        if request.user.get('plan') != 'premium':
            logger.warning(f"Acesso negado. Plano insuficiente: {request.user.get('plan')}")
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Esta funcionalidade é exclusiva para assinantes premium.'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """
    Decorator para verificar se o usuário é administrador
    
    Args:
        f: Função a ser decorada
        
    Returns:
        function: Função decorada
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Verificar se o usuário está autenticado
        if not hasattr(request, 'user'):
            logger.warning("Usuário não autenticado")
            return jsonify({
                'success': False,
                'message': 'Autenticação necessária.'
            }), 401
        
        # Verificar se é administrador
        if not request.user.get('is_admin', False):
            logger.warning(f"Acesso negado. Usuário não é administrador: {request.user.get('sub')}")
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Esta funcionalidade é exclusiva para administradores.'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated

def html_token_required(f):
    """
    Decorator para verificar se o token é válido em rotas HTML
    
    Args:
        f: Função a ser decorada
        
    Returns:
        function: Função decorada
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Obter token do cabeçalho Authorization ou do cookie
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = request.cookies.get('auth_token')
        
        if not token:
            logger.warning("Token ausente")
            return redirect(url_for('login'))
        
        # Verificar token
        payload = auth.verify_access(token)
        
        if not payload:
            logger.warning("Token inválido ou expirado")
            return redirect(url_for('login'))
        
        # Adicionar dados do usuário ao request
        request.user = payload
        
        return f(*args, **kwargs)
    
    return decorated

def html_premium_required(f):
    """
    Decorator para verificar se o usuário tem plano premium em rotas HTML
    
    Args:
        f: Função a ser decorada
        
    Returns:
        function: Função decorada
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Verificar se o usuário está autenticado
        if not hasattr(request, 'user'):
            logger.warning("Usuário não autenticado")
            return redirect(url_for('login'))
        
        # Verificar plano
        if request.user.get('plan') != 'premium':
            logger.warning(f"Acesso negado. Plano insuficiente: {request.user.get('plan')}")
            return redirect(url_for('upgrade_plan'))
        
        return f(*args, **kwargs)
    
    return decorated
