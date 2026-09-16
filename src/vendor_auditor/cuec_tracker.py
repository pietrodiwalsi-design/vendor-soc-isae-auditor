from typing import Dict, Any, List

class CUECTracker:
    """Tracks Complementary User Entity Controls (CUECs) and assigns internal accountability."""

    def analyze_cuec_gaps(self, extracted_cuecs: List[str], implemented_internal_controls: List[str]) -> Dict[str, Any]:
        cuec_items = []
        unassigned_count = 0

        # Build list of key control terms from implemented controls
        key_terms = []
        for ic in implemented_internal_controls:
            for word in ic.lower().split():
                if len(word) >= 3 and word not in ["the", "via", "and", "for", "with", "must"]:
                    key_terms.append(word)
        
        for idx, cuec_text in enumerate(extracted_cuecs, 1):
            cuec_lower = cuec_text.lower()
            is_covered = any(term in cuec_lower for term in key_terms)
            status = "IMPLEMENTED" if is_covered else "GAP_ACTION_REQUIRED"
            if not is_covered:
                unassigned_count += 1
                
            cuec_items.append({
                "cuec_id": f"CUEC-{idx:02d}",
                "description": cuec_text,
                "status": status,
                "assigned_owner": "IT Risk / SecOps" if not is_covered else "Internal Audit"
            })

        return {
            "total_cuecs_demanded_by_vendor": len(extracted_cuecs),
            "internal_gaps_identified": unassigned_count,
            "cuec_compliance_pct": round(((len(extracted_cuecs) - unassigned_count) / max(len(extracted_cuecs), 1)) * 100, 1),
            "cuec_matrix": cuec_items
        }
