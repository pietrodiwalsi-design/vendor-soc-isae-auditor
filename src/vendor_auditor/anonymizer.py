import re
from typing import Dict, Any, Tuple

class AnonymizerProxy:
    """Tier 2 Local Anonymization: Strips PII, employee names, vendor entities, and specific IPs."""

    # Precompiled: hardened IPv4 pattern validates octet range (0-255) instead of any 1-3 digit
    # group, avoiding both false positives (e.g. version strings like "999.999.999.999") and
    # unnecessary redaction of non-IP numeric sequences. Patterns compiled once per process.
    _RE_IPV4 = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    )
    _RE_EMAIL = re.compile(r"[\w.\-]+@[\w\-]+\.[\w.\-]+")
    _RE_VENDORS = re.compile(
        r"\b(Microsoft Ireland Operations Ltd|Amazon Web Services EMEA SARL|Salesforce\.com Inc)\b",
        re.IGNORECASE
    )

    def redact_sensitive_data(self, text: str) -> Tuple[str, Dict[str, str]]:
        if text is None:
            text = ""
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        # Redact IP addresses
        text_clean = self._RE_IPV4.sub("[REDACTED_IP]", text)

        # Redact Email addresses
        text_clean = self._RE_EMAIL.sub("[REDACTED_EMAIL]", text_clean)

        # Redact Specific Vendor Legal Entities
        text_clean = self._RE_VENDORS.sub("[VENDOR_ORGANIZATION]", text_clean)

        return text_clean, {"status": "ANONYMIZED", "pii_redacted": True}
