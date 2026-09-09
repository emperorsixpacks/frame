"""
SPIKE: Validate Remotion render inside AgentCore Code Interpreter.

This script is the code that would be injected into an AgentCore
Code Interpreter session. It:
1. Installs Remotion + deps in the sandbox
2. Writes a minimal motion scene
3. Renders to mp4
4. Confirms the output file exists and has size

Run this in an AgentCore Code Interpreter session with Public network mode.
"""

REMOTION_SCENE_CODE = '''
const { Composition } = require("remotion");
const { Video } = require("remotion");
const { AbsoluteFill, useCurrentFrame, interpolate } = require("remotion");

const PromoScene = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: "clamp",
  });
  const scale = interpolate(frame, [0, 30], [0.8, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0D0F12",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          opacity,
          transform: `scale(${scale})`,
          color: "#EDEDEE",
          fontSize: 72,
          fontFamily: "monospace",
          textAlign: "center",
        }}
      >
        <div style={{ color: "#E8B84B", fontSize: 48, marginBottom: 20 }}>
          FRAME
        </div>
        <div>New Release</div>
        <div style={{ fontSize: 36, color: "#4A5058", marginTop: 10 }}>
          v1.0.0 — First drop
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Root = () => {
  return (
    <>
      <Composition
        id="PromoScene"
        component={PromoScene}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};

module.exports = { Root };
'''

RENDER_CONFIG_CODE = '''
const { bundle } = require("@remotion/bundler");
const { renderMedia, selectComposition } = require("@remotion/renderer");
const path = require("path");
const fs = require("fs");

async function render() {
  console.log("[spike] Starting Remotion render...");

  const bundled = await bundle({
    entryPoint: "./src/Root.jsx",
    onProgress: (progress) => {
      if (progress % 25 === 0) console.log(`[spike] Bundle progress: ${progress}%`);
    },
  });

  console.log("[spike] Bundle complete. Selecting composition...");

  const composition = await selectComposition({
    serveUrl: bundled,
    id: "PromoScene",
  });

  console.log("[spike] Composition selected. Rendering to mp4...");

  const outputPath = path.resolve("./out/promo.mp4");
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });

  await renderMedia({
    composition,
    serveUrl: bundled,
    codec: "h264",
    outputLocation: outputPath,
  });

  const stats = fs.statSync(outputPath);
  console.log(`[spike] Render complete: ${outputPath} (${(stats.size / 1024).toFixed(1)} KB)`);
  return outputPath;
}

render().catch((err) => {
  console.error("[spike] Render failed:", err);
  process.exit(1);
});
'''

SPIKE_INSTALL_AND_RUN = '''#!/bin/bash
set -euo pipefail

echo "=== SPIKE: Remotion inside AgentCore Code Interpreter ==="
echo "Step 1: Install dependencies..."

npm init -y
npm install remotion @remotion/cli @remotion/bundler @remotion/renderer react react-dom

echo "Step 2: Write scene files..."
# (scene files would be written here via the Code Interpreter's file write capability)

echo "Step 3: Render..."
npx remotion render PromoScene out/promo.mp4 --frames=0-89

echo "Step 4: Validate output..."
if [ -f out/promo.mp4 ]; then
  SIZE=$(stat -f%z out/promo.mp4 2>/dev/null || stat --format=%s out/promo.mp4)
  echo "SUCCESS: mp4 exists, size=${SIZE} bytes"
  echo "Step 5: Upload to S3..."
  # aws s3 cp out/promo.mp4 s3://frame-renders/${SESSION_ID}/promo.mp4
  echo "S3 upload would happen here"
else
  echo "FAILURE: mp4 not found"
  exit 1
fi
'''

if __name__ == "__main__":
    print(__doc__)
    print("=== Code to inject into AgentCore Code Interpreter session ===")
    print()
    print("--- Install & Run Script ---")
    print(SPIKE_INSTALL_AND_RUN)
    print()
    print("--- Scene Code (Root.jsx) ---")
    print(REMOTION_SCENE_CODE)
    print()
    print("=== Expected AgentCore session config ===")
    print("  - Custom Code Interpreter with Public network mode")
    print("  - Execution role needs S3 write permission")
    print("  - Session timeout: 300s (headless Chromium + render is heavy)")
    print("  - Output: s3://frame-renders/{session_id}/promo.mp4")
