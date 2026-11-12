#!/usr/bin/env python3
# Cyan Eclipse Darkseal — seal store, executing-surface
# provenance, receipt chain (SPEC-DARKSEAL sections 2-4).
# Copyright © 2026 Cyan Eclipse Technologies LLC · cetech.ai
"""State layer for the Darkseal MCP server.

Custody (DK-C5 / DRK-REQ-005): the store carries ONLY the
section 2 field set — element class + identity as presented,
default state as rendered, flow identity, timestamps, seals,
outcome-artifact digests, verdict + named grammar basis.
Form-field values are never captured, held, or sealed: an
element record carrying any field beyond the grammar's three is
refused outright, the refusal receipted, and nothing is retained.
No page bodies, no browsing history, no principal profile.

Provenance (DK-C4 / DRK-REQ-012, the DK-K1 guard): a default
state is witnessed only when it arrives from the executing
surface's own witness module — source == "executing-surface", an
HMAC attestation from the surface registered for that channel,
and a binding reference to the traversal event. Bundles from any
other source — a standalone notary, a merchant, a third-party
integration — are rejected, the rejection receipted, and zero
witnessed records are created.

Capture standard (DK-C4): a capture whose grammar-covered
elements cannot be enumerated to the section 2 standard mints
UNVERIFIABLE and nothing else; no other verdict is mintable from
a below-standard bundle.

Separation (DK-C10): a checkout capture whose pre-selected
elements are all checkbox-class add-on defaults is Upsellseal's
object; the record is marked UPSELLSEAL-OBJECT and Darkseal
mints no duplicate whole-flow verdict for it.

FREE shape (DK-C3 / DRK-REQ-016): there is no metering anywhere
in this module — no charge event, no per-check price, no premium
tier. Verdict wording is identical at every tier because there
is only the free check.

Aggregation fence (DK-C6): per-principal, per-record reads only.
There is no cross-principal aggregation code path.
"""
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import logic  # noqa: E402

TOOL_VERSION = "0.1.0"
SERVER_ID = "eclipse-darkseal"

CLAIM = ("Darkseal seals the state the flow started in — every "
         "pre-ticked add-on, pre-chosen plan, and continuity "
         "toggle, element by element — at the moment your agent "
         "entered it. If a charge began as a default you never "
         "chose, the sealed record names the element it began "
         "as, and anyone can recompute the verdict from the "
         "record itself.")

