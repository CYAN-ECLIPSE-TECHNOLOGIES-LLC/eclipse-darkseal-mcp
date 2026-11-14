#!/usr/bin/env python3
# Cyan Eclipse Darkseal — requirement-mapped test suite.
# Copyright © 2026 Cyan Eclipse Technologies LLC · cetech.ai
"""Every test names the requirement it verifies (SPEC-DARKSEAL
section 3) and, where the bench plan restates it, the bench
claim (section 6). Builder tests are not bench evidence; they
are the build's own verification that the bench can later
re-run.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "fixtures"))

import logic  # noqa: E402
import darkseal  # noqa: E402
import server  # noqa: E402
import captures  # noqa: E402

KEYS = darkseal.load_surface_keys(
    os.path.join(ROOT, "keys", "surface-keys.json"))

# Gate section 5 / spec P4: none of these strings may appear as
# a verdict, label, or output string on any surface. (This tuple
# is the scan list itself; the scan targets product surfaces and
# outputs, never this file.)
BANNED = ("dark pattern", "dark-pattern", "darkpattern",
          "tricked", "deceived", "merchant intended",
          "ftc violation", "premium verdict")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "state.json")
        self.store = darkseal.Store(self.path, KEYS)

    def seal(self, **kw):
        return self.store.seal_defaults(captures.capture(**kw))

    def seal_and_diff(self, artifacts=(), **kw):
        out = self.seal(**kw)
        cid = out["capture_id"]
        return cid, self.store.diff_outcome(cid, list(artifacts))


class TestOutcomeDiff(Base):
    """DRK-REQ-013 / DK-B1: a charge traceable to a sealed
    pre-selected element verdicts PRESELECTED-AND-CHARGED naming
    it; sealed-but-uncharged verdicts PRESELECTED-NOT-CHARGED;
    clean flows verdict NO-PRESELECTION."""

    def test_preselected_and_charged_names_element(self):
        _, out = self.seal_and_diff(
            artifacts=[captures.artifact("auto-renew")])
        self.assertEqual(out["verdict"], "PRESELECTED-AND-CHARGED")
        self.assertEqual(out["charged_elements"], ["auto-renew"])

    def test_binding_term_also_charges(self):
        _, out = self.seal_and_diff(artifacts=[
            captures.artifact("plan-tier", kind="binding-term")])
        self.assertEqual(out["verdict"], "PRESELECTED-AND-CHARGED")
        self.assertEqual(out["charged_elements"], ["plan-tier"])

    def test_preselected_not_charged(self):
        _, out = self.seal_and_diff(artifacts=[])
        self.assertEqual(out["verdict"], "PRESELECTED-NOT-CHARGED")
        self.assertEqual(out["charged_elements"], [])

    def test_artifact_for_unselected_element_does_not_charge(self):
        _, out = self.seal_and_diff(
            artifacts=[captures.artifact("newsletter-opt-in")])
        self.assertEqual(out["verdict"], "PRESELECTED-NOT-CHARGED")

    def test_clean_flow_no_preselection(self):
        elements = [captures.el("checkbox", "add-on: warranty",
                                "unchecked"),
                    captures.el("toggle", "auto-renew", "off"),
                    captures.el("radio/plan selector", "plan-tier",
                                "none-selected")]
        _, out = self.seal_and_diff(
            artifacts=[captures.artifact("plan-tier")],
            elements=elements)
        self.assertEqual(out["verdict"], "NO-PRESELECTION")

    def test_checkbox_preselected_charged(self):
        elements = [captures.el("checkbox", "insurance add-on",
                                "checked")]
        _, out = self.seal_and_diff(
            artifacts=[captures.artifact("insurance add-on")],
            flow_kind="subscription", elements=elements)
        self.assertEqual(out["verdict"], "PRESELECTED-AND-CHARGED")


class TestRecompute(Base):
    """DRK-REQ-002(iii) / DRK-REQ-014 / DK-B2: a verifier holding
    only the sealed bundle + grammar + artifacts reproduces the
    verdict with no service access."""

    def test_recompute_charged_matches(self):
        cid, out = self.seal_and_diff(
            artifacts=[captures.artifact("auto-renew")])
        export = self.store.export_captures(cid)
        fresh = darkseal.recompute(
            export["capture"], export["grammar_version"],
            [captures.artifact("auto-renew")])
        self.assertEqual(fresh["verdict"], out["verdict"])
        self.assertEqual(fresh["charged_elements"], ["auto-renew"])

    def test_recompute_not_charged_matches(self):
        cid, out = self.seal_and_diff(artifacts=[])
        export = self.store.export_captures(cid)
        fresh = darkseal.recompute(export["capture"],
                                   export["grammar_version"], [])
        self.assertEqual(fresh["verdict"],
                         "PRESELECTED-NOT-CHARGED")

    def test_recompute_unknown_grammar_unverifiable(self):
        cid, _ = self.seal_and_diff(artifacts=[])
        export = self.store.export_captures(cid)
        fresh = darkseal.recompute(export["capture"],
                                   "darkseal-grammar/99", [])
        self.assertEqual(fresh["verdict"], "UNVERIFIABLE")


class TestSealIntegrityRecompute(Base):
    """P6 test shape / cure F-1 (VERDICT-DELTA-20261113, C6):
    recompute verifies the capture's seal and derives the
    capture standard before minting anything. A fabricated or
    tampered capture mints NO verdict class — named refusal,
    fail closed."""

    def _fabricated(self):
        return {
            "capture_id": "drk-fabricated000000",
            "flow_id": "flow-fabricated-001",
            "flow_kind": "signup",
            "elements": [captures.el("continuity switch",
                                     "auto-renew", "on")],
            "grammar_coverage": ["continuity switch"],
            "covered_classes": ["continuity switch"],
            "outside_coverage": [],
            "surface_id": "surface-alpha",
            "traversal_timestamp": "2026-11-11T12:00:00Z",
            "grammar_version": logic.GRAMMAR_VERSION,
            "capture_standard": "full",
            "seal": "0" * 64,
            "separation": None,
            "verdict": None,
            "charged_elements": [],
            "grammar_basis": None,
            "outcome_artifacts": [],
            "receipt_ref": None,
        }

    def test_fabricated_capture_mints_no_verdict(self):
        fresh = darkseal.recompute(
            self._fabricated(), logic.GRAMMAR_VERSION,
            [captures.artifact("auto-renew")])
        self.assertIsNone(fresh["verdict"])
        self.assertEqual(fresh["error"],
                         "SEAL_VERIFICATION_FAILED")

    def test_flipped_element_breaks_seal_refused(self):
        cid, _ = self.seal_and_diff(
            artifacts=[captures.artifact("auto-renew")])
        export = self.store.export_captures(cid)
        tampered = json.loads(json.dumps(export["capture"]))
        for el in tampered["elements"]:
            if el["identity"] == "auto-renew":
                el["default_state"] = "off"
        fresh = darkseal.recompute(
            tampered, logic.GRAMMAR_VERSION,
            [captures.artifact("auto-renew")])
        self.assertIsNone(fresh["verdict"])
        self.assertEqual(fresh["error"],
                         "SEAL_VERIFICATION_FAILED")

    def test_genuine_capture_still_recomputes(self):
        cid, out = self.seal_and_diff(
            artifacts=[captures.artifact("auto-renew")])
        export = self.store.export_captures(cid)
        fresh = darkseal.recompute(
            export["capture"], export["grammar_version"],
            [captures.artifact("auto-renew")])
        self.assertEqual(fresh["verdict"],
                         "PRESELECTED-AND-CHARGED")


class TestCaptureHonesty(Base):
    """DRK-REQ-004 / DRK-REQ-011 / DK-B3: below-standard captures
    verdict UNVERIFIABLE in 100% of cases; out-of-grammar
    elements are named in the coverage statement and never
    judged."""

    def test_malformed_state_below_standard(self):
        elements = [captures.el("checkbox", "add-on", "maybe")]
        out = self.seal(elements=elements)
        self.assertEqual(out["verdict"], "UNVERIFIABLE")
        diff = self.store.diff_outcome(
            out["capture_id"],
            [captures.artifact("add-on")])
        self.assertEqual(diff["verdict"], "UNVERIFIABLE")

    def test_empty_vector_unverifiable(self):
        out = self.seal(elements=[])
        self.assertEqual(out["verdict"], "UNVERIFIABLE")

    def test_no_covered_elements_unverifiable(self):
        elements = [{"class": "canvas-widget", "identity": "hero",
                     "default_state": "active"}]
        out = self.seal(elements=elements)
        self.assertEqual(out["verdict"], "UNVERIFIABLE")
        self.assertEqual(out["outside_coverage"], ["hero"])

    def test_out_of_grammar_named_not_judged(self):
        elements = captures.SIGNUP_ELEMENTS + [
            {"class": "canvas-widget", "identity": "hero-banner",
             "default_state": "active"}]
        cid, out = self.seal_and_diff(
            artifacts=[captures.artifact("hero-banner")],
            elements=elements)
        self.assertEqual(out["verdict"], "PRESELECTED-NOT-CHARGED")
        view = self.store.get_verdict(cid)
        self.assertEqual(view["outside_coverage"], ["hero-banner"])
        self.assertIn("checkbox", view["covered_classes"])


class TestProvenance(Base):
    """DRK-REQ-012 / ADV-1 (DK-K1 guard): bundles from any
    non-executing source are rejected and receipted; zero
    witnessed records are created."""

    def _rejected(self, **kw):
        out = self.seal(**kw)
        self.assertFalse(out["accepted"])
        self.assertEqual(out["error"], "PROVENANCE_FAILURE")
        self.assertEqual(len(self.store.captures), 0)
        ok, _ = self.store.verify_chain()
        self.assertTrue(ok)
        self.assertEqual(self.store.journal[-1]["kind"],
                         "capture_rejected_provenance")

    def test_notary_submission_rejected(self):
        self._rejected(source="standalone-notary")

    def test_merchant_submission_rejected(self):
        self._rejected(source="merchant-submitted")

    def test_relayed_capture_rejected(self):
        self._rejected(source="integration-relay")

    def test_forged_attestation_rejected(self):
        cap = captures.capture()
        cap["surface_attestation"] = "0" * 64
        out = self.store.seal_defaults(cap)
        self.assertFalse(out["accepted"])
        self.assertEqual(len(self.store.captures), 0)

    def test_wrong_surface_key_rejected(self):
        self._rejected(key="fixture-surface-key-surface-beta")

    def test_unregistered_surface_rejected(self):
        self._rejected(surface_id="surface-unknown")


class TestCustody(Base):
    """DRK-REQ-005 / DK-B4: the store contains only the section
    2 field set; form-field values are never captured, held, or
    sealed."""

    def test_form_value_element_refused(self):
        elements = [{"class": "checkbox", "identity": "add-on",
                     "default_state": "checked",
                     "value": "jane@example.com"}]
        out = self.seal(elements=elements)
        self.assertFalse(out["accepted"])
        self.assertEqual(out["error"], "FIELD_OUTSIDE_GRAMMAR")
        self.assertEqual(len(self.store.captures), 0)
        with open(self.path, encoding="utf-8") as fh:
            self.assertNotIn("jane@example.com", fh.read())

    def test_record_field_set_exact(self):
        out = self.seal()
        record = self.store.captures[out["capture_id"]]
        self.assertEqual(set(record.keys()),
                         set(darkseal.CAPTURE_FIELDS))
        for el in record["elements"]:
            self.assertEqual(set(el.keys()),
                             set(logic.ELEMENT_FIELDS))

    def test_artifact_extra_field_refused(self):
        out = self.seal()
        bad = {"artifact_digest": "x" * 8,
               "element_identity": "auto-renew", "kind": "charge",
               "merchant_account": "m-123"}
        diff = self.store.diff_outcome(out["capture_id"], [bad])
        self.assertFalse(diff["accepted"])
        self.assertEqual(diff["error"], "ARTIFACT_FIELD_VIOLATION")
        record = self.store.captures[out["capture_id"]]
        self.assertIsNone(record["verdict"])
        self.assertEqual(record["outcome_artifacts"], [])


class TestSeparation(Base):
    """DRK-REQ-010 / DK-B5 (second half) / ADV-2: the DK-C10
    separation fixture set — Darkseal-only fixtures verdict;
    the Upsellseal-object checkout fixture is marked and mints
    no duplicate whole-flow verdict."""

    def test_upsellseal_object_marked_no_verdict(self):
        out = self.store.seal_defaults(
            captures.upsellseal_object_fixture())
        self.assertEqual(out["separation"], "UPSELLSEAL-OBJECT")
        diff = self.store.diff_outcome(
            out["capture_id"],
            [captures.artifact("add-on: priority support")])
        self.assertIsNone(diff["verdict"])
        self.assertEqual(diff["separation"], "UPSELLSEAL-OBJECT")
        view = self.store.get_verdict(out["capture_id"])
        self.assertIsNone(view["verdict"])

    def test_upsellseal_object_recompute_separates(self):
        out = self.store.seal_defaults(
            captures.upsellseal_object_fixture())
        export = self.store.export_captures(out["capture_id"])
        fresh = darkseal.recompute(export["capture"],
                                   export["grammar_version"], [])
        self.assertIsNone(fresh["verdict"])
        self.assertEqual(fresh["separation"], "UPSELLSEAL-OBJECT")

    def test_plan_fixture_verdicts(self):
        out = self.store.seal_defaults(captures.plan_fixture())
        self.assertIsNone(out["separation"])
        diff = self.store.diff_outcome(
            out["capture_id"],
            [captures.artifact("plan-tier", kind="binding-term")])
        self.assertEqual(diff["verdict"], "PRESELECTED-AND-CHARGED")

    def test_continuity_fixture_verdicts(self):
        out = self.store.seal_defaults(
            captures.continuity_fixture())
        diff = self.store.diff_outcome(
            out["capture_id"], [captures.artifact("auto-renew")])
        self.assertEqual(diff["verdict"], "PRESELECTED-AND-CHARGED")

    def test_signup_fixture_verdicts(self):
        out = self.store.seal_defaults(captures.signup_fixture())
        diff = self.store.diff_outcome(out["capture_id"], [])
        self.assertEqual(diff["verdict"], "PRESELECTED-NOT-CHARGED")

    def test_checkout_with_plan_is_whole_flow(self):
        elements = [captures.el("checkbox", "add-on: warranty",
                                "checked"),
                    captures.el("radio/plan selector", "plan-tier",
                                "Pro (annual)")]
        out = self.seal(flow_kind="checkout", elements=elements)
        self.assertIsNone(out["separation"])
        diff = self.store.diff_outcome(
            out["capture_id"],
            [captures.artifact("plan-tier", kind="binding-term")])
        self.assertEqual(diff["verdict"], "PRESELECTED-AND-CHARGED")


class TestGrammarVersioning(Base):
    """DRK-REQ-007 / DK-B5 (first half): verdicts name their
    grammar version; a revision never retro-alters a minted
    verdict."""

    def test_verdict_names_grammar_version(self):
        _, out = self.seal_and_diff(artifacts=[])
        self.assertEqual(out["grammar_version"],
                         logic.GRAMMAR_VERSION)

    def test_revision_does_not_rewrite(self):
        cid, out = self.seal_and_diff(
            artifacts=[captures.artifact("auto-renew")])
        before = json.dumps(self.store.captures[cid],
                            sort_keys=True)
        logic.GRAMMARS["darkseal-grammar/2"] = \
            logic.ELEMENT_CLASSES + ("slider",)
        try:
            after = json.dumps(self.store.captures[cid],
                               sort_keys=True)
            self.assertEqual(before, after)
            export = self.store.export_captures(cid)
            fresh = darkseal.recompute(
                export["capture"], "darkseal-grammar/1",
                [captures.artifact("auto-renew")])
            self.assertEqual(fresh["verdict"],
                             "PRESELECTED-AND-CHARGED")
        finally:
            del logic.GRAMMARS["darkseal-grammar/2"]


class TestReceiptChain(Base):
    """DRK-REQ-015: one receipt per capture and per verdict;
    the chain verifies end-to-end; tamper and truncation are
    detected; a tampered store fails closed."""

    def test_chain_verifies_and_counts(self):
        cid, _ = self.seal_and_diff(
            artifacts=[captures.artifact("auto-renew")])
        ok, head = self.store.verify_chain()
        self.assertTrue(ok)
        kinds = [e["kind"] for e in self.store.journal]
        self.assertEqual(kinds, ["default_state_capture",
                                 "verdict"])
        export = self.store.export_captures(cid)
        self.assertEqual(export["chain_head"], head)

    def test_tamper_detected(self):
        self.seal()
        journal = json.loads(json.dumps(self.store.journal))
        journal[0]["payload_digest"] = "0" * 64
        ok, _ = self.store.verify_chain(journal)
        self.assertFalse(ok)

    def test_truncated_export_detected(self):
        cid, _ = self.seal_and_diff(artifacts=[])
        self.seal(flow_id="flow-second-001")
        export = self.store.export_captures(cid)
        ok, head = self.store.verify_chain(
            self.store.journal[:-1])
        self.assertTrue(ok)
        self.assertNotEqual(head, export["chain_head"])

    def test_store_fails_closed_on_tampered_verdict(self):
        # P6 test shape / cure F-2 (VERDICT-DELTA-20261113, C8):
        # a state-file edit flipping a minted verdict must be
        # refused loudly at load, never served.
        cid, _ = self.seal_and_diff(
            artifacts=[captures.artifact("auto-renew")])
        with open(self.path, encoding="utf-8") as fh:
            data = json.load(fh)
        data["captures"][cid]["verdict"] = "NO-PRESELECTION"
        data["captures"][cid]["charged_elements"] = []
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        with self.assertRaises(ValueError):
            darkseal.Store(self.path, KEYS)

    def test_store_fails_closed_on_tampered_element(self):
        cid, _ = self.seal_and_diff(artifacts=[])
        with open(self.path, encoding="utf-8") as fh:
            data = json.load(fh)
        for el in data["captures"][cid]["elements"]:
            if el["identity"] == "auto-renew":
                el["default_state"] = "off"
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        with self.assertRaises(ValueError):
            darkseal.Store(self.path, KEYS)

    def test_genuine_store_reloads_and_serves(self):
        cid, _ = self.seal_and_diff(
            artifacts=[captures.artifact("auto-renew")])
        reloaded = darkseal.Store(self.path, KEYS)
        view = reloaded.check(cid)
        self.assertEqual(view["verdict"],
                         "PRESELECTED-AND-CHARGED")
        self.assertEqual(view["charged_elements"], ["auto-renew"])

    def test_store_fails_closed_on_tampered_journal(self):
        self.seal()
        with open(self.path, encoding="utf-8") as fh:
            data = json.load(fh)
        data["journal"][0]["payload_digest"] = "0" * 64
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        with self.assertRaises(ValueError):
            darkseal.Store(self.path, KEYS)


class TestFreeShape(Base):
    """DRK-REQ-016 / DRK-REQ-003: no metering exists anywhere in
    the product — no charge event, no per-check price, no tier
    parameter; the verdict grammar is the same on every call."""

    def test_no_metering_anywhere(self):
        self.seal_and_diff(
            artifacts=[captures.artifact("auto-renew")])
        self.assertFalse(hasattr(self.store, "metering"))
        with open(self.path, encoding="utf-8") as fh:
            blob = fh.read().lower()
        for token in ("metering", "\"price\"", "\"amount\"",
                      "charge_amount", "per_check"):
            self.assertNotIn(token, blob)
        schema_blob = json.dumps(server.SCHEMAS).lower()
        for token in ("tier", "price", "payment", "plan"):
            self.assertNotIn(token, schema_blob)

    def test_verdict_grammar_fixed(self):
        self.assertEqual(
            set(logic.VERDICTS),
            {"PRESELECTED-AND-CHARGED", "PRESELECTED-NOT-CHARGED",
             "NO-PRESELECTION", "UNVERIFIABLE"})


class TestInterface(Base):
    """DRK-REQ-014: tool inventory == section 4.1 exactly;
    check reveals verdict + charged element names only; no
    banned term appears on any output surface."""

    def test_tool_inventory_exact(self):
        self.assertEqual(
            list(server.SCHEMAS.keys()),
            ["darkseal_seal_defaults", "darkseal_diff_outcome",
             "darkseal_get_verdict", "darkseal_check",
             "darkseal_recompute", "darkseal_export_captures"])
        manifest = json.load(open(os.path.join(
            ROOT, "tools-manifest.json"), encoding="utf-8"))
        self.assertEqual(manifest["tools"],
                         list(server.SCHEMAS.keys()))

    def test_no_such_tool_for_aggregation_or_merchant(self):
        for name in ("darkseal_merchant_stats",
                     "darkseal_aggregate", "darkseal_audit_site"):
            self.assertEqual(server.call_tool(name, {}),
                             {"error": "NO_SUCH_TOOL"})

    def test_check_reveals_names_only(self):
        st = server.store()
        out = st.seal_defaults(captures.capture(
            flow_id="flow-api-check-001"))
        cid = out["capture_id"]
        st.diff_outcome(cid, [captures.artifact("auto-renew")])
        view = server.call_tool("darkseal_check",
                                {"capture_id": cid})
        self.assertEqual(set(view.keys()),
                         {"verdict", "charged_elements"})
        self.assertEqual(view["verdict"],
                         "PRESELECTED-AND-CHARGED")

    def test_banned_terms_absent_from_surfaces(self):
        blob = json.dumps(server.DESCRIPTIONS) + darkseal.CLAIM
        for name in ("README.md", "GRAMMAR.md", "WATCH.md",
                     "tools-manifest.json"):
            with open(os.path.join(ROOT, name),
                      encoding="utf-8") as fh:
                blob += fh.read()
        for term in BANNED:
            self.assertNotIn(term, blob.lower())

    def test_banned_terms_absent_from_outputs(self):
        outputs = []
        cid, diff = self.seal_and_diff(
            artifacts=[captures.artifact("auto-renew")])
        outputs.append(diff)
        outputs.append(self.store.get_verdict(cid))
        outputs.append(self.store.check(cid))
        outputs.append(self.store.export_captures(cid))
        out2 = self.store.seal_defaults(
            captures.upsellseal_object_fixture())
        outputs.append(self.store.diff_outcome(
            out2["capture_id"], []))
        outputs.append(self.seal(source="standalone-notary"))
        blob = json.dumps(outputs).lower()
        for term in BANNED:
            self.assertNotIn(term, blob)

    def test_no_aggregation_surface(self):
        names = [n for n in dir(darkseal.Store)
                 if not n.startswith("_")]
        names += list(server.SCHEMAS.keys())
        for token in ("aggregat", "stats", "dossier", "feed",
                      "insight", "merchant"):
            self.assertFalse(any(token in n for n in names),
                             f"aggregation surface present: {token}")


if __name__ == "__main__":
    unittest.main()
