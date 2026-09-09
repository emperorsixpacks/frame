<p align="center">
  <img src="dashboard/public/frame-logo.svg" alt="Frame logo" width="120" height="120" />
</p>

<h1 align="center">Frame</h1>

<p align="center">
  <strong>Zero-UI GitHub App that turns merged PRs into promo videos.</strong><br/>
  Install once. Set brand config once. The agent handles the rest.
</p>

<p align="center">
  <a href="https://github.com/emperorsixpacks/frame/actions"><img src="https://img.shields.io/badge/status-alpha-orange" alt="Status" /></a>
  <a href="https://github.com/emperorsixpacks/frame/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License" /></a>
  <a href="https://github.com/emperorsixpacks/frame"><img src="https://img.shields.io/badge/python-3.11+-green" alt="Python" /></a>
  <a href="https://github.com/emperorsixpacks/frame"><img src="https://img.shields.io/badge/AWS-AgentCore-FF9900" alt="AgentCore" /></a>
  <a href="https://github.com/emperorsixpacks/frame"><img src="https://img.shields.io/badge/Strands-SDK-purple" alt="Strands" /></a>
</p>

---

## What it does

Frame watches a connected GitHub repo. When a PR merges or a release publishes, an autonomous Strands agent decides if the change is worth a promo clip. If yes, it writes Remotion scene code, renders the video inside an AgentCore Code Interpreter sandbox, and posts a Check Run on the PR with a preview link. On approval, it publishes to Facebook with Conversions API tracking.

**No CLI. No editor. No manual prompting.** The agent — not the human — makes every decision.

## How it works

```
 PR merged / release published
         │
         ▼
 ┌──────────────────┐
 │  Webhook (FastAPI) │  ← receives GitHub event
 └────────┬─────────┘
          │
          ▼
 ┌──────────────────┐
 │  Strands Agent     │  ← the core brain
 │                    │
 │  1. Judge          │  promo-worthy? (reads diff + metadata)
 │  2. Storyboard     │  3-scene motion plan
 │  3. Render         │  writes Remotion JSX, executes in AgentCore
 │  4. Confidence     │  checks brand compliance
 └────────┬─────────┘
          │
          ▼
 ┌──────────────────┐
 │  GitHub Checks API │  ← preview link + approve/request-changes
 └────────┬─────────┘
          │ (on approve)
          ▼
 ┌──────────────────┐
 │  Facebook Graph API │  ← posts video + fires Conversions event
 └──────────────────┘
```

## Architecture

```
frame/
├── agent/                    # Strands agent core
│   ├── config/
│   │   ├── prompts/          # .md templates + manifest.json + loader
│   │   └── settings.py       # AgentConfig, BrandConfig (pydantic)
│   ├── strands/              # Agent orchestrator
│   └── tools/                # Code Interpreter, GitHub diff tools
│
├── app/                      # FastAPI backend
│   ├── webhooks/             # GitHub webhook receiver
│   ├── github/               # GitHub API client (Checks, PRs)
│   └── checks/               # Check Run lifecycle manager
│
└── dashboard/                # Next.js minimal UI
    └── src/
        ├── app/              # Pages
        ├── components/       # BrandConfig, ModelConfig, ActivityFeed
        └── styles/           # Design tokens + globals
```

## Stack

| Layer | Tech | Why |
|-------|------|-----|
| Agent brain | **Strands Agents SDK** (Python) | Core judged component — genuine multi-step agentic behavior |
| Video render | **Remotion** (React/TS) inside **AgentCore Code Interpreter** | Agent writes code and executes it — strongest AgentCore usage story |
| Webhook + API | **FastAPI** (Python) | Lightweight, async, same language as agent |
| Dashboard | **Next.js** + TypeScript | Repo connect, brand config, status — small surface |
| Storage | **S3** | Rendered clips, presigned URLs for Check previews |
| Infra | **AWS CDK** (Python) | IaC in same language as backend |

## Quick start

### Prerequisites

- Python 3.11+
- Node.js 18+
- AWS account with Bedrock AgentCore access
- GitHub App (create at [github.com/settings/apps](https://github.com/settings/apps))

### Install

```bash
# Clone
git clone https://github.com/emperorsixpacks/frame.git
cd frame

# Python deps
pip install -e ".[dev]"

# Dashboard
cd dashboard && npm install && cd ..
```

### Run locally

```bash
# Webhook server
uvicorn app.webhooks.server:app --reload --port 8000

# Dashboard (separate terminal)
cd dashboard && npm run dev
```

### Environment

```bash
# GitHub App
export GITHUB_APP_ID="..."
export GITHUB_WEBHOOK_SECRET="..."
export GITHUB_PRIVATE_KEY_PATH="./private-key.pem"

# AWS
export AWS_REGION="us-east-1"
export S3_BUCKET="frame-renders"
export AGENTCORE_CODE_INTERPRETER_ID="..."

# Database (v1 uses in-memory, swap for Postgres)
export DATABASE_URL="postgresql://localhost/frame"

# Redis (v1 uses in-memory queue)
export REDIS_URL="redis://localhost:6379"

# Facebook (optional — for auto-posting)
export FACEBOOK_PAGE_ID="..."
export FACEBOOK_ACCESS_TOKEN="..."
export FACEBOOK_CAPI_TOKEN="..."
```

## Agent pipeline

The Strands agent runs a 4-step pipeline, each step backed by its own prompt template:

| Step | Prompt | What it does |
|------|--------|-------------|
| 1. Judge | `promo_judge.md` | Reads PR title, description, changed files. Scores promo-worthiness (0-1). Skips trivial changes. |
| 2. Storyboard | `storyboard.md` | Drafts 3 scenes: Hook (3s) → Show (8s) → Close (4s). Defines text overlays, visuals, animations. |
| 3. Render | `remotion_writer.md` | Writes complete Remotion JSX from the storyboard. Executes via AgentCore Code Interpreter. |
| 4. Confidence | `brand_confidence.md` | Checks output against brand config (colors, tone, do's/don'ts). High → auto-post. Low → human review. |

All prompts live in `agent/config/prompts/` as markdown. Edit them directly — the loader reads `.md` files and renders with `{{variables}}`.

## Development

```bash
# Lint (Python)
ruff check agent/ app/

# Type check
mypy agent/ app/

# Test
pytest tests/

# Dashboard dev
cd dashboard && npm run dev
```

## License

MIT
