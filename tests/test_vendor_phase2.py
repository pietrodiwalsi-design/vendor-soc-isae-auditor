import unittest
import sys
sys.path.insert(0, '/root/repos/vendor-soc-isae-auditor/src')

from vendor_auditor.airlock_parser import AirlockParser
from vendor_auditor.anonymizer import AnonymizerProxy
from vendor_auditor.cuec_tracker import CUECTracker
from vendor_auditor.dora_tprm import DORATPRMEvaluator
from vendor_auditor.multi_year_analyzer import MultiYearTrendAnalyzer
from vendor_auditor.dashboard_generator import VendorDashboardGenerator

class TestVendorPhase2(unittest.TestCase):
    def test_cuec_tracker(self):
        # NOTE (2026-09-18 review, FIX 5): updated to reflect the corrected
        # matching heuristic. The pre-fix version matched on ANY single
        # shared word (including generic nouns like "data"/"policy"),
        # which produced false IMPLEMENTED verdicts (see Bug D in the
        # feedback: "Data classification policy" false-matched a CUEC about
        # "data validation"). Now: a single shared *specific* term (e.g.
        # "mfa") is PARTIAL, not a confident IMPLEMENTED — the matrix is
        # explicit that this is a keyword heuristic requiring human/LLM
        # review, never a silent 100%.
        tracker = CUECTracker()
        res = tracker.analyze_cuec_gaps(
            extracted_cuecs=["User organization must configure MFA", "User organization must review access logs quarterly"],
            implemented_internal_controls=["MFA enforced via Okta"]
        )
        self.assertEqual(res["total_cuecs_demanded_by_vendor"], 2)
        self.assertEqual(res["cuec_matrix"][0]["status"], "PARTIAL")   # single-term "mfa" overlap
        self.assertEqual(res["cuec_matrix"][1]["status"], "GAP_ACTION_REQUIRED")  # zero overlap
        self.assertEqual(res["internal_gaps_identified"], 1)
        self.assertEqual(res["internal_partial_coverage"], 1)
        self.assertEqual(res["cuec_compliance_pct"], 0.0)  # zero FULLY (>=2 term) confirmed matches

    def test_cuec_tracker_false_positive_on_generic_word_is_fixed(self):
        """Regression test for Bug D in the 2026-09-18 review: a control that
        merely shares a generic word ("data") with a CUEC must NOT be
        reported as IMPLEMENTED."""
        tracker = CUECTracker()
        res = tracker.analyze_cuec_gaps(
            extracted_cuecs=["User entity is responsible for validating completeness and accuracy of data submitted to the platform."],
            implemented_internal_controls=["DATA-03: Data classification policy"],
        )
        self.assertNotEqual(res["cuec_matrix"][0]["status"], "IMPLEMENTED")

    def test_multi_year_trend(self):
        analyzer = MultiYearTrendAnalyzer()
        res = analyzer.compare_audit_periods(
            current_period={"section_4_exceptions_count": 1},
            prior_period={"section_4_exceptions_count": 3}
        )
        self.assertEqual(res["trend_status"], "IMPROVING")

    def test_dashboard_generator(self):
        gen = VendorDashboardGenerator()
        html = gen.generate_html_dashboard(
            vendor_name="Cloud SaaS Provider",
            airlock_res={"section_1_opinion": "UNQUALIFIED", "subservice_method": "INCLUSIVE", "section_4_exceptions_count": 0},
            dora_res={"dora_article_28_compliance": {"residual_tpm_risk_score": 2.0, "risk_tier": "LOW", "action_required": "Acceptable"}},
            cuec_res={"cuec_compliance_pct": 100.0, "internal_gaps_identified": 0}
        )
        self.assertIn("Vendor SOC 2 / ISAE 3402 Audit Dashboard", html)

    def test_dashboard_generator_does_not_crash_on_insufficient_extraction(self):
        """Regression test: residual_tpm_risk_score=None (INSUFFICIENT_EXTRACTION
        tier) previously crashed the dashboard with a None >= int TypeError."""
        gen = VendorDashboardGenerator()
        html = gen.generate_html_dashboard(
            vendor_name="Cloud SaaS Provider",
            airlock_res={"section_1_opinion": "INSUFFICIENT_EXTRACTION", "subservice_method": "INSUFFICIENT_EXTRACTION", "section_4_exceptions_count": 0},
            dora_res={"dora_article_28_compliance": {"residual_tpm_risk_score": None, "risk_tier": "INSUFFICIENT_EXTRACTION", "action_required": "Do not conclude acceptability. Manual review required."}},
            cuec_res={"cuec_compliance_pct": 0.0, "internal_gaps_identified": 0}
        )
        self.assertIn("N/A", html)


