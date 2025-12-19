#!/usr/bin/env python3
"""
🔥 STRESS TEST - Dummy Crypto Swap System
Testa o sistema ao máximo com operações randômicas
"""

import requests
import random
import time
import threading
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "http://localhost:5581"

# Estatísticas globais
stats = {
    'mints': 0,
    'burns': 0,
    'transfers': 0,
    'swaps': 0,
    'pix_buys': 0,
    'pix_sells': 0,
    'wallets_created': 0,
    'errors': 0,
    'total_operations': 0
}

wallets_pool = {}  # {coin_id: [addresses]}
active_threads = []
stop_test = False

def log(message, color=Fore.WHITE):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{color}[{timestamp}] {message}{Style.RESET_ALL}")

def log_success(message):
    log(f"✅ {message}", Fore.GREEN)

def log_error(message):
    log(f"❌ {message}", Fore.RED)

def log_info(message):
    log(f"ℹ️  {message}", Fore.CYAN)

def log_warning(message):
    log(f"⚠️  {message}", Fore.YELLOW)

def get_coins():
    """Obtém lista de moedas"""
    try:
        response = requests.get(f"{BASE_URL}/api/coins", timeout=5)
        return response.json()
    except Exception as e:
        log_error(f"Erro ao buscar moedas: {e}")
        return []

def generate_wallet(coin_id, coin_symbol):
    """Gera uma nova carteira"""
    try:
        response = requests.get(f"{BASE_URL}/api/generate-address/{coin_symbol}", timeout=5)
        data = response.json()
        
        if 'address' in data:
            address = data['address']
            
            if coin_id not in wallets_pool:
                wallets_pool[coin_id] = []
            
            wallets_pool[coin_id].append(address)
            
            stats['wallets_created'] += 1
            stats['total_operations'] += 1
            
            log_success(f"Carteira criada: {address[:20]}... ({coin_symbol})")
            return address
        
        return None
    except Exception as e:
        log_error(f"Erro ao gerar carteira: {e}")
        stats['errors'] += 1
        return None

def mint_coins(coin_id, coin_symbol, amount=None):
    """Mint de moedas aleatórias"""
    try:
        if not amount:
            amount = random.uniform(100, 5000)
        
        # Pegar ou criar carteira
        if coin_id in wallets_pool and wallets_pool[coin_id]:
            address = random.choice(wallets_pool[coin_id])
        else:
            address = generate_wallet(coin_id, coin_symbol)
        
        if not address:
            return False
        
        response = requests.post(f"{BASE_URL}/api/mint", 
                                json={
                                    'coin_id': coin_id,
                                    'address': address,
                                    'amount': amount
                                },
                                timeout=5)
        
        data = response.json()
        
        if data.get('success'):
            stats['mints'] += 1
            stats['total_operations'] += 1
            log_success(f"MINT: {amount:.2f} {coin_symbol} → {address[:15]}...")
            return True
        else:
            log_error(f"Falha no mint: {data.get('error')}")
            stats['errors'] += 1
            return False
            
    except Exception as e:
        log_error(f"Erro no mint: {e}")
        stats['errors'] += 1
        return False

def burn_coins(coin_id, coin_symbol):
    """Burn de moedas aleatórias"""
    try:
        if coin_id not in wallets_pool or not wallets_pool[coin_id]:
            return False
        
        address = random.choice(wallets_pool[coin_id])
        amount = random.uniform(1, 100)
        
        response = requests.post(f"{BASE_URL}/api/burn",
                                json={
                                    'coin_id': coin_id,
                                    'address': address,
                                    'amount': amount
                                },
                                timeout=5)
        
        data = response.json()
        
        if data.get('success'):
            stats['burns'] += 1
            stats['total_operations'] += 1
            log_success(f"BURN: {amount:.2f} {coin_symbol} from {address[:15]}...")
            return True
        else:
            stats['errors'] += 1
            return False
            
    except Exception as e:
        stats['errors'] += 1
        return False

