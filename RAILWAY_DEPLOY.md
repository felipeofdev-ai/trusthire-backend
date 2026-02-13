# 🚂 TrustHire — Deploy no Railway (Guia Passo a Passo)

## ✅ Correções aplicadas nesta versão

| Problema | Causa | Correção |
|----------|-------|----------|
| `healthcheck failed` | App crashava por variáveis ausentes | `validate_production_config()` agora só avisa, nunca encerra |
| `$PORT not valid integer` | Dockerfile usava `CMD ["uvicorn", ..., "$PORT"]` | Trocado para shell form: `CMD uvicorn ... --port ${PORT:-8000}` |
| `requests not found` | Healthcheck usava Python requests | Trocado para `curl` (mais confiável) |
| `stripe import error` | `import stripe` no topo do billing.py | Stripe agora é importado condicionalmente |
| Healthcheck muito rápido | `start-period=5s` era curto demais | Aumentado para `start-period=20s` |

---

## 🚀 PASSO A PASSO — Deploy mínimo (sem Stripe/DB ainda)

### 1. Push das correções pro GitHub

```bash
# No seu terminal local — com os novos arquivos copiados do zip:
git add -A
git commit -m "fix: railway healthcheck, graceful startup, conditional stripe"
git push origin main
```

### 2. No Railway Dashboard

1. Acesse https://railway.app → seu projeto TrustHire
2. Vá em **Variables** → adicione:

```
ENV=prod
SECRET_KEY=gere-com-openssl-rand-hex-32
PORT=8000
```

3. Railway vai redetectar o `Dockerfile` e fazer redeploy.

### 3. Verificar que funcionou

Assim que o deploy terminar:

```
GET https://SEU-APP.up.railway.app/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "environment": "prod",
  "ai_enabled": false,
  "billing_enabled": false,
  "db_enabled": false
}
```

✅ Verde = app rodando. Agora adicione as outras vars uma a uma.

---

## 📦 PASSO 2 — Adicionar PostgreSQL no Railway

1. No Railway Dashboard → **+ New** → **Database** → **Add PostgreSQL**
2. Railway cria e injeta `DATABASE_URL` automaticamente no seu app
3. Vá em **Variables** do seu app → confirme que `DATABASE_URL` apareceu

---

## 📦 PASSO 3 — Adicionar Redis no Railway

1. **+ New** → **Database** → **Add Redis**
2. Railway injeta `REDIS_URL` automaticamente

Agora `/health` deve mostrar `"db_enabled": true`.

---

## 🤖 PASSO 4 — Adicionar Anthropic (Claude AI)

No Railway → Variables:

```
ANTHROPIC_API_KEY=sk-ant-SEU-KEY-AQUI
```

Obter em: https://console.anthropic.com/ → API Keys

---

## 💳 PASSO 5 — Configurar Stripe

### 5.1 Criar conta Stripe
https://dashboard.stripe.com/register

### 5.2 Criar produtos

Stripe Dashboard → **Products** → **+ Add Product**:

**Produto 1: TrustHire Pro**
- Name: `TrustHire Pro`
- Pricing → Recurring → Monthly → `$19.90`
  → Copie o `price_XXXX` → STRIPE_PRICE_PRO_MONTHLY
- Add another price → Yearly → `$178.80`
  → STRIPE_PRICE_PRO_YEARLY

**Produto 2: TrustHire Enterprise**
- Name: `TrustHire Enterprise`
- Monthly `$99.90` → STRIPE_PRICE_ENTERPRISE_MONTHLY
- Yearly `$948.00` → STRIPE_PRICE_ENTERPRISE_YEARLY

### 5.3 Adicionar no Railway

```
STRIPE_SECRET_KEY=sk_test_SEU_KEY
STRIPE_PUBLISHABLE_KEY=pk_test_SEU_KEY
STRIPE_PRICE_PRO_MONTHLY=price_XXXX
STRIPE_PRICE_PRO_YEARLY=price_XXXX
STRIPE_PRICE_ENTERPRISE_MONTHLY=price_XXXX
STRIPE_PRICE_ENTERPRISE_YEARLY=price_XXXX
```

### 5.4 Configurar Webhook

Stripe Dashboard → **Developers** → **Webhooks** → **+ Add endpoint**:

- Endpoint URL: `https://SEU-APP.up.railway.app/api/v1/billing/webhook`
- Events:
  - `checkout.session.completed`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_failed`

Copie o **Signing secret** → Railway:
```
STRIPE_WEBHOOK_SECRET=whsec_XXXX
```

---

## 🌐 PASSO 6 — Conectar o Frontend (GitHub Pages)

No seu `index.html` ou arquivo JS principal, encontre onde a API é chamada e substitua:

```javascript
// ANTES (local):
const API_BASE = 'http://localhost:8000/api/v1'

// DEPOIS (Railway):
const API_BASE = 'https://SEU-APP.up.railway.app/api/v1'
```

Adicione também os CORS Origins no Railway:
```
CORS_ORIGINS=https://felipeofdev-ai.github.io,https://SEU-APP.up.railway.app
```

---

## 🔁 Checklist completo

- [ ] Push do código corrigido no GitHub
- [ ] Railway detectou e fez redeploy
- [ ] `/health` retorna 200 ✅
- [ ] PostgreSQL adicionado → `db_enabled: true`
- [ ] Redis adicionado
- [ ] `ANTHROPIC_API_KEY` configurada → `ai_enabled: true`
- [ ] Produtos Stripe criados
- [ ] `STRIPE_SECRET_KEY` e price IDs configurados → `billing_enabled: true`
- [ ] Webhook Stripe configurado
- [ ] Frontend atualizado para URL do Railway
- [ ] CORS_ORIGINS atualizado

---

## 🐛 Debug rápido

### Ver logs em tempo real
Railway Dashboard → seu serviço → **Logs**

### Testar API diretamente
```bash
# Health
curl https://SEU-APP.up.railway.app/health

# Analisar mensagem (sem auth — free tier)
curl -X POST https://SEU-APP.up.railway.app/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Urgent! You got the job. Send $200 via Bitcoin for equipment."}'
```

### Swagger UI
https://SEU-APP.up.railway.app/api/v1/docs
