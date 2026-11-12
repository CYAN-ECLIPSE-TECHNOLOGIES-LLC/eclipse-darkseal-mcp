#!/usr/bin/env python3
# Cyan Eclipse Darkseal — fixture capture builder.
# Copyright © 2026 Cyan Eclipse Technologies LLC · cetech.ai
"""Builds traversal-start captures the way the executing
surface's witness module presents them: the element vector as
rendered, flow identity, grammar coverage, and the surface's
HMAC attestation over (flow_id | canonical core). Also builds
the principal's outcome artifacts (digests only) and the
DK-C10 separation fixtures.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
import darkseal  # noqa: E402
import logic  # noqa: E402

KEY = "fixture-surface-key-surface-alpha"

# A signup flow (no checkout, no charge possible at traversal):
# a pre-chosen plan + a continuity toggle that started on.
SIGNUP_ELEMENTS = [
    {"class": "radio/plan selector", "identity": "plan-tier",
     "default_state": "Pro (annual)"},
    {"class": "continuity switch", "identity": "auto-renew",
     "default_state": "on"},
    {"class": "checkbox", "identity": "newsletter-opt-in",
     "default_state": "unchecked"},
]
COVERAGE = ["checkbox", "continuity switch", "radio/plan selector",
            "toggle"]


def el(cls, identity, state):
    return {"class": cls, "identity": identity,
            "default_state": state}


def capture(flow_id="flow-signup-001", flow_kind="signup",
            elements=None, source="executing-surface",
            surface_id="surface-alpha", key=KEY,
            coverage=None, **overrides):
    cap = {
        "flow_id": flow_id,
        "flow_kind": flow_kind,
        "elements": SIGNUP_ELEMENTS if elements is None
        else elements,
        "grammar_coverage": COVERAGE if coverage is None
        else coverage,
        "surface_id": surface_id,
        "source": source,
        "traversal_timestamp": "2026-11-11T12:00:00Z",
    }
    cap.update(overrides)
    core = {k: cap.get(k) for k in
            ("flow_kind", "elements", "grammar_coverage",
             "surface_id", "traversal_timestamp")}
    cap["surface_attestation"] = darkseal.Store.make_attestation(
        key, cap["flow_id"], core)
    return cap


def artifact(element_identity, kind="charge", label="receipt"):
    return {"artifact_digest":
            logic.digest_obj({"artifact": label,
                              "element": element_identity}),
            "element_identity": element_identity, "kind": kind}


# --- DK-C10 separation fixtures --------------------------------
# Darkseal-only: plan pre-selection in a subscription flow.
def plan_fixture():
    return capture(
        flow_id="flow-plan-001", flow_kind="subscription",
        elements=[el("radio/plan selector", "plan-tier",
                     "Pro (annual)"),
                  el("toggle", "usage-alerts", "off")])


# Darkseal-only: continuity toggle in a signup flow.
def continuity_fixture():
    return capture(
        flow_id="flow-continuity-001", flow_kind="signup",
        elements=[el("continuity switch", "auto-renew", "on"),
                  el("checkbox", "newsletter-opt-in", "unchecked")])


# Darkseal-only: a signup flow (no checkout exists in it at all).
def signup_fixture():
    return capture()


# Upsellseal-only: add-on defaults at a checkout decision — the
# add-on vector against charge lines, Upsellseal's exact object.
def upsellseal_object_fixture():
    return capture(
        flow_id="flow-checkout-001", flow_kind="checkout",
        elements=[el("checkbox", "add-on: priority support",
                     "checked"),
                  el("checkbox", "add-on: extended warranty",
                     "checked"),
                  el("toggle", "gift-wrap", "off")])
