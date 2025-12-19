from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import hashlib
import json
from datetime import datetime
import secrets
import random
import time
import threading
from colorama import Fore, Back, Style, init

init(autoreset=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dummy-crypto-swap-secret-key'

DATABASE = 'blockchain.db'

# ==================== CONTROLE GLOBAL ====================
simulation_active = {}
simulation_threads = {}
rate_fluctuation_active = False
rate_fluctuation_thread = None
fluctuation_interval = 300
swap_monitor_active = True
swap_monitor_thread = None
pix_brl_rates = {}  # Taxas BRL para cada moeda

# ==================== LOGGING ====================
def log_info(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{Fore.CYAN}[INFO] {Fore.WHITE}{timestamp} | {Fore.GREEN}{message}{Style.RESET_ALL}")

def log_success(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{Fore.GREEN}[SUCCESS] {Fore.WHITE}{timestamp} | {Fore.GREEN}{message}{Style.RESET_ALL}")

def log_warning(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{Fore.YELLOW}[WARN] {Fore.WHITE}{timestamp} | {Fore.YELLOW}{message}{Style.RESET_ALL}")

def log_error(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{Fore.RED}[ERROR] {Fore.WHITE}{timestamp} | {Fore.RED}{message}{Style.RESET_ALL}")

def log_transaction(coin, from_addr, to_addr, amount):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{Fore.MAGENTA}[TX] {Fore.WHITE}{timestamp} | {Fore.CYAN}{coin}{Fore.WHITE} | "
          f"{Fore.YELLOW}{from_addr[:15]}... {Fore.WHITE}→ {Fore.GREEN}{to_addr[:15]}... {Fore.WHITE}| "
          f"{Fore.MAGENTA}{amount:.4f} {coin}{Style.RESET_ALL}")

def log_pix(operation, amount, coin=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if operation == 'buy':
        print(f"{Fore.GREEN}[PIX-BUY] {Fore.WHITE}{timestamp} | {Fore.YELLOW}R$ {amount:.2f} {Fore.WHITE}→ {Fore.CYAN}{coin}{Style.RESET_ALL}")
    else:
        print(f"{Fore.BLUE}[PIX-SELL] {Fore.WHITE}{timestamp} | {Fore.CYAN}{coin} {Fore.WHITE}→ {Fore.YELLOW}R$ {amount:.2f}{Style.RESET_ALL}")

# ==================== DATABASE ====================
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            symbol TEXT NOT NULL UNIQUE,
            prefix TEXT NOT NULL,
            total_supply REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id INTEGER NOT NULL,
            block_number INTEGER NOT NULL,
            hash TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            nonce INTEGER DEFAULT 0,
            FOREIGN KEY (coin_id) REFERENCES coins (id),
            UNIQUE(coin_id, block_number)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_id INTEGER NOT NULL,
            coin_id INTEGER NOT NULL,
            from_address TEXT NOT NULL,
            to_address TEXT NOT NULL,
            amount REAL NOT NULL,
            tx_type TEXT DEFAULT 'transfer',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (block_id) REFERENCES blocks (id),
            FOREIGN KEY (coin_id) REFERENCES coins (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id INTEGER NOT NULL,
            address TEXT NOT NULL,
            balance REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coin_id) REFERENCES coins (id),
            UNIQUE(coin_id, address)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS swaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_coin_id INTEGER NOT NULL,
            to_coin_id INTEGER NOT NULL,
            from_address TEXT NOT NULL,
            to_address TEXT NOT NULL,
            from_amount REAL NOT NULL,
            to_amount REAL NOT NULL,
            exchange_rate REAL NOT NULL,
            fee_amount REAL DEFAULT 0,
            fee_percentage REAL DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_coin_id) REFERENCES coins (id),
            FOREIGN KEY (to_coin_id) REFERENCES coins (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_coin_id INTEGER NOT NULL,
            to_coin_id INTEGER NOT NULL,
            rate REAL NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_coin_id) REFERENCES coins (id),
            FOREIGN KEY (to_coin_id) REFERENCES coins (id),
            UNIQUE(from_coin_id, to_coin_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS liquidity_pools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id INTEGER NOT NULL,
            total_liquidity REAL DEFAULT 0,
            reserved_liquidity REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coin_id) REFERENCES coins (id),
            UNIQUE(coin_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS swap_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL UNIQUE,
            from_coin_id INTEGER,
            to_coin_id INTEGER,
            from_amount REAL NOT NULL,
            to_amount REAL NOT NULL,
            exchange_rate REAL NOT NULL,
            fee_percentage REAL NOT NULL,
            fee_amount REAL NOT NULL,
            deposit_address TEXT NOT NULL,
            destination_address TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            order_type TEXT DEFAULT 'crypto',
            pix_key TEXT,
            pix_qrcode TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)

    # NOVA: Tabela de taxas PIX/BRL
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pix_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id INTEGER NOT NULL,
            buy_rate REAL NOT NULL,
            sell_rate REAL NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coin_id) REFERENCES coins (id),
            UNIQUE(coin_id)
        )
    """)

    # Inserir moedas
    coins_data = [
        ('Dummy Coin 1', 'D1', 'd1_'),
        ('Dummy Coin 2', 'D2', 'd2_'),
        ('Dummy Coin 3', 'D3', 'd3_'),
        ('Dummy Coin 4', 'D4', 'd4_'),
        ('Dummy Coin 5', 'D5', 'd5_'),
        ('Dummy Coin 6', 'D6', 'd6_')
    ]

    for name, symbol, prefix in coins_data:
        cursor.execute('SELECT id FROM coins WHERE symbol = ?', (symbol,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO coins (name, symbol, prefix) VALUES (?, ?, ?)',
                         (name, symbol, prefix))
            log_success(f"Moeda {name} ({symbol}) criada!")

            coin_id = cursor.lastrowid
            genesis_hash = hashlib.sha256(f'{symbol}_genesis_block'.encode()).hexdigest()
            cursor.execute("""
                INSERT INTO blocks (coin_id, block_number, hash, previous_hash, nonce)
                VALUES (?, 0, ?, '0', 0)
            """, (coin_id, genesis_hash))

    # Inicializar taxas de câmbio entre moedas
    cursor.execute('SELECT id, symbol FROM coins')
    coins_list = cursor.fetchall()

    for from_coin in coins_list:
        for to_coin in coins_list:
            if from_coin['id'] != to_coin['id']:
                cursor.execute("""
                    SELECT id FROM exchange_rates 
                    WHERE from_coin_id = ? AND to_coin_id = ?
                """, (from_coin['id'], to_coin['id']))

                if not cursor.fetchone():
                    initial_rate = random.uniform(0.5, 2.0)
                    cursor.execute("""
                        INSERT INTO exchange_rates (from_coin_id, to_coin_id, rate)
                        VALUES (?, ?, ?)
                    """, (from_coin['id'], to_coin['id'], initial_rate))

        # Criar pool
        cursor.execute('SELECT id FROM liquidity_pools WHERE coin_id = ?', (from_coin['id'],))
        if not cursor.fetchone():
            initial_liquidity = random.uniform(50000, 100000)
            cursor.execute("""
                INSERT INTO liquidity_pools (coin_id, total_liquidity, reserved_liquidity)
                VALUES (?, ?, 0)
            """, (from_coin['id'], initial_liquidity))

            pool_address = f"POOL_{from_coin['symbol']}_LIQUIDITY"
            cursor.execute("""
                INSERT OR IGNORE INTO wallets (coin_id, address, balance)
                VALUES (?, ?, ?)
            """, (from_coin['id'], pool_address, initial_liquidity))

        # Criar carteira de taxas
        fee_wallet = f"FEE_WALLET_{from_coin['symbol']}"
        cursor.execute("""
            INSERT OR IGNORE INTO wallets (coin_id, address, balance)
            VALUES (?, ?, 0)
        """, (from_coin['id'], fee_wallet))

        # Criar taxas PIX/BRL
        cursor.execute('SELECT id FROM pix_rates WHERE coin_id = ?', (from_coin['id'],))
        if not cursor.fetchone():
            buy_rate = random.uniform(5.0, 50.0)  # R$ 5 a R$ 50 por moeda
            sell_rate = buy_rate * 0.95  # Venda é 5% menor
            cursor.execute("""
                INSERT INTO pix_rates (coin_id, buy_rate, sell_rate)
                VALUES (?, ?, ?)
            """, (from_coin['id'], buy_rate, sell_rate))
            log_info(f"Taxa PIX para {from_coin['symbol']}: Compra R$ {buy_rate:.2f} | Venda R$ {sell_rate:.2f}")

    conn.commit()
    conn.close()
    log_success("Banco de dados inicializado!")

# ==================== HELPER FUNCTIONS ====================
def generate_address(coin_prefix):
    random_code = secrets.token_hex(16)
    return f"{coin_prefix}{random_code}"

def calculate_block_hash(block_number, previous_hash, transactions, nonce):
    block_data = f"{block_number}{previous_hash}{json.dumps(transactions)}{nonce}"
    return hashlib.sha256(block_data.encode()).hexdigest()

def get_wallet_balance(coin_id, address):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM wallets WHERE coin_id = ? AND address = ?',
                  (coin_id, address))
    result = cursor.fetchone()
    conn.close()
    return result['balance'] if result else 0

def update_wallet_balance(coin_id, address, amount, operation='add'):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT balance FROM wallets WHERE coin_id = ? AND address = ?',
                  (coin_id, address))
    wallet = cursor.fetchone()

    if wallet:
        current_balance = wallet['balance']
        new_balance = current_balance + amount if operation == 'add' else current_balance - amount
        cursor.execute('UPDATE wallets SET balance = ? WHERE coin_id = ? AND address = ?',
                      (new_balance, coin_id, address))
    else:
        new_balance = amount if operation == 'add' else 0
        cursor.execute('INSERT INTO wallets (coin_id, address, balance) VALUES (?, ?, ?)',
                      (coin_id, address, new_balance))

    conn.commit()
    conn.close()
    return new_balance

def get_pix_rates(coin_id):
    """Retorna taxas de compra e venda PIX"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT buy_rate, sell_rate FROM pix_rates WHERE coin_id = ?', (coin_id,))
    result = cursor.fetchone()
    conn.close()
    return {'buy': result['buy_rate'], 'sell': result['sell_rate']} if result else None

def generate_pix_qrcode():
    """Gera QR Code PIX falso"""
    return f"00020126580014BR.GOV.BCB.PIX0136{secrets.token_hex(18)}520400005303986540{random.randint(1,999):03d}.{random.randint(0,99):02d}5802BR5925Dummy Crypto Swap6009SAO PAULO62{secrets.token_hex(4)}6304{secrets.token_hex(2)}"

print("✅ Parte 1 criada - Inicialização do sistema")

# ==================== TRANSACTION FUNCTIONS ====================
def mint_transaction(coin_id, address, amount):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM blocks WHERE coin_id = ? 
        ORDER BY block_number DESC LIMIT 1
    """, (coin_id,))
    last_block = cursor.fetchone()

    new_block_number = last_block['block_number'] + 1
    previous_hash = last_block['hash']
    nonce = secrets.randbelow(1000000)

    tx_data = [{'from': 'MINT', 'to': address, 'amount': amount}]
    new_hash = calculate_block_hash(new_block_number, previous_hash, tx_data, nonce)

    cursor.execute("""
        INSERT INTO blocks (coin_id, block_number, hash, previous_hash, nonce)
        VALUES (?, ?, ?, ?, ?)
    """, (coin_id, new_block_number, new_hash, previous_hash, nonce))

    block_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO transactions (block_id, coin_id, from_address, to_address, amount, tx_type)
        VALUES (?, ?, 'MINT', ?, ?, 'mint')
    """, (block_id, coin_id, address, amount))

    cursor.execute("""
        UPDATE coins SET total_supply = total_supply + ? WHERE id = ?
    """, (amount, coin_id))

    cursor.execute('SELECT symbol FROM coins WHERE id = ?', (coin_id,))
    coin_symbol = cursor.fetchone()['symbol']

    conn.commit()
    conn.close()

    update_wallet_balance(coin_id, address, amount, 'add')
    log_transaction(coin_symbol, 'MINT', address, amount)

    return {'block_number': new_block_number, 'hash': new_hash}

def burn_transaction(coin_id, address, amount):
    balance = get_wallet_balance(coin_id, address)
    if balance < amount:
        return None

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM blocks WHERE coin_id = ? 
        ORDER BY block_number DESC LIMIT 1
    """, (coin_id,))
    last_block = cursor.fetchone()

    new_block_number = last_block['block_number'] + 1
    previous_hash = last_block['hash']
    nonce = secrets.randbelow(1000000)

    tx_data = [{'from': address, 'to': 'BURN', 'amount': amount}]
    new_hash = calculate_block_hash(new_block_number, previous_hash, tx_data, nonce)

    cursor.execute("""
        INSERT INTO blocks (coin_id, block_number, hash, previous_hash, nonce)
        VALUES (?, ?, ?, ?, ?)
    """, (coin_id, new_block_number, new_hash, previous_hash, nonce))

    block_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO transactions (block_id, coin_id, from_address, to_address, amount, tx_type)
        VALUES (?, ?, ?, 'BURN', ?, 'burn')
    """, (block_id, coin_id, address, amount))

    cursor.execute("""
        UPDATE coins SET total_supply = total_supply - ? WHERE id = ?
    """, (amount, coin_id))

    cursor.execute('SELECT symbol FROM coins WHERE id = ?', (coin_id,))
    coin_symbol = cursor.fetchone()['symbol']

    conn.commit()
    conn.close()

    update_wallet_balance(coin_id, address, amount, 'subtract')
    log_transaction(coin_symbol, address, 'BURN', amount)

    return {'block_number': new_block_number, 'hash': new_hash}

