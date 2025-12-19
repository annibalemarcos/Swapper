
# 3. Checkout e páginas restantes

shop_checkout = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checkout - TechStore</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .checkout-card { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark navbar-expand-lg mb-4">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-store"></i> <strong>TechStore</strong></a>
        </div>
    </nav>

    <div class="container mb-5">
        <h2 class="mb-4"><i class="fas fa-credit-card"></i> Finalizar Compra</h2>
        
        <div class="row">
            <div class="col-lg-7">
                <div class="checkout-card mb-4">
                    <h4 class="mb-3">Dados de Entrega</h4>
                    <form id="checkoutForm">
                        <div class="mb-3">
                            <label class="form-label">Nome Completo</label>
                            <input type="text" class="form-control" id="name" required>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" id="email" required>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Endereço Completo</label>
                            <textarea class="form-control" id="address" rows="3" required></textarea>
                        </div>
                        
                        <button type="submit" class="btn btn-primary btn-lg w-100">
                            <i class="fas fa-lock"></i> Ir para Pagamento
                        </button>
                    </form>
                </div>
            </div>

            <div class="col-lg-5">
                <div class="checkout-card">
                    <h4 class="mb-3">Resumo do Pedido</h4>
                    
                    {% for item in cart %}
                    <div class="d-flex justify-content-between mb-2">
                        <span>{{ item.name }} ({{ item.quantity }}x)</span>
                        <strong>R$ {{ "%.2f"|format(item.price * item.quantity) }}</strong>
                    </div>
                    {% endfor %}
                    
                    <hr>
                    
                    <div class="d-flex justify-content-between mb-4">
                        <h5>Total:</h5>
                        <h4 class="text-success">R$ {{ "%.2f"|format(total) }}</h4>
                    </div>
                    
                    <div class="alert alert-info">
                        <i class="fas fa-coins"></i> 
                        <strong>Pagamento com Crypto</strong>
                        <p class="mb-0 small">Você será redirecionado para escolher a criptomoeda</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('checkoutForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = e.target.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
            
            const data = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                address: document.getElementById('address').value
            };

            try {
                const response = await fetch('/api/checkout/process', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (result.success) {
                    // Redirecionar para gateway de pagamento
                    window.location.href = result.checkout_url;
                } else {
                    alert('❌ Erro: ' + result.error);
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-lock"></i> Ir para Pagamento';
                }
            } catch (error) {
                alert('❌ Erro ao processar pedido: ' + error);
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-lock"></i> Ir para Pagamento';
            }
        });
    </script>
</body>
</html>'''

# 4. Configuração
shop_config = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuração - TechStore</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; }
        .config-card { background: white; border-radius: 20px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 600px; margin: 0 auto; }
        .api-key-box { background: #f8f9fa; border: 2px dashed #667eea; padding: 15px; border-radius: 10px; font-family: monospace; word-break: break-all; }
    </style>
</head>
<body>
    <div class="container">
        <div class="config-card">
            <h2 class="text-center mb-4"><i class="fas fa-cog"></i> Configuração da Loja</h2>
            
            <div class="alert alert-info">
                <strong><i class="fas fa-info-circle"></i> Importante:</strong>
                <p class="mb-0">Para aceitar pagamentos, você precisa de uma API Key do Crypto Payment Gateway</p>
            </div>
            
            <h5 class="mt-4">Como obter API Key:</h5>
            <ol>
                <li>Acesse: <a href="http://localhost:5583" target="_blank">http://localhost:5583</a></li>
                <li>Clique em "Registrar"</li>
                <li>Preencha os dados da sua loja</li>
                <li>Copie a API Key gerada</li>
                <li>Cole abaixo:</li>
            </ol>
            
            <form id="configForm" class="mt-4">
                <div class="mb-3">
                    <label class="form-label">API Key do Gateway</label>
                    <input type="text" class="form-control" id="apiKey" 
                           placeholder="pk_..." value="{{ api_key }}" required>
                    <small class="text-muted">Formato: pk_...</small>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Gateway URL</label>
                    <input type="text" class="form-control" value="http://localhost:5583" readonly>
                </div>
                
                <button type="submit" class="btn btn-primary btn-lg w-100">
                    <i class="fas fa-save"></i> Salvar Configuração
                </button>
            </form>
            
            <div class="text-center mt-4">
                <a href="/" class="btn btn-outline-secondary">
                    <i class="fas fa-arrow-left"></i> Voltar para Loja
                </a>
            </div>
            
            {% if api_key and api_key != 'pk_sua_api_key_aqui' %}
            <div class="alert alert-success mt-4">
                <i class="fas fa-check-circle"></i> API Key configurada! Sua loja está pronta para receber pagamentos.
            </div>
            {% endif %}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('configForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const apiKey = document.getElementById('apiKey').value;
            
            try {
                const response = await fetch('/api/config/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({api_key: apiKey})
                });

                const data = await response.json();

                if (data.success) {
                    alert('✅ ' + data.message);
                    location.reload();
                } else {
                    alert('❌ Erro: ' + data.error);
                }
            } catch (error) {
                alert('❌ Erro ao salvar configuração');
            }
        });
    </script>
</body>
</html>'''

