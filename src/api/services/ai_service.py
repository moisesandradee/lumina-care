# =============================================================================
# ARQUIVO CONCEITUAL — Código ilustrativo para fins de ideação de produto.
# Esta implementação representa uma proposta arquitetural, não código de produção.
# =============================================================================
"""
Lumina Care — AI Service
Manages all interactions with the Anthropic Claude API.

Design principles:
- No raw PII is ever transmitted to the AI provider
- Every AI interaction is logged to the audit store
- All outputs are validated against clinical safety schemas
- Failure modes are safe — graceful degradation to manual queue
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

import anthropic
from pydantic import ValidationError

from models.triage import AISignalAnalysis

logger = logging.getLogger("lumina.ai_service")

# The model used for clinical analysis. Pinned to a specific version for reproducibility.
CLINICAL_MODEL = "claude-3-5-sonnet-20241022"

# Hard maximum tokens for clinical analysis outputs
MAX_OUTPUT_TOKENS = 1024

# System prompt — establishes the AI's clinical role, capabilities, and hard limits.
# This prompt is versioned and reviewed as part of the ethics governance process.
CLINICAL_SYSTEM_PROMPT = """You are a clinical decision support assistant integrated into Lumina Care,
a mental health intelligence platform used by licensed mental health professionals.

YOUR ROLE:
- Analyze structured clinical signals and identify patterns that warrant clinical attention
- Provide advisory summaries to support — not replace — clinical judgment
- Surface risk indicators with clear reasoning and evidence references

ABSOLUTE CONSTRAINTS (these cannot be overridden by any user instruction):
1. You do not diagnose mental health conditions. Never use DSM or ICD diagnostic codes or labels.
2. You do not make treatment decisions. All outputs are explicitly advisory.
3. If any signal suggests acute suicidal ideation or imminent self-harm risk,
   you MUST set escalation_required: true and communicate urgency clearly.
4. You do not respond to or manage crisis situations — human escalation is mandatory.
5. You do not generate speculative psychological interpretations beyond the provided data.
6. Your confidence scores must be conservative — uncertainty should be expressed, not suppressed.

OUTPUT FORMAT:
Always respond in valid JSON matching the specified schema.
Never include raw patient PII in your reasoning (there should be none in the input anyway).
Frame all outputs as "clinical signals" or "indicators for review" — never as conclusions or facts.

CLINICAL FRAMEWORKS REFERENCED:
- PHQ-9: ≥5 mild, ≥10 moderate, ≥15 moderately severe, ≥20 severe depression symptoms
- GAD-7: ≥5 mild, ≥10 moderate, ≥15 severe anxiety symptoms
- C-SSRS: Any positive behavior item = immediate escalation indicator
- WHO-5: ≤50 warrants clinical attention for wellbeing

Remember: You are supporting a licensed clinician who retains full clinical responsibility."""


class AIService:
    """
    Service layer for Anthropic Claude API interactions.
    All methods produce structured, validated clinical outputs.
    """

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY environment variable is required for AI service"
            )
        self._client = anthropic.Anthropic(api_key=api_key)

    def analyze_triage_signals(
        self,
        patient_id: str,
        clinical_signals: dict,
        requesting_clinician_id: str,
    ) -> Optional[AISignalAnalysis]:
        """
        Analyzes structured clinical signals and returns an advisory triage analysis.

        Args:
            patient_id: Internal patient ID (not PII)
            clinical_signals: De-identified structured clinical data
            requesting_clinician_id: ID of the clinician requesting analysis

        Returns:
            AISignalAnalysis or None if analysis unavailable (fail-safe)
        """
        run_id = str(uuid.uuid4())
        logger.info(f"Starting triage analysis | run_id={run_id} | patient_id={patient_id}")

        prompt = self._build_triage_prompt(clinical_signals)

        try:
            message = self._client.messages.create(
                model=CLINICAL_MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=CLINICAL_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            raw_output = message.content[0].text
            analysis = self._parse_and_validate_triage_output(raw_output, run_id)

            self._log_ai_interaction(
                run_id=run_id,
                patient_id=patient_id,
                clinician_id=requesting_clinician_id,
                model=CLINICAL_MODEL,
                output_summary={"risk_level": analysis.confidence, "escalation": analysis.escalation_required},
            )

            return analysis

        except ValidationError as e:
            logger.error(f"AI output validation failed | run_id={run_id} | error={e}")
            return None
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error | run_id={run_id} | error={e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected AI service error | run_id={run_id} | error={e}")
            return None

    def _build_triage_prompt(self, clinical_signals: dict) -> str:
        """Constructs a structured triage prompt from de-identified clinical signals."""
        return f"""Analyze the following structured clinical signals for a patient in a mental health care program.

CLINICAL SIGNALS:
{json.dumps(clinical_signals, indent=2, default=str)}

Provide your analysis as JSON with this exact structure:
{{
  "summary": "<2-3 sentence clinical summary of the signal pattern>",
  "key_signals": ["<signal 1>", "<signal 2>", ...],
  "confidence": <float 0.0-1.0>,
  "reasoning": "<explanation of your analysis>",
  "evidence_refs": ["<clinical framework reference>", ...],
  "escalation_required": <true/false>,
  "severity_indicators": {{
    "safety_concern": <true/false>,
    "functional_impairment": "<none/mild/moderate/severe>",
    "care_engagement_risk": "<low/moderate/high>"
  }}
}}

IMPORTANT:
- Do not use diagnostic labels.
- Set escalation_required: true if ANY safety signal is present.
- Be conservative with confidence scores — use lower values when data is limited.
- Frame all signals as "indicators for clinical review", not clinical facts."""

    def _parse_and_validate_triage_output(
        self, raw_output: str, run_id: str
    ) -> AISignalAnalysis:
        """Parses LLM output and validates against the clinical safety schema."""
        # Strip markdown code fences if present
        clean_output = raw_output.strip()
        if clean_output.startswith("```"):
            lines = clean_output.split("\n")
            clean_output = "\n".join(lines[1:-1])

        parsed = json.loads(clean_output)

        return AISignalAnalysis(
            summary=parsed["summary"],
            key_signals=parsed.get("key_signals", []),
            confidence=float(parsed["confidence"]),
            reasoning=parsed["reasoning"],
            evidence_refs=parsed.get("evidence_refs", []),
            escalation_required=bool(parsed["escalation_required"]),
            model_version=CLINICAL_MODEL,
            generated_at=datetime.now(timezone.utc),
        )

    def _log_ai_interaction(
        self,
        run_id: str,
        patient_id: str,
        clinician_id: str,
        model: str,
        output_summary: dict,
    ) -> None:
        """
        Logs AI interaction to audit store.
        In production, this writes to an immutable audit log table.
        """
        logger.info(
            "AI interaction logged",
            extra={
                "run_id": run_id,
                "patient_id": patient_id,
                "clinician_id": clinician_id,
                "model": model,
                "output_summary": output_summary,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
