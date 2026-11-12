#!/usr/bin/env python3
# Cyan Eclipse Darkseal — element grammar + outcome-diff engine
# (SPEC-DARKSEAL sections 2, 3; gate DK-C4/C7/C10).
# Copyright © 2026 Cyan Eclipse Technologies LLC · cetech.ai
"""Pure verdict logic. Holds no state and reads no store: given a
sealed traversal-start element vector and the principal's own
outcome artifacts, it mints exactly one verdict from the fixed
grammar:

  PRESELECTED-AND-CHARGED · PRESELECTED-NOT-CHARGED ·
  NO-PRESELECTION · UNVERIFIABLE

The comparison runs under the published element grammar
(GRAMMAR.md, `darkseal-grammar/1`):

  - element classes (the bounded v1 set, DK-C10): checkbox ·
    toggle · radio/plan selector · continuity switch. An element
    outside these classes is outside the grammar's coverage: it is
    reported in the coverage statement, never judged;
  - pre-selection rules (per class): a checkbox rendered
    "checked", a toggle rendered "on", a continuity switch
    rendered "on", and a radio/plan selector rendered with a
    chosen option are pre-selected; every other rendered state is
    not;
  - field discipline: an element record is exactly {class,
    identity, default_state}. Anything more — above all a
    form-field value — is outside the record grammar (DK-C5);
  - the diff runs over the sealed defaults plus the principal's
    own confirmation/charge artifacts only. Merchant-side records
    are never diff inputs (DRK-REQ-013).

Verdicts name facts only — element identities, rendered states,
and the grammar basis. No string in this module speaks to what
any person saw, understood, agreed to, or meant, and no verdict
carries any label the gate bans (spec section 5, P4).
"""
import hashlib
import json

GRAMMAR_VERSION = "darkseal-grammar/1"

VERDICTS = ("PRESELECTED-AND-CHARGED", "PRESELECTED-NOT-CHARGED",
            "NO-PRESELECTION", "UNVERIFIABLE")

ELEMENT_CLASSES = ("checkbox", "toggle", "radio/plan selector",
                   "continuity switch")

ELEMENT_FIELDS = ("class", "identity", "default_state")

ARTIFACT_FIELDS = ("artifact_digest", "element_identity", "kind")
ARTIFACT_KINDS = ("charge", "binding-term")

# Rendered-state conventions per class (GRAMMAR.md carries the
# same table; the two are kept in step). For the radio/plan
# selector the rendered state is the identity of the option shown
# chosen, or the sentinel "none-selected".
_BINARY_STATES = {
    "checkbox": ("checked", "unchecked"),
    "toggle": ("on", "off"),
    "continuity switch": ("on", "off"),
}
_PRESELECTED_STATE = {"checkbox": "checked", "toggle": "on",
                      "continuity switch": "on"}
SELECTOR_NONE = "none-selected"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def digest_obj(obj) -> str:
    return sha(canon(obj))


def element_problem(element):
    """None when the element record conforms to the grammar's
    record shape, else a short problem string. A record carrying
    any field beyond the three grammar fields — a form-field
    value above all — does not conform (DK-C5)."""
    if not isinstance(element, dict):
        return "element_not_an_object"
    if set(element.keys()) - set(ELEMENT_FIELDS):
        return "field_outside_grammar"
    if set(element.keys()) != set(ELEMENT_FIELDS):
        return "field_missing"
    if not str(element.get("identity") or "").strip():
        return "identity_missing"
    cls = element.get("class")
    state = element.get("default_state")
    if cls in _BINARY_STATES:
        if state not in _BINARY_STATES[cls]:
            return "state_outside_grammar"
    elif cls == "radio/plan selector":
        if not isinstance(state, str) or not state.strip():
            return "state_outside_grammar"
    return None


def is_covered(element) -> bool:
    return isinstance(element, dict) and \
        element.get("class") in ELEMENT_CLASSES


def is_preselected(element) -> bool:
    """The grammar's pre-selection rule for one covered element."""
    cls = element.get("class")
    state = element.get("default_state")
    if cls == "radio/plan selector":
        return isinstance(state, str) and \
            state.strip() not in ("", SELECTOR_NONE)
    return _PRESELECTED_STATE.get(cls) == state


def coverage_of(elements):
    """Split a presented element vector into the grammar-covered
    elements and the outside-coverage identities, and name the
    covered classes (DRK-REQ-011)."""
    covered, outside = [], []
    for el in elements if isinstance(elements, list) else []:
        if is_covered(el):
            covered.append(el)
        elif isinstance(el, dict):
            outside.append(str(el.get("identity") or "<unnamed>"))
        else:
            outside.append("<unnamed>")
    classes = sorted({el["class"] for el in covered})
    return covered, outside, classes


def separation_class(flow_kind, covered_elements):
    """The DK-C10 separation classification. Upsellseal's object
    is the add-on default vector at a checkout decision: a
    checkout flow whose pre-selected covered elements are ALL
    checkbox-class add-on defaults is that object, and Darkseal
    mints no duplicate whole-flow verdict for it. Everything else
    — plan pre-selection, continuity toggles, signup flows with
    no checkout — is Darkseal's whole-flow object."""
    preselected = [el for el in covered_elements
                   if is_preselected(el)]
    if flow_kind == "checkout" and preselected and all(
            el["class"] == "checkbox" for el in preselected):
        return "UPSELLSEAL-OBJECT"
    return None


def diff_outcome(elements, outcome_artifacts,
                 grammar_version: str = GRAMMAR_VERSION) -> dict:
    """Diff the principal's outcome artifacts against the sealed
    default vector (DRK-REQ-013). Returns the verdict fields:
    verdict · charged_elements · grammar_basis ·
    grammar_version. `elements` is the sealed covered vector;
    `outcome_artifacts` are the principal's own artifacts,
    already field-validated by the caller."""
    base = {"grammar_version": grammar_version,
            "charged_elements": [], "grammar_basis": None}
    if grammar_version not in GRAMMARS:
        return {**base, "verdict": "UNVERIFIABLE",
                "grammar_basis": "unknown_grammar_version"}
    preselected = [el["identity"] for el in elements
                   if is_preselected(el)]
    charged = []
    for artifact in outcome_artifacts or []:
        target = artifact.get("element_identity")
        if target in preselected and target not in charged:
            charged.append(target)
    if preselected and charged:
        return {**base, "verdict": "PRESELECTED-AND-CHARGED",
                "charged_elements": charged,
                "grammar_basis": "sealed_default_produced_outcome"}
    if preselected:
        return {**base, "verdict": "PRESELECTED-NOT-CHARGED",
                "grammar_basis": "sealed_default_no_outcome"}
    return {**base, "verdict": "NO-PRESELECTION",
            "grammar_basis": "no_preselected_element"}


# Grammar registry: version -> element-class set. A revision adds
# a new version; minted verdicts keep the version they name and
# are never recomputed under a later one (DK-C7).
GRAMMARS = {GRAMMAR_VERSION: ELEMENT_CLASSES}
