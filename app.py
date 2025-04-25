
from flask import Flask, render_template, request, jsonify, redirect
import os
import logging
import json
from datetime import datetime
from scripts.pagamento.stripe_integration import StripeIntegration

# Corrigir conflitos com arquivo 'logs'
if os.path.isfile("logs"):
    os.remove("logs")
os.makedirs("logs", exist_ok=True)

# Configurar logging para arquivo relativo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/app.log',
    filemode='a'
)

# Inicializar integração com Stripe
stripe_integration = StripeIntegration()

# Criar diretórios necessários
os.makedirs('data/assinaturas', exist_ok=True)
os.makedirs('data/usuarios', exist_ok=True)
os.makedirs('data/emails', exist_ok=True)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/pagamento")
def pagamento():
    return render_template("pagamento.html")

@app.route('/pagamento/sucesso')
def pagamento_sucesso():
    """Rota para página de sucesso após pagamento"""
    session_id = request.args.get('session_id', '')
    return render_template('pagamento_sucesso.html', session_id=session_id)

@app.route('/pagamento/cancelado')
def pagamento_cancelado():
    """Rota para página de cancelamento de pagamento"""
    return render_template('pagamento_cancelado.html')

@app.route('/api/assinatura/criar', methods=['POST'])
def criar_assinatura():
    """
    Cria uma nova assinatura
    
    Espera um JSON com os seguintes campos:
    - name: Nome do usuário
    - email: E-mail do usuário
    - phone: Telefone do usuário (opcional)
    - plan_type: Tipo de plano ('basic' ou 'premium')
    
    Retorna um JSON com os dados da assinatura, incluindo URL de pagamento
    """
    try:
        data = request.json
        
        # Validar dados
        if not data or 'name' not in data or 'email' not in data or 'plan_type' not in data:
            return jsonify({"error": "Dados incompletos"}), 400
        
        # Criar assinatura
        subscription_data = stripe_integration.create_subscription(data, data['plan_type'])
        
        return jsonify({
            "success": True,
            "subscription_id": subscription_data['id'],
            "payment_url": subscription_data['payment_url']
        })
    except Exception as e:
        logging.error(f"Erro ao criar assinatura: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/assinatura/status/<subscription_id>', methods=['GET'])
def verificar_status(subscription_id):
    """
    Verifica o status de uma assinatura
    
    Args:
        subscription_id (str): ID da assinatura
        
    Retorna um JSON com o status da assinatura
    """
    try:
        status = stripe_integration.check_subscription_status(subscription_id)
        return jsonify(status)
    except Exception as e:
        logging.error(f"Erro ao verificar status da assinatura {subscription_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/usuario/login', methods=['POST'])
def login_usuario():
    """
    Realiza login do usuário
    
    Espera um JSON com os seguintes campos:
    - email: E-mail do usuário
    - password: Senha do usuário
    
    Retorna um JSON com os dados do usuário em caso de sucesso
    """
    try:
        data = request.json
        
        # Validar dados
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Dados incompletos"}), 400
        
        # Verificar credenciais
        email = data['email']
        password = data['password']
        
        # Em um ambiente real, isso seria feito em um banco de dados
        # Aqui estamos verificando o arquivo JSON
        file_path = f'data/usuarios/{email.replace("@", "_").replace(".", "_")}.json'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            # Verificar senha
            if user_data['password'] == password:
                # Remover senha do retorno
                user_data.pop('password', None)
                
                # Verificar validade da assinatura
                subscription_end = datetime.fromisoformat(user_data['subscription_end'])
                if subscription_end < datetime.now():
                    user_data['status'] = 'expired'
                
                return jsonify({
                    "success": True,
                    "user": user_data
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Credenciais inválidas"
                }), 401
        except FileNotFoundError:
            return jsonify({
                "success": False,
                "error": "Usuário não encontrado"
            }), 404
    except Exception as e:
        logging.error(f"Erro ao realizar login: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webhook/stripe', methods=['POST'])
def webhook_stripe():
    """
    Webhook para receber notificações do Stripe
    """
    try:
        payload = request.data.decode('utf-8')
        sig_header = request.headers.get('Stripe-Signature')
        
        # Processar evento
        result = stripe_integration.handle_webhook_event(payload, sig_header)
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Erro ao processar webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
