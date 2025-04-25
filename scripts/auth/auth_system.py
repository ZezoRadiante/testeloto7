#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de autenticação de usuários para o Gerador de Jogos da Lotofácil
"""

import os
import json
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
import jwt

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/auth.log',
    filemode='a'
)
logger = logging.getLogger('auth_system')

class AuthSystem:
    """Classe para gerenciamento de autenticação de usuários"""
    
    def __init__(self):
        """Inicializa o sistema de autenticação"""
        # Criar diretórios necessários
        os.makedirs('/home/ubuntu/lotofacil/logs', exist_ok=True)
        os.makedirs('/home/ubuntu/lotofacil/data/usuarios', exist_ok=True)
        
        # Chave secreta para JWT
        self.secret_key = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))
        
        # Tempo de expiração do token (em horas)
        self.token_expiration = 24
    
    def _hash_password(self, password):
        """
        Cria um hash seguro da senha
        
        Args:
            password (str): Senha em texto plano
            
        Returns:
            str: Hash da senha
        """
        # Em um ambiente de produção, usaríamos bcrypt ou Argon2
        # Para simplificar, usaremos SHA-256 com salt
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((password + salt).encode())
        password_hash = hash_obj.hexdigest()
        
        return f"{salt}${password_hash}"
    
    def _verify_password(self, stored_hash, password):
        """
        Verifica se a senha corresponde ao hash armazenado
        
        Args:
            stored_hash (str): Hash armazenado
            password (str): Senha em texto plano
            
        Returns:
            bool: True se a senha corresponder, False caso contrário
        """
        salt, hash_value = stored_hash.split('$')
        hash_obj = hashlib.sha256((password + salt).encode())
        password_hash = hash_obj.hexdigest()
        
        return password_hash == hash_value
    
    def _generate_token(self, user_data):
        """
        Gera um token JWT para o usuário
        
        Args:
            user_data (dict): Dados do usuário
            
        Returns:
            str: Token JWT
        """
        # Definir payload
        payload = {
            'sub': user_data['email'],
            'name': user_data['name'],
            'plan': user_data['plan_type'],
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiration)
        }
        
        # Gerar token
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        
        return token
    
    def _verify_token(self, token):
        """
        Verifica se um token JWT é válido
        
        Args:
            token (str): Token JWT
            
        Returns:
            dict: Dados do usuário se o token for válido, None caso contrário
        """
        try:
            # Decodificar token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Verificar se o token expirou
            if datetime.fromtimestamp(payload['exp']) < datetime.utcnow():
                logger.warning(f"Token expirado para o usuário {payload['sub']}")
                return None
            
            return payload
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token inválido: {str(e)}")
            return None
    
    def register_user(self, user_data, password_hash=None):
        """
        Registra um novo usuário
        
        Args:
            user_data (dict): Dados do usuário
            password_hash (str): Hash da senha (opcional)
            
        Returns:
            dict: Dados do usuário registrado
        """
        try:
            logger.info(f"Registrando usuário: {user_data['email']}")
            
            # Verificar se o usuário já existe
            if self.get_user(user_data['email']):
                logger.warning(f"Usuário já existe: {user_data['email']}")
                return None
            
            # Criar hash da senha se não fornecido
            if not password_hash and 'password' in user_data:
                password_hash = self._hash_password(user_data['password'])
            
            # Remover senha em texto plano
            if 'password' in user_data:
                user_data.pop('password')
            
            # Adicionar hash da senha
            user_data['password_hash'] = password_hash
            
            # Adicionar data de criação
            user_data['created_at'] = datetime.now().isoformat()
            
            # Salvar usuário
            file_path = f"/home/ubuntu/lotofacil/data/usuarios/{user_data['email'].replace('@', '_').replace('.', '_')}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Usuário registrado com sucesso: {user_data['email']}")
            
            # Remover hash da senha do retorno
            user_data.pop('password_hash', None)
            
            return user_data
        except Exception as e:
            logger.error(f"Erro ao registrar usuário: {str(e)}")
            return None
    
    def login(self, email, password):
        """
        Realiza login do usuário
        
        Args:
            email (str): E-mail do usuário
            password (str): Senha do usuário
            
        Returns:
            dict: Token e dados do usuário se o login for bem-sucedido, None caso contrário
        """
        try:
            logger.info(f"Tentativa de login: {email}")
            
            # Obter dados do usuário
            user_data = self.get_user(email, include_password_hash=True)
            
            if not user_data:
                logger.warning(f"Usuário não encontrado: {email}")
                return None
            
            # Verificar senha
            if not self._verify_password(user_data['password_hash'], password):
                logger.warning(f"Senha incorreta para o usuário: {email}")
                return None
            
            # Verificar se a assinatura está ativa
            if 'subscription_end' in user_data:
                subscription_end = datetime.fromisoformat(user_data['subscription_end'])
                if subscription_end < datetime.now():
                    logger.warning(f"Assinatura expirada para o usuário: {email}")
                    user_data['status'] = 'expired'
            
            # Gerar token
            token = self._generate_token(user_data)
            
            # Remover hash da senha do retorno
            user_data.pop('password_hash', None)
            
            logger.info(f"Login bem-sucedido: {email}")
            
            return {
                'token': token,
                'user': user_data
            }
        except Exception as e:
            logger.error(f"Erro ao realizar login: {str(e)}")
            return None
    
    def get_user(self, email, include_password_hash=False):
        """
        Obtém dados de um usuário
        
        Args:
            email (str): E-mail do usuário
            include_password_hash (bool): Se True, inclui o hash da senha no retorno
            
        Returns:
            dict: Dados do usuário se encontrado, None caso contrário
        """
        try:
            logger.info(f"Obtendo dados do usuário: {email}")
            
            # Caminho do arquivo
            file_path = f"/home/ubuntu/lotofacil/data/usuarios/{email.replace('@', '_').replace('.', '_')}.json"
            
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                logger.warning(f"Usuário não encontrado: {email}")
                return None
            
            # Carregar dados
            with open(file_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            # Remover hash da senha se necessário
            if not include_password_hash and 'password_hash' in user_data:
                user_data.pop('password_hash')
            
            logger.info(f"Dados do usuário obtidos com sucesso: {email}")
            
            return user_data
        except Exception as e:
            logger.error(f"Erro ao obter dados do usuário: {str(e)}")
            return None
    
    def update_user(self, email, update_data):
        """
        Atualiza dados de um usuário
        
        Args:
            email (str): E-mail do usuário
            update_data (dict): Dados a serem atualizados
            
        Returns:
            dict: Dados atualizados do usuário se bem-sucedido, None caso contrário
        """
        try:
            logger.info(f"Atualizando dados do usuário: {email}")
            
            # Obter dados atuais do usuário
            user_data = self.get_user(email, include_password_hash=True)
            
            if not user_data:
                logger.warning(f"Usuário não encontrado: {email}")
                return None
            
            # Atualizar dados
            for key, value in update_data.items():
                # Tratar senha separadamente
                if key == 'password':
                    user_data['password_hash'] = self._hash_password(value)
                else:
                    user_data[key] = value
            
            # Adicionar data de atualização
            user_data['updated_at'] = datetime.now().isoformat()
            
            # Salvar usuário
            file_path = f"/home/ubuntu/lotofacil/data/usuarios/{email.replace('@', '_').replace('.', '_')}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Dados do usuário atualizados com sucesso: {email}")
            
            # Remover hash da senha do retorno
            user_data.pop('password_hash', None)
            
            return user_data
        except Exception as e:
            logger.error(f"Erro ao atualizar dados do usuário: {str(e)}")
            return None
    
    def delete_user(self, email):
        """
        Remove um usuário
        
        Args:
            email (str): E-mail do usuário
            
        Returns:
            bool: True se o usuário foi removido com sucesso, False caso contrário
        """
        try:
            logger.info(f"Removendo usuário: {email}")
            
            # Caminho do arquivo
            file_path = f"/home/ubuntu/lotofacil/data/usuarios/{email.replace('@', '_').replace('.', '_')}.json"
            
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                logger.warning(f"Usuário não encontrado: {email}")
                return False
            
            # Remover arquivo
            os.remove(file_path)
            
            logger.info(f"Usuário removido com sucesso: {email}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao remover usuário: {str(e)}")
            return False
    
    def verify_access(self, token, required_plan=None):
        """
        Verifica se um usuário tem acesso a uma funcionalidade
        
        Args:
            token (str): Token JWT
            required_plan (str): Plano necessário para acesso (opcional)
            
        Returns:
            dict: Dados do usuário se tiver acesso, None caso contrário
        """
        try:
            logger.info("Verificando acesso")
            
            # Verificar token
            payload = self._verify_token(token)
            
            if not payload:
                logger.warning("Token inválido ou expirado")
                return None
            
            # Verificar plano se necessário
            if required_plan and payload['plan'] != required_plan:
                logger.warning(f"Plano insuficiente: {payload['plan']} (necessário: {required_plan})")
                return None
            
            logger.info(f"Acesso concedido para o usuário: {payload['sub']}")
            
            return payload
        except Exception as e:
            logger.error(f"Erro ao verificar acesso: {str(e)}")
            return None
    
    def list_users(self):
        """
        Lista todos os usuários
        
        Returns:
            list: Lista de usuários
        """
        try:
            logger.info("Listando usuários")
            
            # Diretório de usuários
            users_dir = "/home/ubuntu/lotofacil/data/usuarios"
            
            # Listar arquivos
            users = []
            
            for filename in os.listdir(users_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(users_dir, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        user_data = json.load(f)
                    
                    # Remover hash da senha
                    user_data.pop('password_hash', None)
                    
                    users.append(user_data)
            
            logger.info(f"Usuários listados: {len(users)}")
            
            return users
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {str(e)}")
            return []

# Função para testar o sistema de autenticação
def test_auth_system():
    """Testa o sistema de autenticação"""
    # Criar sistema de autenticação
    auth = AuthSystem()
    
    # Registrar usuário
    user_data = {
        'email': 'teste@exemplo.com',
        'name': 'Usuário Teste',
        'password': 'senha123',
        'plan_type': 'premium',
        'subscription_start': datetime.now().isoformat(),
        'subscription_end': (datetime.now() + timedelta(days=30)).isoformat(),
        'status': 'active'
    }
    
    registered_user = auth.register_user(user_data)
    
    if registered_user:
        print(f"Usuário registrado: {registered_user['email']}")
        
        # Realizar login
        login_result = auth.login('teste@exemplo.com', 'senha123')
        
        if login_result:
            print(f"Login bem-sucedido: {login_result['user']['email']}")
            print(f"Token: {login_result['token']}")
            
            # Verificar acesso
            token = login_result['token']
            access_result = auth.verify_access(token, required_plan='premium')
            
            if access_result:
                print(f"Acesso concedido para o usuário: {access_result['sub']}")
            else:
                print("Acesso negado")
        else:
            print("Login falhou")
    else:
        print("Registro falhou")
    
    # Listar usuários
    users = auth.list_users()
    print(f"Usuários: {len(users)}")
    
    return registered_user is not None

if __name__ == "__main__":
    test_auth_system()
