// =============================================================================
// ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
// Esta implementação representa uma proposta arquitetural, não código de produção.
// =============================================================================
"use client";

import { useState } from "react";

const MOCK_QUEUE = [
  {
    id: "pat_001",
    risk: "high",
    priorityScore: 87.5,
    signal: "PHQ-9 increased 8 points since last assessment",
    daysSinceContact: 12,
    action: "Priority Contact",
    trend: "deteriorating",
  },
  {
    id: "pat_007",
    risk: "moderate",
    priorityScore: 54.2,
    signal: "Care gap: 19 days since last contact",
    daysSinceContact: 19,
    action: "Enhanced Monitoring",
    trend: "stable",
  },
  {
    id: "pat_013",
    risk: "moderate",
    priorityScore: 42.1,
    signal: "GAD-7 moderate range; low appointment adherence (58%)",
    daysSinceContact: 7,
    action: "Enhanced Monitoring",
    trend: "stable",
  },
  {
    id: "pat_022",
    risk: "low",
    priorityScore: 18.0,
    signal: "Routine reassessment due",
    daysSinceContact: 10,
    action: "Routine Follow-up",
    trend: "improving",
  },
];

const RISK_COLORS: Record<string, string> = {
  acute: "bg-red-500 text-white",
  high: "bg-orange-500 text-white",
  moderate: "bg-yellow-500 text-slate-900",
  low: "bg-emerald-500 text-white",
};

const TREND_ICONS: Record<string, string> = {
  deteriorating: "↑",
  stable: "→",
  improving: "↓",
};

const TREND_COLORS: Record<string, string> = {
  deteriorating: "text-red-400",
  stable: "text-slate-400",
  improving: "text-emerald-400",
};

export default function DashboardPage() {
  const [overriddenIds, setOverriddenIds] = useState<Set<string>>(new Set());

  const teamStats = {
    activePatients: 38,
    highUrgency: 1,
    careGaps: 3,
    avgDaysSinceContact: 9.2,
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center">
            <span className="text-white font-bold text-sm">L</span>
          </div>
          <span className="font-semibold text-lg">Lumina</span>
          <span className="text-slate-600 text-sm ml-2">/ Clinical Dashboard</span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span className="text-slate-400">Dr. Beatriz Tavares</span>
          <div className="w-8 h-8 rounded-full bg-indigo-700 flex items-center justify-center text-xs font-medium">
            BT
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-8 py-8">
        {/* AI advisory banner */}
        <div className="bg-amber-950 border border-amber-800 rounded-lg px-4 py-3 mb-8 flex items-center gap-3">
          <span className="text-amber-400 text-sm">⚑</span>
          <span className="text-amber-200 text-sm">
            All AI-generated insights are advisory. Clinical judgment and human review are required
            before any care decision.
          </span>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { label: "Active Patients", value: teamStats.activePatients, color: "text-white" },
            { label: "High Urgency", value: teamStats.highUrgency, color: "text-orange-400" },
            { label: "Critical Care Gaps", value: teamStats.careGaps, color: "text-red-400" },
            {
              label: "Avg Days Since Contact",
              value: teamStats.avgDaysSinceContact,
              color: "text-slate-300",
            },
          ].map((stat) => (
            <div
              key={stat.label}
              className="bg-slate-900 border border-slate-800 rounded-xl p-5"
            >
              <p className="text-slate-500 text-xs uppercase tracking-wide mb-1">{stat.label}</p>
              <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Priority Queue */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl">
          <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-lg">Priority Queue</h2>
              <p className="text-slate-500 text-sm mt-0.5">
                Ordered by risk score · Updated 4 minutes ago
              </p>
            </div>
            <button aria-label="Refresh priority queue" className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
              Refresh
            </button>
          </div>

          <div className="divide-y divide-slate-800">
            {MOCK_QUEUE.map((patient) => (
              <div key={patient.id} className="px-6 py-4 hover:bg-slate-800/50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {/* Risk badge */}
                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wide ${
                        RISK_COLORS[patient.risk]
                      }`}
                    >
                      {patient.risk}
                    </span>

                    {/* Patient info */}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm font-mono">{patient.id}</span>
                        <span
                          className={`text-sm ${TREND_COLORS[patient.trend]}`}
                          title={`Trend: ${patient.trend}`}
                        >
                          {TREND_ICONS[patient.trend]}
                        </span>
                      </div>
                      <p className="text-slate-400 text-sm mt-0.5">{patient.signal}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-6 text-sm">
                    {/* Days since contact */}
                    <div className="text-right">
                      <p className="text-slate-500 text-xs">Days since contact</p>
                      <p
                        className={`font-medium ${
                          patient.daysSinceContact > 14 ? "text-orange-400" : "text-slate-300"
                        }`}
                      >
                        {patient.daysSinceContact}d
                      </p>
                    </div>

                    {/* Priority score */}
                    <div className="text-right">
                      <p className="text-slate-500 text-xs">Priority score</p>
                      <p className="font-medium text-slate-300">{patient.priorityScore}</p>
                    </div>

                    {/* Action */}
                    <div className="text-right">
                      <p className="text-slate-500 text-xs">Recommended action</p>
                      <p className="text-indigo-400 text-xs font-medium">{patient.action}</p>
                    </div>

                    {/* Override */}
                    {overriddenIds.has(patient.id) ? (
                      <span className="text-xs text-slate-500 italic">Overridden</span>
                    ) : (
                      <button
                        onClick={() =>
                          setOverriddenIds((prev) => new Set([...prev, patient.id]))
                        }
                        className="text-xs text-slate-500 hover:text-slate-300 border border-slate-700 hover:border-slate-500 px-3 py-1.5 rounded transition-colors"
                      >
                        Override
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Risk distribution */}
        <div className="mt-6 grid grid-cols-2 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="font-semibold mb-4">Risk Distribution</h3>
            <div className="space-y-3">
              {[
                { label: "Low", count: 21, total: 38, color: "bg-emerald-500" },
                { label: "Moderate", count: 12, total: 38, color: "bg-yellow-500" },
                { label: "High", count: 4, total: 38, color: "bg-orange-500" },
                { label: "Acute", count: 1, total: 38, color: "bg-red-500" },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-3">
                  <span className="text-sm text-slate-400 w-20">{item.label}</span>
                  <div className="flex-1 bg-slate-800 rounded-full h-2" role="progressbar" aria-label={`${item.label} risk level`} aria-valuenow={item.count} aria-valuemin={0} aria-valuemax={item.total}>
                    <div
                      className={`${item.color} h-2 rounded-full`}
                      style={{ width: `${(item.count / item.total) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-slate-400 w-6 text-right">{item.count}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="font-semibold mb-4">Care Continuity</h3>
            <div className="space-y-4">
              {[
                { label: "Within care plan", value: "76%", color: "text-emerald-400" },
                { label: "Gap warning (>14d)", value: "16%", color: "text-yellow-400" },
                { label: "Critical gap (>21d)", value: "8%", color: "text-red-400" },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">{item.label}</span>
                  <span className={`font-semibold ${item.color}`}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
