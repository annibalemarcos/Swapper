# 💳 Crypto Payment Gateway

Gateway de pagamento que aceita criptomoedas e converte para PIX automaticamente.

## 🚀 Início Rápido

### 1. Instalar dependências
```bash
pip install flask colorama requests
```

### 2. Iniciar o Gateway
```bash
python gateway.py
```

### 3. Acessar
- **Home**: http://localhost:5583
- **Dashboard**: http://localhost:5583/merchant/dashboard

## 📋 Como Funciona

1. **Merchant se registra** e obtém API Key
2. **Merchant cria invoice** (via dashboard ou API)
3. **Cliente escolhe criptomoeda** (D1-D6)
4. **Cliente paga** enviando crypto para endereço gerado
5. **Sistema detecta pagamento** automaticamente
6. **Sistema converte** crypto → BRL
7. **Sistema envia PIX** para merchant (simulado)

## 🔌 Integração via API

### Criar Invoice
```python
import requests

response = requests.post(
    'http://localhost:5583/api/invoice/create',
    headers={'X-API-Key': 'pk_sua_api_key'},
    json={
        'amount': 150.00,
        'description': 'Pedido #123',
        'customer_email': 'cliente@email.com'
    }
)

data = response.json()
checkout_url = data['checkout_url']
# Redirecionar cliente para checkout_url
```

### Consultar Status
```python
response = requests.get(
    'http://localhost:5583/api/invoice/inv_abc123...'
)

status = response.json()
print(status['status'])  # 'pending' ou 'paid'
```

## 🪝 Webhook

Configure webhook URL no cadastro para receber notificações:

```python
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    if data['status'] == 'paid':
        # Processar pedido
        process_order(data['invoice_id'])
    
    return {'success': True}
```

## 💰 Criptomoedas Aceitas

- D1, D2, D3, D4, D5, D6
- Conversão automática para BRL
- Taxas de câmbio em tempo real

## 🔐 Segurança

- API Key para autenticação
- Endereços únicos por invoice
- Monitor automático de pagamentos
- Confirmação em blockchain

## 📊 Dashboard

Acesse seu dashboard para:
- Ver invoices
- Criar novas invoices
- Acompanhar pagamentos
- Gerenciar configurações

## 🛠️ Integração com E-commerce

### WooCommerce
```php
// Criar invoice ao finalizar compra
$response = wp_remote_post('http://localhost:5583/api/invoice/create', [
    'headers' => ['X-API-Key' => 'pk_...'],
    'body' => json_encode([
        'amount' => $order->get_total(),
        'description' => 'Pedido #' . $order->get_id()
    ])
]);
```

### Shopify
Webhooks configuráveis para receber notificações

## 📝 Exemplo Completo

Veja `gateway_integration_example.py` para exemplos completos de integração.

## ⚡ Recursos

- ✅ Cadastro de merchants
- ✅ Dashboard interativo
- ✅ API REST completa
- ✅ Webhook para notificações
- ✅ 6 criptomoedas suportadas
- ✅ Conversão automática para PIX
- ✅ Monitor de pagamentos em tempo real
- ✅ Interface de checkout moderna

## 🔗 URLs Importantes

- Gateway: http://localhost:5583
- Sistema Swap: http://localhost:5581
- Documentação API: Incluída no código

## 📞 Suporte

Para dúvidas, consulte os exemplos de integração ou a documentação da API.
