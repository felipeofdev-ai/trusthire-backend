# 🚀 TrustHire SaaS — Guia Completo de Deploy e Monetização

## O que foi adicionado nesta versão

| Módulo | Arquivo | Descrição |
|--------|---------|-----------|
| Auth JWT | `auth/auth_service.py` | Login, registro, refresh tokens, API keys |
| User Models | `models/user_models.py` | Schemas de usuário, tiers, assinatura |
| Auth API | `api/auth.py` | `/register`, `/login`, `/refresh`, `/me`, `/api-keys` |
| Billing API | `api/billing.py` | Stripe checkout, portal, webhook handler |
| User DB | `database/user_repository.py` | CRUD de usuários com controle de uso diário |
| Rate Limiting | `api/analysis.py` | Limites por tier (FREE/PRO/ENTERPRISE) |
| Deploy Railway | `railway.toml` | Config de deploy Railway |
| Deploy Render | `render.yaml` | Config de deploy Render + PostgreSQL + Redis |

---

## 📦 PASSO 1 — Instalação local

```bash
# Clone o repositório
git clone https://github.com/felipeofdev-ai/trusthire.git
cd trusthire

# Copie e configure o .env
cp .env.example .env
# Edite o .env com suas chaves (ver seção abaixo)

# Instale as dependências
pip install -r requirements.txt

# Rode localmente
uvicorn main:app --reload --port 8000
```

Acesse: http://localhost:8000/api/v1/docs

---

## 🔐 PASSO 2 — Configurar Variáveis de Ambiente

### Chaves obrigatórias no `.env`

#### 1. SECRET_KEY
```bash
# Gere uma chave segura:
openssl rand -hex 32
# Cole no .env: SECRET_KEY=resultado_aqui
```

#### 2. ANTHROPIC_API_KEY
- Acesse: https://console.anthropic.com/
- Vá em "API Keys" → Create Key
- Cole no `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

#### 3. Stripe (para pagamentos)
- Acesse: https://dashboard.stripe.com
- **Keys:** https://dashboard.stripe.com/apikeys
  - `STRIPE_SECRET_KEY=sk_test_...`
  - `STRIPE_PUBLISHABLE_KEY=pk_test_...`
- **Webhook** (ver Passo 4 para detalhes)

---

## 💳 PASSO 3 — Configurar Stripe

### 3.1 Criar Produtos no Stripe

No Stripe Dashboard → Products → Add Product:

**Produto 1: TrustHire Pro**
- Name: `TrustHire Pro`
- Price 1: `$19.90 / month` → copie o `price_XXXX` → `STRIPE_PRICE_PRO_MONTHLY`
- Price 2: `$178.80 / year` ($14.90×12) → `STRIPE_PRICE_PRO_YEARLY`

**Produto 2: TrustHire Enterprise**
- Name: `TrustHire Enterprise`
- Price 1: `$99.90 / month` → `STRIPE_PRICE_ENTERPRISE_MONTHLY`
- Price 2: `$948.00 / year` ($79×12) → `STRIPE_PRICE_ENTERPRISE_YEARLY`

### 3.2 Configurar Webhook

No Stripe Dashboard → Webhooks → Add Endpoint:

- **URL**: `https://SEU-DOMINIO.com/api/v1/billing/webhook`
- **Events**:
  - `checkout.session.completed`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_failed`

Copie o **Signing Secret** → `STRIPE_WEBHOOK_SECRET=whsec_...`

### 3.3 Testar webhook localmente (Stripe CLI)

```bash
# Instalar Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login
stripe listen --forward-to localhost:8000/api/v1/billing/webhook
# Isso mostra o webhook secret temporário para testes locais
```

---

## 🚂 PASSO 4 — Deploy no Railway

Railway é o deploy mais simples. **Tem free tier** com $5/mês de crédito grátis.

### 4.1 Criar conta e projeto

1. Acesse: https://railway.app
2. Login com GitHub
3. **New Project** → **Deploy from GitHub repo**
4. Selecione `felipeofdev-ai/trusthire`

### 4.2 Adicionar PostgreSQL

No Railway Dashboard:
1. Clique **+ New** → **Database** → **PostgreSQL**
2. Ele cria automaticamente e injeta `DATABASE_URL` no seu app

### 4.3 Adicionar Redis

1. Clique **+ New** → **Database** → **Redis**
2. Ele injeta `REDIS_URL` automaticamente

### 4.4 Configurar variáveis no Railway

Clique no seu serviço → **Variables** → Add:

```
ENV=prod
SECRET_KEY=sua-chave-gerada-com-openssl
ANTHROPIC_API_KEY=sk-ant-...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PRO_MONTHLY=price_...
STRIPE_PRICE_PRO_YEARLY=price_...
STRIPE_PRICE_ENTERPRISE_MONTHLY=price_...
STRIPE_PRICE_ENTERPRISE_YEARLY=price_...
```

### 4.5 Deploy!

Railway detecta o `Dockerfile` automaticamente e faz o deploy.
URL gerada: `https://trusthire-production.up.railway.app`

**Custo Railway estimado:**
- Starter: $5/mês (inclui $5 crédito grátis = praticamente FREE para começar)
- Pro: $20/mês para mais recursos

---

## 🎨 PASSO 5 — Deploy no Render (alternativa gratuita)

Render tem **free tier genuíno**, mas dorme após 15min de inatividade.

### 5.1 Deploy com render.yaml

```bash
# O arquivo render.yaml já está configurado no projeto
# Basta conectar no Render Dashboard
```

