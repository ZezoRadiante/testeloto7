# Sistema de Assinatura com Stripe para Gerador de Jogos da Lotofácil

Este projeto implementa um sistema de assinatura utilizando o gateway de pagamento Stripe para o Gerador de Jogos da Lotofácil, permitindo que os usuários assinem planos Básico ou Premium para acessar as funcionalidades do sistema.

## Estrutura do Projeto

```
projeto/
├── app.py                  # Aplicação Flask principal
├── main.py                 # Script para gerenciar serviços
├── scripts/
│   ├── auth/               # Autenticação de usuários
│   ├── estrategias/        # Estratégias de geração de jogos
│   ├── ia/                 # Modelos de IA para previsão
│   ├── pagamento/          # Sistema de pagamento
│   │   ├── email_sender.py
│   │   ├── generate_qr_code.py
│   │   ├── mercadopago_integration.py  # Integração anterior (MercadoPago)
│   │   ├── payment_api.py              # API de pagamento anterior
│   │   ├── payment_api_stripe.py       # Nova API de pagamento com Stripe
│   │   └── stripe_integration.py       # Nova integração com Stripe
│   └── test/
│       ├── test_system.py
│       └── test_stripe.py              # Testes para o sistema Stripe
├── static/
│   ├── css/
│   └── js/
└── templates/
    ├── dashboard.html
    ├── index.html
    ├── index_atualizado.html           # Versão atualizada com links para Stripe
    ├── login.html
    ├── pagamento.html                  # Página de pagamento anterior (MercadoPago)
    ├── pagamento_cancelado.html        # Página de cancelamento de pagamento Stripe
    ├── pagamento_stripe.html           # Nova página de pagamento com Stripe
    └── pagamento_sucesso.html          # Página de sucesso de pagamento Stripe
```

## Requisitos

- Python 3.6+
- Flask
- Stripe
- Outras dependências listadas em `requirements.txt`

## Configuração

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Configure as chaves de API do Stripe:
   - Substitua a chave de API de teste em `stripe_integration.py` por sua chave real
   - Em produção, use variáveis de ambiente para armazenar as chaves de forma segura

3. Configure os planos de assinatura:
   - Os IDs dos preços no Stripe devem ser atualizados em `stripe_integration.py`
   - Crie os produtos e preços correspondentes no painel do Stripe

## Funcionalidades Implementadas

### 1. Integração com Stripe

O arquivo `stripe_integration.py` implementa a integração com a API do Stripe, incluindo:
- Criação de clientes
- Criação de assinaturas
- Verificação de status de pagamento
- Processamento de webhooks

### 2. API de Pagamento

O arquivo `payment_api_stripe.py` implementa os endpoints da API Flask para:
- Criação de assinaturas
- Verificação de status
- Processamento de webhooks
- Login de usuários
- Verificação de e-mail

### 3. Templates Atualizados

Foram criados novos templates para o fluxo de pagamento com Stripe:
- `pagamento_stripe.html`: Formulário de pagamento com redirecionamento para Stripe Checkout
- `pagamento_sucesso.html`: Página de confirmação após pagamento bem-sucedido
- `pagamento_cancelado.html`: Página exibida quando o pagamento é cancelado
- `index_atualizado.html`: Versão atualizada da página inicial com links para o novo sistema

## Fluxo de Assinatura

1. O usuário seleciona um plano (Básico ou Premium) na página inicial
2. O usuário é redirecionado para a página de pagamento onde preenche seus dados
3. Ao clicar em "Prosseguir para Pagamento", é criada uma assinatura no Stripe
4. O usuário é redirecionado para o Stripe Checkout para inserir os dados do cartão
5. Após o pagamento, o usuário é redirecionado para a página de sucesso
6. O Stripe envia uma notificação via webhook que é processada pelo sistema
7. O sistema cria credenciais de acesso para o usuário e envia por e-mail
8. O usuário pode fazer login com as credenciais recebidas

## Webhooks do Stripe

Para receber notificações de pagamento em tempo real, configure um endpoint de webhook no painel do Stripe apontando para:
```
https://seu-dominio.com/api/webhook/stripe
```

## Testes

O arquivo `test_stripe.py` contém testes para verificar a integração com o Stripe:
- Teste de inicialização da integração
- Teste de criação de assinatura
- Teste dos endpoints da API
- Teste de processamento de webhooks

Para executar os testes:
```
python scripts/test/test_stripe.py
```

## Migração do MercadoPago para Stripe

Este projeto implementa uma migração do gateway de pagamento MercadoPago para o Stripe. Os arquivos relacionados ao MercadoPago (`mercadopago_integration.py` e `payment_api.py`) foram mantidos para referência, mas o sistema agora utiliza o Stripe como gateway principal.

## Próximos Passos

1. Implementar gestão de assinaturas (cancelamento, atualização de plano)
2. Adicionar página de histórico de pagamentos no dashboard
3. Implementar notificações de renovação de assinatura
4. Adicionar suporte a cupons de desconto

## Segurança

Em um ambiente de produção, certifique-se de:
- Usar HTTPS para todas as comunicações
- Armazenar chaves de API em variáveis de ambiente
- Implementar validação de assinatura de webhooks
- Armazenar senhas de usuários com hash seguro
- Implementar proteção contra CSRF em todos os formulários
