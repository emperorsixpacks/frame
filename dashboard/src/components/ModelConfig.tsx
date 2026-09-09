"use client";

import { useState } from "react";

interface ModelState {
  region: string;
  modelId: string;
  interpreterId: string;
  s3Bucket: string;
}

export function ModelConfig() {
  const [model, setModel] = useState<ModelState>({
    region: "us-east-1",
    modelId: "us.anthropic.claude-sonnet-4-20250514-v1:0",
    interpreterId: "",
    s3Bucket: "frame-renders",
  });

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <section>
      <h2
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "0.875rem",
          fontWeight: 600,
          marginBottom: "var(--space-4)",
          color: "var(--color-text-secondary)",
          textTransform: "lowercase",
        }}
      >
        model config
      </h2>

      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
        <Field label="aws region">
          <input
            type="text"
            value={model.region}
            onChange={(e) => setModel({ ...model, region: e.target.value })}
            style={inputStyle}
          />
        </Field>

        <Field label="bedrock model id">
          <input
            type="text"
            value={model.modelId}
            onChange={(e) => setModel({ ...model, modelId: e.target.value })}
            style={inputStyle}
          />
        </Field>

        <Field label="agentcore code interpreter id">
          <input
            type="text"
            value={model.interpreterId}
            onChange={(e) => setModel({ ...model, interpreterId: e.target.value })}
            placeholder="create in AWS console"
            style={inputStyle}
          />
        </Field>

        <Field label="s3 bucket">
          <input
            type="text"
            value={model.s3Bucket}
            onChange={(e) => setModel({ ...model, s3Bucket: e.target.value })}
            style={inputStyle}
          />
        </Field>

        <button onClick={handleSave} style={buttonStyle}>
          {saved ? "saved" : "save config"}
        </button>
      </div>
    </section>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label
        style={{
          display: "block",
          fontFamily: "var(--font-mono)",
          fontSize: "0.75rem",
          color: "var(--color-text-secondary)",
          marginBottom: "var(--space-1)",
        }}
      >
        {label}
      </label>
      {children}
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  width: "100%",
  fontFamily: "var(--font-mono)",
  fontSize: "0.8125rem",
  background: "var(--color-surface)",
  color: "var(--color-text)",
  border: "1px solid var(--color-border)",
  padding: "var(--space-2) var(--space-3)",
  borderRadius: "var(--radius-sm)",
  outline: "none",
};

const buttonStyle: React.CSSProperties = {
  fontFamily: "var(--font-mono)",
  fontSize: "0.8125rem",
  background: "var(--color-surface-raised)",
  color: "var(--color-text)",
  border: "1px solid var(--color-border)",
  padding: "var(--space-2) var(--space-4)",
  borderRadius: "var(--radius-sm)",
  cursor: "pointer",
  alignSelf: "flex-start",
};
