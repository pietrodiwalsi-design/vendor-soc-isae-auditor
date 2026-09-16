#!/usr/bin/env python3
"""
Vendor SOC / ISAE Auditor — Model Context Protocol (MCP) Server.
Enables Claude Desktop, Cursor, and OpenClaw to perform privacy-preserving TPRM audits under DORA Art. 28.
"""

import sys
import os
import json
from vendor_auditor.airlock_parser import AirlockParser
from vendor_auditor.anonymizer import AnonymizerProxy
from vendor_auditor.dora_tprm import DORATPRMEvaluator
from vendor_auditor.cuec_tracker import CUECTracker

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {
    "name": "vendor-soc-isae-auditor-mcp",
    "version": "1.0.0"
}

TOOLS = [
    {
        "name": "audit_soc_report_text",
        "description": "Runs privacy-preserving local Air-Lock extraction and DORA Art. 28 risk evaluation on SOC 2/ISAE 3402 report text.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "report_text": {"type": "string", "description": "Raw extracted text of SOC report"},
                "vendor_name": {"type": "string", "default": "[VENDOR_A]", "description": "Vendor identifier"}
            },
            "required": ["report_text"]
        }
    },
    {
        "name": "analyze_cuec_controls",
        "description": "Analyzes vendor Complementary User Entity Controls (CUECs) against internal control implementations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cuecs": {"type": "array", "items": {"type": "string"}, "description": "List of CUEC requirement strings"},
                "internal_controls": {"type": "array", "items": {"type": "string"}, "description": "List of implemented internal controls"}
            },
            "required": ["cuecs", "internal_controls"]
        }
    }
]

def handle_request(req):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO
            }
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS}
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "audit_soc_report_text":
            anon = AnonymizerProxy()
            clean_text, _ = anon.redact_sensitive_data(args.get("report_text", ""))
            airlock = AirlockParser()
            sections = airlock.extract_critical_sections(clean_text)
            evaluator = DORATPRMEvaluator()
            dora = evaluator.evaluate_vendor_risk(sections)
            out = {
                "airlock_sections": sections,
                "dora_evaluation": dora
            }
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(out, indent=2)}], "isError": False}
            }
        elif tool_name == "analyze_cuec_controls":
            tracker = CUECTracker()
            res = tracker.analyze_cuec_gaps(args.get("cuecs", []), args.get("internal_controls", []))
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}], "isError": False}
            }
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": f"Unknown tool: {tool_name}"}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
