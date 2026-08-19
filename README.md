# Vendor SOC / ISAE Auditor (`vendor-soc-isae-auditor`)

> **Privacy-Preserving Third-Party Risk Assessment Tool**  
> Designed for SOC 1/2 Type II & ISAE 3402/3000 report analysis under **DORA Article 28** and strict NDA compliance.

---

## 🎯 Executive Overview

**Vendor SOC / ISAE Auditor** is an enterprise-grade, privacy-first tool built specifically for **Heads of IT Risk**, **Third-Party Risk Management (TPRM)** teams, and **Internal Audit** functions in regulated financial services.

The tool enables **confidential, automated evaluation** of SOC 1 Type II, SOC 2 Type II, and ISAE 3402/3000 reports without ever exposing sensitive vendor data (IP addresses, employee names, specific exceptions) to external LLM providers or public cloud services.

---

## 🛡️ Privacy-First Architecture (The "Air-Lock" Design)

The system uses a strict **three-tier local processing model**:

### Tier 1 — Local Air-Lock Extraction
- Extracts **only the 3 risk-critical sections** from the PDF:
  1. **Section I**: Auditor's Opinion (Qualified/Unqualified, Carve-out vs. Inclusive method)
  2. **Section IV**: Deviations & Exceptions Table (with Management Response)
  3. **CUECs / CSOCs**: Complementary User Entity Controls & Complementary Subservice Organization Controls

### Tier 2 — Local Redaction & Anonymization Proxy
- Strips all sensitive identifiers:
  - Vendor legal entity names → `[VENDOR_A]`
  - Employee names & titles → `[AUDITOR_1]`, `[VENDOR_CISO]`
  - Specific IP addresses, CIDRs, datacenter names → `[DC_REGION_EU]`
- Ensures the downstream AI model only sees **abstracted control descriptions**.

### Tier 3 — Local Compliance Mapping
- Maps extracted controls against **NIST CSF 2.0** and **MITRE D3FEND** using the local 817-skill reference library.
- Produces a fully auditable **Vendor IT Risk Memo** and internal CUEC action matrix.

---

## 🏗️ High-Level Architecture

```
[SOC / ISAE PDF Report]
          │
          ▼ (Local Python Parser)
┌───────────────────────────────┐
│  Tier 1: Air-Lock Extractor   │ ← Extracts only Opinion, Exceptions, CUECs
└───────────────┬───────────────┘
                │
                ▼ (Local Redaction Engine)
┌───────────────────────────────┐
│  Tier 2: Anonymization Proxy  │ ← Replaces names, IPs, locations
└───────────────┬───────────────┘
                │
                ▼ (Local Model / Reference Library)
┌───────────────────────────────┐
│  Tier 3: NIST CSF / D3FEND    │ ← Benchmarking against 800+ skills
│         Mapping Engine        │
└───────────────┬───────────────┘
                │
                ▼
   [Vendor Risk Memo + Action Plan]
```

---

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/pietrodiwalsi-design/vendor-soc-isae-auditor.git
cd vendor-soc-isae-auditor
pip install -r requirements.txt
```

### Basic Usage
```bash
# Extract critical sections from a SOC2 report
python3 -m src.cli extract --pdf /path/to/vendor-soc2-2026.pdf --output ./extracted/

# Run NIST CSF 2.0 gap analysis (after redaction)
python3 -m src.cli analyze --redacted ./extracted/ --framework nist-csf-2.0

# Generate final executive memo
python3 -m src.cli report --input ./extracted/ --format pdf
```

---

## 📋 Compliance & Framework Coverage

| Framework | Coverage | Status |
| :--- | :--- | :--- |
| **NIST CSF 2.0** | Identify, Protect, Detect, Respond, Recover | ✅ Planned |
| **MITRE D3FEND** | Defensive Countermeasures | ✅ Planned |
| **DORA Art. 28** | ICT Third-Party Risk Management | ✅ Planned |
| **ISAE 3000 / 3402** | Assurance Standards | ✅ Planned |

---

## 📄 License
MIT License. Developed by [pietrodiwalsi-design](https://github.com/pietrodiwalsi-design).
