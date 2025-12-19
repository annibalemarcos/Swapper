# 🚀 GUIA RÁPIDO - ECOSISTEMA COMPLETO

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
