// =============================================================================
// ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
// Esta implementação representa uma proposta arquitetural, não código de produção.
// =============================================================================
"use client";

import { useState } from "react";
import Link from "next/link";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Legend,
} from "recharts";

// ---------------------------------------------------------------------------
// Mock data — production would fetch from /api/v1/patients/{id}/longitudinal
// ---------------------------------------------------------------------------

const PATIENT = {
  id: "pat_001",
  riskLevel: "high" as const,
  careIntensity: "Enhanced",
  careStatus: "Active",
  assignedClinician: "Dr. Beatriz Tavares",
  daysSinceContact: 8,
  openFlags: 2,
  carePlan: {
    contact_frequency_days: 14,
    review_date: "2024-04-05",
    goals: [
      { description: "Reduce PHQ-9 to mild range (<10)", target: 9, current: 12, baseline: 14 },
      { description: "WHO-5 wellbeing above 50%", target: 13, current: 11, baseline: 9 },
    ],
  },
};

// Assessment history — ordered oldest to most recent
const SYMPTOM_HISTORY = [
  { date: "Jan 15", PHQ9: 6, GAD7: 5, WHO5pct: 76 },
  { date: "Feb 5",  PHQ9: 8, GAD7: 7, WHO5pct: 68 },
  { date: "Feb 22", PHQ9: 10, GAD7: 7, WHO5pct: 56 },
  { date: "Mar 8",  PHQ9: 14, GAD7: 9, WHO5pct: 40 },
  { date: "Mar 22", PHQ9: 12, GAD7: 8, WHO5pct: 56 },
];

const CHECK_IN_HISTORY = [
  { date: "Mar 22", who5: 14, who5pct: 56, band: "high",   mood: 4, sleep: "good",      flags: [] },
  { date: "Mar 15", who5: 10, who5pct: 40, band: "moderate", mood: 2, sleep: "poor",    flags: ["Low mood", "Poor sleep"] },
  { date: "Mar 8",  who5: 8,  who5pct: 32, band: "low",    mood: 2, sleep: "very poor", flags: ["WHO-5 low wellbeing", "Low mood", "Poor sleep"] },
];

const OPEN_FLAGS = [
  {
    id: "f1",
    type: "score_deterioration",
    severity: "urgent",
    title: "PHQ-9 deterioration — 8 point increase",
    description: "PHQ-9 increased from 6 to 14 (mild → moderate). MCID threshold crossed.",
    triggered: "Mar 8, 2024",
  },
  {
    id: "f2",
    type: "assessment_due",
    severity: "info",
    title: "GAD-7 reassessment due",
    description: "Last GAD-7 was 38 days ago. Monthly reassessment recommended.",
    triggered: "Mar 14, 2024",
  },
];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

const RISK_COLORS: Record<string, string> = {
  acute: "bg-red-500 text-white",
  high: "bg-orange-500 text-white",
  moderate: "bg-yellow-500 text-slate-900",
  low: "bg-emerald-500 text-white",
};

const SEVERITY_COLORS: Record<string, string> = {
  urgent: "border-l-orange-500 bg-orange-950/40",
  warning: "border-l-yellow-500 bg-yellow-950/40",
  info: "border-l-slate-500 bg-slate-800/40",
  critical: "border-l-red-500 bg-red-950/40",
};

const SEVERITY_LABEL_COLORS: Record<string, string> = {
  urgent: "text-orange-400",
  warning: "text-yellow-400",
  info: "text-slate-400",
  critical: "text-red-400",
};

const WHO5_BAND_COLORS: Record<string, string> = {
  high: "text-emerald-400",
  moderate: "text-yellow-400",
  low: "text-red-400",
};

// PHQ-9 severity reference lines
const PHQ9_BANDS = [
  { y: 5,  label: "Mild",      color: "#facc15" },
  { y: 10, label: "Moderate",  color: "#f97316" },
  { y: 15, label: "Mod-Severe",color: "#ef4444" },
  { y: 20, label: "Severe",    color: "#dc2626" },
];

