#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar todas as funcionalidades do sistema
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime, timedelta
import time
import subprocess
import signal
import threading

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/test_system.log',
    filemode='a'
)
logger = logging.getLogger('test_system')

class SystemTester:
    """Classe para testar todas as funcionalidades do sistema"""
    
    def __init__(self):
        """Inicializa o testador do sistema"""
        # Criar diretórios necessários
        os.makedirs('/home/ubuntu/lotofacil/logs', exist_ok=True)
        os.makedirs('/home/ubuntu/lotofacil/data/test', exist_ok=True)
        
        # URLs dos serviços
        self.payment_api_url = "http://localhost:5000"
        self.lstm_api_url = "http://localhost:5001"
        self.ciclo_api_url = "http://localhost:5002"
        self.auth_api_url = "http://localhost:5003"
        
        # Processos dos serviços
        self.processes = {}
        
        # Dados de teste
        self.test_user = {
            'email': 'teste@exemplo.com',
            'name': 'Usuário Teste',
            'password': 'senha123',
            'plan_type': 'premium'
        }
        
        self.test_payment = {
            'name': 'Usuário Teste',
            'email': 'teste@exemplo.com',
            'phone': '11999999999',
            'plan_type': 'premium'
        }
        
        # Token de autenticação
        self.auth_token = None
    
    def start_services(self):
        """
        Inicia todos os serviços
        
        Returns:
            bool: True se todos os serviços foram iniciados com sucesso, False caso contrário
        """
        try:
            logger.info("Iniciando serviços...")
            
            # Iniciar serviço de pagamento
            payment_cmd = "cd /home/ubuntu/lotofacil && python3 scripts/pagamento/payment_api.py"
            payment_process = subprocess.Popen(payment_cmd, shell=True, preexec_fn=os.setsid)
            self.processes['payment'] = payment_process
            
            # Iniciar serviço de IA LSTM
            lstm_cmd = "cd /home/ubuntu/lotofacil && python3 scripts/ia/lstm_api.py"
            lstm_process = subprocess.Popen(lstm_cmd, shell=True, preexec_fn=os.setsid)
            self.processes['lstm'] = lstm_process
            
            # Iniciar serviço de ciclo de dezenas
            ciclo_cmd = "cd /home/ubuntu/lotofacil && python3 scripts/estrategias/ciclo_api.py"
            ciclo_process = subprocess.Popen(ciclo_cmd, shell=True, preexec_fn=os.setsid)
            self.processes['ciclo'] = ciclo_process
            
            # Iniciar serviço de autenticação
            auth_cmd = "cd /home/ubuntu/lotofacil && python3 scripts/auth/auth_api.py"
            auth_process = subprocess.Popen(auth_cmd, shell=True, preexec_fn=os.setsid)
            self.processes['auth'] = auth_process
            
            # Aguardar serviços iniciarem
            logger.info("Aguardando serviços iniciarem...")
            time.sleep(5)
            
            # Verificar se os serviços estão rodando
            all_running = True
            
            for name, process in self.processes.items():
                if process.poll() is not None:
                    logger.error(f"Serviço {name} não está rodando")
                    all_running = False
            
            if all_running:
                logger.info("Todos os serviços iniciados com sucesso")
            else:
                logger.error("Falha ao iniciar todos os serviços")
            
            return all_running
        except Exception as e:
            logger.error(f"Erro ao iniciar serviços: {str(e)}")
            self.stop_services()
            return False
    
    def stop_services(self):
        """
        Para todos os serviços
        
        Returns:
            bool: True se todos os serviços foram parados com sucesso, False caso contrário
        """
        try:
            logger.info("Parando serviços...")
            
            for name, process in self.processes.items():
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    logger.info(f"Serviço {name} parado com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao parar serviço {name}: {str(e)}")
            
            # Limpar processos
            self.processes = {}
            
            logger.info("Todos os serviços parados")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao parar serviços: {str(e)}")
            return False
    
    def test_auth_service(self):
        """
        Testa o serviço de autenticação
        
        Returns:
            bool: True se o teste foi bem-sucedido, False caso contrário
        """
        try:
            logger.info("Testando serviço de autenticação...")
            
            # Registrar usuário
            register_url = f"{self.auth_api_url}/api/auth/register"
            register_response = requests.post(register_url, json=self.test_user)
            
            if register_response.status_code != 200:
                logger.error(f"Falha ao registrar usuário: {register_response.text}")
                return False
            
            logger.info("Usuário registrado com sucesso")
            
            # Realizar login
            login_url = f"{self.auth_api_url}/api/auth/login"
            login_data = {
                'email': self.test_user['email'],
                'password': self.test_user['password']
            }
            
            login_response = requests.post(login_url, json=login_data)
            
            if login_response.status_code != 200:
                logger.error(f"Falha ao realizar login: {login_response.text}")
                return False
            
            # Obter token
            login_result = login_response.json()
            self.auth_token = login_result['token']
            
            logger.info("Login realizado com sucesso")
            
            # Verificar token
            verify_url = f"{self.auth_api_url}/api/auth/verify"
            headers = {'Authorization': f"Bearer {self.auth_token}"}
            
            verify_response = requests.get(verify_url, headers=headers)
            
            if verify_response.status_code != 200:
                logger.error(f"Falha ao verificar token: {verify_response.text}")
                return False
            
            logger.info("Token verificado com sucesso")
            
            # Obter dados do usuário
            user_url = f"{self.auth_api_url}/api/auth/user/{self.test_user['email']}"
            
            user_response = requests.get(user_url, headers=headers)
            
            if user_response.status_code != 200:
                logger.error(f"Falha ao obter dados do usuário: {user_response.text}")
                return False
            
            logger.info("Dados do usuário obtidos com sucesso")
            
            # Atualizar dados do usuário
            update_data = {'name': 'Usuário Teste Atualizado'}
            
            update_response = requests.put(user_url, headers=headers, json=update_data)
            
            if update_response.status_code != 200:
                logger.error(f"Falha ao atualizar dados do usuário: {update_response.text}")
                return False
            
            logger.info("Dados do usuário atualizados com sucesso")
            
            # Listar usuários
            users_url = f"{self.auth_api_url}/api/auth/users"
            
            users_response = requests.get(users_url, headers=headers)
            
            if users_response.status_code != 200:
                logger.error(f"Falha ao listar usuários: {users_response.text}")
                return False
            
            logger.info("Usuários listados com sucesso")
            
            # Realizar logout
            logout_url = f"{self.auth_api_url}/api/auth/logout"
            
            logout_response = requests.post(logout_url, headers=headers)
            
            if logout_response.status_code != 200:
                logger.error(f"Falha ao realizar logout: {logout_response.text}")
                return False
            
            logger.info("Logout realizado com sucesso")
            
            # Realizar login novamente para os próximos testes
            login_response = requests.post(login_url, json=login_data)
            
            if login_response.status_code != 200:
                logger.error(f"Falha ao realizar login novamente: {login_response.text}")
                return False
            
            # Obter token
            login_result = login_response.json()
            self.auth_token = login_result['token']
            
            logger.info("Login realizado novamente com sucesso")
            
            logger.info("Teste do serviço de autenticação concluído com sucesso")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao testar serviço de autenticação: {str(e)}")
            return False
    
    def test_payment_service(self):
        """
        Testa o serviço de pagamento
        
        Returns:
            bool: True se o teste foi bem-sucedido, False caso contrário
        """
        try:
            logger.info("Testando serviço de pagamento...")
            
            # Criar pagamento
            payment_url = f"{self.payment_api_url}/api/pagamento/criar"
            headers = {'Authorization': f"Bearer {self.auth_token}"}
            
            payment_response = requests.post(payment_url, headers=headers, json=self.test_payment)
            
            if payment_response.status_code != 200:
                logger.error(f"Falha ao criar pagamento: {payment_response.text}")
                return False
            
            # Obter dados do pagamento
            payment_result = payment_response.json()
            payment_id = payment_result['id']
            
            logger.info(f"Pagamento criado com sucesso: {payment_id}")
            
            # Verificar status do pagamento
            status_url = f"{self.payment_api_url}/api/pagamento/status/{payment_id}"
            
            status_response = requests.get(status_url, headers=headers)
            
            if status_response.status_code != 200:
                logger.error(f"Falha ao verificar status do pagamento: {status_response.text}")
                return False
            
            logger.info("Status do pagamento verificado com sucesso")
            
            # Obter QR Code
            qrcode_url = f"{self.payment_api_url}/api/qrcode/{payment_id}"
            
            qrcode_response = requests.get(qrcode_url, headers=headers)
            
            if qrcode_response.status_code != 200:
                logger.error(f"Falha ao obter QR Code: {qrcode_response.text}")
                return False
            
            logger.info("QR Code obtido com sucesso")
            
            # Verificar e-mail
            email_url = f"{self.payment_api_url}/api/usuario/verificar-email"
            email_data = {'email': self.test_user['email']}
            
            email_response = requests.post(email_url, headers=headers, json=email_data)
            
            if email_response.status_code != 200:
                logger.error(f"Falha ao verificar e-mail: {email_response.text}")
                return False
            
            logger.info("E-mail verificado com sucesso")
            
            # Simular webhook do Mercado Pago
            webhook_url = f"{self.payment_api_url}/api/webhook/mercadopago"
            webhook_data = {
                'data': {
                    'id': payment_id
                }
            }
            
            webhook_response = requests.post(webhook_url, headers=headers, json=webhook_data)
            
            if webhook_response.status_code != 200:
                logger.error(f"Falha ao processar webhook: {webhook_response.text}")
                return False
            
            logger.info("Webhook processado com sucesso")
            
            logger.info("Teste do serviço de pagamento concluído com sucesso")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao testar serviço de pagamento: {str(e)}")
            return False
    
    def test_lstm_service(self):
        """
        Testa o serviço de IA LSTM
        
        Returns:
            bool: True se o teste foi bem-sucedido, False caso contrário
        """
        try:
            logger.info("Testando serviço de IA LSTM...")
            
            # Iniciar treinamento
            train_url = f"{self.lstm_api_url}/api/lstm/train"
            headers = {'Authorization': f"Bearer {self.auth_token}"}
            train_data = {
                'epochs': 5,
                'batch_size': 32,
                'sequence_length': 5
            }
            
            train_response = requests.post(train_url, headers=headers, json=train_data)
            
            if train_response.status_code != 200:
                logger.error(f"Falha ao iniciar treinamento: {train_response.text}")
                return False
            
            logger.info("Treinamento iniciado com sucesso")
            
            # Verificar status do treinamento
            status_url = f"{self.lstm_api_url}/api/lstm/status"
            
            # Aguardar treinamento concluir (ou timeout após 60 segundos)
            start_time = time.time()
            training_completed = False
            
            while time.time() - start_time < 60:
                status_response = requests.get(status_url, headers=headers)
                
                if status_response.status_code != 200:
                    logger.error(f"Falha ao verificar status do treinamento: {status_response.text}")
                    return False
                
                status_result = status_response.json()
                
                if not status_result['status']['is_training']:
                    training_completed = True
                    break
                
                logger.info(f"Progresso do treinamento: {status_result['status']['progress']}%")
                time.sleep(5)
            
            if not training_completed:
                logger.warning("Timeout ao aguardar treinamento concluir")
            
            # Obter previsões
            predictions_url = f"{self.lstm_api_url}/api/lstm/predictions"
            
            predictions_response = requests.get(predictions_url, headers=headers)
            
            if predictions_response.status_code != 200:
                logger.error(f"Falha ao obter previsões: {predictions_response.text}")
                return False
            
            logger.info("Previsões obtidas com sucesso")
            
            # Obter histórico de treinamento
            history_url = f"{self.lstm_api_url}/api/lstm/history"
            
            history_response = requests.get(history_url, headers=headers)
            
            if history_response.status_code != 200:
                logger.error(f"Falha ao obter histórico de treinamento: {history_response.text}")
                return False
            
            logger.info("Histórico de treinamento obtido com sucesso")
            
            # Obter métricas
            metrics_url = f"{self.lstm_api_url}/api/lstm/metrics"
            
            metrics_response = requests.get(metrics_url, headers=headers)
            
            if metrics_response.status_code != 200:
                logger.error(f"Falha ao obter métricas: {metrics_response.text}")
                return False
            
            logger.info("Métricas obtidas com sucesso")
            
            logger.info("Teste do serviço de IA LSTM concluído com sucesso")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao testar serviço de IA LSTM: {str(e)}")
            return False
    
    def test_ciclo_service(self):
        """
        Testa o serviço de ciclo de dezenas fora
        
        Returns:
            bool: True se o teste foi bem-sucedido, False caso contrário
        """
        try:
            logger.info("Testando serviço de ciclo de dezenas fora...")
            
            # Iniciar ciclo
            iniciar_url = f"{self.ciclo_api_url}/api/ciclo/iniciar"
            headers = {'Authorization': f"Bearer {self.auth_token}"}
            
            iniciar_response = requests.post(iniciar_url, headers=headers)
            
            if iniciar_response.status_code != 200:
                logger.error(f"Falha ao iniciar ciclo: {iniciar_response.text}")
                return False
            
            logger.info("Ciclo iniciado com sucesso")
            
            # Analisar ciclo
            analisar_url = f"{self.ciclo_api_url}/api/ciclo/analisar"
            
            analisar_response = requests.get(analisar_url, headers=headers)
            
            if analisar_response.status_code != 200:
                logger.error(f"Falha ao analisar ciclo: {analisar_response.text}")
                return False
            
            logger.info("Ciclo analisado com sucesso")
            
            # Gerar jogos
            jogos_url = f"{self.ciclo_api_url}/api/ciclo/gerar-jogos"
            
            jogos_response = requests.get(jogos_url, headers=headers)
            
            if jogos_response.status_code != 200:
                logger.error(f"Falha ao gerar jogos: {jogos_response.text}")
                return False
            
            logger.info("Jogos gerados com sucesso")
            
            # Atualizar ciclo
            atualizar_url = f"{self.ciclo_api_url}/api/ciclo/atualizar"
            
            atualizar_response = requests.post(atualizar_url, headers=headers)
            
            if atualizar_response.status_code != 200:
                logger.error(f"Falha ao atualizar ciclo: {atualizar_response.text}")
                return False
            
            logger.info("Ciclo atualizado com sucesso")
            
            # Executar pipeline
            pipeline_url = f"{self.ciclo_api_url}/api/ciclo/pipeline"
            
            pipeline_response = requests.post(pipeline_url, headers=headers)
            
            if pipeline_response.status_code != 200:
                logger.error(f"Falha ao executar pipeline: {pipeline_response.text}")
                return False
            
            logger.info("Pipeline executado com sucesso")
            
            logger.info("Teste do serviço de ciclo de dezenas fora concluído com sucesso")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao testar serviço de ciclo de dezenas fora: {str(e)}")
            return False
    
    def test_frontend(self):
        """
        Testa o frontend
        
        Returns:
            bool: True se o teste foi bem-sucedido, False caso contrário
        """
        try:
            logger.info("Testando frontend...")
            
            # Verificar se os arquivos existem
            frontend_files = [
                '/home/ubuntu/lotofacil/templates/index.html',
                '/home/ubuntu/lotofacil/templates/login.html',
                '/home/ubuntu/lotofacil/templates/pagamento.html',
                '/home/ubuntu/lotofacil/templates/dashboard.html',
                '/home/ubuntu/lotofacil/static/css/style.css',
                '/home/ubuntu/lotofacil/static/js/matrix.js'
            ]
            
            for file_path in frontend_files:
                if not os.path.exists(file_path):
                    logger.error(f"Arquivo não encontrado: {file_path}")
                    return False
            
            logger.info("Todos os arquivos do frontend encontrados")
            
            # Verificar conteúdo dos arquivos
            for file_path in frontend_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    if len(content) == 0:
                        logger.error(f"Arquivo vazio: {file_path}")
                        return False
            
            logger.info("Conteúdo dos arquivos do frontend verificado")
            
            logger.info("Teste do frontend concluído com sucesso")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao testar frontend: {str(e)}")
            return False
    
    def run_all_tests(self):
        """
        Executa todos os testes
        
        Returns:
            dict: Resultados dos testes
        """
        try:
            logger.info("Iniciando todos os testes...")
            
            # Iniciar serviços
            services_started = self.start_services()
            
            if not services_started:
                logger.error("Falha ao iniciar serviços. Testes interrompidos.")
                return {
                    'success': False,
                    'message': 'Falha ao iniciar serviços',
                    'results': {}
                }
            
            # Executar testes
            results = {}
            
            # Testar frontend
            results['frontend'] = self.test_frontend()
            
            # Testar serviço de autenticação
            results['auth'] = self.test_auth_service()
            
            # Testar serviço de pagamento
            results['payment'] = self.test_payment_service()
            
            # Testar serviço de IA LSTM
            results['lstm'] = self.test_lstm_service()
            
            # Testar serviço de ciclo de dezenas fora
            results['ciclo'] = self.test_ciclo_service()
            
            # Parar serviços
            self.stop_services()
            
            # Verificar resultados
            all_passed = all(results.values())
            
            if all_passed:
                logger.info("Todos os testes concluídos com sucesso")
                message = "Todos os testes concluídos com sucesso"
            else:
                failed_tests = [name for name, passed in results.items() if not passed]
                logger.error(f"Falha nos testes: {', '.join(failed_tests)}")
                message = f"Falha nos testes: {', '.join(failed_tests)}"
            
            return {
                'success': all_passed,
                'message': message,
                'results': results
            }
        except Exception as e:
            logger.error(f"Erro ao executar todos os testes: {str(e)}")
            self.stop_services()
            return {
                'success': False,
                'message': f'Erro ao executar todos os testes: {str(e)}',
                'results': {}
            }

# Função para executar os testes
def run_tests():
    """Executa os testes do sistema"""
    tester = SystemTester()
    results = tester.run_all_tests()
    
    print(f"Resultados dos testes: {json.dumps(results, indent=4)}")
    
    return results['success']

if __name__ == "__main__":
    run_tests()
