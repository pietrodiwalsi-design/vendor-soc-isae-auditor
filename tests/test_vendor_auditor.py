import unittest
import sys
sys.path.insert(0, '/root/repos/vendor-soc-isae-auditor/src')

from vendor_auditor.airlock_parser import AirlockParser
from vendor_auditor.anonymizer import AnonymizerProxy
from vendor_auditor.dora_tprm import DORATPRMEvaluator

class TestVendorAuditor(unittest.TestCase):
    def test_anonymizer(self):
        proxy = AnonymizerProxy()
        clean, meta = proxy.redact_sensitive_data("Audit team contacted user@company.com at IP 192.168.1.100 for AWS EMEA.")
        self.assertNotIn("192.168.1.100", clean)
        self.assertNotIn("user@company.com", clean)

    def test_airlock_and_dora(self):
        sample = "The controls present fairly in all material respects. One exception noted during Q3 sample testing. Carve-out method applied."
        parser = AirlockParser()
        data = parser.extract_critical_sections(sample)
        self.assertEqual(data["section_1_opinion"], "UNQUALIFIED")
        self.assertEqual(data["subservice_method"], "CARVE_OUT")
        self.assertGreaterEqual(data["section_4_exceptions_count"], 1)

        evaluator = DORATPRMEvaluator()
        dora = evaluator.evaluate_vendor_risk(data)
        self.assertTrue(dora["dora_article_28_compliance"]["fourth_party_risk_identified"])

if __name__ == '__main__':
    unittest.main()
