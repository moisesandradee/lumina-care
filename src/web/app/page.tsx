// =============================================================================
// ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
// Esta implementação representa uma proposta arquitetural, não código de produção.
// =============================================================================
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* Navigation */}
      <nav aria-label="Main navigation" className="border-b border-slate-800 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center">
            <span className="text-white font-bold text-sm">L</span>
          </div>
          <span className="font-semibold text-lg tracking-tight">Lumina</span>
        </div>
        <div className="flex items-center gap-6 text-sm text-slate-400">
          <Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
          <Link href="/dashboard" className="hover:text-white transition-colors">Triage</Link>
          <Link href="/dashboard" className="hover:text-white transition-colors">Patients</Link>
          <Link
            href="/dashboard"
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Open Platform
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-8 pt-24 pb-20 text-center">
        <div className="inline-flex items-center gap-2 bg-indigo-950 border border-indigo-800 rounded-full px-4 py-1.5 text-indigo-300 text-sm mb-8">
          <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
          MVP in Development — Phase 1
        </div>

        <h1 className="text-5xl font-bold tracking-tight mb-6 leading-tight">
          From signal to care.
          <br />
          <span className="text-indigo-400">From data to empathy.</span>
        </h1>

        <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Lumina is an AI-native clinical intelligence platform that helps mental health
          care teams detect psychosocial risk earlier, maintain care continuity, and act
          with confidence — without replacing the human at the center of care.
        </p>

        <div className="flex items-center justify-center gap-4">
          <Link
            href="/dashboard"
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            View Dashboard
          </Link>
          <a
            href="https://github.com/moisesandradee/lumina-care"
            target="_blank"
            rel="noopener noreferrer"
            className="border border-slate-700 hover:border-slate-500 text-slate-300 px-6 py-3 rounded-lg font-medium transition-colors"
          >
            View on GitHub
          </a>
        </div>
      </section>

      {/* Capabilities */}
      <section className="max-w-5xl mx-auto px-8 pb-24">
        <div className="grid grid-cols-3 gap-6">
          {[
            {
              icon: "◈",
              title: "Intelligent Triage",
              desc: "Psychosocial risk scoring grounded in PHQ-9, GAD-7, and C-SSRS. Prioritize patient attention before crisis.",
            },
            {
              icon: "◎",
              title: "Care Journey Intelligence",
              desc: "Track continuity of care, detect gaps, and model longitudinal patient trajectories across your panel.",
            },
            {
              icon: "◐",
              title: "Clinical Decision Support",
              desc: "AI-assisted session preparation and team-level analytics. Advisory, explainable, and always overridable.",
            },
          ].map((cap) => (
            <div
              key={cap.title}
              className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-colors"
            >
              <div className="text-indigo-400 text-2xl mb-4">{cap.icon}</div>
              <h3 className="font-semibold text-lg mb-2">{cap.title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{cap.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Ethics banner */}
      <section className="border-t border-slate-800 px-8 py-8">
        <div className="max-w-5xl mx-auto flex items-center justify-center gap-3 text-slate-500 text-sm">
          <span>Ethics-first architecture</span>
          <span>·</span>
          <span>Explainable AI outputs</span>
          <span>·</span>
          <span>Clinical authority always preserved</span>
          <span>·</span>
          <span>No black-box decisions</span>
        </div>
      </section>
    </main>
  );
}
