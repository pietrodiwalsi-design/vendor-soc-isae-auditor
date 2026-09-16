from typing import Dict, Any

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
                "action_required": "Demand Management Response & Remediation Plan" if exceptions > 0 else "Acceptable under DORA Article 28"
            }
        }
