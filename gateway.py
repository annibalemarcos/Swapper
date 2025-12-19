from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import hashlib
import json
from datetime import datetime
import secrets
import random
import threading
import time
from colorama import Fore, Style, init

init(autoreset=True)

app = Flask(__name__, template_folder='templates_gateway')
app.config['SECRET_KEY'] = 'crypto-gateway-secret-key-2024'

DATABASE = 'gateway.db'
SWAP_API = 'http://localhost:5581/api'

# ==================== DATABASE ====================
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabela de Merchants (Lojas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            api_key TEXT NOT NULL UNIQUE,
            pix_key TEXT NOT NULL,
            webhook_url TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de Invoices (Faturas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            merchant_id INTEGER NOT NULL,
            invoice_id TEXT NOT NULL UNIQUE,
            amount_brl REAL NOT NULL,
            description TEXT,
            customer_email TEXT,
            status TEXT DEFAULT 'pending',
            payment_crypto TEXT,
            payment_amount REAL,
            deposit_address TEXT,
            crypto_received REAL DEFAULT 0,
            pix_sent REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_at TIMESTAMP,
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        )
    """)
    
    # Tabela de Transações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            tx_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"{Fore.GREEN}✅ Banco de dados do gateway inicializado!{Style.RESET_ALL}")

def log_info(message):
    print(f"{Fore.CYAN}[GATEWAY] {Fore.WHITE}{datetime.now().strftime('%H:%M:%S')} | {Fore.GREEN}{message}{Style.RESET_ALL}")

def log_payment(invoice_id, amount, crypto):
    print(f"{Fore.GREEN}💰 [PAYMENT] {Fore.WHITE}{datetime.now().strftime('%H:%M:%S')} | {Fore.YELLOW}Invoice #{invoice_id[:8]}... | {Fore.CYAN}{amount} {crypto}{Style.RESET_ALL}")

# ==================== HELPER FUNCTIONS ====================
def generate_api_key():
    return f"pk_{''.join(secrets.token_hex(16))}"

def generate_invoice_id():
    return f"inv_{''.join(secrets.token_hex(12))}"

def get_crypto_rates():
    """Taxas de conversão BRL por moeda"""
    return {
        'D1': 15.50,
        'D2': 22.30,
        'D3': 8.75,
        'D4': 35.20,
        'D5': 12.90,
        'D6': 18.40
    }

def check_deposit_balance(address, crypto):
    """Verifica saldo REAL no sistema swap via API"""
    try:
        import requests
        
        crypto_to_id = {
            'D1': 1, 'D2': 2, 'D3': 3,
            'D4': 4, 'D5': 5, 'D6': 6
        }
        
        coin_id = crypto_to_id.get(crypto)
        if not coin_id:
            return 0
        
        response = requests.get(
            f'http://localhost:5581/api/wallet/{coin_id}/{address}',
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            balance = data.get('balance', 0)
            if balance > 0:
                print(f"{Fore.GREEN}💰 Saldo detectado: {balance} {crypto} no endereço {address[:20]}...{Style.RESET_ALL}")
            return balance
        
        return 0
        
    except Exception as e:
        return 0

def monitor_payments():
    """Monitora pagamentos pendentes"""
    log_info("🔍 Monitor de pagamentos iniciado")
    
    while True:
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM invoices 
                WHERE status = 'pending' AND deposit_address IS NOT NULL
            """)
            
            pending = cursor.fetchall()
            
            for invoice in pending:
                # Verificar saldo REAL no blockchain
                balance = check_deposit_balance(invoice['deposit_address'], invoice['payment_crypto'])
                
                # COMPARAR COM 4 CASAS DECIMAIS (igual ao swap)
                balance_rounded = round(balance, 4)
                payment_amount_rounded = round(invoice['payment_amount'], 4)
                
                if balance_rounded >= payment_amount_rounded:
                    # PAGAMENTO DETECTADO!
                    cursor.execute("""
                        UPDATE invoices
                        SET status = 'paid', 
                            crypto_received = ?,
                            paid_at = CURRENT_TIMESTAMP
                        WHERE invoice_id = ?
                    """, (balance, invoice['invoice_id']))
                    
                    # Registrar transação
                    cursor.execute("""
                        INSERT INTO transactions (invoice_id, type, amount, currency)
                        VALUES (?, 'crypto_in', ?, ?)
                    """, (invoice['invoice_id'], balance, invoice['payment_crypto']))
                    
                    # Simular conversão e envio PIX
                    rates = get_crypto_rates()
                    brl_amount = balance * rates.get(invoice['payment_crypto'], 10)
                    
                    cursor.execute("""
                        UPDATE invoices
                        SET pix_sent = ?
                        WHERE invoice_id = ?
                    """, (brl_amount, invoice['invoice_id']))
                    
                    cursor.execute("""
                        INSERT INTO transactions (invoice_id, type, amount, currency)
                        VALUES (?, 'pix_out', ?, 'BRL')
                    """, (invoice['invoice_id'], brl_amount))
                    
                    conn.commit()
                    log_payment(invoice['invoice_id'], balance, invoice['payment_crypto'])
                    
                    # Chamar webhook se configurado
                    cursor.execute('SELECT webhook_url FROM merchants WHERE id = ?', (invoice['merchant_id'],))
                    merchant = cursor.fetchone()
                    if merchant and merchant['webhook_url']:
                        notify_webhook(merchant['webhook_url'], invoice['invoice_id'], 'paid')
            
            conn.close()
            time.sleep(5)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erro no monitor: {e}{Style.RESET_ALL}")
            time.sleep(10)

