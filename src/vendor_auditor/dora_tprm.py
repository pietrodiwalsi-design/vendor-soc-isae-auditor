from typing import Dict, Any

# FIX 6 (2026-09-18 review): the conclusion sentence must be a deterministic
# function of the risk_tier alone, via a fixed lookup table. Previously
# CRITICAL and MEDIUM cases could both surface "Acceptable under DORA
# Article 28" (the action_required text was derived only from
# exceptions > 0, completely independent of risk_tier/risk_score). A
# CRITICAL finding must never read as "Acceptable".
_ACTION_REQUIRED_BY_TIER = {
    "CRITICAL": "Escalate immediately: demand Management Response & Remediation Plan; consider DORA Art. 28 exit/contingency planning.",
    "HIGH": "Demand Management Response & Remediation Plan; re-test within 90 days.",
    "MEDIUM": "Demand Management Response & Remediation Plan; monitor at next scheduled review.",
    "LOW": "Acceptable under DORA Article 28; no immediate action required.",
    "INSUFFICIENT_EXTRACTION": "Do not conclude acceptability. Manual review required — automated extraction could not reliably classify the auditor opinion.",
}


class DORATPRMEvaluator:
    """Tier 3 Evaluator for DORA Article 28 (Third-Party ICT Risk)."""

    def evaluate_vendor_risk(self, airlock_data: Dict[str, Any]) -> Dict[str, Any]:
        airlock_data = airlock_data or {}
        if not isinstance(airlock_data, dict):
            raise TypeError("airlock_data must be a dict")
        opinion = airlock_data.get("section_1_opinion")
        exceptions = airlock_data.get("section_4_exceptions_count", 0) or 0
        if not isinstance(exceptions, (int, float)) or isinstance(exceptions, bool):
            exceptions = 0
        is_carveout = (airlock_data.get("subservice_method") == "CARVE_OUT")

        # FIX 2 (2026-09-18 review): fail-open scoring. An opinion the parser
        # could not classify (INSUFFICIENT_EXTRACTION, or missing/None) must
        # NEVER be treated as the LOW-risk baseline. It is reported as its
        # own explicit, non-scoreable state instead of a fabricated number.
        if opinion in (None, "INSUFFICIENT_EXTRACTION"):
            return {
                "dora_article_28_compliance": {
                    "auditor_opinion": opinion or "INSUFFICIENT_EXTRACTION",
                    "fourth_party_risk_identified": is_carveout,
                    "residual_tpm_risk_score": None,
                    "risk_tier": "INSUFFICIENT_EXTRACTION",
                    "action_required": _ACTION_REQUIRED_BY_TIER["INSUFFICIENT_EXTRACTION"],
                }
            }

        # Risk scoring
        risk_score = 2.0
        if opinion == "QUALIFIED":
            risk_score += 5.0
        if exceptions > 0:
            risk_score += min(exceptions * 0.8, 3.0)
        if is_carveout:
            risk_score += 1.0 # 4th party risk tracking required under DORA

        risk_tier = "CRITICAL" if risk_score >= 7.5 else "HIGH" if risk_score >= 5.0 else "MEDIUM" if risk_score >= 3.0 else "LOW"

        return {
            "dora_article_28_compliance": {
                "auditor_opinion": opinion,
                "fourth_party_risk_identified": is_carveout,
                "residual_tpm_risk_score": round(risk_score, 1),
                "risk_tier": risk_tier,
                "action_required": _ACTION_REQUIRED_BY_TIER[risk_tier],
            }
        }