def transfer_transaction(coin_id, from_address, to_address, amount):
    balance = get_wallet_balance(coin_id, from_address)
    if balance < amount:
        return None

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM blocks WHERE coin_id = ? 
        ORDER BY block_number DESC LIMIT 1
    """, (coin_id,))
    last_block = cursor.fetchone()

    new_block_number = last_block['block_number'] + 1
    previous_hash = last_block['hash']
    nonce = secrets.randbelow(1000000)

    tx_data = [{'from': from_address, 'to': to_address, 'amount': amount}]
    new_hash = calculate_block_hash(new_block_number, previous_hash, tx_data, nonce)

    cursor.execute("""
        INSERT INTO blocks (coin_id, block_number, hash, previous_hash, nonce)
        VALUES (?, ?, ?, ?, ?)
    """, (coin_id, new_block_number, new_hash, previous_hash, nonce))

    block_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO transactions (block_id, coin_id, from_address, to_address, amount, tx_type)
        VALUES (?, ?, ?, ?, ?, 'transfer')
    """, (block_id, coin_id, from_address, to_address, amount))

    cursor.execute('SELECT symbol FROM coins WHERE id = ?', (coin_id,))
    coin_symbol = cursor.fetchone()['symbol']

    conn.commit()
    conn.close()

    update_wallet_balance(coin_id, from_address, amount, 'subtract')
    update_wallet_balance(coin_id, to_address, amount, 'add')
    log_transaction(coin_symbol, from_address, to_address, amount)

    return {'block_number': new_block_number, 'hash': new_hash}

