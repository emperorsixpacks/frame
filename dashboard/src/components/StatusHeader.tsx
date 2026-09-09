"use client";

import { useState } from "react";

export function StatusHeader() {
  const [repoName] = useState("acme/widget");
  const [connected] = useState(true);
  const [status, setStatus] = useState<"idle" | "rendering" | "done">("idle");

  return (
    <header
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        paddingBottom: "var(--space-6)",
        borderBottom: "1px solid var(--color-border)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
        <h1
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "1.25rem",
            fontWeight: 600,
            letterSpacing: "-0.02em",
          }}
        >
          frame
        </h1>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "0.8125rem",
            color: "var(--color-text-secondary)",
          }}
        >
          {repoName}
        </span>
        {connected && (
          <span
            style={{
              fontSize: "0.75rem",
              color: "var(--color-success)",
              fontFamily: "var(--font-mono)",
            }}
          >
            connected
          </span>
        )}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "0.8125rem",
            color:
              status === "rendering"
                ? "var(--color-accent)"
                : status === "done"
                  ? "var(--color-success)"
                  : "var(--color-text-secondary)",
          }}
        >
          status: {status}
        </span>
        {status === "idle" && (
          <button
            onClick={() => {
              setStatus("rendering");
              setTimeout(() => setStatus("done"), 3000);
            }}
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "0.8125rem",
              background: "var(--color-accent)",
              color: "var(--color-base)",
              border: "none",
              padding: "var(--space-2) var(--space-4)",
              borderRadius: "var(--radius-sm)",
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            simulate render
          </button>
        )}
      </div>
    </header>
  );
}
