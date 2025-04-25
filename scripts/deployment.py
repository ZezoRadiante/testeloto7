#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para preparar o pacote de implantação do Gerador de Jogos da Lotofácil
"""

import os
import sys
import shutil
import subprocess
import logging
import json
import zipfile
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/deployment.log',
    filemode='a'
)
logger = logging.getLogger('deployment')

class DeploymentManager:
    """Classe para gerenciar a implantação do sistema"""
    
    def __init__(self):
        """Inicializa o gerenciador de implantação"""
        # Criar diretórios necessários
        os.makedirs('/home/ubuntu/lotofacil/logs', exist_ok=True)
        os.makedirs('/home/ubuntu/lotofacil/deployment', exist_ok=True)
        
        # Caminho do pacote de implantação
        self.deployment_dir = '/home/ubuntu/lotofacil/deployment'
        self.package_name = f"lotofacil_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.package_dir = os.path.join(self.deployment_dir, self.package_name)
        
        # Arquivos e diretórios a serem incluídos no pacote
        self.include_files = [
            '/home/ubuntu/lotofacil/app.py',
            '/home/ubuntu/lotofacil/scripts/main.py',
            '/home/ubuntu/lotofacil/README.md',
            '/home/ubuntu/lotofacil/requirements.txt'
        ]
        
        self.include_dirs = [
            '/home/ubuntu/lotofacil/scripts',
            '/home/ubuntu/lotofacil/templates',
            '/home/ubuntu/lotofacil/static',
            '/home/ubuntu/lotofacil/data'
        ]
        
        # Arquivos e diretórios a serem excluídos do pacote
        self.exclude_patterns = [
            '*.pyc',
            '__pycache__',
            '.git',
            '.gitignore',
            '*.log',
            'logs',
            'deployment'
        ]
    
    def create_requirements_file(self):
        """
        Cria o arquivo requirements.txt com as dependências do projeto
        
        Returns:
            bool: True se o arquivo foi criado com sucesso, False caso contrário
        """
        try:
            logger.info("Criando arquivo requirements.txt...")
            
            # Lista de dependências
            dependencies = [
                'flask==2.0.1',
                'requests==2.26.0',
                'numpy==1.21.2',
                'pandas==1.3.3',
                'tensorflow==2.6.0',
                'scikit-learn==1.0',
                'matplotlib==3.4.3',
                'pyjwt==2.1.0',
                'qrcode==7.3',
                'pillow==8.3.2'
            ]
            
            # Criar arquivo
            requirements_path = '/home/ubuntu/lotofacil/requirements.txt'
            
            with open(requirements_path, 'w', encoding='utf-8') as f:
                for dependency in dependencies:
                    f.write(f"{dependency}\n")
            
            logger.info(f"Arquivo requirements.txt criado com sucesso: {requirements_path}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao criar arquivo requirements.txt: {str(e)}")
            return False
    
    def create_readme_file(self):
        """
        Cria o arquivo README.md com instruções de implantação
        
        Returns:
            bool: True se o arquivo foi criado com sucesso, False caso contrário
        """
        try:
            logger.info("Criando arquivo README.md...")
            
            # Conteúdo do README
            readme_content = """# Gerador de Jogos da Lotofácil

Sistema completo para geração de jogos da Lotofácil com estratégias avançadas e IA LSTM.

## Requisitos

- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)
- Navegador web moderno

## Instalação

1. Extraia o conteúdo do pacote em um diretório de sua escolha
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração

1. Edite o arquivo `scripts/pagamento/mercadopago_integration.py` e verifique se a chave PIX está correta:

```python
self.pix_key = "42f51e7f-7586-4f26-a5b2-837ef34a0bfb"  # Chave PIX
```

2. Crie os diretórios necessários:

```bash
mkdir -p logs data/pagamentos data/usuarios data/emails data/modelos data/estrategias
```

## Inicialização

Para iniciar todos os serviços:

```bash
python scripts/main.py start
```

Para iniciar apenas serviços específicos:

```bash
python scripts/main.py start --services payment lstm ciclo auth
```

## Acesso

Após iniciar os serviços, acesse o sistema em:

```
http://localhost:5004
```

## Gerenciamento

- Verificar status dos serviços: `python scripts/main.py status`
- Parar serviços: `python scripts/main.py stop`
- Reiniciar serviços: `python scripts/main.py restart`
- Executar testes: `python scripts/main.py test`

## Estrutura do Sistema

- `app.py`: Aplicação principal
- `scripts/`: Scripts do sistema
  - `auth/`: Sistema de autenticação
  - `pagamento/`: Sistema de pagamento
  - `ia/`: IA LSTM para análise de dados
  - `estrategias/`: Estratégias de jogo, incluindo ciclo de dezenas fora
  - `test/`: Scripts de teste
- `templates/`: Templates HTML
- `static/`: Arquivos estáticos (CSS, JS, imagens)
- `data/`: Dados do sistema

## Planos de Assinatura

- Básico: R$ 39,90/mês
- Premium: R$ 69,90/mês (inclui estratégia exclusiva de ciclo de dezenas fora)

## Suporte

