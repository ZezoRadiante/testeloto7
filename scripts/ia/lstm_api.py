#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface web para o modelo LSTM da Lotofácil
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, render_template
import logging
from datetime import datetime
import base64
from io import BytesIO

# Importar o modelo LSTM
from lstm_model import LotofacilLSTM

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/lstm_api.log',
    filemode='a'
)
logger = logging.getLogger('lstm_api')

class LotofacilLSTMAPI:
    """Classe para interface web do modelo LSTM da Lotofácil"""
    
    def __init__(self):
        """Inicializa a API"""
        # Criar diretórios necessários
        os.makedirs('/home/ubuntu/lotofacil/logs', exist_ok=True)
        os.makedirs('/home/ubuntu/lotofacil/data/modelos', exist_ok=True)
        os.makedirs('/home/ubuntu/lotofacil/static/images/plots', exist_ok=True)
        
        # Inicializar modelo LSTM
        self.lstm = LotofacilLSTM(l1_reg=0.01, l2_reg=0.01)
        
        # Status do treinamento
        self.training_status = {
            'is_training': False,
            'progress': 0,
            'message': 'Não iniciado',
            'start_time': None,
            'end_time': None
        }
    
    def start_training(self, epochs=100, batch_size=32, sequence_length=5):
        """
        Inicia o treinamento do modelo LSTM
        
        Args:
            epochs (int): Número de épocas
            batch_size (int): Tamanho do batch
            sequence_length (int): Tamanho da sequência de concursos anteriores
            
        Returns:
            dict: Status do treinamento
        """
        try:
            # Verificar se já está treinando
            if self.training_status['is_training']:
                return {
                    'success': False,
                    'message': 'Treinamento já em andamento',
                    'status': self.training_status
                }
            
            # Atualizar status
            self.training_status = {
                'is_training': True,
                'progress': 0,
                'message': 'Preparando dados...',
                'start_time': datetime.now().isoformat(),
                'end_time': None
            }
            
            # Iniciar treinamento em thread separada
            import threading
            
            def train_thread():
                try:
                    # Preparar dados
                    self.training_status['message'] = 'Preparando dados...'
                    X_train, X_test, y_train, y_test = self.lstm.prepare_data(sequence_length=sequence_length)
                    
                    if X_train is None:
                        self.training_status['is_training'] = False
                        self.training_status['message'] = 'Falha ao preparar dados'
                        self.training_status['end_time'] = datetime.now().isoformat()
                        return
                    
                    # Construir modelo
                    self.training_status['message'] = 'Construindo modelo...'
                    self.training_status['progress'] = 10
                    self.lstm.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
                    
                    # Treinar modelo
                    self.training_status['message'] = 'Treinando modelo...'
                    
                    # Criar callback personalizado para atualizar progresso
                    class ProgressCallback(tf.keras.callbacks.Callback):
                        def on_epoch_end(self, epoch, logs=None):
                            progress = int(20 + (epoch + 1) / epochs * 70)
                            self.model.progress = progress
                            self.model.message = f'Treinando modelo... Época {epoch+1}/{epochs}'
                    
                    # Adicionar callback personalizado
                    callbacks = [ProgressCallback()]
                    
                    # Adicionar propriedades ao modelo para armazenar progresso
                    self.lstm.model.progress = 20
                    self.lstm.model.message = 'Treinando modelo... Época 0/{epochs}'
                    
                    # Treinar modelo
                    history = self.lstm.train(X_train, y_train, X_test, y_test, epochs=epochs, batch_size=batch_size)
                    
                    if history is None:
                        self.training_status['is_training'] = False
                        self.training_status['message'] = 'Falha ao treinar modelo'
                        self.training_status['end_time'] = datetime.now().isoformat()
                        return
                    
                    # Avaliar modelo
                    self.training_status['message'] = 'Avaliando modelo...'
                    self.training_status['progress'] = 90
                    metrics = self.lstm.evaluate(X_test, y_test)
                    
                    # Fazer previsões
                    self.training_status['message'] = 'Fazendo previsões...'
                    self.training_status['progress'] = 95
                    predictions = self.lstm.predict_next_draw(num_predictions=5)
                    
                    # Plotar histórico de treinamento
                    self.training_status['message'] = 'Gerando gráficos...'
                    self.training_status['progress'] = 98
                    plot_path = self.lstm.plot_training_history()
                    
                    # Treinamento concluído
                    self.training_status['is_training'] = False
                    self.training_status['progress'] = 100
                    self.training_status['message'] = 'Treinamento concluído com sucesso'
                    self.training_status['end_time'] = datetime.now().isoformat()
                    
                    # Salvar resultados
                    results = {
                        'metrics': metrics,
                        'predictions': predictions,
                        'plot_path': plot_path
                    }
                    
                    results_path = os.path.join('/home/ubuntu/lotofacil/data/modelos', 'training_results.json')
                    with open(results_path, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=4)
                    
                    logger.info("Treinamento concluído com sucesso")
                except Exception as e:
                    logger.error(f"Erro durante o treinamento: {str(e)}")
                    self.training_status['is_training'] = False
                    self.training_status['message'] = f'Erro durante o treinamento: {str(e)}'
                    self.training_status['end_time'] = datetime.now().isoformat()
            
            # Iniciar thread
            thread = threading.Thread(target=train_thread)
            thread.daemon = True
            thread.start()
            
            return {
                'success': True,
                'message': 'Treinamento iniciado com sucesso',
                'status': self.training_status
            }
        except Exception as e:
            logger.error(f"Erro ao iniciar treinamento: {str(e)}")
            self.training_status['is_training'] = False
            self.training_status['message'] = f'Erro ao iniciar treinamento: {str(e)}'
            self.training_status['end_time'] = datetime.now().isoformat()
            
            return {
                'success': False,
                'message': f'Erro ao iniciar treinamento: {str(e)}',
                'status': self.training_status
            }
    
    def get_training_status(self):
        """
        Obtém o status do treinamento
        
        Returns:
            dict: Status do treinamento
        """
        # Se estiver treinando, atualizar progresso com base no modelo
        if self.training_status['is_training'] and hasattr(self.lstm.model, 'progress'):
            self.training_status['progress'] = self.lstm.model.progress
            self.training_status['message'] = self.lstm.model.message
        
        return self.training_status
    
    def get_predictions(self, num_predictions=5):
        """
        Obtém previsões para o próximo sorteio
        
        Args:
            num_predictions (int): Número de previsões a serem feitas
            
        Returns:
            dict: Previsões
        """
        try:
            # Verificar se o modelo foi treinado
            if self.lstm.model is None:
                # Tentar carregar modelo salvo
                model_path = os.path.join('/home/ubuntu/lotofacil/data/modelos', 'final_model.h5')
                if os.path.exists(model_path):
                    self.lstm.model = tf.keras.models.load_model(model_path)
                else:
                    return {
                        'success': False,
                        'message': 'Modelo não treinado'
                    }
            
            # Fazer previsões
            predictions = self.lstm.predict_next_draw(num_predictions=num_predictions)
            
            if predictions is None:
                return {
                    'success': False,
                    'message': 'Falha ao fazer previsões'
                }
            
            return {
                'success': True,
                'predictions': predictions
            }
        except Exception as e:
            logger.error(f"Erro ao obter previsões: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao obter previsões: {str(e)}'
            }
    
    def get_training_history(self):
        """
        Obtém o histórico de treinamento
        
        Returns:
            dict: Histórico de treinamento
        """
        try:
            # Verificar se o histórico existe
            history_path = os.path.join('/home/ubuntu/lotofacil/data/modelos', 'training_history.json')
            if not os.path.exists(history_path):
                return {
                    'success': False,
                    'message': 'Histórico de treinamento não disponível'
                }
            
            # Carregar histórico
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Verificar se o plot existe
            plot_path = os.path.join('/home/ubuntu/lotofacil/data/modelos', 'training_history.png')
            plot_url = None
            
            if os.path.exists(plot_path):
                # Copiar para diretório estático
                import shutil
                static_plot_path = '/home/ubuntu/lotofacil/static/images/plots/training_history.png'
                shutil.copy(plot_path, static_plot_path)
                
                plot_url = '/static/images/plots/training_history.png'
            
            return {
                'success': True,
                'history': history,
                'plot_url': plot_url
            }
        except Exception as e:
            logger.error(f"Erro ao obter histórico de treinamento: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao obter histórico de treinamento: {str(e)}'
            }
    
    def get_metrics(self):
        """
        Obtém as métricas de avaliação do modelo
        
        Returns:
            dict: Métricas de avaliação
        """
        try:
            # Verificar se as métricas existem
            metrics_path = os.path.join('/home/ubuntu/lotofacil/data/modelos', 'evaluation_metrics.json')
            if not os.path.exists(metrics_path):
                return {
                    'success': False,
                    'message': 'Métricas de avaliação não disponíveis'
                }
            
            # Carregar métricas
            with open(metrics_path, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            
            return {
                'success': True,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"Erro ao obter métricas: {str(e)}")
            return {
                'success': False,
                'message': f'Erro ao obter métricas: {str(e)}'
            }

# Inicializar Flask
app = Flask(__name__, 
            template_folder='/home/ubuntu/lotofacil/templates',
            static_folder='/home/ubuntu/lotofacil/static')

# Inicializar API
lstm_api = LotofacilLSTMAPI()

@app.route('/api/lstm/train', methods=['POST'])
def train_model():
    """
    Inicia o treinamento do modelo LSTM
    
    Espera um JSON com os seguintes campos:
    - epochs (int): Número de épocas (opcional, padrão: 100)
    - batch_size (int): Tamanho do batch (opcional, padrão: 32)
    - sequence_length (int): Tamanho da sequência (opcional, padrão: 5)
    
    Retorna um JSON com o status do treinamento
    """
    try:
        data = request.json or {}
        
        epochs = data.get('epochs', 100)
        batch_size = data.get('batch_size', 32)
        sequence_length = data.get('sequence_length', 5)
        
        result = lstm_api.start_training(epochs=epochs, batch_size=batch_size, sequence_length=sequence_length)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao iniciar treinamento: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao iniciar treinamento: {str(e)}'
        }), 500

