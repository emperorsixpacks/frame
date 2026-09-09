"use client";

import { useState } from "react";

interface BrandState {
  name: string;
  tone: string;
  primaryColor: string;
  dos: string;
  donts: string;
}

export function BrandConfig() {
  const [brand, setBrand] = useState<BrandState>({
    name: "Frame",
    tone: "technical, confident, minimal",
    primaryColor: "#E8B84B",
    dos: "Use monospace type, Keep it dark",
    donts: "No stock footage, No voiceover",
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
        brand config
      </h2>

      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
        <Field label="name">
          <input
            type="text"
            value={brand.name}
            onChange={(e) => setBrand({ ...brand, name: e.target.value })}
            style={inputStyle}
          />
        </Field>

        <Field label="tone">
          <input
            type="text"
            value={brand.tone}
            onChange={(e) => setBrand({ ...brand, tone: e.target.value })}
            style={inputStyle}
          />
        </Field>

        <Field label="primary color">
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
            <div
              style={{
                width: 24,
                height: 24,
                borderRadius: "var(--radius-sm)",
                backgroundColor: brand.primaryColor,
                border: "1px solid var(--color-border)",
                flexShrink: 0,
              }}
            />
            <input
              type="text"
              value={brand.primaryColor}
              onChange={(e) => setBrand({ ...brand, primaryColor: e.target.value })}
              style={{ ...inputStyle, flex: 1 }}
            />
          </div>
        </Field>

        <Field label="do's">
          <textarea
            value={brand.dos}
            onChange={(e) => setBrand({ ...brand, dos: e.target.value })}
            style={{ ...inputStyle, resize: "vertical", minHeight: 60 }}
          />
        </Field>

        <Field label="don'ts">
          <textarea
            value={brand.donts}
            onChange={(e) => setBrand({ ...brand, donts: e.target.value })}
            style={{ ...inputStyle, resize: "vertical", minHeight: 60 }}
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
