import re
from typing import Dict, Any, List

class AirlockParser:
    """Tier 1 Local Air-Lock Extraction: Isolates Section I, Section IV exceptions, and CUECs."""

    # Precompiled once at class load; bounded backtracking-free (no nested quantifiers) so this is
    # safe against ReDoS even on very large SOC report texts.
    _RE_UNQUALIFIED = re.compile(r"\b(present fairly|unqualified opinion|in all material respects)\b", re.IGNORECASE)
    _RE_QUALIFIED = re.compile(r"\b(except for|qualified opinion|adverse opinion)\b", re.IGNORECASE)
    _RE_CARVEOUT = re.compile(r"\b(carve-out method|subservice organizations are excluded)\b", re.IGNORECASE)
    _RE_EXCEPTION_LINE = re.compile(r"\b(deviation|exception noted|control failure|sample size mismatch)\b", re.IGNORECASE)
    _RE_CUEC_LINE = re.compile(r"\b(complementary user entity control|cuec|user organization is responsible)\b", re.IGNORECASE)

    def extract_critical_sections(self, raw_text: str) -> Dict[str, Any]:
        if raw_text is None:
            raw_text = ""
        if not isinstance(raw_text, str):
            raise TypeError("raw_text must be a string")

        # Auditor opinion check
        is_unqualified = bool(self._RE_UNQUALIFIED.search(raw_text))
        has_qualification = bool(self._RE_QUALIFIED.search(raw_text))
        
        opinion = "QUALIFIED" if has_qualification else "UNQUALIFIED" if is_unqualified else "UNCONFIRMED"

        # Carve-out vs Inclusive method
        is_carveout = bool(self._RE_CARVEOUT.search(raw_text))

        # Exceptions & Deviations, CUECs / CSOCs (single pass over lines for performance)
        exceptions = []
        cuecs = []
        for line in raw_text.splitlines():
            if self._RE_EXCEPTION_LINE.search(line):
                exceptions.append(line.strip())
            if self._RE_CUEC_LINE.search(line):
                cuecs.append(line.strip())

        return {
            "section_1_opinion": opinion,
            "subservice_method": "CARVE_OUT" if is_carveout else "INCLUSIVE",
            "section_4_exceptions_count": len(exceptions),
            "exceptions_sample": exceptions[:5],
            "cuec_count": len(cuecs),
            "cuecs_sample": cuecs[:5]
        }
