from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import requests
from datetime import datetime
import json

app = Flask(__name__, template_folder='templates_shop', static_folder='static_shop')
app.config['SECRET_KEY'] = 'demo-shop-secret-2024'

# ==================== CONFIGURAÇÃO ====================
GATEWAY_URL = "http://localhost:5583"
GATEWAY_API_KEY = "pk_2c6b3d0887efd00e875db2d07db6fb1d"  # Altere após registrar no gateway

# Produtos da loja (em memória)
PRODUCTS = [
    {
        'id': 1,
        'name': 'Notebook Gamer',
        'description': 'Intel i7, RTX 3060, 16GB RAM',
        'price': 4999.99,
        'image': '💻',
        'category': 'Eletrônicos'
    },
    {
        'id': 2,
        'name': 'Smartphone Pro',
        'description': 'Câmera 108MP, 5G, 256GB',
        'price': 2499.50,
        'image': '📱',
        'category': 'Eletrônicos'
    },
    {
        'id': 3,
        'name': 'Fone Bluetooth Premium',
        'description': 'Cancelamento de ruído, 40h bateria',
        'price': 899.90,
        'image': '🎧',
        'category': 'Áudio'
    },
    {
        'id': 4,
        'name': 'Smart Watch',
        'description': 'Monitor cardíaco, GPS, À prova dágua',
        'price': 1299.00,
        'image': '⌚',
        'category': 'Wearables'
    },
    {
        'id': 5,
        'name': 'Teclado Mecânico RGB',
        'description': 'Switch Blue, Retroiluminação RGB',
        'price': 449.90,
        'image': '⌨️',
        'category': 'Periféricos'
    },
    {
        'id': 6,
        'name': 'Mouse Gamer',
        'description': '16000 DPI, 8 botões programáveis',
        'price': 299.90,
        'image': '🖱️',
        'category': 'Periféricos'
    },
    {
        'id': 7,
        'name': 'Monitor 4K',
        'description': '27 polegadas, 144Hz, HDR',
        'price': 1899.00,
        'image': '🖥️',
        'category': 'Eletrônicos'
    },
    {
        'id': 8,
        'name': 'Webcam Full HD',
        'description': '1080p, 60fps, Microfone embutido',
        'price': 399.00,
        'image': '📹',
        'category': 'Periféricos'
    }
]

DATABASE = 'shop.db'

# ==================== DATABASE ====================
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL UNIQUE,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_address TEXT,
            items TEXT NOT NULL,
            total_amount REAL NOT NULL,
            invoice_id TEXT,
            payment_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_at TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados da loja inicializado")

# ==================== HELPER FUNCTIONS ====================
def get_product_by_id(product_id):
    for p in PRODUCTS:
        if p['id'] == product_id:
            return p
    return None

def get_cart():
    if 'cart' not in session:
        session['cart'] = []
    return session['cart']

def add_to_cart(product_id, quantity=1):
    cart = get_cart()
    
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            session.modified = True
            return
    
    product = get_product_by_id(product_id)
    if product:
        cart.append({
            'product_id': product_id,
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity,
            'image': product['image']
        })
        session.modified = True

def remove_from_cart(product_id):
    cart = get_cart()
    session['cart'] = [item for item in cart if item['product_id'] != product_id]
    session.modified = True

def get_cart_total():
    cart = get_cart()
    return sum(item['price'] * item['quantity'] for item in cart)

def clear_cart():
    session['cart'] = []
    session.modified = True

# ==================== ROUTES ====================
@app.route('/')
def index():
    categories = list(set(p['category'] for p in PRODUCTS))
    return render_template('shop_home.html', products=PRODUCTS, categories=categories)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return "Produto não encontrado", 404
    return render_template('shop_product.html', product=product)

@app.route('/cart')
def cart():
    cart_items = get_cart()
    total = get_cart_total()
    return render_template('shop_cart.html', cart=cart_items, total=total)

@app.route('/api/cart/add', methods=['POST'])
def api_add_to_cart():
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Produto não encontrado'}), 404
    
    add_to_cart(product_id, quantity)
    
    return jsonify({
        'success': True,
        'message': f'{product["name"]} adicionado ao carrinho',
        'cart_count': len(get_cart())
    })

@app.route('/api/cart/remove', methods=['POST'])
def api_remove_from_cart():
    data = request.json
    product_id = data.get('product_id')
    
    remove_from_cart(product_id)
    
    return jsonify({
        'success': True,
        'cart_count': len(get_cart()),
        'cart_total': get_cart_total()
    })

