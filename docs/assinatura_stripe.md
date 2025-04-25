# Documentação do Sistema de Assinatura com Stripe

## Visão Geral do Processo de Assinatura

O sistema de assinatura implementado permite que os usuários assinem planos Básico ou Premium do Gerador de Jogos da Lotofácil utilizando o gateway de pagamento Stripe. O processo completo funciona da seguinte forma:

1. **Seleção do Plano**: O usuário seleciona um dos planos disponíveis na página inicial:
   - **Plano Básico** (R$ 39,90/mês): Acesso à estratégia de Ciclos, 10 jogos por dia, histórico de jogos e suporte por e-mail.
   - **Plano Premium** (R$ 69,90/mês): Todas as estratégias disponíveis, jogos ilimitados, análise de probabilidade, Inteligência Artificial e suporte prioritário.

2. **Preenchimento de Dados**: O usuário preenche seus dados pessoais (nome, e-mail e telefone) no formulário de pagamento.

3. **Processamento do Pagamento**:
   - Ao clicar em "Prosseguir para Pagamento", o sistema cria uma sessão de checkout no Stripe.
   - O usuário é redirecionado para a página segura do Stripe para inserir os dados do cartão.
   - O Stripe processa o pagamento e gerencia a assinatura recorrente.

4. **Confirmação e Acesso**:
   - Após o pagamento bem-sucedido, o usuário é redirecionado para a página de confirmação.
   - O sistema recebe uma notificação do Stripe via webhook.
   - O sistema cria credenciais de acesso para o usuário e envia por e-mail.
   - O usuário pode fazer login com as credenciais recebidas e acessar as funcionalidades do sistema.

## Detalhes Técnicos da Implementação

### Componentes Principais

1. **Integração com Stripe** (`stripe_integration.py`):
   - Gerencia a comunicação com a API do Stripe
   - Cria clientes e assinaturas no Stripe
   - Verifica status de pagamentos
   - Processa eventos de webhook

2. **API de Pagamento** (`payment_api_stripe.py`):
   - Implementa endpoints RESTful para o fluxo de assinatura
   - Gerencia sessões de usuário e autenticação
   - Processa callbacks e webhooks do Stripe

3. **Templates de Interface** (diretório `templates/`):
   - `pagamento_stripe.html`: Interface para coleta de dados e redirecionamento ao Stripe
   - `pagamento_sucesso.html`: Página de confirmação após pagamento bem-sucedido
   - `pagamento_cancelado.html`: Página exibida quando o pagamento é cancelado

### Fluxo de Dados

1. **Criação de Assinatura**:
   ```
   Cliente -> payment_api_stripe.py (/api/assinatura/criar) -> stripe_integration.py -> API Stripe -> URL de Checkout
   ```

2. **Processamento de Pagamento**:
   ```
   Cliente -> Stripe Checkout -> Stripe -> Webhook -> payment_api_stripe.py (/api/webhook/stripe) -> stripe_integration.py
   ```

3. **Verificação de Status**:
   ```
   Cliente -> payment_api_stripe.py (/api/assinatura/status/<id>) -> stripe_integration.py -> API Stripe -> Status
   ```

## Configuração e Personalização

### Chaves de API

Para utilizar o sistema em produção, é necessário substituir as chaves de API de teste por chaves reais:

1. Acesse o painel do Stripe (https://dashboard.stripe.com/)
2. Obtenha suas chaves de API (pública e secreta)
3. Substitua a chave de teste em `stripe_integration.py`:
   ```python
   self.api_key = api_key or os.environ.get('STRIPE_API_KEY', 'sua_chave_secreta_aqui')
   ```

### Configuração de Produtos e Preços

Os planos de assinatura devem ser configurados no painel do Stripe:

1. Crie produtos para cada plano (Básico e Premium)
2. Defina preços recorrentes para cada produto
3. Atualize os IDs dos preços em `stripe_integration.py`:
   ```python
   self.plans = {
       'basic': {
           'name': 'Básico',
           'price_id': 'price_seu_id_aqui',  # ID do preço no Stripe
           'amount': 3990,  # em centavos
           'interval': 'month',
           'description': 'Plano Básico - Gerador de Jogos da Lotofácil'
       },
       'premium': {
           'name': 'Premium',
           'price_id': 'price_seu_id_aqui',  # ID do preço no Stripe
           'amount': 6990,  # em centavos
           'interval': 'month',
           'description': 'Plano Premium - Gerador de Jogos da Lotofácil'
       }
   }
   ```

### Configuração de Webhooks

Para receber notificações em tempo real sobre eventos de pagamento:

1. No painel do Stripe, vá para Developers > Webhooks
2. Adicione um endpoint apontando para sua URL:
   ```
   https://seu-dominio.com/api/webhook/stripe
   ```
3. Selecione os eventos a serem monitorados (pelo menos `checkout.session.completed`)
4. Obtenha o segredo do webhook e atualize em `stripe_integration.py`:
   ```python
   endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', 'seu_segredo_aqui')
   ```

## Considerações de Segurança

1. **Armazenamento de Chaves**: Em produção, armazene todas as chaves sensíveis em variáveis de ambiente, nunca no código-fonte.

2. **Validação de Webhooks**: Sempre verifique a assinatura dos webhooks para garantir que as notificações são realmente do Stripe.

3. **HTTPS**: Utilize HTTPS para todas as comunicações, especialmente para páginas de pagamento.

4. **Proteção de Dados**: Armazene apenas os dados mínimos necessários sobre cartões e transações.

5. **Logs e Monitoramento**: Implemente logs detalhados e monitoramento para detectar problemas rapidamente.

## Solução de Problemas Comuns

1. **Pagamentos não processados**:
   - Verifique se os webhooks estão configurados corretamente
   - Confirme que as chaves de API estão corretas
   - Verifique os logs do Stripe para erros de processamento

2. **Erro na criação de assinatura**:
   - Confirme que os IDs de preço estão corretos e ativos
   - Verifique se o cliente está sendo criado corretamente no Stripe

3. **Redirecionamento falha após pagamento**:
   - Verifique se as URLs de sucesso e cancelamento estão configuradas corretamente
   - Confirme que as rotas correspondentes estão implementadas no servidor

4. **Webhooks não recebidos**:
   - Verifique a configuração do endpoint no painel do Stripe
   - Confirme que o servidor está acessível publicamente
   - Verifique os logs de tentativas de entrega no painel do Stripe
