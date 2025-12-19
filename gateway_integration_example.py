#!/usr/bin/env python3
"""
EXEMPLO DE INTEGRAÇÃO - Crypto Payment Gateway
Como integrar o gateway na sua loja/sistema
"""

import requests
import time

# Configuração
GATEWAY_URL = "http://localhost:5583"
API_KEY = "pk_2c6b3d0887efd00e875db2d07db6fb1d"  # Obtenha no dashboard

def criar_invoice(valor, descricao, email_cliente):
    """
    Cria uma nova invoice
    """
    response = requests.post(
        f"{GATEWAY_URL}/api/invoice/create",
        headers={"X-API-Key": API_KEY},
        json={
            "amount": valor,
            "description": descricao,
            "customer_email": email_cliente
        }
    )
    
    data = response.json()
    
    if data.get('success'):
        print(f"✅ Invoice criada: {data['invoice_id']}")
        print(f"📄 Checkout URL: {data['checkout_url']}")
        return data
    else:
        print(f"❌ Erro: {data.get('error')}")
        return None

def consultar_invoice(invoice_id):
    """
    Consulta status de uma invoice
    """
    response = requests.get(f"{GATEWAY_URL}/api/invoice/{invoice_id}")
    data = response.json()
    
    print(f"\nStatus: {data['status']}")
    print(f"Valor: R$ {data['amount_brl']:.2f}")
    
    if data['status'] == 'paid':
        print(f"💰 Pago com: {data['crypto_received']} {data['payment_crypto']}")
        print(f"💸 PIX enviado: R$ {data['pix_sent']:.2f}")
    
    return data

# ==================== EXEMPLOS DE USO ====================

print("🔥 EXEMPLOS DE INTEGRAÇÃO\n")

# Exemplo 1: Criar invoice simples
print("1️⃣ Criar Invoice Simples")
print("-" * 50)
invoice = criar_invoice(
    valor=150.00,
    descricao="Pedido #12345",
    email_cliente="cliente@email.com"
)

if invoice:
    invoice_id = invoice['invoice_id']
    
    # Exemplo 2: Monitorar pagamento
    print("\n2️⃣ Monitorar Pagamento")
    print("-" * 50)
    print("Aguardando pagamento...")
    
    # Em produção, use um webhook ao invés de polling
    # for _ in range(60):  # Verificar por 5 minutos
    #     status = consultar_invoice(invoice_id)
    #     if status['status'] == 'paid':
    #         print("\n✅ PAGAMENTO CONFIRMADO!")
    #         break
    #     time.sleep(5)

# Exemplo 3: Webhook Handler (Flask/FastAPI)
webhook_code = """
# Exemplo de handler de webhook

from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    data = request.json
    
    invoice_id = data.get('invoice_id')
    status = data.get('status')
    
    if status == 'paid':
        # Processar pedido
        # Enviar produto
        # Enviar email
        print(f"Pagamento confirmado: {invoice_id}")
    
    return {'success': True}

if __name__ == '__main__':
    app.run(port=8000)
"""

print("\n3️⃣ Webhook Handler")
print("-" * 50)
print(webhook_code)

# Exemplo 4: Integração com E-commerce
ecommerce_example = """
# Exemplo de integração com carrinho de compras

def checkout_process(cart_total, order_id, customer_email):
    # 1. Criar invoice
    invoice = criar_invoice(
        valor=cart_total,
        descricao=f"Pedido #{order_id}",
        email_cliente=customer_email
    )
    
    # 2. Redirecionar cliente para checkout
    checkout_url = invoice['checkout_url']
    return redirect(checkout_url)

def webhook_handler(invoice_id, status):
    if status == 'paid':
        # Buscar pedido pelo invoice_id
        order = Order.query.filter_by(invoice_id=invoice_id).first()
        
        # Atualizar status
        order.status = 'paid'
        order.save()
        
        # Processar pedido
        process_order(order)
        
        # Enviar email
        send_confirmation_email(order)
"""

print("\n4️⃣ Integração E-commerce")
print("-" * 50)
print(ecommerce_example)

print("\n" + "="*70)
print("📚 DOCUMENTAÇÃO COMPLETA")
print("="*70)
print("\nEndpoints disponíveis:")
print("  POST /api/invoice/create      - Criar nova invoice")
print("  GET  /api/invoice/<id>         - Consultar invoice")
print("\nWebhook:")
print("  POST <sua_url>                 - Recebe notificações")
print("  Payload: {invoice_id, status}")
print("\nDashboard:")
print("  http://localhost:5583/merchant/dashboard")
print("="*70)
