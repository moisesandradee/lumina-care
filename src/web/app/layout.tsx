// =============================================================================
// ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
// Esta implementação representa uma proposta arquitetural, não código de produção.
// =============================================================================
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Lumina — Clinical Mental Health Intelligence",
  description:
    "AI-native mental health intelligence platform for ethical triage, care journey support, and psychosocial risk analysis.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
