// =============================================================================
// ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
// Esta implementação representa uma proposta arquitetural, não código de produção.
// =============================================================================
"use client";

import { useState } from "react";
import Link from "next/link";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type RiskLevel = "low" | "moderate" | "high" | "acute";

type TriageResult = {
  overall_risk_level: RiskLevel;
  priority_score: number;
  recommended_action: string;
  risk_dimensions: Array<{
    dimension: string;
    level: RiskLevel;
    score: number;
    contributing_signals: string[];
  }>;
  requires_override_review: boolean;
  computed_at: string;
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const RISK_COLORS: Record<RiskLevel, string> = {
  acute: "bg-red-500 text-white",
  high: "bg-orange-500 text-white",
  moderate: "bg-yellow-500 text-slate-900",
  low: "bg-emerald-500 text-white",
};

const RISK_BORDER: Record<RiskLevel, string> = {
  acute: "border-red-500",
  high: "border-orange-500",
  moderate: "border-yellow-500",
  low: "border-emerald-500",
};

const ACTION_LABELS: Record<string, string> = {
  immediate_escalation: "Immediate Escalation",
  urgent_clinical_review: "Urgent Clinical Review",
  priority_contact: "Priority Contact",
  enhanced_monitoring: "Enhanced Monitoring",
  routine_follow_up: "Routine Follow-up",
};

const DIMENSION_LABELS: Record<string, string> = {
  safety: "Safety (C-SSRS)",
  depression_symptoms: "Depression (PHQ-9)",
  anxiety_symptoms: "Anxiety (GAD-7)",
  care_engagement: "Care Engagement",
};

// Simulate the backend scoring logic in-browser for the conceptual demo
function computeLocalRisk(form: FormState): TriageResult {
  const dimensions = [];
  let priorityComponents: number[] = [];

  // Safety dimension
  let safetyLevel: RiskLevel = "low";
  let safetyScore = 0;
  let safetySignals: string[] = [];

  if (!form.cssrsAvailable) {
    safetySignals = ["No C-SSRS data available"];
  } else if (form.behaviorPresent) {
    safetyLevel = "acute";
    safetyScore = 1.0;
    safetySignals = ["C-SSRS: suicidal behavior present — immediate escalation indicated"];
  } else if (form.ideationPresent) {
    const intensity = form.ideationIntensity ?? 0;
    safetyLevel = intensity >= 4 ? "high" : "moderate";
    safetyScore = intensity >= 4 ? 0.8 : 0.5;
    safetySignals = [`C-SSRS: suicidal ideation (intensity ${intensity}/5)`];
  } else {
    safetySignals = ["C-SSRS: no ideation or behavior reported"];
  }

  dimensions.push({ dimension: "safety", level: safetyLevel, score: safetyScore, contributing_signals: safetySignals });
  priorityComponents.push(levelWeight(safetyLevel, safetyScore, 3.0));

  // PHQ-9
  if (form.phq9Score !== null) {
    const s = form.phq9Score;
    const level: RiskLevel = s >= 10 ? (s >= 15 ? "high" : "moderate") : "low";
    const label = s >= 20 ? "severe" : s >= 15 ? "moderately severe" : s >= 10 ? "moderate" : s >= 5 ? "mild" : "minimal";
    dimensions.push({
      dimension: "depression_symptoms", level, score: s / 27,
      contributing_signals: [`PHQ-9: ${s}/27 — ${label} range`],
    });
    priorityComponents.push(levelWeight(level, s / 27, 2.0));
  }

  // GAD-7
  if (form.gad7Score !== null) {
    const s = form.gad7Score;
    const level: RiskLevel = s >= 10 ? (s >= 15 ? "high" : "moderate") : "low";
    const label = s >= 15 ? "severe" : s >= 10 ? "moderate" : s >= 5 ? "mild" : "minimal";
    dimensions.push({
      dimension: "anxiety_symptoms", level, score: s / 21,
      contributing_signals: [`GAD-7: ${s}/21 — ${label} range`],
    });
    priorityComponents.push(levelWeight(level, s / 21, 1.5));
  }

  // Care engagement
  let engScore = 0;
  const engSignals: string[] = [];
  if (form.daysSinceContact !== null) {
    if (form.daysSinceContact > 21) { engScore = Math.max(engScore, 0.8); engSignals.push(`Care gap: ${form.daysSinceContact} days since contact (>21 day threshold)`); }
    else if (form.daysSinceContact > 14) { engScore = Math.max(engScore, 0.5); engSignals.push(`Care gap approaching: ${form.daysSinceContact} days since contact`); }
  }
  if (form.adherenceRate !== null && form.adherenceRate < 0.6) {
    engScore = Math.max(engScore, 0.6);
    engSignals.push(`Low appointment adherence: ${Math.round(form.adherenceRate * 100)}%`);
  }
  if (!engSignals.length) engSignals.push("Care engagement within expected parameters");
  const engLevel: RiskLevel = engScore >= 0.7 ? "high" : engScore >= 0.4 ? "moderate" : "low";
  dimensions.push({ dimension: "care_engagement", level: engLevel, score: engScore, contributing_signals: engSignals });
  priorityComponents.push(levelWeight(engLevel, engScore, 1.5));

  const priorityScore = Math.min(100, priorityComponents.reduce((a, b) => a + b, 0));

  const levelOrder: RiskLevel[] = ["low", "moderate", "high", "acute"];
  let overallLevel: RiskLevel = dimensions.reduce((max, d) =>
    levelOrder.indexOf(d.level) > levelOrder.indexOf(max) ? d.level : max, "low" as RiskLevel);

  if (form.behaviorPresent) overallLevel = "acute";

  const action = computeAction(overallLevel);

  return {
    overall_risk_level: overallLevel,
    priority_score: Math.round(priorityScore * 100) / 100,
    recommended_action: action,
    risk_dimensions: dimensions as TriageResult["risk_dimensions"],
    requires_override_review: overallLevel === "acute",
    computed_at: new Date().toISOString(),
  };
}

function levelWeight(level: RiskLevel, score: number, weight: number): number {
  const base: Record<RiskLevel, number> = { low: 10, moderate: 30, high: 60, acute: 100 };
  return base[level] * weight * score;
}

function computeAction(level: RiskLevel): string {
  if (level === "acute") return "immediate_escalation";
  if (level === "high") return "priority_contact";
  if (level === "moderate") return "enhanced_monitoring";
  return "routine_follow_up";
}

// ---------------------------------------------------------------------------
// Form state
// ---------------------------------------------------------------------------

type FormState = {
  patientId: string;
  clinicianId: string;
  phq9Score: number | null;
  gad7Score: number | null;
  cssrsAvailable: boolean;
  ideationPresent: boolean;
  behaviorPresent: boolean;
  ideationIntensity: number | null;
  daysSinceContact: number | null;
  adherenceRate: number | null;
};

const INITIAL_FORM: FormState = {
  patientId: "",
  clinicianId: "clin_dr_tavares",
  phq9Score: null,
  gad7Score: null,
  cssrsAvailable: false,
  ideationPresent: false,
  behaviorPresent: false,
  ideationIntensity: null,
  daysSinceContact: null,
  adherenceRate: null,
};

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function TriagePage() {
  const [form, setForm] = useState<FormState>(INITIAL_FORM);
  const [result, setResult] = useState<TriageResult | null>(null);
  const [overridden, setOverridden] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setResult(computeLocalRisk(form));
    setOverridden(false);
  };

  const handleReset = () => {
    setForm(INITIAL_FORM);
    setResult(null);
    setOverridden(false);
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
          <span className="text-slate-600 text-sm mx-2">/</span>
          <Link href="/dashboard" className="text-slate-500 text-sm hover:text-slate-300 transition-colors">
            Dashboard
          </Link>
          <span className="text-slate-600 text-sm mx-2">/</span>
          <span className="text-slate-300 text-sm">New Triage</span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span className="text-slate-400">Dr. Beatriz Tavares</span>
          <div className="w-8 h-8 rounded-full bg-indigo-700 flex items-center justify-center text-xs font-medium">
            BT
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-8 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Psychosocial Risk Triage</h1>
          <p className="text-slate-400 text-sm mt-1">
            Enter clinical assessment data to compute a structured risk profile.
            All outputs are advisory — clinical judgment is required.
          </p>
        </div>

        {/* AI advisory banner */}
        <div className="bg-amber-950 border border-amber-800 rounded-lg px-4 py-3 mb-6 flex items-center gap-3">
          <span className="text-amber-400 text-sm">⚑</span>
          <span className="text-amber-200 text-sm">
            This triage tool uses validated clinical instruments (PHQ-9, GAD-7, C-SSRS).
            Outputs are advisory. Clinical authority is always preserved.
          </span>
        </div>

        <div className="grid grid-cols-2 gap-8">
          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">

            {/* Patient identification */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h2 className="font-semibold text-sm text-slate-300 mb-4">Patient & Clinician</h2>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-slate-500 mb-1">Patient ID (internal)</label>
                  <input
                    type="text"
                    placeholder="e.g., pat_001"
                    value={form.patientId}
                    onChange={(e) => setForm({ ...form, patientId: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>
            </div>

            {/* PHQ-9 */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="font-semibold text-sm text-slate-300">PHQ-9 Depression Scale</h2>
                  <p className="text-xs text-slate-600 mt-0.5">0–27 · Mild ≥5, Moderate ≥10, Severe ≥20</p>
                </div>
                <label className="flex items-center gap-2 text-xs text-slate-500 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.phq9Score !== null}
                    onChange={(e) => setForm({ ...form, phq9Score: e.target.checked ? 0 : null })}
                    className="accent-indigo-500"
                  />
                  Include
                </label>
              </div>
              {form.phq9Score !== null && (
                <div>
                  <input
                    type="range"
                    min={0}
                    max={27}
                    value={form.phq9Score}
                    onChange={(e) => setForm({ ...form, phq9Score: Number(e.target.value) })}
                    className="w-full accent-indigo-500"
                  />
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-xs text-slate-500">0 (minimal)</span>
                    <span className="text-2xl font-bold text-indigo-400">{form.phq9Score}</span>
                    <span className="text-xs text-slate-500">27 (severe)</span>
                  </div>
                </div>
              )}
            </div>

            {/* GAD-7 */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="font-semibold text-sm text-slate-300">GAD-7 Anxiety Scale</h2>
                  <p className="text-xs text-slate-600 mt-0.5">0–21 · Mild ≥5, Moderate ≥10, Severe ≥15</p>
                </div>
                <label className="flex items-center gap-2 text-xs text-slate-500 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.gad7Score !== null}
                    onChange={(e) => setForm({ ...form, gad7Score: e.target.checked ? 0 : null })}
                    className="accent-indigo-500"
                  />
                  Include
                </label>
              </div>
              {form.gad7Score !== null && (
                <div>
                  <input
                    type="range"
                    min={0}
                    max={21}
                    value={form.gad7Score}
                    onChange={(e) => setForm({ ...form, gad7Score: Number(e.target.value) })}
                    className="w-full accent-indigo-500"
                  />
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-xs text-slate-500">0 (minimal)</span>
                    <span className="text-2xl font-bold text-violet-400">{form.gad7Score}</span>
                    <span className="text-xs text-slate-500">21 (severe)</span>
                  </div>
                </div>
              )}
            </div>

            {/* C-SSRS */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="font-semibold text-sm text-slate-300">C-SSRS Safety Assessment</h2>
                  <p className="text-xs text-slate-600 mt-0.5">Columbia Suicide Severity Rating Scale</p>
                </div>
                <label className="flex items-center gap-2 text-xs text-slate-500 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.cssrsAvailable}
                    onChange={(e) => setForm({ ...form, cssrsAvailable: e.target.checked, ideationPresent: false, behaviorPresent: false, ideationIntensity: null })}
                    className="accent-indigo-500"
                  />
                  C-SSRS administered
                </label>
              </div>
              {form.cssrsAvailable && (
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      id="ideation"
                      checked={form.ideationPresent}
                      onChange={(e) => setForm({ ...form, ideationPresent: e.target.checked, ideationIntensity: e.target.checked ? (form.ideationIntensity ?? 0) : null })}
                      className="accent-indigo-500"
                    />
                    <label htmlFor="ideation" className="text-sm text-slate-300">Suicidal ideation present</label>
                  </div>
                  {form.ideationPresent && (
                    <div>
                      <p className="text-xs text-slate-500 mb-2">Ideation intensity (0–5)</p>
                      <input
                        type="range"
                        min={0}
                        max={5}
                        value={form.ideationIntensity ?? 0}
                        onChange={(e) => setForm({ ...form, ideationIntensity: Number(e.target.value) })}
                        className="w-full accent-orange-500"
                      />
                      <div className="flex justify-between mt-1">
                        <span className="text-xs text-slate-600">0 (low)</span>
                        <span className="text-lg font-bold text-orange-400">{form.ideationIntensity ?? 0}</span>
                        <span className="text-xs text-slate-600">5 (high)</span>
                      </div>
                    </div>
                  )}
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      id="behavior"
                      checked={form.behaviorPresent}
                      onChange={(e) => setForm({ ...form, behaviorPresent: e.target.checked })}
                      className="accent-red-500"
                    />
                    <label htmlFor="behavior" className="text-sm text-red-400 font-medium">
                      Suicidal behavior present
                    </label>
                  </div>
                  {form.behaviorPresent && (
                    <div className="bg-red-950 border border-red-800 rounded-lg px-3 py-2">
                      <p className="text-red-300 text-xs font-medium">
                        ⚠ C-SSRS behavior present will escalate overall risk to ACUTE.
                        Immediate clinical action is required.
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Care engagement */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h2 className="font-semibold text-sm text-slate-300 mb-4">Care Engagement</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-xs text-slate-500 mb-1">Days since last contact (optional)</label>
                  <input
                    type="number"
                    min={0}
                    placeholder="e.g., 12"
                    value={form.daysSinceContact ?? ""}
                    onChange={(e) => setForm({ ...form, daysSinceContact: e.target.value ? Number(e.target.value) : null })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-500 mb-2">
                    Appointment adherence rate: {form.adherenceRate !== null ? `${Math.round(form.adherenceRate * 100)}%` : "—"}
                  </label>
                  <input
                    type="range"
                    min={0}
                    max={100}
                    value={form.adherenceRate !== null ? form.adherenceRate * 100 : 100}
                    onChange={(e) => setForm({ ...form, adherenceRate: Number(e.target.value) / 100 })}
                    className="w-full accent-indigo-500"
                  />
                  <div className="flex justify-between text-xs text-slate-600 mt-1">
                    <span>0%</span>
                    <span>Low threshold: 60%</span>
                    <span>100%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-lg font-medium transition-colors"
              >
                Compute Risk Profile
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="border border-slate-700 hover:border-slate-500 text-slate-400 px-5 py-3 rounded-lg transition-colors"
              >
                Reset
              </button>
            </div>
          </form>

          {/* Results panel */}
          <div>
            {!result ? (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-600 h-full flex flex-col items-center justify-center">
                <div className="text-4xl mb-4 text-slate-800">◎</div>
                <p className="text-sm">Enter assessment data and submit to compute a risk profile.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Overall risk */}
                <div className={`bg-slate-900 border-2 ${RISK_BORDER[result.overall_risk_level]} rounded-xl p-6`}>
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Overall Risk Level</p>
                      <span
                        className={`px-3 py-1.5 rounded-full text-sm font-bold uppercase tracking-wide ${
                          RISK_COLORS[result.overall_risk_level]
                        }`}
                      >
                        {result.overall_risk_level}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Priority Score</p>
                      <p className="text-3xl font-bold text-white">{result.priority_score}</p>
                    </div>
                  </div>

                  <div className="border-t border-slate-800 pt-4">
                    <p className="text-xs text-slate-500 mb-1">Recommended Action</p>
                    <p className="text-indigo-400 font-semibold text-sm">
                      {ACTION_LABELS[result.recommended_action] ?? result.recommended_action}
                    </p>
                  </div>

                  {result.requires_override_review && (
                    <div className="mt-4 bg-red-950 border border-red-800 rounded-lg px-3 py-2">
                      <p className="text-red-300 text-xs font-medium">
                        ⚠ Acute risk — mandatory clinician override review required before any automated action.
                      </p>
                    </div>
                  )}
                </div>

                {/* Risk dimensions */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                  <h3 className="font-semibold text-sm text-slate-300 mb-4">Risk Dimensions</h3>
                  <div className="space-y-4">
                    {result.risk_dimensions.map((dim) => (
                      <div key={dim.dimension}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-slate-300">
                            {DIMENSION_LABELS[dim.dimension] ?? dim.dimension}
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded-full text-xs font-semibold uppercase ${
                              RISK_COLORS[dim.level]
                            }`}
                          >
                            {dim.level}
                          </span>
                        </div>
                        <div className="h-1.5 bg-slate-800 rounded-full mb-2">
                          <div
                            className={`h-1.5 rounded-full ${
                              dim.level === "acute" ? "bg-red-500" :
                              dim.level === "high" ? "bg-orange-500" :
                              dim.level === "moderate" ? "bg-yellow-500" : "bg-emerald-500"
                            }`}
                            style={{ width: `${dim.score * 100}%` }}
                          />
                        </div>
                        {dim.contributing_signals.map((signal, i) => (
                          <p key={i} className="text-xs text-slate-500">{signal}</p>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Override */}
                {!overridden ? (
                  <button
                    onClick={() => setOverridden(true)}
                    className="w-full text-sm border border-slate-700 hover:border-slate-500 text-slate-400 hover:text-slate-200 py-3 rounded-xl transition-colors"
                  >
                    Override Assessment
                  </button>
                ) : (
                  <div className="bg-slate-900 border border-indigo-700 rounded-xl p-4">
                    <p className="text-sm text-indigo-300 font-medium mb-1">Override recorded</p>
                    <p className="text-xs text-slate-500">
                      Clinical override logged with clinician attribution. The AI assessment remains in the audit record.
                    </p>
                  </div>
                )}

                <p className="text-xs text-slate-600 text-center">
                  Computed at {new Date(result.computed_at).toLocaleTimeString()} ·
                  All AI outputs are advisory · Clinical judgment required
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
