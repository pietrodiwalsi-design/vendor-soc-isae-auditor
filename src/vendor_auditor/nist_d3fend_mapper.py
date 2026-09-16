import re
from typing import Dict, Any, List

class NISTD3FENDMapper:
    """Maps vendor SOC/ISAE control exceptions to NIST CSF 2.0 functions and MITRE D3FEND defensive countermeasures."""

    CSF_MAPPINGS = [
        {"pattern": r"(access|mfa|password|privilege|credential|authentication|login)", "function": "PR.AC (Identity Management & Access Control)", "d3fend": "D3-MFA (Multi-factor Authentication) / D3-URAM (User Rights Management)"},
        {"pattern": r"(encryption|key|tls|ssl|crypto|certificate)", "function": "PR.DS (Data Security & Cryptographic Protection)", "d3fend": "D3-EOT (Encrypt Operational Traffic) / D3-EOD (Encrypt Operational Data)"},
        {"pattern": r"(backup|recovery|retention|archive|disaster|restore)", "function": "RC.RP (Recovery Planning & Restoration)", "d3fend": "D3-DBR (Database Backup & Restoration)"},
        {"pattern": r"(log|monitoring|audit|alert|siem|detection|soc)", "function": "DE.CM (Continuous Monitoring & Detection)", "d3fend": "D3-SML (Security Monitoring & Log Analysis)"},
        {"pattern": r"(patch|vulnerability|update|flaw|cve)", "function": "PR.IP (Information Protection Processes / Vulnerability Mgmt)", "d3fend": "D3-SPA (Software Patch Application)"}
    ]

    def map_exceptions_to_frameworks(self, exceptions: List[str]) -> Dict[str, Any]:
        mapped_results = []
        for exc in exceptions:
            matched_csf = "GV.SC (Supply Chain Risk Management - General Exception)"
            matched_d3fend = "D3-TPCM (Third-Party Compensating Measure)"
            
            for rule in self.CSF_MAPPINGS:
                if re.search(rule["pattern"], exc, re.IGNORECASE):
                    matched_csf = rule["function"]
                    matched_d3fend = rule["d3fend"]
                    break
                    
            mapped_results.append({
                "exception_text": exc,
                "nist_csf_2_0": matched_csf,
                "mitre_d3fend_countermeasure": matched_d3fend
            })

        return {
            "total_exceptions_mapped": len(exceptions),
            "nist_csf_2_0_alignment": mapped_results
        }
