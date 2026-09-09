# Spike: Remotion Render in AgentCore Code Interpreter

## Goal
Validate that a full Remotion render (headless Chromium + mp4 encode) can complete inside an AgentCore Code Interpreter session within time/resource limits.

## Pre-reqs
1. AWS account with Bedrock AgentCore access
2. Create a custom Code Interpreter with **Public network mode** (needed for `npm install`)
3. Execution role with S3 write permission to `frame-renders` bucket
4. Session timeout set to 300s minimum

## Steps

### 1. Create the Code Interpreter
```bash
aws bedrock-agentcore create-code-interpreter \
  --name "frame-remotion-renderer" \
  --network-mode PUBLIC \
  --execution-role-arn arn:aws:iam::ACCOUNT:role/frame-agentcore-role
```

### 2. Start a session
```bash
aws bedrock-agentcore start-code-interpreter-session \
  --code-interpreter-id <ID> \
  --session-timeout 300
```

### 3. Inject and run the spike script
The agent would write these files into the session:
- `package.json` (npm init + deps)
- `src/Root.jsx` (Remotion composition)
- `render.js` (render script)

Then execute:
```bash
npm install remotion @remotion/cli @remotion/bundler @remotion/renderer react react-dom
npx remotion render PromoScene out/promo.mp4 --frames=0-89
```

### 4. Validate output
- Confirm `out/promo.mp4` exists and has reasonable size (>100KB)
- Pull file from session, upload to S3

### 5. Check timing
- Total session time should be < 3 minutes
- If headless Chromium install is the bottleneck, consider pre-baking a custom runtime image

## Fallback: Nova Reel
If Remotion render fails (too slow, OOM, Chromium issues):
- Use Bedrock Nova Reel text-to-video as the render engine
- Agent drafts a text prompt instead of code
- Less "agent does real work" story but still valid
- Keep `agent/tools/nova_reel.py` as the fallback path
