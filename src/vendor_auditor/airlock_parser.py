import re
from typing import Dict, Any, List

class AirlockParser:
    """Tier 1 Local Air-Lock Extraction: Isolates Section I, Section IV exceptions, and CUECs."""

    # FIX 4 (2026-09-18 review): broadened beyond a single report-house's
    # boilerplate to cover at least three distinct styles: (1) AICPA SOC 2
    # Type II phrasing, (2) ISAE 3402 / IAASB international phrasing, and
    # (3) common alternate auditor-firm phrasing ("unmodified opinion",
    # short-form "Opinion: QUALIFIED" style headers, etc.). Same content in
    # different report-house formatting must now yield the same
    # exception/CUEC counts (see test_multi_format_recognition).
    #
    # Precompiled once at class load; bounded backtracking-free (no nested quantifiers) so this is
    # safe against ReDoS even on very large SOC report texts.
    _RE_UNQUALIFIED = re.compile(
        r"\b(present fairly|unqualified opinion|in all material respects|"
        r"unmodified opinion|opinion:\s*unqualified|opinion:\s*unmodified)\b",
        re.IGNORECASE,
    )
    _RE_QUALIFIED = re.compile(
        r"\b(except for|qualified opinion|adverse opinion|disclaimer of opinion|"
        r"opinion:\s*qualified|opinion:\s*adverse|opinion:\s*disclaimer)\b",
        re.IGNORECASE,
    )
    _RE_CARVEOUT = re.compile(
        r"\b(carve-out method|carve out method|subservice organizations are excluded|"
        r"subservice organisations are excluded|complementary subservice organization controls\s*\(cs?soc\))\b",
        re.IGNORECASE,
    )
    _RE_INCLUSIVE = re.compile(
        r"\b(inclusive method|subservice organizations are included|"
        r"subservice organisations are included)\b",
        re.IGNORECASE,
    )
    _RE_EXCEPTION_LINE = re.compile(
        r"\b(deviation|exception noted|control failure|sample size mismatch|"
        r"exceptions? identified|non[- ]conformity|nonconformity|test result:\s*fail(ed)?|"
        r"finding\s*#?\d*\s*[:\-]|control gap)\b",
        re.IGNORECASE,
    )
    _RE_CUEC_LINE = re.compile(
        r"\b(complementary user entity control|cuec|user organization is responsible|"
        r"user organisation is responsible|user entity control|"
        r"user entity is responsible|complementary end[- ]user control)\b",
        re.IGNORECASE,
    )

    def extract_critical_sections(self, raw_text: str) -> Dict[str, Any]:
        if raw_text is None:
            raw_text = ""
        if not isinstance(raw_text, str):
            raise TypeError("raw_text must be a string")

        # FIX 2 (2026-09-18 review): fail-open scoring. Previously an opinion
        # that matched neither the QUALIFIED nor UNQUALIFIED boilerplate
        # patterns fell through to "UNCONFIRMED", which downstream scored as
        # LOW risk (score 2.0) — i.e. the LESS the parser understood, the
        # LOWER the reported risk. That is the most expensive failure mode
        # for a risk tool: a crash gets fixed, a reassuring wrong answer gets
        # filed. Now: if the extraction genuinely could not classify the
        # opinion, we return status="INSUFFICIENT_EXTRACTION" instead of a
        # score-bearing state, and record exactly what regex categories were
        # tried and matched so a silent empty extraction is visible (Stage 3).
        is_unqualified = bool(self._RE_UNQUALIFIED.search(raw_text))
        has_qualification = bool(self._RE_QUALIFIED.search(raw_text))

        if has_qualification:
            opinion = "QUALIFIED"
        elif is_unqualified:
            opinion = "UNQUALIFIED"
        else:
            opinion = "INSUFFICIENT_EXTRACTION"

        # Carve-out vs Inclusive method
        is_carveout = bool(self._RE_CARVEOUT.search(raw_text))
        is_inclusive_stated = bool(self._RE_INCLUSIVE.search(raw_text))
        if is_carveout:
            subservice_method = "CARVE_OUT"
        elif is_inclusive_stated:
            subservice_method = "INCLUSIVE"
        else:
            subservice_method = "INSUFFICIENT_EXTRACTION"

        # Exceptions & Deviations, CUECs / CSOCs (single pass over lines for performance)
        exceptions = []
        cuecs = []
        for line in raw_text.splitlines():
            if self._RE_EXCEPTION_LINE.search(line):
                exceptions.append(line.strip())
            if self._RE_CUEC_LINE.search(line):
                cuecs.append(line.strip())

        # FIX 3 (2026-09-18 review): make silence visible. A report with zero
        # extracted exceptions or CUECs looks IDENTICAL to a genuinely clean
        # report unless we say what was found/tried/matched. This is the
        # extraction_diagnostics block that stops an empty extraction from
        # looking like a clean audit.
        diagnostics = {
            "input_length_chars": len(raw_text),
            "input_line_count": raw_text.count("\n") + 1 if raw_text else 0,
            "opinion_patterns_tried": ["unqualified", "qualified"],
            "opinion_pattern_matched": (
                "qualified" if has_qualification else "unqualified" if is_unqualified else None
            ),
            "subservice_patterns_tried": ["carve_out", "inclusive"],
            "subservice_pattern_matched": (
                "carve_out" if is_carveout else "inclusive" if is_inclusive_stated else None
            ),
            "exception_lines_scanned": raw_text.count("\n") + 1 if raw_text else 0,
            "exception_lines_matched": len(exceptions),
            "cuec_lines_matched": len(cuecs),
            "low_confidence_extraction": (
                opinion == "INSUFFICIENT_EXTRACTION"
                or (len(raw_text) > 200 and len(exceptions) == 0 and len(cuecs) == 0)
            ),
        }

        return {
            "section_1_opinion": opinion,
            "subservice_method": subservice_method,
            "section_4_exceptions_count": len(exceptions),
            "exceptions_sample": exceptions[:5],
            "cuec_count": len(cuecs),
            "cuecs_sample": cuecs[:5],
            "extraction_diagnostics": diagnostics,
        }