# The whole store field set (SPEC section 2, plus the DK-C10
# separation marker the separation deliverable requires).
# Nothing else is written into a record. (DK-C5 / DRK-REQ-005.)
CAPTURE_FIELDS = ("capture_id", "flow_id", "flow_kind",
                  "elements", "grammar_coverage",
                  "covered_classes", "outside_coverage",
                  "surface_id", "traversal_timestamp",
                  "grammar_version", "capture_standard", "seal",
                  "separation", "verdict", "charged_elements",
                  "grammar_basis", "outcome_artifacts",
                  "receipt_ref")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Store:
    """JSON record store + hash-chained receipt journal. Fails
    closed: a journal that does not verify at load raises."""

    def __init__(self, state_path: str, surface_keys: dict):
        self.state_path = state_path
        self.surface_keys = surface_keys  # surface_id -> key
        self.captures = {}
        self.journal = []
        if os.path.exists(state_path):
            with open(state_path, encoding="utf-8") as fh:
                data = json.load(fh)
            self.captures = data.get("captures", {})
            self.journal = data.get("journal", [])
            ok, _ = self.verify_chain()
            if not ok:
                raise ValueError("receipt journal failed "
                                 "verification at load; store "
                                 "fails closed")

    # ---------------------------------------------------------- io
    def _save(self):
        tmp = self.state_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"captures": self.captures,
                       "journal": self.journal}, fh,
                      indent=1, sort_keys=True)
        os.replace(tmp, self.state_path)

    # --------------------------------------------------- receipts
    def _append_receipt(self, kind: str, payload: dict) -> dict:
        prev = self.journal[-1]["record_hash"] if self.journal \
            else "GENESIS"
        entry = {"seq": len(self.journal) + 1,
                 "timestamp": _now(), "kind": kind,
                 "payload_digest": logic.digest_obj(payload),
                 "prev_hash": prev}
        entry["record_hash"] = logic.digest_obj(
            {k: entry[k] for k in
             ("seq", "timestamp", "kind", "payload_digest",
              "prev_hash")})
        self.journal.append(entry)
        return entry

    def verify_chain(self, journal=None):
        journal = self.journal if journal is None else journal
        prev = "GENESIS"
        for entry in journal:
            if entry.get("prev_hash") != prev:
                return False, f"link broken at seq {entry.get('seq')}"
            expect = logic.digest_obj(
                {k: entry.get(k) for k in
                 ("seq", "timestamp", "kind", "payload_digest",
                  "prev_hash")})
            if entry.get("record_hash") != expect:
                return False, \
                    f"hash mismatch at seq {entry.get('seq')}"
            prev = entry["record_hash"]
        return True, prev

    def chain_head(self) -> str:
        return self.journal[-1]["record_hash"] if self.journal \
            else "GENESIS"

    # ------------------------------------------------- provenance
    def _attestation_valid(self, surface_id, flow_id,
                           core: dict, attestation) -> bool:
        key = self.surface_keys.get(surface_id)
        if not key or not attestation:
            return False
        msg = (flow_id + "|" + logic.canon(core)).encode()
        expect = hmac.new(key.encode(), msg,
                          hashlib.sha256).hexdigest()
        return hmac.compare_digest(expect, attestation)

    @staticmethod
    def make_attestation(key: str, flow_id: str,
                         core: dict) -> str:
        """The surface side of the channel: the executing
        surface's witness module, holding its registered channel
        key, attests a capture core bound to the traversal's flow
        identity."""
        msg = (flow_id + "|" + logic.canon(core)).encode()
        return hmac.new(key.encode(), msg,
                        hashlib.sha256).hexdigest()

    # ------------------------------------------------ seal defaults
    def seal_defaults(self, capture: dict) -> dict:
        """Seal a traversal-start default-state capture from the
        executing surface (DRK-REQ-002(i), DRK-REQ-012)."""
        flow_id = capture.get("flow_id")
        # Custody gate first (DK-C5): an element carrying any
        # field beyond the grammar's three — a form-field value
        # above all — refuses the whole capture; nothing at all
        # is retained from it.
        elements = capture.get("elements")
        if isinstance(elements, list):
            for i, el in enumerate(elements):
                if isinstance(el, dict):
                    extra = set(el.keys()) - \
                        set(logic.ELEMENT_FIELDS)
                    if extra:
                        receipt = self._append_receipt(
                            "capture_refused_field_set",
                            {"flow_id": flow_id,
                             "element_index": i,
                             "field": sorted(extra)[0]})
                        self._save()
                        return {"accepted": False,
                                "error": "FIELD_OUTSIDE_GRAMMAR",
                                "field": sorted(extra)[0],
                                "receipt_ref":
                                    receipt["record_hash"]}
        core = {k: capture.get(k) for k in
                ("flow_kind", "elements", "grammar_coverage",
                 "surface_id", "traversal_timestamp")}
        provenance_ok = (
            capture.get("source") == "executing-surface"
            and bool(flow_id)
            and self._attestation_valid(
                capture.get("surface_id"), flow_id or "", core,
                capture.get("surface_attestation")))
        if not provenance_ok:
            # ADV-1 (DK-K1 guard): bundles from a non-executing
            # party are rejected on provenance, the rejection
            # receipted, and zero witnessed records are created.
            receipt = self._append_receipt(
                "capture_rejected_provenance",
                {"flow_id": flow_id,
                 "source": capture.get("source"),
                 "surface_id": capture.get("surface_id"),
                 "reason": "provenance_failure"})
            self._save()
            return {"accepted": False,
                    "error": "PROVENANCE_FAILURE",
                    "receipt_ref": receipt["record_hash"]}

        covered, outside, classes = logic.coverage_of(elements)
        problems = [logic.element_problem(el) for el in covered]
        standard = "full"
        if not isinstance(elements, list) or not covered or \
                any(p is not None for p in problems):
            # DK-C4: below the capture standard, UNVERIFIABLE is
            # the only mintable verdict.
            standard = "below-standard"
        bundle = {
            "flow_id": flow_id,
            "flow_kind": capture.get("flow_kind") or "other",
            "elements": covered,
            "grammar_coverage":
                list(capture.get("grammar_coverage") or classes),
            "surface_id": capture.get("surface_id"),
            "traversal_timestamp":
                capture.get("traversal_timestamp") or _now(),
            "grammar_version": logic.GRAMMAR_VERSION,
            "capture_standard": standard,
        }
        capture_id = "drk-" + logic.digest_obj(bundle)[:16]
        if capture_id in self.captures:
            return {"accepted": False, "error": "DUPLICATE_CAPTURE",
                    "capture_id": capture_id}
        record = {
            "capture_id": capture_id,
            "flow_id": bundle["flow_id"],
            "flow_kind": bundle["flow_kind"],
            "elements": bundle["elements"],
            "grammar_coverage": bundle["grammar_coverage"],
            "covered_classes": classes,
            "outside_coverage": outside,
            "surface_id": bundle["surface_id"],
            "traversal_timestamp": bundle["traversal_timestamp"],
            "grammar_version": logic.GRAMMAR_VERSION,
            "capture_standard": standard,
            "seal": logic.digest_obj(bundle),
            "separation": logic.separation_class(
                bundle["flow_kind"], covered)
            if standard == "full" else None,
            "verdict": "UNVERIFIABLE" if standard != "full"
            else None,
            "charged_elements": [],
            "grammar_basis": "below_capture_standard"
            if standard != "full" else None,
            "outcome_artifacts": [],
            "receipt_ref": None,
        }
        receipt = self._append_receipt(
            "default_state_capture",
            {"capture_id": capture_id, "seal": record["seal"],
             "capture_standard": standard,
             "separation": record["separation"]})
        record["receipt_ref"] = receipt["record_hash"]
        assert set(record.keys()) == set(CAPTURE_FIELDS)
        self.captures[capture_id] = record
        self._save()
        return {"accepted": True, "capture_id": capture_id,
                "receipt_ref": record["receipt_ref"],
                "grammar_version": logic.GRAMMAR_VERSION,
                "covered_classes": classes,
                "outside_coverage": outside,
                "separation": record["separation"],
                "verdict": record["verdict"]}

    # ------------------------------------------------ outcome diff
    def diff_outcome(self, capture_id: str,
                     outcome_artifacts) -> dict:
        """Mint the verdict over the sealed defaults + the
        principal's own artifacts (DRK-REQ-013)."""
        record = self.captures.get(capture_id)
        if record is None:
            return {"accepted": False, "error": "NO_SUCH_CAPTURE"}
        if record["verdict"] is not None:
            return {"accepted": True, "capture_id": capture_id,
                    "verdict": record["verdict"],
                    "charged_elements": record["charged_elements"],
                    "grammar_version": record["grammar_version"],
                    "receipt_ref": record["receipt_ref"],
                    "already_minted": True}
        # Artifact field discipline: an outcome artifact is
        # exactly a digest + the element it traces to + its kind.
        # Anything else — a merchant-side record shape above all —
        # is refused as a diff input.
        if not isinstance(outcome_artifacts, list):
            return {"accepted": False,
                    "error": "ARTIFACT_FIELD_VIOLATION"}
        for artifact in outcome_artifacts:
            if not isinstance(artifact, dict) or \
                    set(artifact.keys()) != \
                    set(logic.ARTIFACT_FIELDS) or \
                    artifact.get("kind") not in \
                    logic.ARTIFACT_KINDS or \
                    not str(artifact.get("artifact_digest")
                            or "").strip():
                receipt = self._append_receipt(
                    "outcome_diff_refused_artifact",
                    {"capture_id": capture_id,
                     "reason": "artifact_field_violation"})
                self._save()
                return {"accepted": False,
                        "error": "ARTIFACT_FIELD_VIOLATION",
                        "receipt_ref": receipt["record_hash"]}
        if record["separation"] == "UPSELLSEAL-OBJECT":
            # DK-C10 / ADV-2: this residue is Upsellseal's object;
            # Darkseal mints no duplicate whole-flow verdict.
            receipt = self._append_receipt(
                "diff_separation_no_verdict",
                {"capture_id": capture_id,
                 "separation": "UPSELLSEAL-OBJECT"})
            self._save()
            return {"accepted": True, "capture_id": capture_id,
                    "verdict": None,
                    "separation": "UPSELLSEAL-OBJECT",
                    "receipt_ref": receipt["record_hash"]}
        verdict = logic.diff_outcome(
            record["elements"], outcome_artifacts,
            record["grammar_version"])
        record["outcome_artifacts"] = [
            {"artifact_digest": a["artifact_digest"],
             "element_identity": a["element_identity"],
             "kind": a["kind"]} for a in outcome_artifacts]
        record["verdict"] = verdict["verdict"]
        record["charged_elements"] = verdict["charged_elements"]
        record["grammar_basis"] = verdict["grammar_basis"]
        receipt = self._append_receipt(
            "verdict",
            {"capture_id": capture_id,
             "verdict": verdict["verdict"],
             "charged_elements": verdict["charged_elements"],
             "grammar_version": record["grammar_version"]})
        self._save()
        return {"accepted": True, "capture_id": capture_id,
                "verdict": verdict["verdict"],
                "charged_elements": verdict["charged_elements"],
                "grammar_version": record["grammar_version"],
                "receipt_ref": receipt["record_hash"]}

    # ------------------------------------------------------- reads
    def get_verdict(self, capture_id: str) -> dict:
        record = self.captures.get(capture_id)
        if record is None:
            return {"error": "NO_SUCH_CAPTURE"}
        return {"capture_id": capture_id,
                "verdict": record["verdict"],
                "charged_elements": record["charged_elements"],
                "grammar_version": record["grammar_version"],
                "grammar_coverage": record["grammar_coverage"],
                "covered_classes": record["covered_classes"],
                "outside_coverage": record["outside_coverage"],
                "separation": record["separation"],
                "receipt_refs": [record["receipt_ref"]]}

    def check(self, capture_id: str) -> dict:
        """Counterparty view (DRK-REQ-014): the verdict class
        and the names of charged elements only."""
        record = self.captures.get(capture_id)
        if record is None:
            return {"error": "NO_SUCH_CAPTURE"}
        return {"verdict": record["verdict"],
                "charged_elements": record["charged_elements"]}

    def export_captures(self, capture_id: str) -> dict:
        record = self.captures.get(capture_id)
        if record is None:
            return {"error": "NO_SUCH_CAPTURE"}
        return {"capture": dict(record),
                "chain_head": self.chain_head(),
                "grammar_version": record["grammar_version"]}