function GoalProgressBar({ goal }: { goal: typeof PATIENT.carePlan.goals[0] }) {
  const range = goal.baseline - goal.target;
  const progress = goal.baseline - goal.current;
  const pct = Math.min(100, Math.max(0, (progress / range) * 100));

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-slate-300">{goal.description}</span>
        <span className="text-slate-400">
          {goal.current} → <span className="text-indigo-400">{goal.target} target</span>
        </span>
      </div>
      <div className="h-2 bg-slate-800 rounded-full" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
        <div
          className="h-2 rounded-full bg-indigo-500 transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-xs text-slate-500 mt-1">{Math.round(pct)}% toward goal (baseline: {goal.baseline})</p>
    </div>
  );
}

// Custom Recharts tooltip
function SymptomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 text-sm shadow-xl">
      <p className="text-slate-300 font-medium mb-2">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: entry.color }} />
          <span className="text-slate-400">{entry.name}:</span>
          <span className="text-white font-medium">{entry.value}</span>
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function PatientDetailPage({ params }: { params: { id: string } }) {
  const patientId = params.id ?? PATIENT.id;
  const [acknowledgedFlags, setAcknowledgedFlags] = useState<Set<string>>(new Set());
  const [activeChart, setActiveChart] = useState<"phq9_gad7" | "who5">("phq9_gad7");

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center">
            <span className="text-white font-bold text-sm">L</span>
          </div>
          <span className="font-semibold text-lg">Lumina</span>
          <span className="text-slate-600 text-sm mx-2">/</span>
          <Link href="/dashboard" className="text-slate-500 text-sm hover:text-slate-300 transition-colors">
            Dashboard
          </Link>
          <span className="text-slate-600 text-sm mx-2">/</span>
          <span className="text-slate-300 text-sm font-mono">{patientId}</span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <Link
            href="/triage"
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg transition-colors text-sm"
          >
            New Triage
          </Link>
          <span className="text-slate-400">Dr. Beatriz Tavares</span>
          <div className="w-8 h-8 rounded-full bg-indigo-700 flex items-center justify-center text-xs font-medium">
            BT
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-8 py-8">
        {/* AI advisory banner */}
        <div className="bg-amber-950 border border-amber-800 rounded-lg px-4 py-3 mb-6 flex items-center gap-3">
          <span className="text-amber-400 text-sm">⚑</span>
          <span className="text-amber-200 text-sm">
            All AI-generated insights are advisory. Clinical judgment and human review are required
            before any care decision.
          </span>
        </div>

        {/* Patient header */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-5">
              <div className="w-14 h-14 rounded-full bg-slate-700 flex items-center justify-center text-xl font-bold text-slate-300">
                {patientId.replace("pat_", "P")}
              </div>
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-xl font-semibold font-mono">{patientId}</h1>
                  <span
                    className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wide ${
                      RISK_COLORS[PATIENT.riskLevel]
                    }`}
                  >
                    {PATIENT.riskLevel} risk
                  </span>
                  {PATIENT.openFlags > 0 && (
                    <span className="bg-orange-900 border border-orange-700 text-orange-300 text-xs px-2 py-0.5 rounded-full">
                      {PATIENT.openFlags} open {PATIENT.openFlags === 1 ? "flag" : "flags"}
                    </span>
                  )}
                </div>
                <p className="text-slate-400 text-sm mt-1">
                  {PATIENT.careIntensity} care · {PATIENT.careStatus} ·{" "}
                  <span className={PATIENT.daysSinceContact > 14 ? "text-orange-400" : "text-slate-400"}>
                    {PATIENT.daysSinceContact} days since contact
                  </span>{" "}
                  · {PATIENT.assignedClinician}
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <button className="text-sm border border-slate-700 hover:border-slate-500 text-slate-300 px-4 py-2 rounded-lg transition-colors">
                Log Contact
              </button>
              <Link
                href={`/triage?patient=${patientId}`}
                className="text-sm bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Run Triage
              </Link>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Left column: charts + check-ins */}
          <div className="col-span-2 space-y-6">

            {/* Symptom trajectory chart */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-5">
                <div>
                  <h2 className="font-semibold">Symptom Trajectory</h2>
                  <p className="text-slate-500 text-xs mt-0.5">Serial assessment scores — ordered chronologically</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setActiveChart("phq9_gad7")}
                    className={`text-xs px-3 py-1.5 rounded-lg transition-colors ${
                      activeChart === "phq9_gad7"
                        ? "bg-indigo-600 text-white"
                        : "border border-slate-700 text-slate-400 hover:border-slate-500"
                    }`}
                  >
                    PHQ-9 / GAD-7
                  </button>
                  <button
                    onClick={() => setActiveChart("who5")}
                    className={`text-xs px-3 py-1.5 rounded-lg transition-colors ${
                      activeChart === "who5"
                        ? "bg-indigo-600 text-white"
                        : "border border-slate-700 text-slate-400 hover:border-slate-500"
                    }`}
                  >
                    WHO-5 Wellbeing
                  </button>
                </div>
              </div>

              {activeChart === "phq9_gad7" ? (
                <>
                  <ResponsiveContainer width="100%" height={220}>
                    <LineChart data={SYMPTOM_HISTORY} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis domain={[0, 27]} tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <Tooltip content={<SymptomTooltip />} />
                      <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                      {/* PHQ-9 severity reference lines */}
                      {PHQ9_BANDS.map((band) => (
                        <ReferenceLine
                          key={band.label}
                          y={band.y}
                          stroke={band.color}
                          strokeDasharray="4 4"
                          strokeOpacity={0.3}
                        />
                      ))}
                      <Line
                        type="monotone"
                        dataKey="PHQ9"
                        name="PHQ-9"
                        stroke="#6366f1"
                        strokeWidth={2}
                        dot={{ r: 4, fill: "#6366f1", strokeWidth: 0 }}
                        activeDot={{ r: 6 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="GAD7"
                        name="GAD-7"
                        stroke="#a78bfa"
                        strokeWidth={2}
                        dot={{ r: 4, fill: "#a78bfa", strokeWidth: 0 }}
                        activeDot={{ r: 6 }}
                        strokeDasharray="5 3"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                  <p className="text-xs text-slate-600 mt-3">
                    Dashed lines: PHQ-9 severity thresholds (mild ≥5, moderate ≥10, mod-severe ≥15, severe ≥20)
                  </p>
                </>
              ) : (
                <>
                  <ResponsiveContainer width="100%" height={220}>
                    <LineChart data={SYMPTOM_HISTORY} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <Tooltip content={<SymptomTooltip />} />
                      <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                      {/* WHO-5 clinical threshold at 50% */}
                      <ReferenceLine y={50} stroke="#f97316" strokeDasharray="4 4" strokeOpacity={0.5} />
                      <ReferenceLine y={28} stroke="#ef4444" strokeDasharray="4 4" strokeOpacity={0.5} />
                      <Line
                        type="monotone"
                        dataKey="WHO5pct"
                        name="WHO-5 (%)"
                        stroke="#34d399"
                        strokeWidth={2}
                        dot={{ r: 4, fill: "#34d399", strokeWidth: 0 }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                  <p className="text-xs text-slate-600 mt-3">
                    Orange line: WHO-5 ≤50% warrants clinical attention · Red line: WHO-5 ≤28% = low wellbeing
                  </p>
                </>
              )}
            </div>

            {/* Digital check-in history */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl">
              <div className="px-6 py-4 border-b border-slate-800">
                <h2 className="font-semibold">Digital Check-ins</h2>
                <p className="text-slate-500 text-xs mt-0.5">Patient self-report via Lumina app · WHO-5 Wellbeing Index</p>
              </div>
              <div className="divide-y divide-slate-800">
                {CHECK_IN_HISTORY.map((checkin, i) => (
                  <div key={i} className="px-6 py-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-3 mb-1">
                          <span className="text-sm font-medium text-slate-300">{checkin.date}</span>
                          <span className={`text-xs font-medium ${WHO5_BAND_COLORS[checkin.band]}`}>
                            WHO-5: {checkin.who5}/25 ({checkin.who5pct}%) — {checkin.band} wellbeing
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          <span className="text-xs text-slate-500">Mood: {checkin.mood}/5</span>
                          <span className="text-slate-700">·</span>
                          <span className="text-xs text-slate-500">Sleep: {checkin.sleep.replace("_", " ")}</span>
                          {checkin.flags.length > 0 && (
                            <>
                              <span className="text-slate-700">·</span>
                              {checkin.flags.map((f) => (
                                <span key={f} className="text-xs text-orange-400">{f}</span>
                              ))}
                            </>
                          )}
                        </div>
                      </div>
                      {checkin.flags.length > 0 && (
                        <span className="text-xs bg-orange-900/50 text-orange-300 border border-orange-800 px-2 py-0.5 rounded-full">
                          Review triggered
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Right column: flags + care plan */}
          <div className="space-y-6">

            {/* Open flags */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl">
              <div className="px-5 py-4 border-b border-slate-800">
                <h2 className="font-semibold text-sm">Open Flags</h2>
              </div>
              <div className="p-3 space-y-2">
                {OPEN_FLAGS.map((flag) => (
                  <div
                    key={flag.id}
                    className={`border-l-2 rounded-r-lg p-3 ${SEVERITY_COLORS[flag.severity]}`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className={`text-xs font-semibold uppercase tracking-wide mb-1 ${SEVERITY_LABEL_COLORS[flag.severity]}`}>
                          {flag.severity}
                        </p>
                        <p className="text-xs font-medium text-slate-200">{flag.title}</p>
                        <p className="text-xs text-slate-500 mt-1">{flag.description}</p>
                        <p className="text-xs text-slate-600 mt-1">Triggered: {flag.triggered}</p>
                      </div>
                    </div>
                    {!acknowledgedFlags.has(flag.id) ? (
                      <button
                        onClick={() => setAcknowledgedFlags((p) => new Set([...p, flag.id]))}
                        className="mt-2 text-xs text-slate-500 hover:text-slate-300 border border-slate-700 hover:border-slate-500 px-2 py-1 rounded transition-colors w-full"
                      >
                        Acknowledge
                      </button>
                    ) : (
                      <p className="mt-2 text-xs text-slate-600 italic text-center">Acknowledged</p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Care plan goals */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl">
              <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
                <h2 className="font-semibold text-sm">Care Plan Goals</h2>
                <span className="text-xs text-slate-500">
                  Review: {PATIENT.carePlan.review_date}
                </span>
              </div>
              <div className="p-5 space-y-5">
                {PATIENT.carePlan.goals.map((goal, i) => (
                  <GoalProgressBar key={i} goal={goal} />
                ))}
                <p className="text-xs text-slate-600">
                  Contact frequency: every {PATIENT.carePlan.contact_frequency_days} days
                </p>
              </div>
            </div>

            {/* Session prep link */}
            <div className="bg-indigo-950 border border-indigo-800 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-indigo-300 mb-2">Session Preparation</h3>
              <p className="text-xs text-indigo-400 mb-4">
                AI-generated briefing for your next session with this patient. Reviews changes since last visit.
              </p>
              <button className="w-full text-sm bg-indigo-700 hover:bg-indigo-600 text-white py-2 rounded-lg transition-colors">
                Generate Session Briefing
              </button>
            </div>

          </div>
        </div>
      </main>
    </div>
  );
}
