// =============================================================================
// ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
// Esta implementação representa uma proposta arquitetural, não código de produção.
// =============================================================================
"use client";

import { useState } from "react";
import Link from "next/link";

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const MOCK_QUEUE = [
  {
    id: "pat_001",
    risk: "high" as const,
    priorityScore: 87.5,
    signal: "PHQ-9 increased 8 points since last assessment",
    daysSinceContact: 12,
    action: "priority_contact",
    trend: "deteriorating" as const,
    trajectory: "acute_deterioration",
  },
  {
    id: "pat_007",
    risk: "moderate" as const,
    priorityScore: 54.2,
    signal: "Care gap: 19 days since last contact",
    daysSinceContact: 19,
    action: "enhanced_monitoring",
    trend: "stable" as const,
    trajectory: "stable_high",
  },
  {
    id: "pat_013",
    risk: "moderate" as const,
    priorityScore: 42.1,
    signal: "GAD-7 moderate range; appointment adherence 58%",
    daysSinceContact: 7,
    action: "enhanced_monitoring",
    trend: "stable" as const,
    trajectory: "fluctuating",
  },
  {
    id: "pat_022",
    risk: "low" as const,
    priorityScore: 18.0,
    signal: "Routine reassessment due",
    daysSinceContact: 10,
    action: "routine_follow_up",
    trend: "improving" as const,
    trajectory: "sustained_improvement",
  },
];

const MOCK_ALERTS = [
  {
    id: "a1",
    patientId: "pat_001",
    type: "score_deterioration",
    severity: "urgent" as const,
    title: "PHQ-9 deterioration — 8 point increase",
    description: "PHQ-9 increased from 6 to 14 (mild → moderate). MCID threshold crossed.",
    triggered: "2h ago",
  },
  {
    id: "a2",
    patientId: "pat_007",
    type: "care_gap",
    severity: "warning" as const,
    title: "Care gap: 19 days without contact",
    description: "Exceeds 14-day warning threshold.",
    triggered: "1d ago",
  },
  {
    id: "a3",
    patientId: "pat_019",
    type: "digital_checkin_concern",
    severity: "warning" as const,
    title: "Check-in: WHO-5 low wellbeing (32%)",
    description: "WHO-5 score below clinical threshold. Low mood and poor sleep reported.",
    triggered: "6h ago",
  },
  {
    id: "a4",
    patientId: "pat_031",
    type: "assessment_due",
    severity: "info" as const,
    title: "PHQ-9 reassessment overdue (42 days)",
    description: "Monthly reassessment target exceeded.",
    triggered: "3d ago",
  },
];