def transfer_coins(coin_id, coin_symbol):
    """Transfer entre carteiras"""
    try:
        if coin_id not in wallets_pool or len(wallets_pool[coin_id]) < 2:
            return False
        
        from_address = random.choice(wallets_pool[coin_id])
        to_address = random.choice([a for a in wallets_pool[coin_id] if a != from_address])
        
        if not to_address:
            to_address = generate_wallet(coin_id, coin_symbol)
        
        amount = random.uniform(1, 50)
        
        response = requests.post(f"{BASE_URL}/api/transfer",
                                json={
                                    'coin_id': coin_id,
                                    'from_address': from_address,
                                    'to_address': to_address,
                                    'amount': amount
                                },
                                timeout=5)
        
        data = response.json()
        
        if data.get('success'):
            stats['transfers'] += 1
            stats['total_operations'] += 1
            log_success(f"TRANSFER: {amount:.2f} {coin_symbol} ({from_address[:10]}... → {to_address[:10]}...)")
            return True
        else:
            stats['errors'] += 1
            return False
            
    except Exception as e:
        stats['errors'] += 1
        return False

def create_crypto_swap(coins):
    """Cria swap crypto-crypto"""
    try:
        if len(coins) < 2:
            return False
        
        from_coin = random.choice(coins)
        to_coin = random.choice([c for c in coins if c['id'] != from_coin['id']])
        
        # Criar carteiras se necessário
        if from_coin['id'] not in wallets_pool or not wallets_pool[from_coin['id']]:
            generate_wallet(from_coin['id'], from_coin['symbol'])
        
        if to_coin['id'] not in wallets_pool or not wallets_pool[to_coin['id']]:
            generate_wallet(to_coin['id'], to_coin['symbol'])
        
        from_amount = random.uniform(10, 100)
        destination = random.choice(wallets_pool[to_coin['id']])
        
        # Primeiro, mint moedas para a carteira de origem
        from_address = random.choice(wallets_pool[from_coin['id']])
        mint_coins(from_coin['id'], from_coin['symbol'], from_amount + 10)
        
        time.sleep(0.5)
        
        # Criar ordem de swap
        response = requests.post(f"{BASE_URL}/api/swap/create-order",
                                json={
                                    'from_type': 'coin',
                                    'to_type': 'coin',
                                    'from_coin_id': from_coin['id'],
                                    'to_coin_id': to_coin['id'],
                                    'from_amount': from_amount,
                                    'destination_address': destination
                                },
                                timeout=5)
        
        data = response.json()
        
        if data.get('success'):
            deposit_address = data['deposit_address']
            
            # Enviar moedas para o depósito
            requests.post(f"{BASE_URL}/api/transfer",
                         json={
                             'coin_id': from_coin['id'],
                             'from_address': from_address,
                             'to_address': deposit_address,
                             'amount': from_amount
                         },
                         timeout=5)
            
            stats['swaps'] += 1
            stats['total_operations'] += 1
            log_success(f"SWAP: {from_amount:.2f} {from_coin['symbol']} → {to_coin['symbol']}")
            return True
        else:
            stats['errors'] += 1
            return False
            
    except Exception as e:
        log_error(f"Erro no swap: {e}")
        stats['errors'] += 1
        return False

def create_pix_buy(coins):
    """Simula compra PIX → Crypto"""
    try:
        coin = random.choice(coins)
        
        if coin['id'] not in wallets_pool or not wallets_pool[coin['id']]:
            generate_wallet(coin['id'], coin['symbol'])
        
        brl_amount = random.uniform(50, 500)
        destination = random.choice(wallets_pool[coin['id']])
        
        # Criar ordem
        response = requests.post(f"{BASE_URL}/api/swap/create-order",
                                json={
                                    'from_type': 'pix',
                                    'to_type': 'coin',
                                    'to_coin_id': coin['id'],
                                    'from_amount': brl_amount,
                                    'destination_address': destination
                                },
                                timeout=5)
        
        data = response.json()
        
        if data.get('success'):
            order_id = data['order_id']
            
            # Simular pagamento
            time.sleep(0.5)
            requests.post(f"{BASE_URL}/api/pix/simulate-payment/{order_id}", timeout=5)
            
            stats['pix_buys'] += 1
            stats['total_operations'] += 1
            log_success(f"PIX BUY: R$ {brl_amount:.2f} → {coin['symbol']}")
            return True
        else:
            stats['errors'] += 1
            return False
            
    except Exception as e:
        log_error(f"Erro na compra PIX: {e}")
        stats['errors'] += 1
        return False

