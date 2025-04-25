#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script principal para iniciar todos os serviços do Gerador de Jogos da Lotofácil
"""

import os
import sys
import subprocess
import signal
import time
import logging
import argparse
import json
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/main.log',
    filemode='a'
)
logger = logging.getLogger('main')

class LotofacilSystem:
    """Classe para gerenciar o sistema do Gerador de Jogos da Lotofácil"""
    
    def __init__(self):
        """Inicializa o sistema"""
        # Criar diretórios necessários
        os.makedirs('/home/ubuntu/lotofacil/logs', exist_ok=True)
        
        # Processos dos serviços
        self.processes = {}
        
        # Portas dos serviços
        self.ports = {
            'payment': 5000,
            'lstm': 5001,
            'ciclo': 5002,
            'auth': 5003,
            'main': 5004
        }
        
        # Caminhos dos scripts
        self.scripts = {
            'payment': '/home/ubuntu/lotofacil/scripts/pagamento/payment_api.py',
            'lstm': '/home/ubuntu/lotofacil/scripts/ia/lstm_api.py',
            'ciclo': '/home/ubuntu/lotofacil/scripts/estrategias/ciclo_api.py',
            'auth': '/home/ubuntu/lotofacil/scripts/auth/auth_api.py',
            'main': '/home/ubuntu/lotofacil/app.py'
        }
    
    def start_services(self, services=None):
        """
        Inicia os serviços especificados
        
        Args:
            services (list): Lista de serviços a serem iniciados (None para todos)
            
        Returns:
            dict: Status dos serviços
        """
        try:
            logger.info(f"Iniciando serviços: {services if services else 'todos'}")
            
            # Se nenhum serviço for especificado, iniciar todos
            if services is None:
                services = list(self.scripts.keys())
            
            # Iniciar serviços
            for service in services:
                if service not in self.scripts:
                    logger.error(f"Serviço desconhecido: {service}")
                    continue
                
                # Verificar se o script existe
                script_path = self.scripts[service]
                if not os.path.exists(script_path):
                    logger.error(f"Script não encontrado: {script_path}")
                    continue
                
                # Iniciar serviço
                cmd = f"cd /home/ubuntu/lotofacil && python3 {script_path}"
                process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
                self.processes[service] = process
                
                logger.info(f"Serviço {service} iniciado (PID: {process.pid})")
            
            # Aguardar serviços iniciarem
            logger.info("Aguardando serviços iniciarem...")
            time.sleep(5)
            
            # Verificar status dos serviços
            status = self.check_services()
            
            return status
        except Exception as e:
            logger.error(f"Erro ao iniciar serviços: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def stop_services(self, services=None):
        """
        Para os serviços especificados
        
        Args:
            services (list): Lista de serviços a serem parados (None para todos)
            
        Returns:
            dict: Status dos serviços
        """
        try:
            logger.info(f"Parando serviços: {services if services else 'todos'}")
            
            # Se nenhum serviço for especificado, parar todos
            if services is None:
                services = list(self.processes.keys())
            
            # Parar serviços
            for service in services:
                if service not in self.processes:
                    logger.error(f"Serviço não está rodando: {service}")
                    continue
                
                # Parar serviço
                process = self.processes[service]
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    logger.info(f"Serviço {service} parado com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao parar serviço {service}: {str(e)}")
                
                # Remover processo
                self.processes.pop(service)
            
            # Verificar status dos serviços
            status = self.check_services()
            
            return status
        except Exception as e:
            logger.error(f"Erro ao parar serviços: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def restart_services(self, services=None):
        """
        Reinicia os serviços especificados
        
        Args:
            services (list): Lista de serviços a serem reiniciados (None para todos)
            
        Returns:
            dict: Status dos serviços
        """
        try:
            logger.info(f"Reiniciando serviços: {services if services else 'todos'}")
            
            # Parar serviços
            self.stop_services(services)
            
            # Iniciar serviços
            status = self.start_services(services)
            
            return status
        except Exception as e:
            logger.error(f"Erro ao reiniciar serviços: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def check_services(self):
        """
        Verifica o status dos serviços
        
        Returns:
            dict: Status dos serviços
        """
        try:
            logger.info("Verificando status dos serviços...")
            
            # Verificar processos
            status = {}
            
            for service, process in self.processes.items():
                # Verificar se o processo está rodando
                if process.poll() is None:
                    status[service] = 'running'
                else:
                    status[service] = 'stopped'
            
            # Verificar serviços que não estão na lista de processos
            for service in self.scripts:
                if service not in status:
                    status[service] = 'not_started'
            
            # Verificar portas
            for service, port in self.ports.items():
                if status.get(service) == 'running':
                    # Verificar se a porta está em uso
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('localhost', port))
                    sock.close()
                    
                    if result == 0:
                        status[service] = 'running'
                    else:
                        status[service] = 'port_not_available'
            
            logger.info(f"Status dos serviços: {status}")
            
            return {
                'success': True,
                'status': status,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao verificar status dos serviços: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def run_tests(self):
        """
        Executa os testes do sistema
        
        Returns:
            dict: Resultados dos testes
        """
        try:
            logger.info("Executando testes do sistema...")
            
            # Verificar se o script de teste existe
            test_script = '/home/ubuntu/lotofacil/scripts/test/test_system.py'
            if not os.path.exists(test_script):
                logger.error(f"Script de teste não encontrado: {test_script}")
                return {'success': False, 'message': 'Script de teste não encontrado'}
            
            # Executar testes
            cmd = f"cd /home/ubuntu/lotofacil && python3 {test_script}"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            # Verificar resultado
            if process.returncode == 0:
                logger.info("Testes concluídos com sucesso")
                
                # Tentar extrair resultados detalhados
                try:
                    output = stdout.decode('utf-8')
                    results_start = output.find('{')
                    results_end = output.rfind('}') + 1
                    
                    if results_start >= 0 and results_end > results_start:
                        results_json = output[results_start:results_end]
                        results = json.loads(results_json)
                    else:
                        results = {'success': True, 'message': 'Testes concluídos com sucesso'}
                except Exception as e:
                    logger.error(f"Erro ao extrair resultados dos testes: {str(e)}")
                    results = {'success': True, 'message': 'Testes concluídos com sucesso'}
            else:
                logger.error(f"Falha nos testes: {stderr.decode('utf-8')}")
                results = {'success': False, 'message': stderr.decode('utf-8')}
            
            return results
        except Exception as e:
            logger.error(f"Erro ao executar testes: {str(e)}")
            return {'success': False, 'message': str(e)}

# Função principal
def main():
    """Função principal"""
    # Criar parser de argumentos
    parser = argparse.ArgumentParser(description='Gerenciador do sistema do Gerador de Jogos da Lotofácil')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'test'], help='Ação a ser executada')
    parser.add_argument('--services', nargs='+', help='Serviços a serem gerenciados (payment, lstm, ciclo, auth, main)')
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Criar sistema
    system = LotofacilSystem()
    
    # Executar ação
    if args.action == 'start':
        result = system.start_services(args.services)
    elif args.action == 'stop':
        result = system.stop_services(args.services)
    elif args.action == 'restart':
        result = system.restart_services(args.services)
    elif args.action == 'status':
        result = system.check_services()
    elif args.action == 'test':
        result = system.run_tests()
    
    # Imprimir resultado
    print(json.dumps(result, indent=4))
    
    # Retornar código de saída
    return 0 if result.get('success', False) else 1

if __name__ == "__main__":
    sys.exit(main())
