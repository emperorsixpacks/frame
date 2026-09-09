import { StatusHeader } from "../components/StatusHeader";
import { BrandConfig } from "../components/BrandConfig";
import { ModelConfig } from "../components/ModelConfig";
import { ActivityFeed } from "../components/ActivityFeed";

export default function Home() {
  return (
    <main style={{ maxWidth: 1200, margin: "0 auto", padding: "var(--space-8) var(--space-6)" }}>
      <StatusHeader />
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "var(--space-6)",
          marginTop: "var(--space-8)",
        }}
      >
        <BrandConfig />
        <ModelConfig />
        <ActivityFeed />
      </div>
    </main>
  );
}
