
# Criar script de inicialização para facilitar

start_all = '''#!/usr/bin/env python3
"""
Script para iniciar todos os sistemas de uma vez
"""

import subprocess
import time
import sys
import os
from colorama import Fore, Style, init

init(autoreset=True)

print(f"\\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
print(f"{Fore.YELLOW}{Style.BRIGHT}  🚀 INICIANDO ECOSISTEMA COMPLETO  {Style.RESET_ALL}")
print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\\n")

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
        print(f"\\n{Fore.YELLOW}Execute este script no diretório correto!{Style.RESET_ALL}")
        sys.exit(1)
    
    # Iniciar sistemas
    print(f"\\n{Fore.CYAN}Iniciando sistemas...{Style.RESET_ALL}\\n")
    
    start_process('app.py', 'Swap System', 5581)
    start_process('gateway.py', 'Payment Gateway', 5583)
    start_process('shop.py', 'TechStore', 5586)
    
    print(f"\\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ TODOS OS SISTEMAS INICIADOS!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\\n")
    
    print(f"{Fore.YELLOW}📋 URLs Disponíveis:{Style.RESET_ALL}\\n")
    print(f"   {Fore.CYAN}🔄 Swap System:{Style.RESET_ALL}     http://localhost:5581")
    print(f"   {Fore.CYAN}💳 Gateway:{Style.RESET_ALL}         http://localhost:5583")
    print(f"   {Fore.CYAN}🛍️  Loja:{Style.RESET_ALL}            http://localhost:5586")
    
    print(f"\\n{Fore.YELLOW}🎯 Próximos Passos:{Style.RESET_ALL}\\n")
    print("   1. Registre no Gateway (porta 5583)")
    print("   2. Configure API Key na Loja (/config)")
    print("   3. Faça uma compra de teste!")
    
    print(f"\\n{Fore.RED}💡 Pressione Ctrl+C para encerrar todos os processos{Style.RESET_ALL}\\n")
    print("="*70)
    
    # Manter script rodando
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print(f"\\n\\n{Fore.YELLOW}🛑 Encerrando todos os processos...{Style.RESET_ALL}")
    
    for name, process in processes:
        try:
            process.terminate()
            print(f"   {Fore.RED}✖️  {name} encerrado{Style.RESET_ALL}")
        except:
            pass
    
    print(f"\\n{Fore.GREEN}✅ Todos os processos foram encerrados{Style.RESET_ALL}\\n")

except Exception as e:
    print(f"\\n{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}")
'''

with open('start_all.py', 'w', encoding='utf-8') as f:
    f.write(start_all)

# Criar guia rápido
quick_start = '''# 🚀 GUIA RÁPIDO - ECOSISTEMA COMPLETO

## 📦 O que você tem agora:

1. **Swap System (5581)** - Blockchain com 6 moedas + PIX
2. **Payment Gateway (5583)** - Gateway de pagamento crypto
3. **TechStore (5586)** - Loja de e-commerce

## ⚡ Início Ultra-Rápido

### Opção 1: Script Automático (Recomendado)
```bash
python start_all.py
```
Isso inicia tudo de uma vez!

### Opção 2: Manual
```bash
# Terminal 1
python app.py

# Terminal 2
python gateway.py

# Terminal 3
python shop.py
```

## 📋 Checklist de Primeiro Uso

- [ ] Inicie os 3 sistemas
- [ ] Acesse o gateway: http://localhost:5583
- [ ] Registre uma conta (anote a API Key)
- [ ] Configure a loja: http://localhost:5586/config
- [ ] Cole a API Key
- [ ] Acesse a loja: http://localhost:5586
- [ ] Adicione produtos ao carrinho
- [ ] Finalize a compra
- [ ] Escolha uma crypto (D1-D6)
- [ ] Clique em "Simular Pagamento"
- [ ] ✅ Compra confirmada!

## 🎯 Teste Completo em 2 Minutos

```bash
# 1. Inicie tudo
python start_all.py

# 2. Abra navegador
http://localhost:5583       # Registre e copie API Key
http://localhost:5586/config # Cole API Key
http://localhost:5586       # Compre algo!
```

## 🔥 Teste de Stress

Enquanto os sistemas rodam:
```bash
python stress_test.py
# Configure: 10 workers, 60 segundos
```

Faça compras na loja simultaneamente e veja tudo funcionando!

## 📊 Arquitetura

```
Cliente
  ↓
🛍️ TechStore (5586)
  ↓ (cria invoice via API)
💳 Gateway (5583)
  ↓ (processa pagamento)
🔄 Swap System (5581)
  ↓
✅ Confirmação automática
```

## 💡 Dicas

- Deixe os 3 sistemas sempre rodando
- O gateway monitora pagamentos a cada 5 segundos
- A loja atualiza status automaticamente
- Use "Simular Pagamento" para testes rápidos

## 📞 Suporte

Documentação completa:
- `API_DOCUMENTATION.md` - APIs do Swap
- `GATEWAY_README.md` - Gateway
- `SHOP_README.md` - Loja

## 🎉 Pronto para Produção?

Para ambiente real:
1. Remova os botões "Simular"
2. Conecte com blockchain real
3. Adicione autenticação
4. Configure HTTPS
5. Use banco de dados robusto

---

**Divirta-se testando! 🚀**
'''

with open('QUICK_START.md', 'w', encoding='utf-8') as f:
    f.write(quick_start)

print("✅ start_all.py criado")
print("✅ QUICK_START.md criado")
print("\n" + "="*70)
print("🎉 ECOSISTEMA COMPLETO FINALIZADO!")
print("="*70)
print("\n📦 Você tem agora:")
print("   ✅ Sistema Swap com blockchain (6 moedas)")
print("   ✅ Gateway de pagamento crypto")
print("   ✅ Loja de e-commerce completa")
print("   ✅ Stress test para testes")
print("   ✅ Documentação completa")
print("\n🚀 INICIAR TUDO:")
print("   python start_all.py")
print("\nOu manual:")
print("   Terminal 1: python app.py")
print("   Terminal 2: python gateway.py")
print("   Terminal 3: python shop.py")
print("\n📚 Leia: QUICK_START.md")
print("="*70)
