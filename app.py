
from flask import Flask, render_template, redirect, url_for, session
import os
import stripe

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

YOUR_DOMAIN = 'https://seusite.com'  # substitua pela URL do seu site no Render

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    session['user'] = 'usuario_exemplo'  # Simula login
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/checkout/<plano>')
def checkout(plano):
    if 'user' not in session:
        return redirect(url_for('login'))

    preco_id = {
        'basico': 'price_1RAaFgCD34s5xyX8T5Exemplo1',
        'premium': 'price_1RAaFgCD34s5xyX8T5Exemplo2'
    }.get(plano)

    if not preco_id:
        return redirect(url_for('home'))

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card', 'pix'],
        line_items=[{
            'price': preco_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=YOUR_DOMAIN + '/success',
        cancel_url=YOUR_DOMAIN + '/',
    )
    return redirect(checkout_session.url, code=303)

@app.route('/success')
def success():
    return "Pagamento realizado com sucesso!"
