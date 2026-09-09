"use client";

interface Generation {
  id: string;
  repo: string;
  pr: string;
  status: "done" | "rendering" | "failed" | "skipped";
  timestamp: string;
}

const MOCK_DATA: Generation[] = [
  { id: "1", repo: "acme/widget", pr: "#142 — Add dark mode", status: "done", timestamp: "2m ago" },
  { id: "2", repo: "acme/widget", pr: "#141 — Fix typo in docs", status: "skipped", timestamp: "18m ago" },
  { id: "3", repo: "acme/widget", pr: "#139 — Launch v2.0", status: "rendering", timestamp: "just now" },
  { id: "4", repo: "acme/api", pr: "#87 — New auth flow", status: "done", timestamp: "1h ago" },
  { id: "5", repo: "acme/widget", pr: "#136 — Bump deps", status: "failed", timestamp: "3h ago" },
];

export function ActivityFeed() {
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
        activity
      </h2>

      <div style={{ display: "flex", flexDirection: "column", gap: 1 }}>
        {MOCK_DATA.map((gen) => (
          <div
            key={gen.id}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "var(--space-2) var(--space-3)",
              background: gen.status === "rendering" ? "var(--color-surface-raised)" : "transparent",
              borderLeft:
                gen.status === "rendering"
                  ? "2px solid var(--color-accent)"
                  : gen.status === "done"
                    ? "2px solid var(--color-success)"
                    : gen.status === "failed"
                      ? "2px solid var(--color-error)"
                      : "2px solid transparent",
            }}
          >
            <div>
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.8125rem",
                }}
              >
                {gen.pr}
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
              <StatusBadge status={gen.status} />
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.75rem",
                  color: "var(--color-text-secondary)",
                }}
              >
                {gen.timestamp}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function StatusBadge({ status }: { status: Generation["status"] }) {
  const colors: Record<Generation["status"], string> = {
    done: "var(--color-success)",
    rendering: "var(--color-accent)",
    failed: "var(--color-error)",
    skipped: "var(--color-neutral)",
  };

  return (
    <span
      style={{
        fontFamily: "var(--font-mono)",
        fontSize: "0.6875rem",
        color: colors[status],
        textTransform: "uppercase",
        letterSpacing: "0.05em",
      }}
    >
      {status === "rendering" ? "rendering..." : status}
    </span>
  );
}