@app.route('/api/lstm/status', methods=['GET'])
def get_training_status():
    """
    Obtém o status do treinamento
    
    Retorna um JSON com o status do treinamento
    """
    try:
        status = lstm_api.get_training_status()
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Erro ao obter status do treinamento: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao obter status do treinamento: {str(e)}'
        }), 500

@app.route('/api/lstm/predictions', methods=['GET'])
def get_predictions():
    """
    Obtém previsões para o próximo sorteio
    
    Parâmetros de consulta:
    - num_predictions (int): Número de previsões a serem feitas (opcional, padrão: 5)
    
    Retorna um JSON com as previsões
    """
    try:
        num_predictions = request.args.get('num_predictions', 5, type=int)
        
        result = lstm_api.get_predictions(num_predictions=num_predictions)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao obter previsões: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao obter previsões: {str(e)}'
        }), 500

@app.route('/api/lstm/history', methods=['GET'])
def get_training_history():
    """
    Obtém o histórico de treinamento
    
    Retorna um JSON com o histórico de treinamento
    """
    try:
        result = lstm_api.get_training_history()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao obter histórico de treinamento: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao obter histórico de treinamento: {str(e)}'
        }), 500

@app.route('/api/lstm/metrics', methods=['GET'])
def get_metrics():
    """
    Obtém as métricas de avaliação do modelo
    
    Retorna um JSON com as métricas de avaliação
    """
    try:
        result = lstm_api.get_metrics()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao obter métricas: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=5001, debug=True)
