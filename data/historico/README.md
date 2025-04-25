# Dados Históricos da Lotofácil

Este diretório contém os dados históricos dos sorteios da Lotofácil que serão utilizados para:

1. Treinar a IA LSTM com regularização L1 e L2
2. Analisar padrões e tendências nos sorteios
3. Implementar a estratégia de "ciclo de dezenas fora"
4. Desenvolver outras estratégias baseadas em análise estatística

## Fontes de Dados

Os dados históricos foram obtidos das seguintes fontes:
- somatematica.com.br
- asloterias.com.br

## Estrutura dos Dados

Os dados serão organizados em formato CSV com as seguintes colunas:
- Concurso (número)
- Data (data do sorteio)
- Dezenas sorteadas (15 números)
- Informações adicionais (quantidade de ganhadores, etc.)

## Estratégia de Ciclo de Dezenas Fora

A estratégia de "ciclo de dezenas fora" consiste em identificar 10 dezenas que ficam fora do sorteio e acompanhar quando cada uma delas é sorteada nos concursos seguintes. Quando todas as 10 dezenas forem sorteadas, o ciclo se fecha e um novo ciclo se inicia.

Esta estratégia permite:
- Identificar quais dezenas têm maior probabilidade de serem sorteadas nos próximos concursos
- Excluir ou fixar dezenas específicas nos jogos
- Aumentar as chances de acerto ao focar nas dezenas que ainda não completaram o ciclo

Esta estratégia será exclusiva para assinantes premium (R$69,90).
