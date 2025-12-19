#!/usr/bin/env python3
"""
Script para iniciar todos os sistemas de uma vez
"""

import subprocess
import time
import sys
import os
from colorama import Fore, Style, init

init(autoreset=True)

print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
print(f"{Fore.YELLOW}{Style.BRIGHT}  🚀 INICIANDO ECOSISTEMA COMPLETO  {Style.RESET_ALL}")
print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

processes = []

def start_process(script, name, port):
    print(f"{Fore.GREEN}▶️  Iniciando {name} (porta {port})...{Style.RESET_ALL}")
    
    if sys.platform == 'win32':
        # Windows
        process = subprocess.Popen(
            ['python', script],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # Linux/Mac
        process = subprocess.Popen(
            ['gnome-terminal', '--', 'python3', script]
        )
    
    processes.append((name, process))
    time.sleep(2)

try:
    # Verificar se os arquivos existem
    files = {
        'app.py': 'Sistema Swap',
        'gateway.py': 'Payment Gateway',
        'shop.py': 'Loja (TechStore)'
    }
    
    missing = []
    for file, name in files.items():
        if not os.path.exists(file):
            missing.append(f"{name} ({file})")
    
    if missing:
        print(f"{Fore.RED}❌ Arquivos não encontrados:{Style.RESET_ALL}")
        for item in missing:
            print(f"   - {item}")
        print(f"\n{Fore.YELLOW}Execute este script no diretório correto!{Style.RESET_ALL}")
        sys.exit(1)
    
    # Iniciar sistemas
    print(f"\n{Fore.CYAN}Iniciando sistemas...{Style.RESET_ALL}\n")
    
    start_process('app.py', 'Swap System', 5581)
    start_process('gateway.py', 'Payment Gateway', 5583)
    start_process('shop.py', 'TechStore', 5586)
    
    print(f"\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ TODOS OS SISTEMAS INICIADOS!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}📋 URLs Disponíveis:{Style.RESET_ALL}\n")
    print(f"   {Fore.CYAN}🔄 Swap System:{Style.RESET_ALL}     http://localhost:5581")
    print(f"   {Fore.CYAN}💳 Gateway:{Style.RESET_ALL}         http://localhost:5583")
    print(f"   {Fore.CYAN}🛍️  Loja:{Style.RESET_ALL}            http://localhost:5586")
    
    print(f"\n{Fore.YELLOW}🎯 Próximos Passos:{Style.RESET_ALL}\n")
    print("   1. Registre no Gateway (porta 5583)")
    print("   2. Configure API Key na Loja (/config)")
    print("   3. Faça uma compra de teste!")
    
    print(f"\n{Fore.RED}💡 Pressione Ctrl+C para encerrar todos os processos{Style.RESET_ALL}\n")
    print("="*70)
    
    # Manter script rodando
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print(f"\n\n{Fore.YELLOW}🛑 Encerrando todos os processos...{Style.RESET_ALL}")
    
    for name, process in processes:
        try:
            process.terminate()
            print(f"   {Fore.RED}✖️  {name} encerrado{Style.RESET_ALL}")
        except:
            pass
    
    print(f"\n{Fore.GREEN}✅ Todos os processos foram encerrados{Style.RESET_ALL}\n")

except Exception as e:
    print(f"\n{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
