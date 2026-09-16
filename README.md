# 🤖 AI Code Review Assistant

AI-powered code review assistant that analyzes source code and pull requests to detect bugs, security vulnerabilities, code smells, performance issues, and coding best-practice violations.

## ✨ Features

- 🧠 AI-assisted review using the OpenAI Responses API
- 🔍 Static checks for common security and quality issues before the AI review
- 📁 Review a single file, a directory, or a unified diff
- 📊 Structured findings with severity, category, line, explanation, and recommendation
- 💻 Friendly CLI for local reviews
- 🌐 Lightweight FastAPI endpoint for integrations
- 🧪 Unit tests with deterministic static-analysis coverage
- ⚙️ GitHub Actions CI
- 🐳 Docker support
- 🔐 Secrets are read from environment variables and never committed

## 🏗️ Architecture

```text
Source / PR diff
      │
      ▼
┌──────────────────┐
│ Input normalizer │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Static analyzers │ ── security / quality rules
└────────┬─────────┘
         ▼
┌──────────────────┐
│ AI reviewer      │ ── contextual analysis
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Review formatter │
└────────┬─────────┘
         ▼
 Markdown / JSON / API response
```

## 🚀 Quick start

### 1. Clone

```bash
git clone https://github.com/aaryachandana/ai-code-review-assistant.git
cd ai-code-review-assistant
```

### 2. Create an environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
```

### 3. Configure AI access

```bash
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env`. The default model is `gpt-5.6-luna`; you can override it with `AI_REVIEW_MODEL`.

### 4. Run a local review

Static-only review works without an API key:

```bash
ai-review review examples/vulnerable.py --no-ai
```

With AI enabled:

```bash
ai-review review examples/vulnerable.py
```

Review a diff:

```bash
ai-review diff examples/sample.diff
```

JSON output:

```bash
ai-review review examples/vulnerable.py --format json
```

## 🌐 API demo

Start the API:

```bash
uvicorn ai_code_review.api:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/review \
  -H "Content-Type: application/json" \
  -d '{"filename":"app.py","code":"password = \\\"secret123\\\""}'
```

## 🧪 Test

```bash
pytest
```

## 🐳 Docker

```bash
docker build -t ai-code-review-assistant .
docker run --rm -p 8000:8000 --env-file .env ai-code-review-assistant
```

## 📋 Example output

```text
AI Code Review — examples/vulnerable.py

CRITICAL  security      line 8
Hard-coded credential detected.
Recommendation: Load secrets from an environment variable or secret manager.

HIGH      security      line 15
Potential SQL injection: user-controlled input is interpolated into a SQL query.
Recommendation: Use parameterized queries.

MEDIUM    quality       line 21
Bare exception handling hides the original failure.
Recommendation: Catch the expected exception and preserve useful error context.

Summary: 3 findings | 1 critical | 1 high | 1 medium
```

## 🔧 Project structure

```text
ai-code-review-assistant/
├── .github/workflows/ci.yml
├── demo/index.html
├── examples/
│   ├── sample.diff
│   └── vulnerable.py
├── src/ai_code_review/
│   ├── __init__.py
│   ├── ai.py
│   ├── analyzer.py
│   ├── api.py
│   ├── cli.py
│   ├── models.py
│   └── rules.py
├── tests/test_analyzer.py
├── .env.example
├── .gitignore
├── Dockerfile
├── LICENSE
├── pyproject.toml
└── README.md
```

## 🔐 Security

Do not commit API keys, tokens, credentials, or `.env` files. The included static analyzer is a helpful signal, not a replacement for a dedicated security scanner or human review.

## 📄 License

MIT License. See [LICENSE](LICENSE).