Para suporte, entre em contato pelo e-mail: suporte@geradorlotofacil.com.br
"""
            
            # Criar arquivo
            readme_path = '/home/ubuntu/lotofacil/README.md'
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logger.info(f"Arquivo README.md criado com sucesso: {readme_path}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao criar arquivo README.md: {str(e)}")
            return False
    
    def prepare_package_directory(self):
        """
        Prepara o diretório do pacote de implantação
        
        Returns:
            bool: True se o diretório foi preparado com sucesso, False caso contrário
        """
        try:
            logger.info(f"Preparando diretório do pacote: {self.package_dir}")
            
            # Criar diretório do pacote
            os.makedirs(self.package_dir, exist_ok=True)
            
            # Copiar arquivos
            for file_path in self.include_files:
                if os.path.exists(file_path):
                    shutil.copy2(file_path, self.package_dir)
                    logger.info(f"Arquivo copiado: {file_path}")
                else:
                    logger.warning(f"Arquivo não encontrado: {file_path}")
            
            # Copiar diretórios
            for dir_path in self.include_dirs:
                if os.path.exists(dir_path):
                    dir_name = os.path.basename(dir_path)
                    target_dir = os.path.join(self.package_dir, dir_name)
                    
                    # Copiar diretório recursivamente, excluindo padrões especificados
                    shutil.copytree(
                        dir_path,
                        target_dir,
                        ignore=shutil.ignore_patterns(*self.exclude_patterns),
                        dirs_exist_ok=True
                    )
                    
                    logger.info(f"Diretório copiado: {dir_path}")
                else:
                    logger.warning(f"Diretório não encontrado: {dir_path}")
            
            logger.info(f"Diretório do pacote preparado com sucesso: {self.package_dir}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao preparar diretório do pacote: {str(e)}")
            return False
    
    def create_zip_package(self):
        """
        Cria um arquivo ZIP do pacote de implantação
        
        Returns:
            str: Caminho do arquivo ZIP criado, None em caso de erro
        """
        try:
            logger.info("Criando arquivo ZIP do pacote...")
            
            # Caminho do arquivo ZIP
            zip_path = f"{self.package_dir}.zip"
            
            # Criar arquivo ZIP
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Adicionar arquivos e diretórios ao ZIP
                for root, dirs, files in os.walk(self.package_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.package_dir)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Arquivo ZIP criado com sucesso: {zip_path}")
            
            return zip_path
        except Exception as e:
            logger.error(f"Erro ao criar arquivo ZIP: {str(e)}")
            return None
    
    def deploy_to_production(self):
        """
        Implanta o sistema em ambiente de produção
        
        Returns:
            dict: Resultado da implantação
        """
        try:
            logger.info("Implantando sistema em ambiente de produção...")
            
            # Verificar se o diretório do pacote existe
            if not os.path.exists(self.package_dir):
                logger.error(f"Diretório do pacote não encontrado: {self.package_dir}")
                return {
                    'success': False,
                    'message': f"Diretório do pacote não encontrado: {self.package_dir}"
                }
            
            # Implantar usando a ferramenta de implantação
            from deploy_apply_deployment import deploy_apply_deployment
            
            result = deploy_apply_deployment(type="static", local_dir=self.package_dir)
            
            if result and 'url' in result:
                logger.info(f"Sistema implantado com sucesso: {result['url']}")
                return {
                    'success': True,
                    'url': result['url'],
                    'message': "Sistema implantado com sucesso"
                }
            else:
                logger.error("Falha ao implantar sistema")
                return {
                    'success': False,
                    'message': "Falha ao implantar sistema"
                }
        except Exception as e:
            logger.error(f"Erro ao implantar sistema: {str(e)}")
            return {
                'success': False,
                'message': f"Erro ao implantar sistema: {str(e)}"
            }
    
    def run(self):
        """
        Executa o processo completo de implantação
        
        Returns:
            dict: Resultado da implantação
        """
        try:
            logger.info("Iniciando processo de implantação...")
            
            # Criar arquivo requirements.txt
            self.create_requirements_file()
            
            # Criar arquivo README.md
            self.create_readme_file()
            
            # Preparar diretório do pacote
            self.prepare_package_directory()
            
            # Criar arquivo ZIP
            zip_path = self.create_zip_package()
            
            # Resultado da implantação
            result = {
                'success': True,
                'package_dir': self.package_dir,
                'zip_path': zip_path,
                'message': "Pacote de implantação criado com sucesso"
            }
            
            # Tentar implantar em produção
            try:
                deploy_result = self.deploy_to_production()
                result.update(deploy_result)
            except Exception as e:
                logger.warning(f"Implantação em produção não realizada: {str(e)}")
                result['deploy_message'] = f"Implantação em produção não realizada: {str(e)}"
            
            logger.info("Processo de implantação concluído com sucesso")
            
            return result
        except Exception as e:
            logger.error(f"Erro no processo de implantação: {str(e)}")
            return {
                'success': False,
                'message': f"Erro no processo de implantação: {str(e)}"
            }

# Função principal
def main():
    """Função principal"""
    # Criar gerenciador de implantação
    deployment = DeploymentManager()
    
    # Executar processo de implantação
    result = deployment.run()
    
    # Imprimir resultado
    print(json.dumps(result, indent=4))
    
    # Retornar código de saída
    return 0 if result.get('success', False) else 1

if __name__ == "__main__":
    sys.exit(main())
