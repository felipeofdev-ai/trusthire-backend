# 🛡️ TrustHire

> **Verify before you trust.**

AI-powered job offer verification system that detects scam indicators in recruitment messages.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Redis (optional, for caching)
- PostgreSQL (optional, for persistence)

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/trusthire.git
cd trusthire

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Running

```bash
# Development mode
python main.py

# Or with uvicorn
uvicorn main:app --reload

# Production mode
ENV=prod uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f app
```

## 📚 API Documentation

Once running, visit:
- Interactive API docs: http://localhost:8000/api/v1/docs
- Alternative docs: http://localhost:8000/api/v1/redoc

### Example API Call

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Urgent! Send $500 for job verification. Contact via Telegram.",
    "include_ai_analysis": true,
    "include_link_scan": true
  }'
```

## 🎯 Features

### Core Analysis
- ✅ Pattern-based scam detection
- ✅ AI-powered contextual analysis (Claude)
- ✅ Risk scoring (0-100)
- ✅ Confidence assessment
- ✅ Social engineering detection
- ✅ URL/link analysis
- ✅ Domain reputation checking

### Detection Categories
- 💰 Financial requests (payments, crypto)
- ⏰ Urgency pressure tactics
- 🔐 Sensitive data requests
- 🎁 Unrealistic promises
- 📱 Off-platform communication
- 🔗 Suspicious links
- 🎣 Phishing patterns
- 🧠 Social engineering

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
┌──────▼──────────────────┐
│   FastAPI Application   │
├─────────────────────────┤
│  ┌─────────────────┐   │
│  │ Pattern Engine  │   │
│  ├─────────────────┤   │
│  │ Risk Scoring    │   │
│  ├─────────────────┤   │
│  │ Link Analyzer   │   │
│  ├─────────────────┤   │
│  │ AI Layer        │   │
│  └─────────────────┘   │
└─────────────────────────┘
       │
┌──────▼──────┬────────────┐
│   Redis     │ PostgreSQL │
│   (Cache)   │   (Data)   │
└─────────────┴────────────┘
```

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/test_analyzer.py -v
```

## 📈 Configuration

Key environment variables:

- `ANTHROPIC_API_KEY` - Required for AI analysis
- `REDIS_URL` - Optional, for caching
- `DATABASE_URL` - Optional, for persistence
- `ENV` - Environment (dev/staging/prod)
- `LOG_LEVEL` - Logging level (INFO/DEBUG/WARNING)

See `.env.example` for all options.

## 🛠️ Development

### Project Structure

```
trusthire/
├── api/          # API routes and endpoints
├── core/         # Core analysis logic
├── engine/       # Detection engines
├── models/       # Pydantic models
├── services/     # External services
├── utils/        # Utilities
├── tests/        # Test suite
└── config.py     # Configuration
```

### Adding New Patterns

Edit `engine/pattern_engine.py`:

```python
PatternRule(
    pattern=re.compile(r"your-regex-here", re.I),
    category=SignalCategory.YOUR_CATEGORY,
    message="Description of what was detected",
    severity=Severity.HIGH,
    confidence=0.90,
)
```

## 📊 Monitoring

- Health check: `GET /health`
- Metrics: `GET /api/v1/stats`
- Structured JSON logging
- Sentry integration (optional)

## 🔒 Security

- Rate limiting per tier
- Input sanitization
- Secure headers
- CORS configuration
- API key authentication (enterprise)

## 📝 License

MIT License - see [LICENSE](LICENSE)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📧 Support

- Issues: [GitHub Issues](https://github.com/your-username/trusthire/issues)
- Discussions: [GitHub Discussions](https://github.com/your-username/trusthire/discussions)

---

**Built with ❤️ to protect job seekers from scams**