def recompute(capture: dict, grammar_version: str,
              outcome_artifacts) -> dict:
    """Third-party recomputation (DRK-REQ-002(iii),
    DRK-REQ-014): the verdict from the exported capture + the
    published element grammar + the outcome artifacts. Reads no
    service state. A below-standard capture recomputes to
    UNVERIFIABLE; an UPSELLSEAL-OBJECT capture recomputes to the
    separation marker, never a whole-flow verdict."""
    cap = capture.get("capture", capture)
    if grammar_version not in logic.GRAMMARS:
        return {"verdict": "UNVERIFIABLE",
                "reason": "unknown_grammar_version"}
    if cap.get("capture_standard") != "full":
        return {"verdict": "UNVERIFIABLE",
                "grammar_version": grammar_version}
    covered, _, _ = logic.coverage_of(cap.get("elements"))
    if logic.separation_class(cap.get("flow_kind"), covered) == \
            "UPSELLSEAL-OBJECT":
        return {"verdict": None,
                "separation": "UPSELLSEAL-OBJECT",
                "grammar_version": grammar_version}
    verdict = logic.diff_outcome(covered, outcome_artifacts or [],
                                 grammar_version)
    return {"verdict": verdict["verdict"],
            "charged_elements": verdict["charged_elements"],
            "grammar_version": grammar_version}


def load_surface_keys(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh).get("surface_keys", {})
