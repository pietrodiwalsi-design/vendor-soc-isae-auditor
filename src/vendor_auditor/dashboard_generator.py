class VendorDashboardGenerator:
    """Generates a standalone interactive HTML TPRM & DORA Article 28 Dashboard."""

    def generate_html_dashboard(self, vendor_name: str, airlock_res: dict, dora_res: dict, cuec_res: dict) -> str:
        dora = dora_res.get("dora_article_28_compliance", {})
        # FIX (2026-09-18 review, dashboard hardening): residual_tpm_risk_score
        # is None when the auditor opinion could not be extracted
        # (risk_tier="INSUFFICIENT_EXTRACTION", see FIX 2). Comparing None >= 5
        # crashed the dashboard render. Render an explicit "N/A" state instead
        # of coercing to 0 (which would look like a clean/low-risk result).
        raw_score = dora.get('residual_tpm_risk_score')
        score_display = f"{raw_score} / 10" if raw_score is not None else "N/A"
        score_color = '#94a3b8' if raw_score is None else ('#ef4444' if raw_score >= 5 else '#10b981')
        action_text = dora.get('action_required', 'N/A') or 'N/A'
        action_display = action_text[:60] + ('...' if len(action_text) > 60 else '')
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Vendor SOC / ISAE Auditor — Third-Party Risk Dashboard</title>
  <style>
    body {{ background: #0f172a; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 30px; margin: 0; }}
    .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(0,0,0,0.3); }}
    .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
    .metric-card {{ background: #0f172a; border-radius: 10px; padding: 18px; border-left: 4px solid #38bdf8; }}
    .metric-val {{ font-size: 24px; font-weight: 800; color: #f8fafc; margin-top: 6px; }}
    .metric-lbl {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }}
  </style>
</head>
<body>
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
    <div>
      <h1 style="margin: 0; font-size: 26px; color: #38bdf8;">🏢 Vendor SOC 2 / ISAE 3402 Audit Dashboard</h1>
      <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 14px;">Target Vendor: <b>{vendor_name}</b> • Compliance Standard: EU DORA (Article 28)</p>
    </div>
    <div style="background: #0f172a; padding: 8px 16px; border-radius: 8px; border: 1px solid #38bdf8; font-size: 13px; font-weight: 600; color: #38bdf8;">
      Opinion: {airlock_res.get('section_1_opinion')}
    </div>
  </div>

  <div class="grid">
    <div class="metric-card" style="border-left-color: #38bdf8;">
      <div class="metric-lbl">TPRM Residual Risk</div>
      <div class="metric-val" style="color: {score_color};">{score_display}</div>
      <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Tier: {dora.get('risk_tier', 'N/A')}</div>
    </div>
    <div class="metric-card" style="border-left-color: #f59e0b;">
      <div class="metric-lbl">Control Exceptions</div>
      <div class="metric-val" style="color: #f59e0b;">{airlock_res.get('section_4_exceptions_count', 0)}</div>
      <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Method: {airlock_res.get('subservice_method')}</div>
    </div>
    <div class="metric-card" style="border-left-color: #10b981;">
      <div class="metric-lbl">CUEC Coverage</div>
      <div class="metric-val" style="color: #10b981;">{cuec_res.get('cuec_compliance_pct', 0)}%</div>
      <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Gaps: {cuec_res.get('internal_gaps_identified', 0)}</div>
    </div>
    <div class="metric-card" style="border-left-color: #a855f7;">
      <div class="metric-lbl">DORA Art. 28 Status</div>
      <div class="metric-val" style="color: #a855f7; font-size: 14px; margin-top: 10px;">{action_display}</div>
    </div>
  </div>
</body>
</html>"""
        return html
