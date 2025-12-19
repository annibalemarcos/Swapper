
print("📊 Criando SUPER DASHBOARD ADMIN para o Gateway...")
print("=" * 70)

# Template completo do Admin Dashboard melhorado
admin_dashboard_enhanced = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Gateway</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); min-height: 100vh; padding: 20px 0; }
        .navbar { background: rgba(255,255,255,0.95) !important; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-card { background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-icon { font-size: 3rem; opacity: 0.2; position: absolute; right: 20px; top: 20px; }
        .big-number { font-size: 2.5rem; font-weight: bold; margin: 0; }
        .stat-label { color: #6c757d; font-size: 0.9rem; text-transform: uppercase; }
        .api-docs { background: #f8f9fa; border-left: 4px solid #0d6efd; padding: 20px; border-radius: 10px; margin: 20px 0; }
        .endpoint { background: #fff; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #dee2e6; }
        .method-badge { font-weight: bold; padding: 5px 10px; border-radius: 5px; font-size: 0.8rem; }
        .method-get { background: #28a745; color: white; }
        .method-post { background: #007bff; color: white; }
        .chart-container { background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/"><i class="fas fa-shield-alt"></i> Gateway Admin</a>
            <div class="navbar-nav ms-auto">
                <span class="nav-link">Administrador</span>
                <a class="nav-link" href="/merchant/dashboard">Dashboard Merchant</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <!-- ESTATÍSTICAS PRINCIPAIS -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stat-card position-relative">
                    <i class="fas fa-store stat-icon text-primary"></i>
                    <div class="stat-label">Total de Lojas</div>
                    <div class="big-number text-primary">{{ stats.total_merchants }}</div>
                    <small class="text-muted">Merchants ativos</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card position-relative">
                    <i class="fas fa-file-invoice stat-icon text-info"></i>
                    <div class="stat-label">Invoices Totais</div>
                    <div class="big-number text-info">{{ stats.total_invoices }}</div>
                    <small class="text-success">{{ stats.paid_invoices }} pagas</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card position-relative">
                    <i class="fas fa-money-bill-wave stat-icon text-success"></i>
                    <div class="stat-label">Volume Total</div>
                    <div class="big-number text-success">R$ {{ "%.2f"|format(stats.total_volume or 0) }}</div>
                    <small class="text-muted">Em transações</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card position-relative">
                    <i class="fas fa-coins stat-icon text-warning"></i>
                    <div class="stat-label">Crypto Recebida</div>
                    <div class="big-number text-warning">{{ "%.2f"|format(stats.total_crypto or 0) }}</div>
                    <small class="text-muted">Total em moedas</small>
                </div>
            </div>
        </div>

        <!-- ESTATÍSTICAS POR MOEDA -->
        <div class="chart-container">
            <h4 class="mb-4"><i class="fas fa-chart-pie"></i> Transações por Criptomoeda</h4>
            <div class="row">
                {% for crypto_stat in crypto_stats %}
                <div class="col-md-4 mb-3">
                    <div class="d-flex justify-content-between align-items-center p-3 border rounded">
                        <div>
                            <h5 class="mb-0"><i class="fas fa-coins text-warning"></i> {{ crypto_stat.crypto }}</h5>
                            <small class="text-muted">{{ crypto_stat.count }} transações</small>
                        </div>
                        <div class="text-end">
                            <strong class="text-primary">R$ {{ "%.2f"|format(crypto_stat.volume or 0) }}</strong>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- ÚLTIMAS INVOICES -->
        <div class="chart-container">
            <h4 class="mb-4"><i class="fas fa-list"></i> Últimas Invoices (Todas as Lojas)</h4>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Invoice ID</th>
                            <th>Loja</th>
                            <th>Valor</th>
                            <th>Crypto</th>
                            <th>Status</th>
                            <th>Data</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for inv in recent_invoices %}
                        <tr>
                            <td><code>{{ inv.invoice_id[:16] }}...</code></td>
                            <td>{{ inv.merchant_name }}</td>
                            <td><strong>R$ {{ "%.2f"|format(inv.amount_brl) }}</strong></td>
                            <td>
                                {% if inv.payment_crypto %}
                                <span class="badge bg-warning">{{ inv.payment_crypto }}</span>
                                {% else %}
                                <span class="badge bg-secondary">Pendente</span>
                                {% endif %}
                            </td>
                            <td>
                                {% if inv.status == 'paid' %}
                                <span class="badge bg-success">PAGO</span>
                                {% else %}
                                <span class="badge bg-warning">PENDENTE</span>
                                {% endif %}
                            </td>
                            <td><small>{{ inv.created_at[:16] }}</small></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- MERCHANTS CADASTRADOS -->
        <div class="chart-container">
            <h4 class="mb-4"><i class="fas fa-store"></i> Lojas Cadastradas</h4>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Nome</th>
                            <th>Email</th>
                            <th>API Key</th>
                            <th>Invoices</th>
                            <th>Volume</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for merchant in merchants %}
                        <tr>
                            <td><strong>{{ merchant.name }}</strong></td>
                            <td>{{ merchant.email }}</td>
                            <td><code>{{ merchant.api_key[:20] }}...</code></td>
                            <td><span class="badge bg-info">{{ merchant.invoice_count }}</span></td>
                            <td><strong>R$ {{ "%.2f"|format(merchant.total_volume or 0) }}</strong></td>
                            <td><span class="badge bg-success">{{ merchant.status }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- DOCUMENTAÇÃO DA API -->
        <div class="api-docs">
            <h4 class="mb-4"><i class="fas fa-code"></i> Documentação da API</h4>
            
            <div class="endpoint">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <span class="method-badge method-post">POST</span>
                        <code class="ms-2">/api/invoice/create</code>
                    </div>
                </div>
                <p class="mb-2"><strong>Descrição:</strong> Criar nova invoice</p>
                <pre class="bg-light p-3 rounded"><code>{
  "amount": 100.00,
  "description": "Pedido #123",
  "customer_email": "cliente@email.com"
}</code></pre>
            </div>

            <div class="endpoint">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <span class="method-badge method-get">GET</span>
                        <code class="ms-2">/api/invoice/&lt;invoice_id&gt;</code>
                    </div>
                </div>
                <p class="mb-0"><strong>Descrição:</strong> Consultar status de uma invoice</p>
            </div>

            <div class="endpoint">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <span class="method-badge method-get">GET</span>
                        <code class="ms-2">/checkout/&lt;invoice_id&gt;</code>
                    </div>
                </div>
                <p class="mb-0"><strong>Descrição:</strong> Página de checkout para pagamento</p>
            </div>

            <div class="alert alert-info mt-3">
                <strong><i class="fas fa-info-circle"></i> Headers necessários:</strong><br>
                <code>X-API-Key: pk_sua_api_key_aqui</code>
            </div>
        </div>

        <!-- MÉTRICAS ADICIONAIS -->
        <div class="row">
            <div class="col-md-6">
                <div class="chart-container">
                    <h5><i class="fas fa-clock"></i> Taxa de Conversão</h5>
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <div>
                            <div class="big-number text-success">{{ "%.1f"|format(stats.conversion_rate or 0) }}%</div>
                            <small class="text-muted">Invoices pagas vs criadas</small>
                        </div>
                        <div>
                            <i class="fas fa-chart-line fa-4x text-success" style="opacity: 0.2;"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <h5><i class="fas fa-dollar-sign"></i> Ticket Médio</h5>
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <div>
                            <div class="big-number text-info">R$ {{ "%.2f"|format(stats.avg_ticket or 0) }}</div>
                            <small class="text-muted">Valor médio por transação</small>
                        </div>
                        <div>
                            <i class="fas fa-receipt fa-4x text-info" style="opacity: 0.2;"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Auto-refresh a cada 30 segundos
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>'''

with open('gateway_admin_dashboard_ENHANCED.html', 'w', encoding='utf-8') as f:
    f.write(admin_dashboard_enhanced)

print("✅ gateway_admin_dashboard_ENHANCED.html criado!")
print("=" * 70)
