#!/usr/bin/env python3
# Cyan Eclipse Darkseal — MCP smoke transcript.
# Copyright © 2026 Cyan Eclipse Technologies LLC · cetech.ai
"""Drives the real server over stdio JSON-RPC: tools/list, a
signup-flow seal, a PRESELECTED-AND-CHARGED diff, a
PRESELECTED-NOT-CHARGED diff, a notary rejection, a
below-standard UNVERIFIABLE, the Upsellseal-object separation,
check, export, an offline recompute, and a form-value refusal.
Exits non-zero on any mismatch."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "fixtures"))
import captures  # noqa: E402


def rpc(proc, mid, method, params=None):
    msg = {"jsonrpc": "2.0", "id": mid, "method": method}
    if params is not None:
        msg["params"] = params
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())


def call(proc, mid, name, args):
    out = rpc(proc, mid, "tools/call",
              {"name": name, "arguments": args})
    return json.loads(out["result"]["content"][0]["text"])


def main():
    tmp = tempfile.mkdtemp()
    env = dict(os.environ,
               ECLIPSE_DARKSEAL_STATE=os.path.join(tmp, "s.json"))
    proc = subprocess.Popen(
        [sys.executable, os.path.join(HERE, "server.py")],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        text=True, env=env)
    try:
        init = rpc(proc, 1, "initialize")
        assert init["result"]["serverInfo"]["name"] == \
            "eclipse-darkseal", init
        tools = rpc(proc, 2, "tools/list")
        names = [t["name"] for t in tools["result"]["tools"]]
        assert names == ["darkseal_seal_defaults",
                         "darkseal_diff_outcome",
                         "darkseal_get_verdict",
                         "darkseal_check",
                         "darkseal_recompute",
                         "darkseal_export_captures"], names
        seal = call(proc, 3, "darkseal_seal_defaults",
                    captures.capture())
        assert seal["accepted"] is True, seal
        cid = seal["capture_id"]
        diff = call(proc, 4, "darkseal_diff_outcome",
                    {"capture_id": cid,
                     "outcome_artifacts":
                         [captures.artifact("auto-renew")]})
        assert diff["verdict"] == "PRESELECTED-AND-CHARGED", diff
        assert diff["charged_elements"] == ["auto-renew"], diff
        seal2 = call(proc, 5, "darkseal_seal_defaults",
                     captures.capture(flow_id="flow-signup-002"))
        diff2 = call(proc, 6, "darkseal_diff_outcome",
                     {"capture_id": seal2["capture_id"],
                      "outcome_artifacts": []})
        assert diff2["verdict"] == "PRESELECTED-NOT-CHARGED", diff2
        notary = call(proc, 7, "darkseal_seal_defaults",
                      captures.capture(flow_id="flow-notary-001",
                                       source="standalone-notary"))
        assert notary["accepted"] is False and \
            notary["error"] == "PROVENANCE_FAILURE", notary
        below = call(proc, 8, "darkseal_seal_defaults",
                     captures.capture(
                         flow_id="flow-below-001",
                         elements=[captures.el("checkbox", "x",
                                               "maybe")]))
        assert below["verdict"] == "UNVERIFIABLE", below
        sep = call(proc, 9, "darkseal_seal_defaults",
                   captures.upsellseal_object_fixture())
        assert sep["separation"] == "UPSELLSEAL-OBJECT", sep
        sepdiff = call(proc, 10, "darkseal_diff_outcome",
                       {"capture_id": sep["capture_id"],
                        "outcome_artifacts": [captures.artifact(
                            "add-on: priority support")]})
        assert sepdiff["verdict"] is None and \
            sepdiff["separation"] == "UPSELLSEAL-OBJECT", sepdiff
        view = call(proc, 11, "darkseal_check",
                    {"capture_id": cid})
        assert view == {"verdict": "PRESELECTED-AND-CHARGED",
                        "charged_elements": ["auto-renew"]}, view
        export = call(proc, 12, "darkseal_export_captures",
                      {"capture_id": cid})
        assert export["chain_head"], export
        fresh = call(proc, 13, "darkseal_recompute",
                     {"capture": export["capture"],
                      "grammar_version": export["grammar_version"],
                      "outcome_artifacts":
                          [captures.artifact("auto-renew")]})
        assert fresh["verdict"] == "PRESELECTED-AND-CHARGED", fresh
        formval = call(proc, 14, "darkseal_seal_defaults",
                       captures.capture(
                           flow_id="flow-form-001",
                           elements=[{"class": "checkbox",
                                      "identity": "add-on",
                                      "default_state": "checked",
                                      "value": "typed-by-principal"}]))
        assert formval["accepted"] is False and \
            formval["error"] == "FIELD_OUTSIDE_GRAMMAR", formval
        print("SMOKE PASS: 6 tools · PRESELECTED-AND-CHARGED · "
              "PRESELECTED-NOT-CHARGED · notary rejected · "
              "below-standard UNVERIFIABLE · UPSELLSEAL-OBJECT "
              "separation · check · export · recompute "
              "reproduced · form-value refused")
        return 0
    finally:
        proc.stdin.close()
        proc.wait(timeout=10)


if __name__ == "__main__":
    sys.exit(main())