def notify_webhook(url, invoice_id, status):
    """Notifica merchant via webhook"""
    try:
        import requests
        requests.post(url, json={'invoice_id': invoice_id, 'status': status}, timeout=5)
    except:
        pass

# ==================== ROUTES - DASHBOARD ====================
@app.route('/')
def index():
    return render_template('gateway_home.html')

@app.route('/merchant/register', methods=['GET', 'POST'])
def merchant_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        pix_key = request.form.get('pix_key')
        webhook_url = request.form.get('webhook_url', '')
        
        api_key = generate_api_key()
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO merchants (name, email, api_key, pix_key, webhook_url)
                VALUES (?, ?, ?, ?, ?)
            """, (name, email, api_key, pix_key, webhook_url))
            
            merchant_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            session['merchant_id'] = merchant_id
            session['api_key'] = api_key
            
            return redirect(url_for('merchant_dashboard'))
            
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('gateway_register.html', error='Email já cadastrado')
    
    return render_template('gateway_register.html')

@app.route('/merchant/login', methods=['GET', 'POST'])
def merchant_login():
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM merchants WHERE api_key = ?', (api_key,))
        merchant = cursor.fetchone()
        conn.close()
        
        if merchant:
            session['merchant_id'] = merchant['id']
            session['api_key'] = api_key
            return redirect(url_for('merchant_dashboard'))
        else:
            return render_template('gateway_login.html', error='API Key inválida')
    
    return render_template('gateway_login.html')

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

@app.route('/merchant/dashboard')
def merchant_dashboard():
    if 'merchant_id' not in session:
        return redirect(url_for('merchant_login'))
    
    merchant_id = session['merchant_id']
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM merchants WHERE id = ?', (merchant_id,))
    merchant = cursor.fetchone()
    
    cursor.execute("""
        SELECT * FROM invoices 
        WHERE merchant_id = ?
        ORDER BY created_at DESC
        LIMIT 50
    """, (merchant_id,))
    invoices = cursor.fetchall()
    
    # Estatísticas
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'paid' THEN amount_brl ELSE 0 END) as total_paid,
            COUNT(CASE WHEN status = 'paid' THEN 1 END) as count_paid
        FROM invoices
        WHERE merchant_id = ?
    """, (merchant_id,))
    stats = cursor.fetchone()
    
    conn.close()
    
    return render_template('gateway_dashboard.html', 
                         merchant=merchant, 
                         invoices=invoices,
                         stats=stats)

@app.route('/merchant/logout')
def merchant_logout():
    session.clear()
    return redirect(url_for('index'))