def create_pix_sell(coins):
    """Simula venda Crypto → PIX"""
    try:
        coin = random.choice(coins)
        
        if coin['id'] not in wallets_pool or not wallets_pool[coin['id']]:
            return False
        
        coin_amount = random.uniform(5, 50)
        from_address = random.choice(wallets_pool[coin['id']])
        pix_key = f"{random.randint(10000000000, 99999999999)}"
        
        # Mint moedas primeiro
        mint_coins(coin['id'], coin['symbol'], coin_amount + 10)
        time.sleep(0.5)
        
        # Criar ordem
        response = requests.post(f"{BASE_URL}/api/swap/create-order",
                                json={
                                    'from_type': 'coin',
                                    'to_type': 'pix',
                                    'from_coin_id': coin['id'],
                                    'from_amount': coin_amount,
                                    'destination_address': pix_key,
                                    'pix_key': pix_key
                                },
                                timeout=5)
        
        data = response.json()
        
        if data.get('success'):
            deposit_address = data['deposit_address']
            
            # Enviar moedas
            requests.post(f"{BASE_URL}/api/transfer",
                         json={
                             'coin_id': coin['id'],
                             'from_address': from_address,
                             'to_address': deposit_address,
                             'amount': coin_amount
                         },
                         timeout=5)
            
            stats['pix_sells'] += 1
            stats['total_operations'] += 1
            log_success(f"PIX SELL: {coin_amount:.2f} {coin['symbol']} → PIX")
            return True
        else:
            stats['errors'] += 1
            return False
            
    except Exception as e:
        log_error(f"Erro na venda PIX: {e}")
        stats['errors'] += 1
        return False

def stress_test_worker(worker_id, coins, operations_per_cycle=10, delay=1):
    """Worker que executa operações aleatórias"""
    global stop_test
    
    log_info(f"Worker #{worker_id} iniciado")
    
    operations = [
        ('mint', 30, lambda: mint_coins(random.choice(coins)['id'], random.choice(coins)['symbol'])),
        ('burn', 10, lambda: burn_coins(random.choice(coins)['id'], random.choice(coins)['symbol'])),
        ('transfer', 25, lambda: transfer_coins(random.choice(coins)['id'], random.choice(coins)['symbol'])),
        ('swap', 15, lambda: create_crypto_swap(coins)),
        ('pix_buy', 10, lambda: create_pix_buy(coins)),
        ('pix_sell', 10, lambda: create_pix_sell(coins))
    ]
    
    while not stop_test:
        try:
            for _ in range(operations_per_cycle):
                if stop_test:
                    break
                
                # Escolher operação aleatória baseada nos pesos
                op_name, weight, func = random.choices(operations, 
                                                       weights=[w for _, w, _ in operations])[0]
                
                try:
                    func()
                except Exception as e:
                    log_error(f"Worker #{worker_id} erro em {op_name}: {e}")
                
                time.sleep(random.uniform(0.1, 0.5))
            
            time.sleep(delay)
            
        except Exception as e:
            log_error(f"Worker #{worker_id} erro crítico: {e}")
            time.sleep(2)
    
    log_warning(f"Worker #{worker_id} finalizado")

