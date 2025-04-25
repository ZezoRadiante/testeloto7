#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implementação de modelo LSTM com regularização L1 e L2 para análise de dados da Lotofácil
"""

import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.regularizers import l1_l2
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import logging
import json
from datetime import datetime

# Importar o coletor de dados
from data_collector import LotofacilDataCollector

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/lstm_model.log',
    filemode='a'
)
logger = logging.getLogger('lstm_model')

class LotofacilLSTM:
    """Classe para implementação de modelo LSTM para análise de dados da Lotofácil"""
    
    def __init__(self, l1_reg=0.01, l2_reg=0.01):
        """
        Inicializa o modelo LSTM
        
        Args:
            l1_reg (float): Valor da regularização L1
            l2_reg (float): Valor da regularização L2
        """
        # Parâmetros de regularização
        self.l1_reg = l1_reg
        self.l2_reg = l2_reg
        
        # Caminhos para salvar o modelo e logs
        self.models_dir = '/home/ubuntu/lotofacil/data/modelos'
        self.logs_dir = '/home/ubuntu/lotofacil/logs/tensorboard'
        
        # Criar diretórios necessários
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Inicializar modelo
        self.model = None
        self.scaler = StandardScaler()
        
        # Métricas de treinamento
        self.history = None
        
        # Coletor de dados
        self.data_collector = LotofacilDataCollector()
    
    def build_model(self, input_shape):
        """
        Constrói o modelo LSTM
        
        Args:
            input_shape (tuple): Formato dos dados de entrada (sequence_length, num_features)
            
        Returns:
            model: Modelo Keras compilado
        """
        try:
            logger.info(f"Construindo modelo LSTM com input_shape={input_shape}")
            
            # Criar regularizador L1L2
            regularizer = l1_l2(l1=self.l1_reg, l2=self.l2_reg)
            
            # Construir modelo
            model = Sequential([
                LSTM(128, input_shape=input_shape, return_sequences=True, 
                     kernel_regularizer=regularizer, recurrent_regularizer=regularizer),
                Dropout(0.2),
                LSTM(64, return_sequences=False, 
                     kernel_regularizer=regularizer, recurrent_regularizer=regularizer),
                Dropout(0.2),
                Dense(32, activation='relu', kernel_regularizer=regularizer),
                Dropout(0.2),
                Dense(25, activation='sigmoid')  # 25 dezenas possíveis
            ])
            
            # Compilar modelo
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Resumo do modelo
            model.summary(print_fn=logger.info)
            
            self.model = model
            return model
        except Exception as e:
            logger.error(f"Erro ao construir modelo: {str(e)}")
            return None
    
    def prepare_data(self, sequence_length=5):
        """
        Prepara os dados para treinamento
        
        Args:
            sequence_length (int): Tamanho da sequência de concursos anteriores
            
        Returns:
            tuple: (X_train, X_test, y_train, y_test)
        """
        try:
            logger.info("Preparando dados para treinamento...")
            
            # Executar coleta e processamento de dados
            self.data_collector.run()
            
            # Criar dados de sequência
            X, y = self.data_collector.create_sequence_data(sequence_length=sequence_length)
            
            if X is None or y is None:
                logger.error("Falha ao criar dados de sequência.")
                return None, None, None, None
            
            # Dividir em conjuntos de treino e teste
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            logger.info(f"Dados preparados: X_train shape {X_train.shape}, y_train shape {y_train.shape}")
            
            return X_train, X_test, y_train, y_test
        except Exception as e:
            logger.error(f"Erro ao preparar dados: {str(e)}")
            return None, None, None, None
    
    def train(self, X_train, y_train, X_test, y_test, epochs=100, batch_size=32):
        """
        Treina o modelo LSTM
        
        Args:
            X_train (numpy.ndarray): Dados de treino
            y_train (numpy.ndarray): Alvos de treino
            X_test (numpy.ndarray): Dados de teste
            y_test (numpy.ndarray): Alvos de teste
            epochs (int): Número de épocas
            batch_size (int): Tamanho do batch
            
        Returns:
            history: Histórico de treinamento
        """
        try:
            logger.info(f"Iniciando treinamento com {epochs} épocas e batch_size={batch_size}")
            
            # Verificar se o modelo foi construído
            if self.model is None:
                logger.error("Modelo não construído. Chamando build_model...")
                self.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
            
            # Definir callbacks
            checkpoint_path = os.path.join(self.models_dir, 'best_model.h5')
            tensorboard_path = os.path.join(self.logs_dir, datetime.now().strftime("%Y%m%d-%H%M%S"))
            
            callbacks = [
                ModelCheckpoint(
                    filepath=checkpoint_path,
                    save_best_only=True,
                    monitor='val_accuracy',
                    mode='max',
                    verbose=1
                ),
                EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True,
                    verbose=1
                ),
                TensorBoard(
                    log_dir=tensorboard_path,
                    histogram_freq=1
                )
            ]
            
            # Treinar modelo
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_test, y_test),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=2
            )
            
            # Salvar histórico
            self.history = history.history
            
            # Salvar histórico em JSON
            history_path = os.path.join(self.models_dir, 'training_history.json')
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Treinamento concluído. Histórico salvo em {history_path}")
            
            # Salvar modelo final
            final_model_path = os.path.join(self.models_dir, 'final_model.h5')
            self.model.save(final_model_path)
            logger.info(f"Modelo final salvo em {final_model_path}")
            
            return history
        except Exception as e:
            logger.error(f"Erro ao treinar modelo: {str(e)}")
            return None
    
    def evaluate(self, X_test, y_test):
        """
        Avalia o modelo treinado
        
        Args:
            X_test (numpy.ndarray): Dados de teste
            y_test (numpy.ndarray): Alvos de teste
            
        Returns:
            dict: Métricas de avaliação
        """
        try:
            logger.info("Avaliando modelo...")
            
            # Verificar se o modelo foi treinado
            if self.model is None:
                logger.error("Modelo não treinado.")
                return None
            
            # Avaliar modelo
            loss, accuracy = self.model.evaluate(X_test, y_test, verbose=0)
            
            # Fazer previsões
            y_pred = self.model.predict(X_test)
            
            # Converter previsões para binário (0 ou 1)
            y_pred_binary = (y_pred > 0.5).astype(int)
            
            # Calcular métricas adicionais
            from sklearn.metrics import precision_score, recall_score, f1_score
            
            precision = precision_score(y_test, y_pred_binary, average='macro')
            recall = recall_score(y_test, y_pred_binary, average='macro')
            f1 = f1_score(y_test, y_pred_binary, average='macro')
            
            # Criar dicionário de métricas
            metrics = {
                'loss': float(loss),
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1': float(f1)
            }
            
            # Salvar métricas em JSON
            metrics_path = os.path.join(self.models_dir, 'evaluation_metrics.json')
            with open(metrics_path, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Avaliação concluída. Métricas: {metrics}")
            
            return metrics
        except Exception as e:
            logger.error(f"Erro ao avaliar modelo: {str(e)}")
            return None
    
    def predict_next_draw(self, num_predictions=5):
        """
        Faz previsões para o próximo sorteio
        
        Args:
            num_predictions (int): Número de previsões a serem feitas
            
        Returns:
            list: Lista de previsões (conjuntos de 15 dezenas)
        """
        try:
            logger.info(f"Fazendo {num_predictions} previsões para o próximo sorteio...")
            
            # Verificar se o modelo foi treinado
            if self.model is None:
                logger.error("Modelo não treinado.")
                return None
            
            # Carregar dados processados
            processed_data_path = self.data_collector.processed_data_path
            if not os.path.exists(processed_data_path):
                logger.error(f"Arquivo de dados processados não encontrado: {processed_data_path}")
                return None
            
            df = pd.read_csv(processed_data_path)
            
            # Selecionar apenas as colunas de dezenas
            dezenas_cols = [f'dezena_{i}' for i in range(1, 26)]
            dezenas_df = df[dezenas_cols]
            
            # Obter os últimos 5 concursos
            last_5_draws = dezenas_df.tail(5).values
            
            # Redimensionar para o formato esperado pelo modelo
            X_pred = np.array([last_5_draws])
            
            # Fazer previsão
            prediction = self.model.predict(X_pred)[0]
            
            # Obter as 15 dezenas com maior probabilidade
            top_15_indices = np.argsort(prediction)[-15:]
            
            # Converter índices para dezenas (1-25)
            top_15_dezenas = [i + 1 for i in top_15_indices]
            
            # Ordenar dezenas
            top_15_dezenas.sort()
            
            # Fazer múltiplas previsões
            predictions = []
            predictions.append(top_15_dezenas)
            
            # Para previsões adicionais, vamos perturbar ligeiramente as probabilidades
            for _ in range(num_predictions - 1):
                # Adicionar ruído às probabilidades
                noisy_prediction = prediction + np.random.normal(0, 0.1, prediction.shape)
                
                # Garantir que as probabilidades estejam entre 0 e 1
                noisy_prediction = np.clip(noisy_prediction, 0, 1)
                
                # Obter as 15 dezenas com maior probabilidade
                top_15_indices = np.argsort(noisy_prediction)[-15:]
                
                # Converter índices para dezenas (1-25)
                top_15_dezenas = [i + 1 for i in top_15_indices]
                
                # Ordenar dezenas
                top_15_dezenas.sort()
                
                predictions.append(top_15_dezenas)
            
            # Salvar previsões em JSON
            predictions_data = {
                'data': datetime.now().isoformat(),
                'predictions': predictions
            }
            
            predictions_path = os.path.join(self.models_dir, 'predictions.json')
            with open(predictions_path, 'w', encoding='utf-8') as f:
                json.dump(predictions_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Previsões concluídas e salvas em {predictions_path}")
            
            return predictions
        except Exception as e:
            logger.error(f"Erro ao fazer previsões: {str(e)}")
            return None
    
    def plot_training_history(self):
        """
        Plota o histórico de treinamento
        
        Returns:
            str: Caminho para a imagem salva
        """
        try:
            logger.info("Plotando histórico de treinamento...")
            
            # Verificar se o histórico existe
            if self.history is None:
                logger.error("Histórico de treinamento não disponível.")
                return None
            
            # Criar figura
            plt.figure(figsize=(12, 5))
            
            # Plot de acurácia
            plt.subplot(1, 2, 1)
            plt.plot(self.history['accuracy'], label='Treino')
            plt.plot(self.history['val_accuracy'], label='Validação')
            plt.title('Acurácia do Modelo')
            plt.xlabel('Época')
            plt.ylabel('Acurácia')
            plt.legend()
            
            # Plot de perda
            plt.subplot(1, 2, 2)
            plt.plot(self.history['loss'], label='Treino')
            plt.plot(self.history['val_loss'], label='Validação')
            plt.title('Perda do Modelo')
            plt.xlabel('Época')
            plt.ylabel('Perda')
            plt.legend()
            
            # Salvar figura
            plt.tight_layout()
            plot_path = os.path.join(self.models_dir, 'training_history.png')
            plt.savefig(plot_path)
            plt.close()
            
            logger.info(f"Histórico de treinamento plotado e salvo em {plot_path}")
            
            return plot_path
        except Exception as e:
            logger.error(f"Erro ao plotar histórico de treinamento: {str(e)}")
            return None
    
    def run_full_pipeline(self, sequence_length=5, epochs=100, batch_size=32):
        """
        Executa o pipeline completo: preparação de dados, treinamento, avaliação e previsão
        
        Args:
            sequence_length (int): Tamanho da sequência de concursos anteriores
            epochs (int): Número de épocas
            batch_size (int): Tamanho do batch
            
        Returns:
            dict: Resultados do pipeline
        """
        try:
            logger.info("Iniciando pipeline completo...")
            
            # Preparar dados
            X_train, X_test, y_train, y_test = self.prepare_data(sequence_length=sequence_length)
            
            if X_train is None:
                logger.error("Falha ao preparar dados. Pipeline interrompido.")
                return None
            
            # Construir modelo
            self.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
            
            # Treinar modelo
            history = self.train(X_train, y_train, X_test, y_test, epochs=epochs, batch_size=batch_size)
            
            if history is None:
                logger.error("Falha ao treinar modelo. Pipeline interrompido.")
                return None
            
            # Avaliar modelo
            metrics = self.evaluate(X_test, y_test)
            
            # Fazer previsões
            predictions = self.predict_next_draw(num_predictions=5)
            
            # Plotar histórico de treinamento
            plot_path = self.plot_training_history()
            
            # Resultados do pipeline
            results = {
                'metrics': metrics,
                'predictions': predictions,
                'plot_path': plot_path
            }
            
            logger.info("Pipeline completo concluído com sucesso.")
            
            return results
        except Exception as e:
            logger.error(f"Erro ao executar pipeline completo: {str(e)}")
            return None

# Função para testar o modelo LSTM
def test_lstm_model():
    """Testa o modelo LSTM"""
    # Criar modelo
    lstm = LotofacilLSTM(l1_reg=0.01, l2_reg=0.01)
    
    # Executar pipeline completo
    results = lstm.run_full_pipeline(sequence_length=5, epochs=10, batch_size=32)
    
    if results is not None:
        print("Pipeline completo concluído com sucesso.")
        print(f"Métricas: {results['metrics']}")
        print(f"Previsões: {results['predictions']}")
        print(f"Plot: {results['plot_path']}")
    else:
        print("Falha ao executar pipeline completo.")
    
    return results is not None

if __name__ == "__main__":
    test_lstm_model()
