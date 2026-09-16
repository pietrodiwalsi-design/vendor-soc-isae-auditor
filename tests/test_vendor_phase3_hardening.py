"""
Phase 3 Hardening Regression Suite (Claude Sonnet 5 Certification Pass).

Covers JSON-RPC 2.0 conformance, input validation, and error-id integrity
for the MCP server, plus edge-case guards added to airlock_parser,
anonymizer, cuec_tracker, dora_tprm, and multi_year_analyzer during the
security review.
"""
import unittest
import sys
sys.path.insert(0, '/root/repos/vendor-soc-isae-auditor/src')

from vendor_auditor.mcp_server import handle_request
from vendor_auditor.airlock_parser import AirlockParser
from vendor_auditor.anonymizer import AnonymizerProxy
from vendor_auditor.cuec_tracker import CUECTracker
from vendor_auditor.dora_tprm import DORATPRMEvaluator
from vendor_auditor.multi_year_analyzer import MultiYearTrendAnalyzer


class TestMCPServerHardening(unittest.TestCase):
    def test_non_string_report_text_rejected_with_matching_id(self):
        resp = handle_request({
            "jsonrpc": "2.0", "id": 42, "method": "tools/call",
            "params": {"name": "audit_soc_report_text", "arguments": {"report_text": 12345}}
        })
        self.assertEqual(resp["id"], 42)
        self.assertIn("error", resp)

    def test_non_array_cuecs_rejected(self):
        resp = handle_request({
            "jsonrpc": "2.0", "id": 7, "method": "tools/call",
            "params": {"name": "analyze_cuec_controls", "arguments": {"cuecs": "not_a_list", "internal_controls": []}}
        })
        self.assertEqual(resp["id"], 7)
        self.assertIn("error", resp)

    def test_unknown_tool_preserves_id(self):
        resp = handle_request({
            "jsonrpc": "2.0", "id": "xyz", "method": "tools/call",
            "params": {"name": "nonexistent_tool", "arguments": {}}
        })
        self.assertEqual(resp["id"], "xyz")
        self.assertEqual(resp["error"]["code"], -32602)


class TestAirlockParserHardening(unittest.TestCase):
    def test_none_raw_text_does_not_crash(self):
        res = AirlockParser().extract_critical_sections(None)
        self.assertEqual(res["section_1_opinion"], "UNCONFIRMED")

    def test_rejects_non_string(self):
        with self.assertRaises(TypeError):
            AirlockParser().extract_critical_sections(12345)


class TestAnonymizerHardening(unittest.TestCase):
    def test_none_text_does_not_crash(self):
        clean, meta = AnonymizerProxy().redact_sensitive_data(None)
        self.assertEqual(clean, "")

    def test_rejects_non_string(self):
        with self.assertRaises(TypeError):
            AnonymizerProxy().redact_sensitive_data(12345)

    def test_ipv4_octet_range_validation(self):
        # 999.999.999.999 is not a valid IPv4 address and should NOT be redacted
        # by the hardened, range-validated regex (avoids false positives on version strings).
        clean, _ = AnonymizerProxy().redact_sensitive_data("Version 999.999.999.999 release notes")
        self.assertIn("999.999.999.999", clean)
        # A legitimate IP must still be redacted
        clean2, _ = AnonymizerProxy().redact_sensitive_data("Server at 10.0.0.1 was compromised")
        self.assertNotIn("10.0.0.1", clean2)


class TestCUECTrackerHardening(unittest.TestCase):
    def test_none_lists_default_to_empty(self):
        res = CUECTracker().analyze_cuec_gaps(None, None)
        self.assertEqual(res["total_cuecs_demanded_by_vendor"], 0)
        self.assertEqual(res["cuec_compliance_pct"], 0.0)

    def test_rejects_non_list(self):
        with self.assertRaises(TypeError):
            CUECTracker().analyze_cuec_gaps("not_a_list", [])


class TestDORATPRMHardening(unittest.TestCase):
    def test_none_airlock_data_does_not_crash(self):
        res = DORATPRMEvaluator().evaluate_vendor_risk(None)
        self.assertIn("dora_article_28_compliance", res)


class TestMultiYearAnalyzerHardening(unittest.TestCase):
    def test_none_periods_do_not_crash(self):
        res = MultiYearTrendAnalyzer().compare_audit_periods(None, None)
        self.assertEqual(res["trend_status"], "STABLE")


if __name__ == "__main__":
    unittest.main()
