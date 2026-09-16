# Vendor SOC / ISAE Auditor (`vendor-soc-isae-auditor`) 🛡️🏢

> **Privacy-Preserving Third-Party Risk Assessment Tool**  
> Designed for SOC 1/2 Type II & ISAE 3402/3000 report analysis under **EU DORA Article 28**, **NIST CSF 2.0**, and strict NDA compliance.

---

## 🎯 Executive Overview

**Vendor SOC / ISAE Auditor** is an enterprise-grade, privacy-first tool built specifically for **Heads of IT Risk**, **Third-Party Risk Management (TPRM)** teams, and **Internal Audit** functions in regulated financial services.

The tool enables **confidential, automated evaluation** of SOC 1 Type II, SOC 2 Type II, and ISAE 3402/3000 reports without ever exposing sensitive vendor data (IP addresses, employee names, specific exceptions) to external LLM providers or public cloud services.

---

## 🛡️ Privacy-First Architecture (The "Air-Lock" Design)

The system uses a strict **three-tier local processing model**:

### Tier 1 — Local Air-Lock Extraction
- Extracts **only the 3 risk-critical sections** from the report:
  1. **Section I**: Auditor's Opinion (Qualified/Unqualified, Carve-out vs. Inclusive method)
  2. **Section IV**: Deviations & Exceptions Table (with Management Response)
  3. **CUECs / CSOCs**: Complementary User Entity Controls & Complementary Subservice Organization Controls

### Tier 2 — Local Redaction & Anonymization Proxy
- Strips all sensitive identifiers:
  - Vendor legal entity names → `[VENDOR_ORGANIZATION]`
  - Employee names & emails → `[REDACTED_EMAIL]`
  - Specific IP addresses, CIDRs → `[REDACTED_IP]`
- Ensures the downstream compliance engine only sees **abstracted control descriptions**.

### Tier 3 — Local Compliance Mapping
- Maps extracted controls against **NIST CSF 2.0**, **MITRE D3FEND**, and **EU DORA (Article 28)**.
- Produces a fully auditable **Vendor IT Risk Memo**, interactive **HTML TPRM Dashboard**, and internal CUEC action matrix.

---

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/pietrodiwalsi-design/vendor-soc-isae-auditor.git
cd vendor-soc-isae-auditor
pip install -r requirements.txt
```

### Basic Usage (CLI)
```bash
# Run full privacy-preserving audit on a SOC 2 / ISAE report
python3 -m vendor_auditor.cli audit --vendor "Cloud-SaaS-Provider" --text-file ./examples/soc2_sample.txt

# Start FastMCP Server for Claude Desktop & Cursor
python3 -m vendor_auditor.mcp_server
```

---

## 📋 Compliance & Framework Coverage

| Framework | Coverage Scope | Implementation Status |
| :--- | :--- | :--- |
| **DORA Art. 28** | ICT Third-Party Risk Management & Register of Information | ✅ **Implemented** |
| **ISAE 3000 / 3402** | Assurance Standards & Subservice Method Analysis (Carve-out vs Inclusive) | ✅ **Implemented** |
| **NIST CSF 2.0** | Function Mapping (PR.AC, PR.DS, RC.RP, DE.CM, GV.SC) | ✅ **Implemented** |
| **MITRE D3FEND** | Defensive Countermeasure Recommendations (D3-MFA, D3-EOT, D3-SPA) | ✅ **Implemented** |
| **CUEC Tracking** | Complementary User Entity Controls Internal Accountability Matrix | ✅ **Implemented** |
| **FastMCP Protocol** | Anthropic Model Context Protocol Server Interface for Claude Desktop | ✅ **Implemented** |

---

## 📄 License & Authors

- **Author & Project Lead:** [Peter Van Walsem](https://github.com/pietrodiwalsi-design) (`pietrodiwalsi-design`)
- **License:** Apache License 2.0 (see `LICENSE` and `AUTHORS.md`).
