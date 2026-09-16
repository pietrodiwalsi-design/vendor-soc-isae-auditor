import unittest
import sys
sys.path.insert(0, '/root/repos/vendor-soc-isae-auditor/src')

from vendor_auditor.cuec_tracker import CUECTracker
from vendor_auditor.multi_year_analyzer import MultiYearTrendAnalyzer
from vendor_auditor.dashboard_generator import VendorDashboardGenerator

class TestVendorPhase2(unittest.TestCase):
    def test_cuec_tracker(self):
        tracker = CUECTracker()
        res = tracker.analyze_cuec_gaps(
            extracted_cuecs=["User organization must configure MFA", "User organization must review access logs quarterly"],
            implemented_internal_controls=["MFA enforced via Okta"]
        )
        self.assertEqual(res["total_cuecs_demanded_by_vendor"], 2)
        self.assertEqual(res["internal_gaps_identified"], 1)
        self.assertEqual(res["cuec_compliance_pct"], 50.0)

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

if __name__ == '__main__':
    unittest.main()