1. Acesse: https://render.com
2. **New** → **Blueprint** → Connect GitHub → selecione o repo
3. Render lê o `render.yaml` e cria todos os serviços automaticamente

### 5.2 Configurar variáveis no Render

No Render Dashboard → seu serviço → **Environment**:
(mesmas variáveis do Railway acima)

### 5.3 Atualizar webhook do Stripe

Após deploy: `https://trusthire-api.onrender.com/api/v1/billing/webhook`

**Custo Render:**
- Free: funciona mas dorme (bom para MVP/testes)
- Starter $7/mês: sem sleep, PostgreSQL incluído

---

## 🔑 PASSO 6 — Testar a API

### Registro e login

```bash
BASE=https://seu-dominio.com/api/v1

# 1. Registrar
curl -X POST $BASE/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"senha123","name":"Felipe"}'

# 2. Login → pega o access_token
curl -X POST $BASE/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"senha123"}'

# 3. Analisar mensagem (autenticado)
curl -X POST $BASE/analyze \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hi! You were selected for our remote job. Send $200 for equipment setup via Bitcoin."}'

# 4. Gerar API Key (para integração programática)
curl -X POST $BASE/auth/api-keys \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{"label":"meu-script"}'

# 5. Usar API Key (alternativa ao JWT)
curl -X POST $BASE/analyze \
  -H "X-API-Key: th_SUA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text":"..."}'
```

### Fluxo de upgrade

```bash
# Criar sessão de checkout Stripe
curl -X POST $BASE/billing/checkout \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "pro_monthly",
    "success_url": "https://seusite.com/success",
    "cancel_url": "https://seusite.com/pricing"
  }'
# Retorna: {"checkout_url": "https://checkout.stripe.com/..."}
# Redirecione o usuário para essa URL
```

---

## 💰 PASSO 7 — Estratégia de Monetização

### Modelo de Pricing

| Plano | Preço | Análises/dia | AI | Target |
|-------|-------|-------------|-----|--------|
| **Free** | Grátis | 10 | ❌ | Testar, estudantes |
| **Pro** | $19.90/mês | 100 | ✅ Claude | Job seekers, HR individuais |
| **Enterprise** | $99.90/mês | 10.000 | ✅ | Empresas, RH corporativo |

### Canais de aquisição

1. **SEO**: Blog sobre scams de emprego + landing page otimizada
2. **LinkedIn**: Conteúdo sobre segurança no recrutamento
3. **GitHub**: README atraente, demo pública
4. **Product Hunt**: Lançar o produto
5. **APIs**: Marketplace RapidAPI (extra revenue stream)

### Métricas para acompanhar

```
MRR (Monthly Recurring Revenue) = usuários_pro × 19.90 + usuários_enterprise × 99.90
Churn Rate = usuários_cancelados / total_usuários
LTV = MRR × (1/churn_rate)
CAC = custo_aquisição / novos_clientes
```

### Expansão de receita

- **Affiliate**: Comissão para quem indicar (ex: plataformas de emprego)
- **White-label**: Licenciar a API para portais de RH
- **RapidAPI**: https://rapidapi.com → cadastrar a API pública
- **B2B direto**: Vender para portais (LinkedIn, Glassdoor, Catho)

---

## 🏗️ Arquitetura Final

```
┌─────────────────────────────────────────────────────┐
│                  GitHub Pages (Frontend)            │
│           felipeofdev-ai.github.io/trusthire        │
└─────────────────────┬───────────────────────────────┘
                      │ HTTPS / REST API
                      ▼
┌─────────────────────────────────────────────────────┐
│              Railway / Render (Backend)             │
│                  FastAPI + Python                   │
│                                                     │
│  /api/v1/auth/*        ← JWT + API Keys             │
│  /api/v1/billing/*     ← Stripe SaaS               │
│  /api/v1/analyze       ← Core engine               │
│                                                     │
└──────┬──────────────────────┬───────────────────────┘
       │                      │
       ▼                      ▼
┌─────────────┐     ┌─────────────────────┐
│  PostgreSQL │     │       Redis         │
│  (Users,    │     │  (Cache, sessions,  │
│  subscriptions)   │   rate limiting)    │
└─────────────┘     └─────────────────────┘
       │
       ▼
┌─────────────────────┐
│    Stripe API       │
│  (Payments, Subs)   │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│   Anthropic API     │
│  (Claude analysis)  │
└─────────────────────┘
```

---

## 🔗 Conectar Frontend (GitHub Pages) ao Backend

No seu `index.html` ou JS frontend, mude o endpoint base:

```javascript
// Antes (mock/local):
const API_BASE = 'http://localhost:8000/api/v1';

// Depois (produção Railway):
const API_BASE = 'https://trusthire-production.up.railway.app/api/v1';

// Exemplo de chamada:
const response = await fetch(`${API_BASE}/analyze`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
  },
  body: JSON.stringify({ text: userMessage }),
});
const result = await response.json();
```

---

## ✅ Checklist de Lançamento

- [ ] Gerar `SECRET_KEY` com `openssl rand -hex 32`
- [ ] Configurar chave Anthropic em produção
- [ ] Criar produtos e preços no Stripe Dashboard
- [ ] Configurar webhook do Stripe
- [ ] Deploy no Railway ou Render
- [ ] Atualizar `CORS_ORIGINS` com domínio do frontend
- [ ] Testar fluxo completo: registro → login → análise → upgrade
- [ ] Configurar Sentry para monitoramento de erros
- [ ] Adicionar domínio customizado (opcional)
- [ ] Publicar no Product Hunt 🚀
