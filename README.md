# Frame

Zero-UI GitHub App that autonomously generates promo videos from merged PRs and releases.

## What it does

1. Watches a connected GitHub repo for merged PRs and published releases
2. An autonomous Strands agent judges whether the change is promo-worthy
3. If yes, the agent writes Remotion scene code and renders a short promo clip inside an AgentCore Code Interpreter sandbox
4. Posts a Check Run on the PR with a preview link and approve/request-changes actions
5. On approval, posts to Facebook with Conversions API tracking

## Architecture

```
GitHub Webhook → FastAPI app → Strands Agent → AgentCore Code Interpreter (Remotion render)
                                    ↓
                              GitHub Checks API
                                    ↓
                         (on approve) Facebook Graph API
```

- **`app/`** — FastAPI webhook receiver, GitHub Checks API integration
- **`agent/`** — Strands agent core: promo-worthiness judgment, storyboard drafting, render orchestration
- **`dashboard/`** — Next.js dashboard: repo connect, brand config, generation status

## Stack

- Python 3.11+ (FastAPI, Strands Agents SDK)
- Remotion (React/TypeScript) rendered inside AgentCore Code Interpreter
- PostgreSQL, Redis, S3
- Next.js + TypeScript (dashboard)
- AWS CDK (infra)

## Development

```bash
# Install Python deps
pip install -e ".[dev]"

# Run the webhook server
uvicorn app.webhooks.server:app --reload

# Run the agent standalone
python -m agent.strands.frame_agent

# Dashboard
cd dashboard && npm install && npm run dev
```

## Configuration

Set these environment variables:

```bash
# GitHub App
GITHUB_APP_ID=...
GITHUB_WEBHOOK_SECRET=...
GITHUB_PRIVATE_KEY_PATH=...

# AWS
AWS_REGION=us-east-1
S3_BUCKET=frame-renders
AGENTCORE_CODE_INTERPRETER_ID=...

# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://...

# Facebook (optional, for auto-posting)
FACEBOOK_PAGE_ID=...
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_CAPI_TOKEN=...
```
