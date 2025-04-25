#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para gerar QR Code PIX para testes
"""

import os
import qrcode
import base64
from io import BytesIO
import json

def generate_pix_qr_code(amount, reference_id, pix_key):
    """
    Gera o código PIX para pagamento
    
    Simulação de um código PIX (em produção, seria gerado pela API do Mercado Pago)
    """
    # Simulação de um código PIX (em produção, seria gerado pela API)
    return f"00020126580014br.gov.bcb.pix0136{pix_key}5204000053039865802BR5923Gerador Jogos Lotofacil6009SAO PAULO62290525{reference_id}6304A123"

def generate_qr_code_image(pix_code, output_path):
    """Gera uma imagem de QR Code a partir do código PIX"""
    # Gerar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(pix_code)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    
    # Também retornar como base64 para uso em HTML
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def main():
    """Função principal"""
    # Criar diretório para QR Codes se não existir
    os.makedirs('/home/ubuntu/lotofacil/static/images/qrcodes', exist_ok=True)
    
    # Chave PIX fornecida pelo usuário
    pix_key = "42f51e7f-7586-4f26-a5b2-837ef34a0bfb"
    
    # Gerar QR Code para plano básico
    basic_reference_id = "basic_example_123456"
    basic_amount = 39.90
    basic_pix_code = generate_pix_qr_code(basic_amount, basic_reference_id, pix_key)
    basic_output_path = '/home/ubuntu/lotofacil/static/images/qrcodes/qr_code_basic.png'
    basic_base64 = generate_qr_code_image(basic_pix_code, basic_output_path)
    
    # Gerar QR Code para plano premium
    premium_reference_id = "premium_example_789012"
    premium_amount = 69.90
    premium_pix_code = generate_pix_qr_code(premium_amount, premium_reference_id, pix_key)
    premium_output_path = '/home/ubuntu/lotofacil/static/images/qrcodes/qr_code_premium.png'
    premium_base64 = generate_qr_code_image(premium_pix_code, premium_output_path)
    
    # Salvar informações em um arquivo JSON para referência
    qr_info = {
        "basic": {
            "reference_id": basic_reference_id,
            "amount": basic_amount,
            "pix_code": basic_pix_code,
            "image_path": basic_output_path,
            "base64": basic_base64
        },
        "premium": {
            "reference_id": premium_reference_id,
            "amount": premium_amount,
            "pix_code": premium_pix_code,
            "image_path": premium_output_path,
            "base64": premium_base64
        }
    }
    
    with open('/home/ubuntu/lotofacil/static/images/qrcodes/qr_info.json', 'w', encoding='utf-8') as f:
        json.dump(qr_info, f, ensure_ascii=False, indent=4)
    
    print("QR Codes gerados com sucesso!")
    print(f"QR Code Básico: {basic_output_path}")
    print(f"QR Code Premium: {premium_output_path}")

if __name__ == "__main__":
    main()
