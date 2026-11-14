#!/usr/bin/env python3
# Cyan Eclipse Darkseal MCP server (spec: SPEC-DARKSEAL
# section 4.1).
# Copyright © 2026 Cyan Eclipse Technologies LLC · cetech.ai
"""MCP over stdio (newline-delimited JSON-RPC 2.0), stdlib only.

Exactly the six section 4.1 tools. There is no aggregation tool,
no merchant-facing tool, and no metering: the check is free at
every tier and no tool creates a charge event of any kind
(DRK-REQ-016). Captures are accepted only from the executing
surface's witness module (DRK-REQ-012); everything else is
rejected on provenance and receipted.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import darkseal  # noqa: E402

SERVER_NAME = "eclipse-darkseal"
SERVER_VERSION = darkseal.TOOL_VERSION
_STR = {"type": "string"}
_OBJ = {"type": "object"}
_ARR_STR = {"type": "array", "items": _STR}

_ELEMENT = {"type": "object",
            "properties": {"class": _STR, "identity": _STR,
                           "default_state": _STR},
            "required": ["class", "identity", "default_state"],
            "additionalProperties": False}
_ARTIFACT = {"type": "object",
             "properties": {"artifact_digest": _STR,
                            "element_identity": _STR,
                            "kind": {"type": "string",
                                     "enum": ["charge",
                                              "binding-term"]}},
             "required": ["artifact_digest", "element_identity",
                          "kind"],
             "additionalProperties": False}


def _obj(props, required):
    return {"type": "object", "properties": props,
            "required": required, "additionalProperties": False}


DESCRIPTIONS = {
    "darkseal_seal_defaults":
        "Seal a flow's default-state vector element by element "
        "at traversal start, as captured by the executing "
        "surface's own witness module: element class, identity "
        "as presented, and default state as rendered, across "
        "checkboxes, toggles, radio/plan selectors, and "
        "continuity switches. Bundles from any non-executing "
        "source are rejected on provenance. The check is free. "
        + darkseal.CLAIM,
    "darkseal_diff_outcome":
        "Diff the principal's own confirmation and charge "
        "artifacts (held as digests) against the sealed "
        "defaults and mint the verdict: a charge or binding term "
        "that began as a sealed pre-selected element verdicts "
        "PRESELECTED-AND-CHARGED naming that element. The check "
        "is free.",
    "darkseal_get_verdict":
        "The full verdict record for a capture: verdict, charged "
        "element names, grammar version, coverage statement, "
        "separation marker, receipt refs. The check is free.",
    "darkseal_check":
        "Counterparty view: the verdict class and the names of "
        "charged elements only. The check is free.",
    "darkseal_recompute":
        "Recompute a verdict from an exported capture plus the "
        "element grammar version plus the outcome artifacts, "
        "with no service state. The check is free.",
    "darkseal_export_captures":
        "Export a sealed capture (element states + seal) with "
        "the receipt chain head and grammar version, for "
        "independent recomputation. The check is free.",
}

SCHEMAS = {
    "darkseal_seal_defaults": _obj({
        "flow_id": _STR, "flow_kind": _STR,
        "elements": {"type": "array", "items": _ELEMENT},
        "grammar_coverage": _ARR_STR,
        "surface_id": _STR, "source": _STR,
        "surface_attestation": _STR,
        "traversal_timestamp": _STR},
        ["flow_id", "elements", "surface_attestation",
         "surface_id", "source"]),
    "darkseal_diff_outcome": _obj({
        "capture_id": _STR,
        "outcome_artifacts": {"type": "array", "items": _ARTIFACT}},
        ["capture_id", "outcome_artifacts"]),
    "darkseal_get_verdict": _obj({"capture_id": _STR},
                                 ["capture_id"]),
    "darkseal_check": _obj({"capture_id": _STR}, ["capture_id"]),
    "darkseal_recompute": _obj({
        "capture": _OBJ, "grammar_version": _STR,
        "outcome_artifacts": {"type": "array", "items": _ARTIFACT}},
        ["capture", "grammar_version", "outcome_artifacts"]),
    "darkseal_export_captures": _obj({"capture_id": _STR},
                                     ["capture_id"]),
}

_store = None


def store() -> darkseal.Store:
    global _store
    if _store is None:
        base = os.path.dirname(os.path.abspath(__file__))
        state = os.environ.get(
            "ECLIPSE_DARKSEAL_STATE",
            os.path.join(base, "data", "darkseal-state.json"))
        os.makedirs(os.path.dirname(state), exist_ok=True)
        keys_path = os.environ.get(
            "ECLIPSE_DARKSEAL_SURFACE_KEYS",
            os.path.join(base, "keys", "surface-keys.json"))
        _store = darkseal.Store(
            state, darkseal.load_surface_keys(keys_path))
    return _store


def call_tool(name: str, args: dict):
    if name not in SCHEMAS:
        return {"error": "NO_SUCH_TOOL"}
    st = store()
    if name == "darkseal_seal_defaults":
        return st.seal_defaults(args)
    if name == "darkseal_diff_outcome":
        return st.diff_outcome(args["capture_id"],
                               args.get("outcome_artifacts"))
    if name == "darkseal_get_verdict":
        return st.get_verdict(args["capture_id"])
    if name == "darkseal_check":
        return st.check(args["capture_id"])
    if name == "darkseal_recompute":
        return darkseal.recompute(args["capture"],
                                  args["grammar_version"],
                                  args.get("outcome_artifacts"))
    if name == "darkseal_export_captures":
        return st.export_captures(args["capture_id"])
    return {"error": "NO_SUCH_TOOL"}


def handle(msg: dict):
    method = msg.get("method")
    if method == "initialize":
        return {"protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME,
                               "version": SERVER_VERSION}}
    if method == "tools/list":
        return {"tools": [{"name": n, "description": DESCRIPTIONS[n],
                           "inputSchema": SCHEMAS[n]}
                          for n in SCHEMAS]}
    if method == "tools/call":
        params = msg.get("params", {})
        result = call_tool(params.get("name"),
                           params.get("arguments", {}))
        return {"content": [{"type": "text",
                             "text": json.dumps(result,
                                                sort_keys=True)}],
                "isError": "error" in result}
    if method and method.startswith("notifications/"):
        return None
    return {"error": "NO_SUCH_METHOD"}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            result = handle(msg)
        except Exception:
            # K4 house guard (ETO-54): a handler fault is a named
            # refusal, never a crash; no exception text surfaces.
            if isinstance(msg, dict) and "id" in msg:
                sys.stdout.write(json.dumps(
                    {"jsonrpc": "2.0", "id": msg["id"], "error": {
                        "code": -32602,
                        "message": "MALFORMED_CONTAINER: argument 'request'"}}) + "\n")
                sys.stdout.flush()
            continue
        if result is not None and "id" in msg:
            sys.stdout.write(json.dumps(
                {"jsonrpc": "2.0", "id": msg["id"],
                 "result": result}) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
