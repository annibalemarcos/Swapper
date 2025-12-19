
# Criar a rota do admin no gateway.py

admin_route_code = '''
# ==================== ADICIONAR NO gateway.py ====================
# Cole ANTES do "if __name__ == '__main__':"

@app.route('/admin')
def admin_dashboard():
    """Dashboard administrativo do gateway"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Estatísticas gerais
    cursor.execute('SELECT COUNT(*) as total FROM merchants WHERE status = "active"')
    total_merchants = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM invoices')
    total_invoices = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM invoices WHERE status = "paid"')
    paid_invoices = cursor.fetchone()['total']
    
    cursor.execute('SELECT SUM(amount_brl) as total FROM invoices WHERE status = "paid"')
    total_volume = cursor.fetchone()['total'] or 0
    
    cursor.execute('SELECT SUM(crypto_received) as total FROM invoices WHERE status = "paid"')
    total_crypto = cursor.fetchone()['total'] or 0
    
    # Taxa de conversão
    conversion_rate = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
    
    # Ticket médio
    avg_ticket = (total_volume / paid_invoices) if paid_invoices > 0 else 0
    
    stats = {
        'total_merchants': total_merchants,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'total_volume': total_volume,
        'total_crypto': total_crypto,
        'conversion_rate': conversion_rate,
        'avg_ticket': avg_ticket
    }
    
    # Estatísticas por moeda
    cursor.execute("""
        SELECT 
            payment_crypto as crypto,
            COUNT(*) as count,
            SUM(amount_brl) as volume
        FROM invoices
        WHERE status = 'paid' AND payment_crypto IS NOT NULL
        GROUP BY payment_crypto
        ORDER BY volume DESC
    """)
    crypto_stats = cursor.fetchall()
    
    # Últimas invoices
    cursor.execute("""
        SELECT i.*, m.name as merchant_name
        FROM invoices i
        JOIN merchants m ON i.merchant_id = m.id
        ORDER BY i.created_at DESC
        LIMIT 20
    """)
    recent_invoices = cursor.fetchall()
    
    # Merchants com estatísticas
    cursor.execute("""
        SELECT 
            m.*,
            COUNT(i.id) as invoice_count,
            SUM(CASE WHEN i.status = 'paid' THEN i.amount_brl ELSE 0 END) as total_volume
        FROM merchants m
        LEFT JOIN invoices i ON m.id = i.merchant_id
        GROUP BY m.id
        ORDER BY total_volume DESC
    """)
    merchants = cursor.fetchall()
    
    conn.close()
    
    return render_template('gateway_admin_dashboard.html',
                         stats=stats,
                         crypto_stats=crypto_stats,
                         recent_invoices=recent_invoices,
                         merchants=merchants)
'''

with open('GATEWAY_ADMIN_ROUTE.txt', 'w', encoding='utf-8') as f:
    f.write(admin_route_code)

print("✅ GATEWAY_ADMIN_ROUTE.txt criado!")
print("\n" + "="*70)
print("📋 INSTRUÇÕES COMPLETAS:")
print("="*70)
print("\n1️⃣ ADICIONAR ROTA no gateway.py:")
print("   - Abra gateway.py")
print("   - Localize: if __name__ == '__main__':")
print("   - ANTES dessa linha, cole o conteúdo de: GATEWAY_ADMIN_ROUTE.txt")
print("   - Salve o arquivo")

print("\n2️⃣ ADICIONAR TEMPLATE:")
print("   - Copie: gateway_admin_dashboard_ENHANCED.html")
print("   - Para: templates_gateway/gateway_admin_dashboard.html")

print("\n3️⃣ REINICIAR:")
print("   - Pare o gateway (Ctrl+C)")
print("   - Execute: python gateway.py")

print("\n4️⃣ ACESSAR:")
print("   - http://localhost:5583/admin")

print("\n" + "="*70)
print("🎉 RECURSOS DO NOVO DASHBOARD ADMIN:")
print("="*70)
print("   ✅ Total de lojas cadastradas")
print("   ✅ Total de invoices (pagas e pendentes)")
print("   ✅ Volume total transacionado em BRL")
print("   ✅ Total de crypto recebida")
print("   ✅ Estatísticas por criptomoeda")
print("   ✅ Últimas 20 invoices de todas as lojas")
print("   ✅ Lista de merchants com volume individual")
print("   ✅ Taxa de conversão (% de pagamentos)")
print("   ✅ Ticket médio")
print("   ✅ Documentação da API integrada")
print("   ✅ Auto-refresh a cada 30 segundos")
print("="*70)