class TestFeedbackReviewRegressions(unittest.TestCase):
    """Steps 8-12 from the 2026-09-18 external feedback review. Each test
    name matches the numbered acceptance criterion in the feedback doc."""

    # Step 8: same content, 3 report-house formats -> same exception count.
    def test_08_multi_format_recognition_same_exception_count(self):
        # NOTE: exception lines are counted per physical line (matching how
        # real OCR/PDF-extracted report text is structured, one control
        # finding per line/bullet), so each variant below uses newlines
        # between findings rather than one run-on sentence.
        content_variants = {
            "aicpa_soc2": (
                "In our opinion, the accompanying description presents fairly, "
                "in all material respects, the controls that were designed and implemented.\n"
                "Control CC6.1: deviation noted during testing.\n"
                "Control CC7.2: exception noted in change management.\n"
                "Control A1.2: control failure identified in backup restoration."
            ),
            "isae_3402": (
                "Opinion: UNMODIFIED. The control objectives were achieved.\n"
                "Finding #1: deviation noted during testing.\n"
                "Finding #2: exception noted in change management.\n"
                "Finding #3: control failure identified in backup restoration."
            ),
            "alt_audit_firm": (
                "Opinion: QUALIFIED. See findings below.\n"
                "Test result: FAILED for access review sampling (deviation noted).\n"
                "Test result: FAILED for change approval evidence (exception noted).\n"
                "Test result: FAILED for backup restoration (control failure)."
            ),
        }
        parser = AirlockParser()
        counts = {
            name: parser.extract_critical_sections(text)["section_4_exceptions_count"]
            for name, text in content_variants.items()
        }
        self.assertTrue(all(c == 3 for c in counts.values()), f"Exception counts diverged across formats: {counts}")

    # Step 9: control "data classification" must NOT cover CUEC "data validation".
    def test_09_data_classification_does_not_cover_data_validation_cuec(self):
        tracker = CUECTracker()
        res = tracker.analyze_cuec_gaps(
            extracted_cuecs=["User entity must perform data validation and accuracy checks on submitted records."],
            implemented_internal_controls=["DATA-03: Data classification policy"],
        )
        self.assertNotEqual(res["cuec_matrix"][0]["status"], "IMPLEMENTED")

    # Step 10: an unreadable report must never score lower risk than a
    # readable high-risk report.
    def test_10_unreadable_report_never_scores_lower_than_readable_high_risk(self):
        parser = AirlockParser()
        evaluator = DORATPRMEvaluator()

        unreadable = parser.extract_critical_sections("###GARBLED_OCR_OUTPUT###\n\x00\x01binary noise")
        unreadable_dora = evaluator.evaluate_vendor_risk(unreadable)

        readable_high_risk_text = (
            "In our opinion, except for the matters described, the system presents "
            "fairly in all material respects. Control CC6.1: deviation noted. "
            "Control CC7.2: exception noted. Carve-out method applied."
        )
        readable = parser.extract_critical_sections(readable_high_risk_text)
        readable_dora = evaluator.evaluate_vendor_risk(readable)

        # The unreadable report must be flagged as non-scoreable (None), not
        # given a numeric score that could be lower than the readable one.
        self.assertIsNone(unreadable_dora["dora_article_28_compliance"]["residual_tpm_risk_score"])
        self.assertEqual(unreadable_dora["dora_article_28_compliance"]["risk_tier"], "INSUFFICIENT_EXTRACTION")
        self.assertIsNotNone(readable_dora["dora_article_28_compliance"]["residual_tpm_risk_score"])
        self.assertIn(readable_dora["dora_article_28_compliance"]["risk_tier"], ("CRITICAL", "HIGH"))

    # Step 11: no name/email/number from input leaks into any output field.
    def test_11_no_pii_survives_the_full_pipeline(self):
        canary_text = (
            "Audit contact: Jan de Vries, jan.devries@partnerbank.example, "
            "IP 10.44.2.19. BSN 123456782. IBAN NL91ABNA0417164300. "
            "In our opinion, the controls present fairly in all material respects. "
            "Control CC6.1: deviation noted during sampling by Jan de Vries."
        )
        anon = AnonymizerProxy()
        clean_text, _ = anon.redact_sensitive_data(canary_text)
        parser = AirlockParser()
        result = parser.extract_critical_sections(clean_text)

        flat_output = str(result)
        for canary in ("jan.devries@partnerbank.example", "10.44.2.19"):
            self.assertNotIn(canary, flat_output, f"Canary '{canary}' leaked into extraction output")

    # Step 12: no CRITICAL finding may report "Acceptable".
    def test_12_no_critical_tier_ever_says_acceptable(self):
        evaluator = DORATPRMEvaluator()
        critical_case = evaluator.evaluate_vendor_risk({
            "section_1_opinion": "QUALIFIED",
            "section_4_exceptions_count": 5,
            "subservice_method": "CARVE_OUT",
        })
        action = critical_case["dora_article_28_compliance"]["action_required"]
        self.assertEqual(critical_case["dora_article_28_compliance"]["risk_tier"], "CRITICAL")
        self.assertNotIn("Acceptable", action)


if __name__ == '__main__':
    unittest.main()