@app.route('/checkout')
def checkout():
    cart_items = get_cart()
    
    if not cart_items:
        return redirect(url_for('index'))
    
    total = get_cart_total()
    return render_template('shop_checkout.html', cart=cart_items, total=total)

@app.route('/api/checkout/process', methods=['POST'])
def api_process_checkout():
    data = request.json
    
    customer_name = data.get('name')
    customer_email = data.get('email')
    customer_address = data.get('address')
    
    cart_items = get_cart()
    
    if not cart_items:
        return jsonify({'error': 'Carrinho vazio'}), 400
    
    total = get_cart_total()
    
    # Gerar ID do pedido
    import secrets
    order_id = f"ORDER_{secrets.token_hex(8).upper()}"
    
    # Salvar pedido no banco
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO orders (order_id, customer_name, customer_email, customer_address, items, total_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (order_id, customer_name, customer_email, customer_address, json.dumps(cart_items), total))
    
    conn.commit()
    conn.close()
    
    # Criar invoice no gateway de pagamento
    try:
        response = requests.post(
            f"{GATEWAY_URL}/api/invoice/create",
            headers={'X-API-Key': GATEWAY_API_KEY},
            json={
                'amount': total,
                'description': f'Pedido {order_id}',
                'customer_email': customer_email
            },
            timeout=5
        )
        
        gateway_data = response.json()
        
        if gateway_data.get('success'):
            invoice_id = gateway_data['invoice_id']
            checkout_url = gateway_data['checkout_url']
            
            # Atualizar pedido com invoice_id
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('UPDATE orders SET invoice_id = ? WHERE order_id = ?', 
                         (invoice_id, order_id))
            conn.commit()
            conn.close()
            
            # Limpar carrinho
            clear_cart()
            
            return jsonify({
                'success': True,
                'order_id': order_id,
                'invoice_id': invoice_id,
                'checkout_url': checkout_url
            })
        else:
            return jsonify({'error': 'Erro ao criar pagamento'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro de conexão: {str(e)}'}), 500

@app.route('/order/<order_id>')
def order_detail(order_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
    order = cursor.fetchone()
    conn.close()
    
    if not order:
        return "Pedido não encontrado", 404
    
    items = json.loads(order['items'])
    
    # Verificar status no gateway
    payment_status = order['payment_status']
    
    if order['invoice_id'] and payment_status == 'pending':
        try:
            response = requests.get(f"{GATEWAY_URL}/api/invoice/{order['invoice_id']}", timeout=5)
            invoice_data = response.json()
            
            if invoice_data.get('status') == 'paid':
                # Atualizar status do pedido
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE orders 
                    SET payment_status = 'paid', paid_at = CURRENT_TIMESTAMP
                    WHERE order_id = ?
                """, (order_id,))
                conn.commit()
                conn.close()
                payment_status = 'paid'
        except:
            pass
    
    return render_template('shop_order.html', 
                         order=order, 
                         items=items, 
                         payment_status=payment_status)

@app.route('/config')
def config_page():
    return render_template('shop_config.html', api_key=GATEWAY_API_KEY)

@app.route('/api/config/update', methods=['POST'])
def api_update_config():
    global GATEWAY_API_KEY
    data = request.json
    new_api_key = data.get('api_key')
    
    if new_api_key:
        GATEWAY_API_KEY = new_api_key
        
        # Salvar em arquivo para persistir
        with open('shop_config.txt', 'w') as f:
            f.write(new_api_key)
        
        return jsonify({'success': True, 'message': 'API Key atualizada!'})
    
    return jsonify({'error': 'API Key inválida'}), 400

# ==================== MAIN ====================
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🛍️  LOJA DE DEMONSTRAÇÃO - CRYPTO PAYMENT GATEWAY")
    print("="*70)
    
    # Tentar carregar API Key salva
    try:
        with open('shop_config.txt', 'r') as f:
            saved_key = f.read().strip()
            if saved_key:
                GATEWAY_API_KEY = saved_key
                print(f"✅ API Key carregada: {GATEWAY_API_KEY[:20]}...")
    except:
        print("⚠️  API Key não configurada - Configure em /config")
    
    init_db()
    
    print("\n" + "="*70)
    print(f"🌐 Loja: http://localhost:5586")
    print(f"⚙️  Config: http://localhost:5586/config")
    print(f"🔗 Gateway: {GATEWAY_URL}")
    print("="*70 + "\n")
    
    app.run(debug=True, port=5586, host='0.0.0.0')
