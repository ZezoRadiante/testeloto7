#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Flask para a estratégia de Ciclo de Dezenas Fora
"""

import os
import json
from flask import Flask, request, jsonify, render_template
import logging
from datetime import datetime
import shutil

# Importar a estratégia de Ciclo de Dezenas Fora
from ciclo_dezenas_fora import CicloDezenasFora

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/ciclo_api.log',
    filemode='a'
)
logger = logging.getLogger('ciclo_api')

class CicloDezenasForaAPI:
    """Classe para API da estratégia de Ciclo de Dezenas Fora"""
    
    def __init__(self):
        """Inicializa a API"""
        # Criar diretórios necessários
        os.makedirs('/home/ubuntu/lotofacil/logs', exist_ok=True)
        os.makedirs('/home/ubuntu/lotofacil/data/estrategias', exist_ok=True)
        os.makedirs('/home/ubuntu/lotofacil/static/images/plots', exist_ok=True)
        
        # Inicializar estratégia
        self.ciclo = CicloDezenasFora()
    
    def analisar_ciclo(self):
        """
        Analisa o ciclo atual
        
        Returns:
            dict: Análise do ciclo atual
        """
        try:
            logger.info("Analisando ciclo atual via API...")
            
            # Executar análise
            analise = self.ciclo.analisar_ciclo_atual()
            
            if analise is None:
                return {
                    'success': False,
                    'message': 'Falha ao analisar ciclo'
                }
            
            # Plotar ciclo
            plot_path = self.ciclo.plotar_ciclo()
            
            # Copiar para diretório estático se necessário
            if plot_path and os.path.exists(plot_path):
                static_plot_path = '/home/ubuntu/lotofacil/static/images/plots/ciclo_dezenas.png'
                if plot_path != static_plot_path:
                    shutil.copy(plot_path, static_plot_path)
                
                plot_url = '/static/images/plots/ciclo_dezenas.png'
            else:
                plot_url = None
            
            return {
                'success': True,
                'analise': analise,
                'plot_url': plot_url
            }
        except Exception as e:
            logger.error(f"Erro ao analisar ciclo: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao analisar ciclo: {str(e)}'
            }
    
    def gerar_jogos(self, num_jogos=5):
        """
        Gera jogos com base no ciclo atual
        
        Args:
            num_jogos (int): Número de jogos a serem gerados
            
        Returns:
            dict: Jogos gerados
        """
        try:
            logger.info(f"Gerando {num_jogos} jogos via API...")
            
            # Gerar jogos
            jogos = self.ciclo.gerar_jogos(num_jogos=num_jogos)
            
            if jogos is None:
                return {
                    'success': False,
                    'message': 'Falha ao gerar jogos'
                }
            
            return {
                'success': True,
                'jogos': jogos
            }
        except Exception as e:
            logger.error(f"Erro ao gerar jogos: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao gerar jogos: {str(e)}'
            }
    
    def iniciar_ciclo(self):
        """
        Inicia um novo ciclo de dezenas fora
        
        Returns:
            dict: Informações do ciclo iniciado
        """
        try:
            logger.info("Iniciando novo ciclo via API...")
            
            # Iniciar ciclo
            ciclo = self.ciclo.iniciar_ciclo()
            
            if ciclo is None:
                return {
                    'success': False,
                    'message': 'Falha ao iniciar ciclo'
                }
            
            return {
                'success': True,
                'ciclo': ciclo
            }
        except Exception as e:
            logger.error(f"Erro ao iniciar ciclo: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao iniciar ciclo: {str(e)}'
            }
    
    def atualizar_ciclo(self):
        """
        Atualiza o ciclo atual com os novos sorteios
        
        Returns:
            dict: Informações do ciclo atualizado
        """
        try:
            logger.info("Atualizando ciclo via API...")
            
            # Atualizar ciclo
            ciclo = self.ciclo.atualizar_ciclo()
            
            if ciclo is None:
                return {
                    'success': False,
                    'message': 'Falha ao atualizar ciclo'
                }
            
            return {
                'success': True,
                'ciclo': ciclo
            }
        except Exception as e:
            logger.error(f"Erro ao atualizar ciclo: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao atualizar ciclo: {str(e)}'
            }
    
    def executar_pipeline(self):
        """
        Executa o pipeline completo
        
        Returns:
            dict: Resultados do pipeline
        """
        try:
            logger.info("Executando pipeline completo via API...")
            
            # Executar pipeline
            resultados = self.ciclo.run()
            
            if resultados is None:
                return {
                    'success': False,
                    'message': 'Falha ao executar pipeline'
                }
            
            # Copiar plot para diretório estático se necessário
            plot_path = resultados.get('plot_path')
            if plot_path and os.path.exists(plot_path):
                static_plot_path = '/home/ubuntu/lotofacil/static/images/plots/ciclo_dezenas.png'
                if plot_path != static_plot_path:
                    shutil.copy(plot_path, static_plot_path)
                
                resultados['plot_url'] = '/static/images/plots/ciclo_dezenas.png'
            
            return {
                'success': True,
                'resultados': resultados
            }
        except Exception as e:
            logger.error(f"Erro ao executar pipeline: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao executar pipeline: {str(e)}'
            }

# Inicializar Flask
app = Flask(__name__, 
            template_folder='/home/ubuntu/lotofacil/templates',
            static_folder='/home/ubuntu/lotofacil/static')

# Inicializar API
ciclo_api = CicloDezenasForaAPI()

@app.route('/api/ciclo/analisar', methods=['GET'])
def analisar_ciclo():
    """
    Analisa o ciclo atual
    
    Retorna um JSON com a análise do ciclo atual
    """
    try:
        resultado = ciclo_api.analisar_ciclo()
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao analisar ciclo: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao analisar ciclo: {str(e)}'
        }), 500

@app.route('/api/ciclo/gerar-jogos', methods=['GET'])
def gerar_jogos():
    """
    Gera jogos com base no ciclo atual
    
    Parâmetros de consulta:
    - num_jogos (int): Número de jogos a serem gerados (opcional, padrão: 5)
    
    Retorna um JSON com os jogos gerados
    """
    try:
        num_jogos = request.args.get('num_jogos', 5, type=int)
        resultado = ciclo_api.gerar_jogos(num_jogos=num_jogos)
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao gerar jogos: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar jogos: {str(e)}'
        }), 500

@app.route('/api/ciclo/iniciar', methods=['POST'])
def iniciar_ciclo():
    """
    Inicia um novo ciclo de dezenas fora
    
    Retorna um JSON com as informações do ciclo iniciado
    """
    try:
        resultado = ciclo_api.iniciar_ciclo()
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao iniciar ciclo: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao iniciar ciclo: {str(e)}'
        }), 500

@app.route('/api/ciclo/atualizar', methods=['POST'])
def atualizar_ciclo():
    """
    Atualiza o ciclo atual com os novos sorteios
    
    Retorna um JSON com as informações do ciclo atualizado
    """
    try:
        resultado = ciclo_api.atualizar_ciclo()
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao atualizar ciclo: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar ciclo: {str(e)}'
        }), 500

@app.route('/api/ciclo/pipeline', methods=['POST'])
def executar_pipeline():
    """
    Executa o pipeline completo
    
    Retorna um JSON com os resultados do pipeline
    """
    try:
        resultado = ciclo_api.executar_pipeline()
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao executar pipeline: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao executar pipeline: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=5002, debug=True)