# ==================== API - CRIAR INVOICE ====================
@app.route('/api/invoice/create', methods=['POST'])
def api_create_invoice():
    api_key = request.headers.get('X-API-Key') or request.json.get('api_key')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM merchants WHERE api_key = ?', (api_key,))
    merchant = cursor.fetchone()
    
    if not merchant:
        conn.close()
        return jsonify({'error': 'API Key inválida'}), 401
    
    data = request.json
    amount_brl = float(data.get('amount'))
    description = data.get('description', '')
    customer_email = data.get('customer_email', '')
    
    invoice_id = generate_invoice_id()
    
    cursor.execute("""
        INSERT INTO invoices (merchant_id, invoice_id, amount_brl, description, customer_email)
        VALUES (?, ?, ?, ?, ?)
    """, (merchant['id'], invoice_id, amount_brl, description, customer_email))
    
    conn.commit()
    conn.close()
    
    log_info(f"📄 Nova invoice criada: {invoice_id} - R$ {amount_brl}")
    
    return jsonify({
        'success': True,
        'invoice_id': invoice_id,
        'amount_brl': amount_brl,
        'checkout_url': f'http://localhost:5583/checkout/{invoice_id}'
    })

@app.route('/api/invoice/<invoice_id>', methods=['GET'])
def api_get_invoice(invoice_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM invoices WHERE invoice_id = ?', (invoice_id,))
    invoice = cursor.fetchone()
    conn.close()
    
    if not invoice:
        return jsonify({'error': 'Invoice não encontrada'}), 404
    
    return jsonify(dict(invoice))

# ==================== CHECKOUT ====================
@app.route('/checkout/<invoice_id>')
def checkout(invoice_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM invoices WHERE invoice_id = ?', (invoice_id,))
    invoice = cursor.fetchone()
    
    if not invoice:
        conn.close()
        return "Invoice não encontrada", 404
    
    cursor.execute('SELECT name FROM merchants WHERE id = ?', (invoice['merchant_id'],))
    merchant = cursor.fetchone()
    
    conn.close()
    
    rates = get_crypto_rates()
    
    return render_template('gateway_checkout.html', 
                         invoice=invoice, 
                         merchant=merchant,
                         rates=rates)

@app.route('/api/checkout/select-crypto', methods=['POST'])
def api_select_crypto():
    data = request.json
    invoice_id = data.get('invoice_id')
    crypto = data.get('crypto')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM invoices WHERE invoice_id = ?', (invoice_id,))
    invoice = cursor.fetchone()
    
    if not invoice or invoice['status'] != 'pending':
        conn.close()
        return jsonify({'error': 'Invoice inválida'}), 400
    
    rates = get_crypto_rates()
    
    # USAR 4 CASAS DECIMAIS (igual ao swap)
    crypto_amount = round(invoice['amount_brl'] / rates.get(crypto, 10), 4)
    
    coin_prefixes = {
        'D1': 'd1', 'D2': 'd2', 'D3': 'd3',
        'D4': 'd4', 'D5': 'd5', 'D6': 'd6'
    }
    
    prefix = coin_prefixes.get(crypto, 'd1')
    deposit_address = f"{prefix}_{secrets.token_hex(20)}"
    
    cursor.execute("""
        UPDATE invoices
        SET payment_crypto = ?, payment_amount = ?, deposit_address = ?
        WHERE invoice_id = ?
    """, (crypto, crypto_amount, deposit_address, invoice_id))
    
    conn.commit()
    conn.close()
    
    log_info(f"Endereço gerado: {deposit_address} para {crypto_amount:.4f} {crypto}")
    
    return jsonify({
        'success': True,
        'crypto': crypto,
        'amount': crypto_amount,
        'deposit_address': deposit_address,
        'rate': rates.get(crypto)
    })

# ==================== MAIN ====================
if __name__ == '__main__':
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}  💳 CRYPTO PAYMENT GATEWAY  {Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    init_db()
    
    # Iniciar monitor de pagamentos
    monitor_thread = threading.Thread(target=monitor_payments, daemon=True)
    monitor_thread.start()
    
    print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  🌐 Gateway: {Fore.CYAN}http://localhost:5583{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  📊 Dashboard: {Fore.CYAN}http://localhost:5583/merchant/dashboard{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  🔑 Registrar: {Fore.CYAN}http://localhost:5583/merchant/register{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")
    
    app.run(debug=True, port=5583, host='0.0.0.0')
