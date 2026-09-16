from typing import Dict, Any, List

class MultiYearTrendAnalyzer:
    """Tracks recurring exceptions and control degradation across multiple SOC 2 Type II audit years."""

    def compare_audit_periods(self, current_period: dict, prior_period: dict) -> Dict[str, Any]:
        current_period = current_period or {}
        prior_period = prior_period or {}
        if not isinstance(current_period, dict) or not isinstance(prior_period, dict):
            raise TypeError("current_period and prior_period must be dicts")
        curr_exc = current_period.get("section_4_exceptions_count", 0) or 0
        prior_exc = prior_period.get("section_4_exceptions_count", 0) or 0

        trend = "IMPROVING" if curr_exc < prior_exc else "DEGRADING" if curr_exc > prior_exc else "STABLE"
        
        return {
            "current_year_exceptions": curr_exc,
            "prior_year_exceptions": prior_exc,
            "trend_status": trend,
            "systemic_control_failure_warning": (curr_exc >= 3 and prior_exc >= 3),
            "dora_escalation_needed": (curr_exc > prior_exc and curr_exc >= 2)
        }
