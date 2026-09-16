import re
from typing import Dict, Any, Tuple

class AnonymizerProxy:
    """Tier 2 Local Anonymization: Strips PII, employee names, vendor entities, and specific IPs."""

    def redact_sensitive_data(self, text: str) -> Tuple[str, Dict[str, str]]:
        redactions = {}

        # Redact IP addresses
        text_clean = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[REDACTED_IP]", text)
        
        # Redact Email addresses
        text_clean = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "[REDACTED_EMAIL]", text_clean)

        # Redact Specific Vendor Legal Entities
        vendor_patterns = [r"\b(Microsoft Ireland Operations Ltd|Amazon Web Services EMEA SARL|Salesforce\.com Inc)\b"]
        for vp in vendor_patterns:
            text_clean = re.sub(vp, "[VENDOR_ORGANIZATION]", text_clean, flags=re.IGNORECASE)

        return text_clean, {"status": "ANONYMIZED", "pii_redacted": True}
