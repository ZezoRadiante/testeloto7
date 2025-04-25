#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implementação da estratégia de Ciclo de Dezenas Fora para a Lotofácil
"""

import os
import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/lotofacil/logs/ciclo_dezenas.log',
    filemode='a'
)
logger = logging.getLogger('ciclo_dezenas')

class CicloDezenasFora:
    """Classe para implementação da estratégia de Ciclo de Dezenas Fora"""
    
    def __init__(self):
        """Inicializa a estratégia de Ciclo de Dezenas Fora"""
        # Criar diretórios necessários
        os.makedirs('/home/ubuntu/lotofacil/logs', exist_ok=True)
        os.makedirs('/home/ubuntu/lotofacil/data/estrategias', exist_ok=True)
        os.makedirs('/home/ubuntu/lotofacil/static/images/plots', exist_ok=True)
        
        # Caminhos dos arquivos
        self.data_path = '/home/ubuntu/lotofacil/data/historico/lotofacil_raw.csv'
        self.ciclos_path = '/home/ubuntu/lotofacil/data/estrategias/ciclos_dezenas.json'
        
        # Número de dezenas no ciclo
        self.num_dezenas_ciclo = 10
        
        # Ciclo atual
        self.ciclo_atual = None
    
    def carregar_dados(self):
        """
        Carrega os dados históricos da Lotofácil
        
        Returns:
            pandas.DataFrame: DataFrame com os dados históricos
        """
        try:
            logger.info("Carregando dados históricos...")
            
            # Verificar se o arquivo existe
            if not os.path.exists(self.data_path):
                logger.error(f"Arquivo de dados não encontrado: {self.data_path}")
                return None
            
            # Carregar dados
            df = pd.read_csv(self.data_path)
            
            # Ordenar por número do concurso
            df = df.sort_values('concurso')
            
            logger.info(f"Dados carregados com sucesso: {len(df)} concursos")
            
            return df
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            return None
    
    def identificar_dezenas_fora(self, df, num_concursos=10):
        """
        Identifica as dezenas que ficaram fora nos últimos concursos
        
        Args:
            df (pandas.DataFrame): DataFrame com os dados históricos
            num_concursos (int): Número de concursos a considerar
            
        Returns:
            dict: Dicionário com as dezenas que ficaram fora e suas frequências
        """
        try:
            logger.info(f"Identificando dezenas fora nos últimos {num_concursos} concursos...")
            
            # Obter os últimos concursos
            ultimos_concursos = df.tail(num_concursos)
            
            # Extrair todas as dezenas sorteadas
            todas_dezenas = []
            for dezenas_str in ultimos_concursos['dezenas']:
                dezenas = [int(d) for d in dezenas_str.split(',')]
                todas_dezenas.extend(dezenas)
            
            # Contar frequência de cada dezena
            contador = Counter(todas_dezenas)
            
            # Identificar dezenas que ficaram fora ou apareceram menos vezes
            todas_possiveis = set(range(1, 26))
            dezenas_sorteadas = set(contador.keys())
            dezenas_fora = todas_possiveis - dezenas_sorteadas
            
            # Criar dicionário com frequências (0 para dezenas que ficaram fora)
            frequencias = {dezena: 0 for dezena in dezenas_fora}
            
            # Adicionar dezenas que apareceram poucas vezes
            for dezena, freq in contador.items():
                if freq <= num_concursos // 3:  # Dezenas que apareceram em menos de 1/3 dos concursos
                    frequencias[dezena] = freq
            
            # Ordenar por frequência
            frequencias = dict(sorted(frequencias.items(), key=lambda x: x[1]))
            
            logger.info(f"Dezenas fora identificadas: {frequencias}")
            
            return frequencias
        except Exception as e:
            logger.error(f"Erro ao identificar dezenas fora: {str(e)}")
            return None
    
    def iniciar_ciclo(self, df=None):
        """
        Inicia um novo ciclo de dezenas fora
        
        Args:
            df (pandas.DataFrame): DataFrame com os dados históricos (opcional)
            
        Returns:
            dict: Informações do ciclo iniciado
        """
        try:
            logger.info("Iniciando novo ciclo de dezenas fora...")
            
            # Carregar dados se não fornecidos
            if df is None:
                df = self.carregar_dados()
                
                if df is None:
                    logger.error("Falha ao carregar dados. Ciclo não iniciado.")
                    return None
            
            # Identificar dezenas fora
            frequencias = self.identificar_dezenas_fora(df, num_concursos=10)
            
            if frequencias is None:
                logger.error("Falha ao identificar dezenas fora. Ciclo não iniciado.")
                return None
            
            # Selecionar as 10 dezenas com menor frequência
            dezenas_ciclo = list(frequencias.keys())[:self.num_dezenas_ciclo]
            
            # Criar ciclo
            ciclo = {
                'id': datetime.now().strftime('%Y%m%d%H%M%S'),
                'data_inicio': datetime.now().isoformat(),
                'concurso_inicio': int(df['concurso'].max()),
                'dezenas': dezenas_ciclo,
                'dezenas_sorteadas': [],
                'concursos': [],
                'status': 'ativo',
                'data_fechamento': None,
                'concurso_fechamento': None
            }
            
            # Salvar ciclo
            self.ciclo_atual = ciclo
            self.salvar_ciclos()
            
            logger.info(f"Novo ciclo iniciado: {ciclo}")
            
            return ciclo
        except Exception as e:
            logger.error(f"Erro ao iniciar ciclo: {str(e)}")
            return None
    
    def atualizar_ciclo(self, df=None):
        """
        Atualiza o ciclo atual com os novos sorteios
        
        Args:
            df (pandas.DataFrame): DataFrame com os dados históricos (opcional)
            
        Returns:
            dict: Informações do ciclo atualizado
        """
        try:
            logger.info("Atualizando ciclo atual...")
            
            # Verificar se existe um ciclo ativo
            if self.ciclo_atual is None:
                self.carregar_ciclos()
                
                if self.ciclo_atual is None:
                    logger.warning("Nenhum ciclo ativo encontrado. Iniciando novo ciclo...")
                    return self.iniciar_ciclo(df)
            
            # Carregar dados se não fornecidos
            if df is None:
                df = self.carregar_dados()
                
                if df is None:
                    logger.error("Falha ao carregar dados. Ciclo não atualizado.")
                    return None
            
            # Obter concursos após o início do ciclo
            concurso_inicio = self.ciclo_atual['concurso_inicio']
            novos_concursos = df[df['concurso'] > concurso_inicio]
            
            if len(novos_concursos) == 0:
                logger.info("Nenhum novo concurso encontrado. Ciclo não atualizado.")
                return self.ciclo_atual
            
            # Atualizar ciclo com novos concursos
            for _, concurso in novos_concursos.iterrows():
                concurso_num = int(concurso['concurso'])
                dezenas = [int(d) for d in concurso['dezenas'].split(',')]
                
                # Verificar se alguma dezena do ciclo foi sorteada
                dezenas_sorteadas = []
                for dezena in self.ciclo_atual['dezenas']:
                    if dezena in dezenas and dezena not in self.ciclo_atual['dezenas_sorteadas']:
                        dezenas_sorteadas.append(dezena)
                
                # Adicionar concurso ao ciclo
                self.ciclo_atual['concursos'].append({
                    'concurso': concurso_num,
                    'data': concurso['data'],
                    'dezenas': dezenas,
                    'dezenas_ciclo_sorteadas': dezenas_sorteadas
                })
                
                # Atualizar dezenas sorteadas
                self.ciclo_atual['dezenas_sorteadas'].extend(dezenas_sorteadas)
                self.ciclo_atual['dezenas_sorteadas'] = sorted(list(set(self.ciclo_atual['dezenas_sorteadas'])))
                
                # Verificar se o ciclo foi fechado
                if len(self.ciclo_atual['dezenas_sorteadas']) == self.num_dezenas_ciclo:
                    self.ciclo_atual['status'] = 'fechado'
                    self.ciclo_atual['data_fechamento'] = datetime.now().isoformat()
                    self.ciclo_atual['concurso_fechamento'] = concurso_num
                    
                    logger.info(f"Ciclo fechado no concurso {concurso_num}")
                    
                    # Iniciar novo ciclo
                    self.salvar_ciclos()
                    self.ciclo_atual = None
                    return self.iniciar_ciclo(df)
            
            # Salvar ciclo atualizado
            self.salvar_ciclos()
            
            logger.info(f"Ciclo atualizado: {self.ciclo_atual}")
            
            return self.ciclo_atual
        except Exception as e:
            logger.error(f"Erro ao atualizar ciclo: {str(e)}")
            return None
    
    def carregar_ciclos(self):
        """
        Carrega os ciclos salvos
        
        Returns:
            list: Lista de ciclos
        """
        try:
            logger.info("Carregando ciclos salvos...")
            
            # Verificar se o arquivo existe
            if not os.path.exists(self.ciclos_path):
                logger.warning(f"Arquivo de ciclos não encontrado: {self.ciclos_path}")
                return []
            
            # Carregar ciclos
            with open(self.ciclos_path, 'r', encoding='utf-8') as f:
                ciclos = json.load(f)
            
            # Identificar ciclo ativo
            for ciclo in ciclos:
                if ciclo['status'] == 'ativo':
                    self.ciclo_atual = ciclo
                    break
            
            logger.info(f"Ciclos carregados: {len(ciclos)}")
            
            return ciclos
        except Exception as e:
            logger.error(f"Erro ao carregar ciclos: {str(e)}")
            return []
    
    def salvar_ciclos(self):
        """
        Salva os ciclos
        
        Returns:
            bool: True se os ciclos foram salvos com sucesso, False caso contrário
        """
        try:
            logger.info("Salvando ciclos...")
            
            # Carregar ciclos existentes
            ciclos = self.carregar_ciclos()
            
            # Verificar se o ciclo atual já existe
            if self.ciclo_atual is not None:
                ciclo_existente = False
                
                for i, ciclo in enumerate(ciclos):
                    if ciclo['id'] == self.ciclo_atual['id']:
                        ciclos[i] = self.ciclo_atual
                        ciclo_existente = True
                        break
                
                if not ciclo_existente:
                    ciclos.append(self.ciclo_atual)
            
            # Salvar ciclos
            with open(self.ciclos_path, 'w', encoding='utf-8') as f:
                json.dump(ciclos, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Ciclos salvos: {len(ciclos)}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar ciclos: {str(e)}")
            return False
    
    def gerar_jogos(self, num_jogos=5):
        """
        Gera jogos com base no ciclo atual
        
        Args:
            num_jogos (int): Número de jogos a serem gerados
            
        Returns:
            list: Lista de jogos gerados
        """
        try:
            logger.info(f"Gerando {num_jogos} jogos com base no ciclo atual...")
            
            # Verificar se existe um ciclo ativo
            if self.ciclo_atual is None:
                self.carregar_ciclos()
                
                if self.ciclo_atual is None:
                    logger.warning("Nenhum ciclo ativo encontrado. Iniciando novo ciclo...")
                    df = self.carregar_dados()
                    self.iniciar_ciclo(df)
            
            # Obter dezenas que ainda não foram sorteadas
            dezenas_pendentes = [d for d in self.ciclo_atual['dezenas'] if d not in self.ciclo_atual['dezenas_sorteadas']]
            
            # Carregar dados
            df = self.carregar_dados()
            
            if df is None:
                logger.error("Falha ao carregar dados. Jogos não gerados.")
                return None
            
            # Obter último concurso
            ultimo_concurso = df.iloc[-1]
            dezenas_ultimo = [int(d) for d in ultimo_concurso['dezenas'].split(',')]
            
            # Gerar jogos
            jogos = []
            
            for _ in range(num_jogos):
                # Incluir dezenas pendentes do ciclo
                jogo = dezenas_pendentes.copy()
                
                # Completar com dezenas aleatórias que não estão no ciclo
                dezenas_disponiveis = [d for d in range(1, 26) if d not in self.ciclo_atual['dezenas']]
                
                # Priorizar dezenas que apareceram no último concurso
                for d in dezenas_ultimo:
                    if d in dezenas_disponiveis and len(jogo) < 15:
                        jogo.append(d)
                        dezenas_disponiveis.remove(d)
                
                # Completar com dezenas aleatórias
                np.random.shuffle(dezenas_disponiveis)
                jogo.extend(dezenas_disponiveis[:15 - len(jogo)])
                
                # Ordenar jogo
                jogo.sort()
                
                jogos.append(jogo)
            
            logger.info(f"Jogos gerados: {jogos}")
            
            return jogos
        except Exception as e:
            logger.error(f"Erro ao gerar jogos: {str(e)}")
            return None
    
    def analisar_ciclo_atual(self):
        """
        Analisa o ciclo atual
        
        Returns:
            dict: Análise do ciclo atual
        """
        try:
            logger.info("Analisando ciclo atual...")
            
            # Verificar se existe um ciclo ativo
            if self.ciclo_atual is None:
                self.carregar_ciclos()
                
                if self.ciclo_atual is None:
                    logger.warning("Nenhum ciclo ativo encontrado. Iniciando novo ciclo...")
                    df = self.carregar_dados()
                    self.iniciar_ciclo(df)
            
            # Calcular estatísticas do ciclo
            dezenas_sorteadas = self.ciclo_atual['dezenas_sorteadas']
            dezenas_pendentes = [d for d in self.ciclo_atual['dezenas'] if d not in dezenas_sorteadas]
            
            # Calcular progresso do ciclo
            progresso = len(dezenas_sorteadas) / self.num_dezenas_ciclo * 100
            
            # Calcular média de concursos por dezena
            concursos_por_dezena = []
            
            if len(self.ciclo_atual['concursos']) > 0:
                concurso_inicio = self.ciclo_atual['concurso_inicio']
                
                for dezena in dezenas_sorteadas:
                    # Encontrar o concurso em que a dezena foi sorteada
                    for concurso in self.ciclo_atual['concursos']:
                        if dezena in concurso['dezenas_ciclo_sorteadas']:
                            concursos_por_dezena.append(concurso['concurso'] - concurso_inicio)
                            break
                
                media_concursos = sum(concursos_por_dezena) / len(concursos_por_dezena) if len(concursos_por_dezena) > 0 else 0
            else:
                media_concursos = 0
            
            # Estimar concursos restantes para fechar o ciclo
            if len(dezenas_pendentes) > 0 and media_concursos > 0:
                estimativa_concursos = media_concursos * len(dezenas_pendentes)
            else:
                estimativa_concursos = len(dezenas_pendentes) * 2  # Estimativa conservadora
            
            # Criar análise
            analise = {
                'ciclo_id': self.ciclo_atual['id'],
                'data_inicio': self.ciclo_atual['data_inicio'],
                'concurso_inicio': self.ciclo_atual['concurso_inicio'],
                'dezenas_ciclo': self.ciclo_atual['dezenas'],
                'dezenas_sorteadas': dezenas_sorteadas,
                'dezenas_pendentes': dezenas_pendentes,
                'progresso': progresso,
                'num_concursos': len(self.ciclo_atual['concursos']),
                'media_concursos_por_dezena': media_concursos,
                'estimativa_concursos_restantes': estimativa_concursos,
                'status': self.ciclo_atual['status']
            }
            
            logger.info(f"Análise do ciclo: {analise}")
            
            return analise
        except Exception as e:
            logger.error(f"Erro ao analisar ciclo: {str(e)}")
            return None
    
    def plotar_ciclo(self):
        """
        Plota o ciclo atual
        
        Returns:
            str: Caminho para a imagem salva
        """
        try:
            logger.info("Plotando ciclo atual...")
            
            # Verificar se existe um ciclo ativo
            if self.ciclo_atual is None:
                self.carregar_ciclos()
                
                if self.ciclo_atual is None:
                    logger.warning("Nenhum ciclo ativo encontrado. Iniciando novo ciclo...")
                    df = self.carregar_dados()
                    self.iniciar_ciclo(df)
            
            # Criar figura
            plt.figure(figsize=(12, 8))
            
            # Plotar dezenas do ciclo
            dezenas = list(range(1, 26))
            status = ['Fora do Ciclo'] * 25
            
            for i, dezena in enumerate(dezenas):
                if dezena in self.ciclo_atual['dezenas']:
                    if dezena in self.ciclo_atual['dezenas_sorteadas']:
                        status[i] = 'Sorteada'
                    else:
                        status[i] = 'Pendente'
            
            # Definir cores
            cores = []
            for s in status:
                if s == 'Fora do Ciclo':
                    cores.append('gray')
                elif s == 'Sorteada':
                    cores.append('green')
                else:
                    cores.append('red')
            
            # Plotar barras
            plt.bar(dezenas, [1] * 25, color=cores)
            
            # Adicionar rótulos
            for i, dezena in enumerate(dezenas):
                plt.text(dezena, 0.5, str(dezena), ha='center', va='center', fontweight='bold')
            
            # Adicionar legenda
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='gray', label='Fora do Ciclo'),
                Patch(facecolor='red', label='Pendente'),
                Patch(facecolor='green', label='Sorteada')
            ]
            plt.legend(handles=legend_elements, loc='upper right')
            
            # Adicionar título e rótulos
            plt.title(f"Ciclo de Dezenas Fora - Progresso: {len(self.ciclo_atual['dezenas_sorteadas'])}/{self.num_dezenas_ciclo}")
            plt.xlabel('Dezenas')
            plt.yticks([])
            
            # Adicionar informações do ciclo
            info_text = f"Ciclo iniciado no concurso {self.ciclo_atual['concurso_inicio']}\n"
            info_text += f"Dezenas sorteadas: {', '.join(map(str, self.ciclo_atual['dezenas_sorteadas']))}\n"
            
            dezenas_pendentes = [d for d in self.ciclo_atual['dezenas'] if d not in self.ciclo_atual['dezenas_sorteadas']]
            info_text += f"Dezenas pendentes: {', '.join(map(str, dezenas_pendentes))}"
            
            plt.figtext(0.5, 0.01, info_text, ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
            
            # Salvar figura
            plt.tight_layout()
            plot_path = '/home/ubuntu/lotofacil/static/images/plots/ciclo_dezenas.png'
            plt.savefig(plot_path)
            plt.close()
            
            logger.info(f"Ciclo plotado e salvo em {plot_path}")
            
            return plot_path
        except Exception as e:
            logger.error(f"Erro ao plotar ciclo: {str(e)}")
            return None
    
    def run(self):
        """
        Executa o pipeline completo: carrega dados, atualiza ciclo, analisa ciclo e gera jogos
        
        Returns:
            dict: Resultados do pipeline
        """
        try:
            logger.info("Iniciando pipeline completo...")
            
            # Carregar dados
            df = self.carregar_dados()
            
            if df is None:
                logger.error("Falha ao carregar dados. Pipeline interrompido.")
                return None
            
            # Atualizar ciclo
            ciclo = self.atualizar_ciclo(df)
            
            if ciclo is None:
                logger.error("Falha ao atualizar ciclo. Pipeline interrompido.")
                return None
            
            # Analisar ciclo
            analise = self.analisar_ciclo_atual()
            
            # Gerar jogos
            jogos = self.gerar_jogos(num_jogos=5)
            
            # Plotar ciclo
            plot_path = self.plotar_ciclo()
            
            # Resultados do pipeline
            resultados = {
                'ciclo': ciclo,
                'analise': analise,
                'jogos': jogos,
                'plot_path': plot_path
            }
            
            logger.info("Pipeline completo concluído com sucesso.")
            
            return resultados
        except Exception as e:
            logger.error(f"Erro ao executar pipeline completo: {str(e)}")
            return None

# Função para testar a estratégia de Ciclo de Dezenas Fora
def test_ciclo_dezenas():
    """Testa a estratégia de Ciclo de Dezenas Fora"""
    # Criar instância
    ciclo = CicloDezenasFora()
    
    # Executar pipeline completo
    resultados = ciclo.run()
    
    if resultados is not None:
        print("Pipeline completo concluído com sucesso.")
        print(f"Ciclo: {resultados['ciclo']['id']}")
        print(f"Dezenas do ciclo: {resultados['ciclo']['dezenas']}")
        print(f"Dezenas sorteadas: {resultados['ciclo']['dezenas_sorteadas']}")
        print(f"Progresso: {resultados['analise']['progresso']:.2f}%")
        print(f"Jogos gerados: {resultados['jogos']}")
        print(f"Plot: {resultados['plot_path']}")
    else:
        print("Falha ao executar pipeline completo.")
    
    return resultados is not None

if __name__ == "__main__":
    test_ciclo_dezenas()
