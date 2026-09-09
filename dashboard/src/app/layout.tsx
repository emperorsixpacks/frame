import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Frame",
  description: "Turn merged PRs into promo videos",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