const TRAJECTORY_DISTRIBUTION = [
  { label: "Sustained Improvement", count: 8, color: "bg-emerald-500" },
  { label: "Stable (subclinical)",  count: 13, color: "bg-emerald-700" },
  { label: "Fluctuating",           count: 9,  color: "bg-yellow-500" },
  { label: "Stable (elevated)",     count: 4,  color: "bg-orange-500" },
  { label: "Deteriorating",         count: 2,  color: "bg-red-500" },
  { label: "Acute Deterioration",   count: 1,  color: "bg-red-600" },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

type RiskLevel = "acute" | "high" | "moderate" | "low";
type Trend = "deteriorating" | "stable" | "improving";
type AlertSeverity = "urgent" | "warning" | "info" | "critical";

const RISK_COLORS: Record<RiskLevel, string> = {
  acute: "bg-red-500 text-white",
  high: "bg-orange-500 text-white",
  moderate: "bg-yellow-500 text-slate-900",
  low: "bg-emerald-500 text-white",
};

const TREND_ICONS: Record<Trend, string> = {
  deteriorating: "↑",
  stable: "→",
  improving: "↓",
};

const TREND_COLORS: Record<Trend, string> = {
  deteriorating: "text-red-400",
  stable: "text-slate-400",
  improving: "text-emerald-400",
};

const ACTION_LABELS: Record<string, string> = {
  immediate_escalation: "Immediate Escalation",
  urgent_clinical_review: "Urgent Clinical Review",
  priority_contact: "Priority Contact",
  enhanced_monitoring: "Enhanced Monitoring",
  routine_follow_up: "Routine Follow-up",
};

const ALERT_SEVERITY_STYLES: Record<AlertSeverity, string> = {
  urgent: "border-l-orange-500 bg-orange-950/30",
  warning: "border-l-yellow-500 bg-yellow-950/30",
  info: "border-l-slate-500 bg-slate-800/30",
  critical: "border-l-red-500 bg-red-950/30",
};

const ALERT_SEVERITY_LABEL: Record<AlertSeverity, string> = {
  urgent: "text-orange-400",
  warning: "text-yellow-400",
  info: "text-slate-400",
  critical: "text-red-400",
};

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function DashboardPage() {
  const [overriddenIds, setOverriddenIds] = useState<Set<string>>(new Set());
  const [acknowledgedAlerts, setAcknowledgedAlerts] = useState<Set<string>>(new Set());
  const [activeTab, setActiveTab] = useState<"queue" | "trajectories" | "coverage">("queue");

  const teamStats = {
    activePatients: 38,
    highUrgency: 5,      // HIGH + ACUTE
    careGaps: 3,
    avgDaysSinceContact: 9.2,
    openAlerts: MOCK_ALERTS.length,
    urgentAlerts: MOCK_ALERTS.filter((a) => a.severity === "urgent").length,
  };

  const openAlerts = MOCK_ALERTS.filter((a) => !acknowledgedAlerts.has(a.id));

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
        <div className="flex items-center gap-4">
          <Link
            href="/triage"
            className="text-sm bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg transition-colors"
          >
            + New Triage
          </Link>
          <div className="flex items-center gap-2 text-sm text-slate-400">
            {teamStats.urgentAlerts > 0 && (
              <span className="bg-orange-600 text-white text-xs px-2 py-0.5 rounded-full font-medium">
                {teamStats.urgentAlerts} urgent
              </span>
            )}
            <span>Dr. Beatriz Tavares</span>
            <div className="w-8 h-8 rounded-full bg-indigo-700 flex items-center justify-center text-xs font-medium">
              BT
            </div>
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
        <div className="grid grid-cols-6 gap-4 mb-8">
          {[
            { label: "Active Patients",        value: teamStats.activePatients,      color: "text-white",       sub: null },
            { label: "High + Acute Urgency",   value: teamStats.highUrgency,         color: "text-orange-400",  sub: null },
            { label: "Critical Care Gaps",     value: teamStats.careGaps,            color: "text-red-400",     sub: null },
            { label: "Avg Days Since Contact", value: teamStats.avgDaysSinceContact, color: "text-slate-300",   sub: null },
            { label: "Open Alerts",            value: openAlerts.length,             color: "text-yellow-400",  sub: null },
            { label: "Assessment Coverage",    value: "84%",                          color: "text-emerald-400", sub: "PHQ-9 / 30d" },
          ].map((stat) => (
            <div key={stat.label} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <p className="text-slate-500 text-xs uppercase tracking-wide mb-1">{stat.label}</p>
              <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
              {stat.sub && <p className="text-xs text-slate-600 mt-0.5">{stat.sub}</p>}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Main panel: queue / trajectories / coverage tabs */}
          <div className="col-span-2 space-y-6">

            {/* Tab nav */}
            <div className="flex gap-1 bg-slate-900 border border-slate-800 rounded-xl p-1">
              {(["queue", "trajectories", "coverage"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex-1 text-sm py-2 rounded-lg transition-colors font-medium ${
                    activeTab === tab
                      ? "bg-indigo-600 text-white"
                      : "text-slate-500 hover:text-slate-300"
                  }`}
                >
                  {tab === "queue" ? "Priority Queue" : tab === "trajectories" ? "Trajectory Distribution" : "Assessment Coverage"}
                </button>
              ))}
            </div>

            {/* Priority Queue */}
            {activeTab === "queue" && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl">
                <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
                  <div>
                    <h2 className="font-semibold">Priority Queue</h2>
                    <p className="text-slate-500 text-sm mt-0.5">Ordered by risk score · Updated 4 minutes ago</p>
                  </div>
                  <button className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
                    Refresh
                  </button>
                </div>
                <div className="divide-y divide-slate-800">
                  {MOCK_QUEUE.map((patient) => (
                    <div key={patient.id} className="px-6 py-4 hover:bg-slate-800/50 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <span
                            className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wide ${
                              RISK_COLORS[patient.risk]
                            }`}
                          >
                            {patient.risk}
                          </span>
                          <div>
                            <div className="flex items-center gap-2">
                              <Link
                                href={`/patients/${patient.id}`}
                                className="font-medium text-sm font-mono text-indigo-400 hover:text-indigo-300 transition-colors"
                              >
                                {patient.id}
                              </Link>
                              <span
                                className={`text-sm ${TREND_COLORS[patient.trend]}`}
                                title={`Trend: ${patient.trend}`}
                              >
                                {TREND_ICONS[patient.trend]}
                              </span>
                              <span className="text-xs text-slate-600 bg-slate-800 px-1.5 py-0.5 rounded">
                                {patient.trajectory.replace(/_/g, " ")}
                              </span>
                            </div>
                            <p className="text-slate-400 text-sm mt-0.5">{patient.signal}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-5 text-sm">
                          <div className="text-right">
                            <p className="text-slate-500 text-xs">Days</p>
                            <p className={`font-medium ${patient.daysSinceContact > 14 ? "text-orange-400" : "text-slate-300"}`}>
                              {patient.daysSinceContact}d
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-slate-500 text-xs">Score</p>
                            <p className="font-medium text-slate-300">{patient.priorityScore}</p>
                          </div>
                          <div className="text-right min-w-[110px]">
                            <p className="text-slate-500 text-xs">Action</p>
                            <p className="text-indigo-400 text-xs font-medium">{ACTION_LABELS[patient.action]}</p>
                          </div>
                          {overriddenIds.has(patient.id) ? (
                            <span className="text-xs text-slate-500 italic">Overridden</span>
                          ) : (
                            <button
                              onClick={() => setOverriddenIds((prev) => new Set([...prev, patient.id]))}
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
            )}

            {/* Trajectory distribution */}
            {activeTab === "trajectories" && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                <h2 className="font-semibold mb-1">Symptom Trajectory Distribution</h2>
                <p className="text-slate-500 text-sm mb-5">
                  How patients' symptom scores are moving over time · Total panel: 38 patients
                </p>
                <div className="space-y-4">
                  {TRAJECTORY_DISTRIBUTION.map((item) => (
                    <div key={item.label} className="flex items-center gap-4">
                      <span className="text-sm text-slate-400 w-44">{item.label}</span>
                      <div className="flex-1 bg-slate-800 rounded-full h-2">
                        <div
                          className={`${item.color} h-2 rounded-full`}
                          style={{ width: `${(item.count / 38) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm text-slate-400 w-6 text-right">{item.count}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-6 bg-slate-800/50 rounded-lg p-4">
                  <p className="text-xs text-slate-400">
                    <span className="text-orange-400 font-medium">1 patient</span> with acute deterioration trajectory —
                    PHQ-9 jump ≥5 points in the last 1–2 assessments. Requires urgent review.
                  </p>
                </div>
              </div>
            )}

            {/* Assessment coverage */}
            {activeTab === "coverage" && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                <h2 className="font-semibold mb-1">Assessment Coverage</h2>
                <p className="text-slate-500 text-sm mb-5">
                  Proportion of patients assessed per instrument in the last 30 days
                </p>
                <div className="space-y-5">
                  {[
                    { label: "PHQ-9",             assessed: 32, total: 38, target: 80 },
                    { label: "GAD-7",             assessed: 30, total: 38, target: 80 },
                    { label: "C-SSRS",            assessed: 35, total: 38, target: 90 },
                    { label: "WHO-5 (digital)",   assessed: 28, total: 38, target: 70 },
                  ].map((item) => {
                    const pct = Math.round((item.assessed / item.total) * 100);
                    const met = pct >= item.target;
                    return (
                      <div key={item.label}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-slate-300">{item.label}</span>
                          <div className="flex items-center gap-2">
                            <span className={`text-xs font-medium ${met ? "text-emerald-400" : "text-yellow-400"}`}>
                              {pct}%
                            </span>
                            {met
                              ? <span className="text-xs text-emerald-600">✓ target met</span>
                              : <span className="text-xs text-yellow-600">target: {item.target}%</span>
                            }
                          </div>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full">
                          <div
                            className={`h-2 rounded-full ${met ? "bg-emerald-500" : "bg-yellow-500"}`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <p className="text-xs text-slate-600 mt-1">{item.assessed}/{item.total} patients assessed</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Risk + Care continuity row */}
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                <h3 className="font-semibold mb-4">Risk Distribution</h3>
                <div className="space-y-3">
                  {[
                    { label: "Low",      count: 21, total: 38, color: "bg-emerald-500" },
                    { label: "Moderate", count: 12, total: 38, color: "bg-yellow-500" },
                    { label: "High",     count: 4,  total: 38, color: "bg-orange-500" },
                    { label: "Acute",    count: 1,  total: 38, color: "bg-red-500" },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center gap-3">
                      <span className="text-sm text-slate-400 w-20">{item.label}</span>
                      <div className="flex-1 bg-slate-800 rounded-full h-2">
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
                    { label: "Within care plan",     value: "76%",  color: "text-emerald-400" },
                    { label: "Gap warning (>14d)",   value: "16%",  color: "text-yellow-400" },
                    { label: "Critical gap (>21d)",  value: "8%",   color: "text-red-400" },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between">
                      <span className="text-sm text-slate-400">{item.label}</span>
                      <span className={`font-semibold ${item.color}`}>{item.value}</span>
                    </div>
                  ))}
                  <div className="border-t border-slate-800 pt-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-400">Digital check-in engagement</span>
                      <span className="font-semibold text-slate-300">74%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right column: alerts */}
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl">
              <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <h2 className="font-semibold text-sm">Active Alerts</h2>
                  <p className="text-slate-500 text-xs mt-0.5">{openAlerts.length} open</p>
                </div>
                <Link href="#" className="text-xs text-indigo-400 hover:text-indigo-300">
                  All alerts
                </Link>
              </div>

              {openAlerts.length === 0 ? (
                <div className="p-6 text-center">
                  <p className="text-emerald-400 text-sm font-medium">No open alerts</p>
                  <p className="text-slate-600 text-xs mt-1">All care signals within expected parameters.</p>
                </div>
              ) : (
                <div className="p-3 space-y-2 max-h-[600px] overflow-y-auto">
                  {openAlerts.map((alert) => (
                    <div
                      key={alert.id}
                      className={`border-l-2 rounded-r-lg p-3 ${ALERT_SEVERITY_STYLES[alert.severity]}`}
                    >
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <div>
                          <p className={`text-xs font-semibold uppercase tracking-wide ${ALERT_SEVERITY_LABEL[alert.severity]}`}>
                            {alert.severity} · {alert.triggered}
                          </p>
                          <p className="text-xs font-medium text-slate-200 mt-0.5">{alert.title}</p>
                          <Link
                            href={`/patients/${alert.patientId}`}
                            className="text-xs text-indigo-400 hover:text-indigo-300 font-mono"
                          >
                            {alert.patientId} →
                          </Link>
                        </div>
                      </div>
                      <p className="text-xs text-slate-500 mb-2">{alert.description}</p>
                      <button
                        onClick={() => setAcknowledgedAlerts((p) => new Set([...p, alert.id]))}
                        className="text-xs text-slate-500 hover:text-slate-300 border border-slate-700 hover:border-slate-500 px-2 py-1 rounded transition-colors w-full"
                      >
                        Acknowledge
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Quick actions */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h3 className="font-semibold text-sm mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <Link
                  href="/triage"
                  className="flex items-center justify-between w-full text-sm text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-4 py-3 rounded-lg transition-colors"
                >
                  <span>Run triage assessment</span>
                  <span className="text-slate-500">→</span>
                </Link>
                <button className="flex items-center justify-between w-full text-sm text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-4 py-3 rounded-lg transition-colors">
                  <span>View team summary</span>
                  <span className="text-slate-500">→</span>
                </button>
                <button className="flex items-center justify-between w-full text-sm text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-4 py-3 rounded-lg transition-colors">
                  <span>Population cohort analytics</span>
                  <span className="text-slate-500">→</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
