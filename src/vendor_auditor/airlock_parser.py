import re
from typing import Dict, Any, List

class AirlockParser:
    """Tier 1 Local Air-Lock Extraction: Isolates Section I, Section IV exceptions, and CUECs."""

    def extract_critical_sections(self, raw_text: str) -> Dict[str, Any]:
        # Auditor opinion check
        is_unqualified = bool(re.search(r"\b(present fairly|unqualified opinion|in all material respects)\b", raw_text, re.IGNORECASE))
        has_qualification = bool(re.search(r"\b(except for|qualified opinion|adverse opinion)\b", raw_text, re.IGNORECASE))
        
        opinion = "QUALIFIED" if has_qualification else "UNQUALIFIED" if is_unqualified else "UNCONFIRMED"

        # Carve-out vs Inclusive method
        is_carveout = bool(re.search(r"\b(carve-out method|subservice organizations are excluded)\b", raw_text, re.IGNORECASE))

        # Exceptions & Deviations
        exceptions = []
        for line in raw_text.splitlines():
            if re.search(r"\b(deviation|exception noted|control failure|sample size mismatch)\b", line, re.IGNORECASE):
                exceptions.append(line.strip())

        # CUECs / CSOCs
        cuecs = []
        for line in raw_text.splitlines():
            if re.search(r"\b(complementary user entity control|cuec|user organization is responsible)\b", line, re.IGNORECASE):
                cuecs.append(line.strip())

        return {
            "section_1_opinion": opinion,
            "subservice_method": "CARVE_OUT" if is_carveout else "INCLUSIVE",
            "section_4_exceptions_count": len(exceptions),
            "exceptions_sample": exceptions[:5],
            "cuec_count": len(cuecs),
            "cuecs_sample": cuecs[:5]
        }