# ==================== SWAP MONITORING ====================
def monitor_swap_deposits():
    """Monitora depósitos em endereços de swap"""
    global swap_monitor_active

    log_info("🔍 Monitor de depósitos iniciado")

    while swap_monitor_active:
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM swap_orders 
                WHERE status = 'pending' AND order_type = 'crypto'
            """)
            pending_orders = cursor.fetchall()

            for order in pending_orders:
                deposit_balance = get_wallet_balance(order['from_coin_id'], order['deposit_address'])

                if deposit_balance >= order['from_amount']:
                    # Processar swap
                    cursor.execute('SELECT symbol FROM coins WHERE id = ?', (order['from_coin_id'],))
                    from_symbol = cursor.fetchone()['symbol']

                    cursor.execute('SELECT symbol FROM coins WHERE id = ?', (order['to_coin_id'],))
                    to_symbol = cursor.fetchone()['symbol']

                    fee_amount = order['fee_amount']
                    fee_wallet = f"FEE_WALLET_{from_symbol}"
                    transfer_transaction(order['from_coin_id'], order['deposit_address'], fee_wallet, fee_amount)

                    remaining_amount = order['from_amount'] - fee_amount
                    pool_address = f"POOL_{from_symbol}_LIQUIDITY"
                    transfer_transaction(order['from_coin_id'], order['deposit_address'], pool_address, remaining_amount)

                    pool_to_address = f"POOL_{to_symbol}_LIQUIDITY"
                    transfer_transaction(order['to_coin_id'], pool_to_address, order['destination_address'], order['to_amount'])

                    cursor.execute("""
                        INSERT INTO swaps (from_coin_id, to_coin_id, from_address, to_address, 
                                         from_amount, to_amount, exchange_rate, fee_amount, fee_percentage)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (order['from_coin_id'], order['to_coin_id'], order['deposit_address'], 
                          order['destination_address'], order['from_amount'], order['to_amount'], 
                          order['exchange_rate'], fee_amount, order['fee_percentage']))

                    cursor.execute("""
                        UPDATE swap_orders 
                        SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (order['id'],))

                    conn.commit()
                    log_success(f"✅ SWAP completo: {order['from_amount']:.2f} {from_symbol} → {order['to_amount']:.2f} {to_symbol}")

            conn.close()
            time.sleep(5)

        except Exception as e:
            log_error(f"Erro no monitor: {e}")
            time.sleep(10)

# ==================== PIX RATE FLUCTUATION ====================
def fluctuate_pix_rates():
    """Flutua taxas PIX/BRL automaticamente"""
    global rate_fluctuation_active

    log_info("💱 Flutuação de taxas PIX iniciada")

    while rate_fluctuation_active:
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM pix_rates')
            rates = cursor.fetchall()

            for rate in rates:
                fluctuation = random.uniform(-0.05, 0.05)
                new_buy = rate['buy_rate'] * (1 + fluctuation)
                new_buy = max(1.0, min(100.0, new_buy))
                new_sell = new_buy * 0.95

                cursor.execute("""
                    UPDATE pix_rates
                    SET buy_rate = ?, sell_rate = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_buy, new_sell, rate['id']))

            conn.commit()
            conn.close()

            time.sleep(fluctuation_interval)

        except Exception as e:
            log_error(f"Erro na flutuação PIX: {e}")
            time.sleep(60)

def fluctuate_exchange_rates():
    """Flutua taxas entre moedas"""
    global rate_fluctuation_active, fluctuation_interval

    log_info("🔄 Flutuação de cotações iniciada")

    while rate_fluctuation_active:
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('SELECT id, from_coin_id, to_coin_id, rate FROM exchange_rates')
            rates = cursor.fetchall()

            for rate_row in rates:
                fluctuation = random.uniform(-0.10, 0.10)
                old_rate = rate_row['rate']
                new_rate = old_rate * (1 + fluctuation)
                new_rate = max(0.1, min(10.0, new_rate))

                cursor.execute("""
                    UPDATE exchange_rates
                    SET rate = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_rate, rate_row['id']))

            conn.commit()
            conn.close()

            wait_time = random.uniform(fluctuation_interval * 0.8, fluctuation_interval * 1.2)
            time.sleep(wait_time)

        except Exception as e:
            log_error(f"Erro na flutuação: {e}")
            time.sleep(60)

print("✅ Parte 2 criada - Transações e monitoramento")