def print_stats():
    """Imprime estatísticas em tempo real"""
    global stop_test
    
    while not stop_test:
        time.sleep(5)
        
        if stop_test:
            break
        
        print(f"\n{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 ESTATÍSTICAS DO STRESS TEST{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Operações Totais: {stats['total_operations']}{Style.RESET_ALL}")
        print(f"   🪙  Mints: {stats['mints']}")
        print(f"   🔥 Burns: {stats['burns']}")
        print(f"   📤 Transfers: {stats['transfers']}")
        print(f"   🔄 Swaps: {stats['swaps']}")
        print(f"   💳 PIX Compras: {stats['pix_buys']}")
        print(f"   💸 PIX Vendas: {stats['pix_sells']}")
        print(f"   👛 Carteiras Criadas: {stats['wallets_created']}")
        print(f"{Fore.RED}❌ Erros: {stats['errors']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")

def main():
    global stop_test
    
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.RED}{Style.BRIGHT}🔥 STRESS TEST - DUMMY CRYPTO SWAP SYSTEM 🔥{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}{'='*70}{Style.RESET_ALL}\n")
    
    log_info("Conectando ao servidor...")
    
    coins = get_coins()
    
    if not coins:
        log_error("Não foi possível conectar ao servidor!")
        log_error("Certifique-se que app.py está rodando em http://localhost:5581")
        return
    
    log_success(f"Conectado! {len(coins)} moedas detectadas")
    
    # Configuração
    print(f"\n{Fore.CYAN}⚙️  CONFIGURAÇÃO DO TESTE{Style.RESET_ALL}")
    print("=" * 70)
    
    try:
        num_workers = int(input(f"{Fore.YELLOW}Número de workers simultâneos (1-20): {Style.RESET_ALL}") or "5")
        num_workers = max(1, min(20, num_workers))
    except:
        num_workers = 5
    
    try:
        duration = int(input(f"{Fore.YELLOW}Duração do teste em segundos (0 = infinito): {Style.RESET_ALL}") or "60")
    except:
        duration = 60
    
    print("=" * 70)
    
    log_info(f"Iniciando {num_workers} workers...")
    log_info(f"Duração: {duration if duration > 0 else 'Infinito'} segundos")
    log_info("Pressione Ctrl+C para parar")
    
    print(f"\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🚀 TESTE INICIADO!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")
    
    time.sleep(1)
    
    # Criar workers
    for i in range(num_workers):
        thread = threading.Thread(target=stress_test_worker, 
                                 args=(i+1, coins, 10, 1),
                                 daemon=True)
        thread.start()
        active_threads.append(thread)
    
    # Thread de estatísticas
    stats_thread = threading.Thread(target=print_stats, daemon=True)
    stats_thread.start()
    
    try:
        if duration > 0:
            time.sleep(duration)
            stop_test = True
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        log_warning("\nInterrompido pelo usuário!")
        stop_test = True
    
    log_info("Aguardando finalização dos workers...")
    time.sleep(2)
    
    # Estatísticas finais
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}📊 RESULTADO FINAL DO STRESS TEST{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Operações Totais: {stats['total_operations']}{Style.RESET_ALL}")
    print(f"   🪙  Mints: {stats['mints']}")
    print(f"   🔥 Burns: {stats['burns']}")
    print(f"   📤 Transfers: {stats['transfers']}")
    print(f"   🔄 Swaps: {stats['swaps']}")
    print(f"   💳 PIX Compras: {stats['pix_buys']}")
    print(f"   💸 PIX Vendas: {stats['pix_sells']}")
    print(f"   👛 Carteiras Criadas: {stats['wallets_created']}")
    print(f"{Fore.RED}❌ Erros: {stats['errors']}{Style.RESET_ALL}")
    
    if stats['total_operations'] > 0:
        success_rate = ((stats['total_operations'] - stats['errors']) / stats['total_operations']) * 100
        print(f"{Fore.CYAN}📈 Taxa de Sucesso: {success_rate:.2f}%{Style.RESET_ALL}")
    
    print(f"{Fore.YELLOW}{Style.BRIGHT}{'='*70}{Style.RESET_ALL}\n")
    
    log_success("Stress test finalizado!")

if __name__ == '__main__':
    main()
