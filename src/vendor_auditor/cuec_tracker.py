from typing import Dict, Any, List

# FIX 5 (2026-09-18 review): stopwords widened beyond the original tiny
# list. The original list ("the","via","and","for","with","must") let broad,
# semantically empty nouns like "data", "policy", "system", "user" act as
# matches on their own — which is exactly how "Data classification policy"
# false-matched a CUEC about "data validation": both merely contain "data".
_STOPWORDS = {
    "the", "via", "and", "for", "with", "must", "is", "are", "be", "to", "of",
    "in", "on", "by", "as", "or", "that", "this", "a", "an", "it", "will",
    "data", "policy", "policies", "system", "systems", "user", "users",
    "control", "controls", "process", "processes", "management", "organization",
    "entity", "entities", "responsible", "maintained", "required", "review",
    "reviewed", "quarterly", "annually", "periodically",
}


class CUECTracker:
    """Tracks Complementary User Entity Controls (CUECs) and assigns internal accountability."""

    def analyze_cuec_gaps(self, extracted_cuecs: List[str], implemented_internal_controls: List[str]) -> Dict[str, Any]:
        extracted_cuecs = extracted_cuecs or []
        implemented_internal_controls = implemented_internal_controls or []
        if not isinstance(extracted_cuecs, list) or not isinstance(implemented_internal_controls, list):
            raise TypeError("extracted_cuecs and implemented_internal_controls must be lists")

        cuec_items = []
        gap_count = 0
        partial_count = 0

        # Build a per-control list of significant (non-stopword) terms,
        # KEEPING them grouped by control so we can require multiple
        # distinct term matches instead of a single incidental word overlap.
        control_term_sets = []
        for ic in implemented_internal_controls:
            terms = {
                w for w in ic.lower().split()
                if len(w) >= 3 and w not in _STOPWORDS
            }
            if terms:
                control_term_sets.append(terms)

        for idx, cuec_text in enumerate(extracted_cuecs, 1):
            cuec_terms = {
                w.strip(".,;:()") for w in cuec_text.lower().split()
                if len(w.strip(".,;:()")) >= 3 and w.strip(".,;:()") not in _STOPWORDS
            }

            best_overlap = 0
            for terms in control_term_sets:
                overlap = len(cuec_terms & terms)
                best_overlap = max(best_overlap, overlap)

            # FIX 5: require >=2 distinct significant-term matches for a
            # full IMPLEMENTED claim (single-word overlap on generic nouns
            # was the root cause of the false positive in the review).
            # A single-term overlap is downgraded to PARTIAL — plausibly
            # related but not confidently verified — rather than silently
            # counted as full coverage.
            if best_overlap >= 2:
                status = "IMPLEMENTED"
            elif best_overlap == 1:
                status = "PARTIAL"
                partial_count += 1
            else:
                status = "GAP_ACTION_REQUIRED"
                gap_count += 1

            # FIX 5: assigned_owner must reflect the SUBJECT MATTER of the
            # CUEC, not merely mirror its computed status (previously every
            # "implemented" got "Internal Audit" and every "gap" got
            # "IT Risk / SecOps" regardless of topic — misleading in a real
            # register). Route by keyword topic first; fall back to a
          
            # status-based default only when no topic keyword is found, and
            # say so explicitly via '_owner_basis'.
            owner, owner_basis = _route_owner(cuec_text, status)

            cuec_items.append({
                "cuec_id": f"CUEC-{idx:02d}",
                "description": cuec_text,
                "status": status,
                "matched_term_count": best_overlap,
                "assigned_owner": owner,
                "assigned_owner_basis": owner_basis,
            })

        total = len(extracted_cuecs)
        fully_covered = total - gap_count - partial_count
        return {
            "total_cuecs_demanded_by_vendor": total,
            "internal_gaps_identified": gap_count,
            "internal_partial_coverage": partial_count,
            "cuec_compliance_pct": round((fully_covered / max(total, 1)) * 100, 1),
            "cuec_matrix": cuec_items,
            "matching_method": "keyword-overlap-heuristic-NOT-semantic",
            "matching_caveat": (
                "This is a deterministic keyword-overlap heuristic, not semantic "
                "matching. IMPLEMENTED/PARTIAL/GAP classifications should be "
                "reviewed by a human (or a downstream LLM given the full CUEC "
                "and control text) before being relied upon for an audit register."
            ),
        }


def _route_owner(cuec_text: str, status: str) -> tuple:
    """Route CUEC ownership by subject-matter keyword, not by status."""
    text = cuec_text.lower()
    topic_routes = [
        (("access", "mfa", "authentication", "password", "privileged"), "Identity & Access Management"),
        (("encrypt", "key management", "cryptograph"), "Security Engineering"),
        (("backup", "restoration", "disaster recovery", "continuity"), "IT Operations / BCM"),
        (("log", "monitoring", "siem", "alert"), "SecOps"),
        (("change management", "deployment", "release"), "IT Change Management"),
        (("data classification", "data validation", "data quality", "completeness and accuracy"), "Data Governance"),
        (("vendor", "third party", "third-party", "subservice"), "Vendor / TPRM"),
    ]
    for keywords, owner in topic_routes:
        if any(kw in text for kw in keywords):
            return owner, "matched_topic_keyword"
    # No topic keyword found — fall back to a status-based default, but
    # label it clearly as a fallback rather than a confident assignment.
    fallback = "IT Risk / SecOps" if status != "IMPLEMENTED" else "Internal Audit"
    return fallback, "fallback_no_topic_match"
