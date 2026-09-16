import sys
import json
import argparse
from vendor_auditor.airlock_parser import AirlockParser
from vendor_auditor.anonymizer import AnonymizerProxy
from vendor_auditor.dora_tprm import DORATPRMEvaluator
from vendor_auditor.memo_generator import MemoGenerator

def main():
    parser = argparse.ArgumentParser(description="Vendor SOC / ISAE Auditor CLI")
    subparsers = parser.add_subparsers(dest="command")

    audit_p = subparsers.add_parser("audit", help="Run privacy-preserving SOC audit")
    audit_p.add_argument("--vendor", default="[VENDOR_A]", help="Vendor Name")
    audit_p.add_argument("--text-file", required=True, help="Path to raw report text")

    args = parser.parse_args()

    if args.command == "audit":
        with open(args.text_file, 'r', errors='ignore') as f:
            raw = f.read()

        anon = AnonymizerProxy()
        clean_text, _ = anon.redact_sensitive_data(raw)

        airlock = AirlockParser()
        sections = airlock.extract_critical_sections(clean_text)

        evaluator = DORATPRMEvaluator()
        dora = evaluator.evaluate_vendor_risk(sections)

        gen = MemoGenerator()
        memo = gen.generate_memo(args.vendor, sections, dora)
        print(memo)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
