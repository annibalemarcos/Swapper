# 🛍️ TechStore - Loja de Demonstração

Loja completa integrada com Crypto Payment Gateway

## 📦 Estrutura

```
shop.py                          # Backend da loja
templates_shop/                  # Templates HTML
├── shop_home.html              # Catálogo de produtos
├── shop_cart.html              # Carrinho de compras
├── shop_checkout.html          # Finalização
├── shop_config.html            # Configuração API Key
└── shop_order.html             # Status do pedido
shop.db                          # Banco de dados (criado automaticamente)
shop_config.txt                  # API Key salva
```

## 🚀 Início Rápido

### Passo 1: Registrar no Gateway
```bash
# Acesse o gateway
http://localhost:5583

# Clique em "Registrar"
# Preencha:
- Nome: TechStore
- Email: techstore@example.com
- Chave PIX: 11999999999

# COPIE A API KEY GERADA (ex: pk_abc123...)
```

### Passo 2: Configurar a Loja
```bash
# Inicie a loja
python shop.py

# Acesse
http://localhost:5586/config

# Cole a API Key
# Clique em Salvar
```

### Passo 3: Fazer uma Compra
```bash
# Acesse a loja
http://localhost:5586

# Adicione produtos ao carrinho
# Clique em "Finalizar Compra"
# Preencha seus dados
# Escolha uma criptomoeda (D1-D6)
# Clique em "Simular Pagamento"
# Pronto! Pedido confirmado ✅
```

## 📋 Produtos Disponíveis

1. **Notebook Gamer** - R$ 4.999,99
2. **Smartphone Pro** - R$ 2.499,50
3. **Fone Bluetooth** - R$ 899,90
4. **Smart Watch** - R$ 1.299,00
5. **Teclado Mecânico** - R$ 449,90
6. **Mouse Gamer** - R$ 299,90
7. **Monitor 4K** - R$ 1.899,00
8. **Webcam Full HD** - R$ 399,00

## 🔗 URLs Importantes

- **Loja**: http://localhost:5586
- **Config**: http://localhost:5586/config
- **Gateway**: http://localhost:5583
- **Swap System**: http://localhost:5581

## 🎯 Fluxo Completo de Compra

1. **Cliente navega** na loja (porta 5586)
2. **Cliente adiciona** produtos ao carrinho
3. **Cliente finaliza** compra
4. **Loja cria invoice** no gateway (porta 5583)
5. **Cliente é redirecionado** para checkout do gateway
6. **Cliente escolhe** criptomoeda (D1-D6)
7. **Cliente paga** com crypto
8. **Gateway converte** crypto → BRL
9. **Gateway envia PIX** para merchant
10. **Loja confirma** pedido automaticamente

## 💡 Funcionalidades

✅ **Catálogo de Produtos** - 8 produtos de tecnologia
✅ **Carrinho de Compras** - Adicionar/remover items
✅ **Sistema de Checkout** - Formulário de dados
✅ **Integração Gateway** - Automática via API
✅ **Pagamento Crypto** - 6 criptomoedas
✅ **Status de Pedido** - Acompanhamento em tempo real
✅ **Configuração Fácil** - Interface para API Key

## 🔧 Personalização

### Adicionar Produtos

Edite `shop.py`, seção `PRODUCTS`:

```python
PRODUCTS = [
    {
        'id': 9,
        'name': 'Novo Produto',
        'description': 'Descrição aqui',
        'price': 999.99,
        'image': '🎮',
        'category': 'Games'
    }
]
```

### Mudar Tema/Cores

Edite os templates em `templates_shop/`, seção `<style>`

### Webhook

O gateway notifica automaticamente quando pagamento é confirmado

## 📊 Testes

### Teste Completo

1. Inicie todos os sistemas:
```bash
# Terminal 1
python app.py         # Swap (5581)

# Terminal 2
python gateway.py     # Gateway (5583)

# Terminal 3
python shop.py        # Loja (5586)
```

2. Configure API Key (http://localhost:5586/config)
3. Faça uma compra de teste
4. Use "Simular Pagamento"
5. Verifique status do pedido

### Stress Test

Use o stress_test.py enquanto faz compras para testar sob carga

## 🐛 Resolução de Problemas

**Erro: "API Key inválida"**
- Registre-se no gateway (porta 5583)
- Copie a API Key correta
- Configure em /config

**Erro: "Erro de conexão"**
- Certifique-se que o gateway está rodando (5583)
- Verifique se a URL está correta

**Pagamento não detectado**
- Aguarde 10 segundos (auto-refresh)
- Recarregue a página manualmente
- Verifique se o swap system está rodando (5581)

## 📞 Suporte

Para dúvidas, consulte:
- API_DOCUMENTATION.md (APIs do swap)
- GATEWAY_README.md (Gateway de pagamento)
- Este arquivo (Loja)

## ⚡ Stack Tecnológico

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, Font Awesome
- **Database**: SQLite
- **Integração**: REST API
- **Pagamento**: Crypto Gateway (porta 5583)
- **Blockchain**: Dummy Crypto Swap (porta 5581)

---

💡 **Dica**: Deixe os 3 sistemas rodando simultaneamente para melhor experiência!
