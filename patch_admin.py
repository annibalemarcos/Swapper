#!/usr/bin/env python3
"""
Script para atualizar a rota /admin no app.py
"""

import re

print("🔧 Atualizando app.py...")
print("=" * 70)

# Ler o app.py
try:
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print("❌ Erro: app.py não encontrado no diretório atual!")
    exit(1)

# Nova rota /admin completa
new_admin_route = """@app.route('/admin')
def admin_panel():
    conn = get_db()
    cursor = conn.cursor()
    
    # Buscar moedas
    cursor.execute('SELECT * FROM coins ORDER BY symbol')
    coins = cursor.fetchall()
    
    # Estatísticas gerais
    cursor.execute('SELECT COUNT(*) as total FROM blocks')
    total_blocks = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM transactions')
    total_transactions = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM wallets WHERE balance > 0')
    total_wallets = cursor.fetchone()['total']
    
    cursor.execute('SELECT SUM(total_supply) as total FROM coins')
    total_supply = cursor.fetchone()['total'] or 0
    
    # Transações recentes (últimas 20)
    cursor.execute("""
        SELECT 
            t.*,
            c.symbol,
            b.block_number
        FROM transactions t
        JOIN coins c ON t.coin_id = c.id
        JOIN blocks b ON t.block_id = b.id
        ORDER BY t.timestamp DESC
        LIMIT 20
    """)
    recent_transactions = cursor.fetchall()
    
    # Swaps crypto-crypto (últimos 15)
    cursor.execute("""
        SELECT 
            s.*,
            c1.symbol as from_symbol,
            c2.symbol as to_symbol
        FROM swaps s
        JOIN coins c1 ON s.from_coin_id = c1.id
        JOIN coins c2 ON s.to_coin_id = c2.id
        ORDER BY s.timestamp DESC
        LIMIT 15
    """)
    recent_swaps = cursor.fetchall()
    
    # Ordens de swap pendentes
    cursor.execute("""
        SELECT 
            so.*,
            c1.symbol as from_symbol,
            c2.symbol as to_symbol
        FROM swap_orders so
        LEFT JOIN coins c1 ON so.from_coin_id = c1.id
        LEFT JOIN coins c2 ON so.to_coin_id = c2.id
        WHERE so.status = 'pending'
        ORDER BY so.created_at DESC
    """)
    pending_orders = cursor.fetchall()
    
    # Ordens PIX recentes
    cursor.execute("""
        SELECT 
            so.*,
            c1.symbol as coin_symbol
        FROM swap_orders so
        LEFT JOIN coins c1 ON (so.from_coin_id = c1.id OR so.to_coin_id = c1.id)
        WHERE so.order_type IN ('pix_buy', 'pix_sell')
        ORDER BY so.created_at DESC
        LIMIT 10
    """)
    pix_orders = cursor.fetchall()
    
    # Carteiras com maior saldo por moeda
    cursor.execute("""
        SELECT 
            w.*,
            c.symbol
        FROM wallets w
        JOIN coins c ON w.coin_id = c.id
        WHERE w.balance > 0
        ORDER BY w.balance DESC
        LIMIT 10
    """)
    top_wallets = cursor.fetchall()
    
    # Taxas acumuladas (carteiras de fee)
    cursor.execute("""
        SELECT 
            w.balance,
            c.symbol
        FROM wallets w
        JOIN coins c ON w.coin_id = c.id
        WHERE w.address LIKE 'FEE_WALLET_%'
        ORDER BY c.symbol
    """)
    fee_wallets = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin.html', 
                         coins=coins,
                         total_blocks=total_blocks,
                         total_transactions=total_transactions,
                         total_wallets=total_wallets,
                         total_supply=total_supply,
                         recent_transactions=recent_transactions,
                         recent_swaps=recent_swaps,
                         pending_orders=pending_orders,
                         pix_orders=pix_orders,
                         top_wallets=top_wallets,
                         fee_wallets=fee_wallets)"""

# Procurar pela rota /admin antiga
pattern = r"@app\.route\('/admin'\)\s*\ndef admin_panel\(\):.*?return render_template\('admin\.html',.*?\)"

# Substituir
if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, new_admin_route, content, flags=re.DOTALL)
    print("✅ Rota /admin encontrada e atualizada!")
else:
    print("⚠️ Rota /admin não encontrada no formato esperado")
    print("   Adicionando nova rota antes da seção de APIs...")
    
    # Tentar adicionar antes da primeira API
    api_marker = "@app.route('/api/"
    if api_marker in content:
        content = content.replace(api_marker, new_admin_route + "\n\n" + api_marker, 1)
        print("✅ Nova rota adicionada!")
    else:
        print("❌ Não foi possível adicionar automaticamente")
        print("   Por favor, adicione manualmente a rota fornecida")
        exit(1)

# Salvar backup
with open('app.py.backup', 'w', encoding='utf-8') as f:
    with open('app.py', 'r', encoding='utf-8') as original:
        f.write(original.read())
print("✅ Backup criado: app.py.backup")

# Salvar app.py atualizado
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ app.py atualizado com sucesso!")
print("=" * 70)
print("\n🎉 ATUALIZAÇÃO CONCLUÍDA!")
print("   Reinicie o servidor: python app.py")
print("   Acesse: http://localhost:5581/admin")