# 5. Página de pedido (simples)
shop_order = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pedido {{ order.order_id }} - TechStore</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .order-card { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark navbar-expand-lg mb-4">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-store"></i> <strong>TechStore</strong></a>
            <a href="/" class="btn btn-outline-light">Voltar para Loja</a>
        </div>
    </nav>

    <div class="container mb-5">
        <div class="order-card">
            <div class="text-center mb-4">
                {% if payment_status == 'paid' %}
                <i class="fas fa-check-circle fa-5x text-success mb-3"></i>
                <h2 class="text-success">Pedido Confirmado!</h2>
                <p class="lead">Obrigado pela sua compra!</p>
                {% else %}
                <i class="fas fa-clock fa-5x text-warning mb-3"></i>
                <h2 class="text-warning">Aguardando Pagamento</h2>
                <p class="lead">Complete o pagamento para confirmar o pedido</p>
                {% endif %}
            </div>

            <div class="row mb-4">
                <div class="col-md-6">
                    <h5>Informações do Pedido</h5>
                    <p><strong>ID:</strong> {{ order.order_id }}</p>
                    <p><strong>Cliente:</strong> {{ order.customer_name }}</p>
                    <p><strong>Email:</strong> {{ order.customer_email }}</p>
                    <p><strong>Data:</strong> {{ order.created_at }}</p>
                </div>
                <div class="col-md-6 text-end">
                    <h5>Total</h5>
                    <h2 class="text-success">R$ {{ "%.2f"|format(order.total_amount) }}</h2>
                </div>
            </div>

            <h5>Itens do Pedido</h5>
            <table class="table">
                <thead>
                    <tr>
                        <th>Produto</th>
                        <th>Quantidade</th>
                        <th>Preço</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr>
                        <td>{{ item.name }}</td>
                        <td>{{ item.quantity }}</td>
                        <td>R$ {{ "%.2f"|format(item.price) }}</td>
                        <td>R$ {{ "%.2f"|format(item.price * item.quantity) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            {% if payment_status == 'pending' and order.invoice_id %}
            <div class="alert alert-warning">
                <strong><i class="fas fa-exclamation-triangle"></i> Ação Necessária:</strong>
                <p class="mb-0">Complete o pagamento para confirmar seu pedido</p>
                <a href="http://localhost:5583/checkout/{{ order.invoice_id }}" 
                   class="btn btn-warning mt-2" target="_blank">
                    <i class="fas fa-credit-card"></i> Ir para Pagamento
                </a>
            </div>
            {% endif %}
        </div>
    </div>

    <script>
        // Auto-refresh se pendente
        {% if payment_status == 'pending' %}
        setTimeout(() => location.reload(), 10000);
        {% endif %}
    </script>
</body>
</html>'''

# Salvar templates
with open('templates_shop/shop_checkout.html', 'w', encoding='utf-8') as f:
    f.write(shop_checkout)

with open('templates_shop/shop_config.html', 'w', encoding='utf-8') as f:
    f.write(shop_config)

with open('templates_shop/shop_order.html', 'w', encoding='utf-8') as f:
    f.write(shop_order)

print("✅ shop_checkout.html criado")
print("✅ shop_config.html criado")
print("✅ shop_order.html criado")
print("\n" + "="*70)
print("🎉 LOJA COMPLETA CRIADA!")
print("="*70)
