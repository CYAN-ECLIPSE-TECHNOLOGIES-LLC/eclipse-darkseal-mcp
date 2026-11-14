PROPRIETARY — CYAN ECLIPSE TECHNOLOGIES LLC · COMPANY INTELLECTUAL PROPERTY

# (INT — INTERNAL) BENCH REQUEST — Cyan Eclipse Darkseal cure delta (F-1/F-2) for VERDICT-DELTA-20261113 FAIL

- Subject: Cyan Eclipse Darkseal v0.1.0 — cure delta against VERDICT-DELTA-20261113.md (CONTRACT: FAIL, fixture scope; F-1 HIGH + F-2 HIGH blocking; C1–C5/C7/C9 passed and are not re-claimed beyond regression)
- Filed: 2026-11-13 · Lane: Darkseal bench-FAIL cure lane (main-seat commission)
- Subject build / artefact: repo `CYAN-ECLIPSE-TECHNOLOGIES-LLC/eclipse-darkseal-mcp`, maintenance home Shard E `/home/witness/app-family/cyan-eclipse-darkseal`, HEAD 49b1af2 (GitHub main == Shard E). Cure commits: ca2e625 (F-1) · 49b1af2 (F-2), on top of the judged HEAD 28f8166.
- Claims: 3 (claim sheet appended below, standard form)
- User-facing surface: YES — MCP tools (six tools, SPEC §4.1 inventory unchanged)

## What is being benched

Two cure claims, each reproduced first-hand before curing (judge probes P1/P2/P3 re-run by the cure lane against HEAD 28f8166, outputs in the evidence pack):

- F-1 (was C6 FAIL) — recompute was seal-blind. Cure: `darkseal.recompute` (and with it the `darkseal_recompute` MCP tool, which delegates to it) now verifies the capture's seal over its bundle fields — and the capture_id that seal derives — and derives `capture_standard` from the sealed elements under the named grammar before computing anything. A fabricated or tampered capture mints NO verdict class: it returns verdict null with the named refusal `SEAL_VERIFICATION_FAILED`, fail closed. A genuine sealed capture recomputes exactly as before.
- F-2 (was C8 FAIL) — capture-record tamper loaded silently. Cure: `Store` load now re-verifies every capture record after the journal check — seal recomputed over the record's bundle fields, the record's capture-receipt binding checked against the journal, and any minted verdict must match a journal verdict-receipt digest. Any mismatch raises at load; the store fails closed and serves nothing.

A PASS unblocks nothing beyond a re-sitting of C6/C8 as re-filed below; fixture scope stays fixture scope — no arming, listing, or external claim rides this delta. Fences held: buyer-side capture only remains the only capture shape; the gate-banned label appears on no surface (suite output scan re-run clean); no metering added.

## Re-filed claims (superseding the C6/C8 wording that failed)

- C6′ / ADV-1 (DRK-REQ-012, DK-K1 guard): default-state bundles submitted by a non-executing third party are rejected on provenance, receipted, zero witnessed records created — and across ALL API paths, including `darkseal_recompute`, no verdict is mintable from submitted material that does not verify against its own seal: unverifiable material returns no verdict class and the named refusal `SEAL_VERIFICATION_FAILED`.
- C8′ (DRK-REQ-015): the receipt journal verifies end-to-end with exactly one receipt per capture and per verdict; a tampered journal record and a truncated export are detected; and a tampered store — journal OR capture record (including a flipped minted verdict or a flipped sealed element state) — fails closed at load, serving nothing.

## Evidence pack

- Verdict cured against: `VERDICT-DELTA-20261113.md` (this home + Shard E build home).
- Cure-lane reproduction + post-cure probe outputs (P1 fabricated capture · P2 flipped element · P3 tampered state file), pre-cure and post-cure, run 2026-11-13 against 28f8166 and 49b1af2 respectively.
- Product suite at 49b1af2: 48/48 OK (42 pre-existing + 6 new: TestSealIntegrityRecompute ×3, TestReceiptChain tamper-at-load ×3), including the regression of C1–C5/C7/C9 behaviours.
- MCP stdio smoke at 49b1af2: PASS (6 tools · recompute reproduced over a genuine sealed capture).
- Live data store regression check: `data/darkseal-state.json` (1 capture, 2 journal entries, minted by the judged code) loads clean under the cured load path.
- Commits ca2e625 + 49b1af2 in the repo of record (diff = darkseal.py + tests/test_darkseal.py only).

## (INT — INTERNAL) QA-pattern conformance

| Pattern | Verdict (CLEAR / HIT / N-A) | Evidence or N-A reason |
|---|---|---|
| P1 — Content-free modes close every ingress | N-A | No content-free mode, tier, or setting exists. The custody rule is a field-set refusal at the single seal ingress (FIELD_OUTSIDE_GRAMMAR, receipted), covered by TestCustody, unchanged by this delta. |
| P2 — Disclosure matches build | CLEAR | This delta's claims are restated to the cured behaviour only (C6′/C8′ above) and each is probe-proven pre/post cure; the product CLAIM's recompute sentence is true of the cured build (seal-bound recompute, TestSealIntegrityRecompute). |
| P3 — Save/close basics | N-A | No save concept and no window: headless MCP server; state persists atomically per operation (os.replace in _save). |
| P4 — AI-applied content is attributed | N-A | The product applies no content — it seals presented element states and diffs artifacts; there is no AI-applied content surface. |
| P5 — Version discipline | HIT | The cure changes the shipped code (darkseal.py) with no version bump: TOOL_VERSION and VERSION still read 0.1.0, as the judged build did. Stated plainly: this is a bench-pending cure delta, no artefact is released under it; the bump belongs to the next release cut, not hidden here. |
| P6 — Integrity warnings are prominent | CLEAR | This delta is the P6 test shape applied to a headless surface: divergence is refused at the point of use, by name — load raises naming the record and the failed binding and serves nothing (probe P3 post-cure); recompute returns the named SEAL_VERIFICATION_FAILED refusal and no verdict class. Tests: TestReceiptChain.test_store_fails_closed_on_tampered_verdict / _on_tampered_element, TestSealIntegrityRecompute. |
| P7 — Erasure-class operations | N-A | No erasure story: the product makes no history-erasure claim and offers no erasure operation; nothing in its copy credits any action with erasure. |
| P8 — Preview equals apply | N-A | No preview, dry-run, plan, or proposal surface exists. Recompute is a verification path over the sealed record, not a preview of an apply. |

## Claim sheet (standard form, added 2026-11-04 — bench efficiency lever 1)

Form only: statements extracted from this request; no claim substance changed.

```claims
[
  {"id": "DC1", "statement": "Recompute verifies the capture seal over its bundle fields and derives capture_standard from the sealed elements; a fabricated or tampered capture mints no verdict class and is refused by name (SEAL_VERIFICATION_FAILED), while a genuine sealed capture recomputes as before", "evidence": "darkseal.py recompute/_seal_intact/_derived_standard at 49b1af2; tests TestSealIntegrityRecompute; cure-lane probes P1/P2 pre/post cure", "verify": "recompute", "class": "chain"},
  {"id": "DC2", "statement": "Store load re-verifies every capture record (seal over bundle fields, capture-receipt binding, verdict-receipt binding); a tampered capture record — flipped minted verdict or flipped sealed element — fails closed at load and is never served", "evidence": "darkseal.py Store._verify_record at 49b1af2; tests TestReceiptChain.test_store_fails_closed_on_tampered_verdict/_on_tampered_element; cure-lane probe P3 pre/post cure", "verify": "recompute", "class": "chain"},
  {"id": "DC3", "statement": "No regression: C1-C5/C7/C9 behaviours of the judged build are unchanged; product suite 48/48 and MCP smoke PASS at HEAD 49b1af2, and the pre-existing live data store loads clean under the cured load path", "evidence": "tests/test_darkseal.py full run at 49b1af2; smoke.py output; data/darkseal-state.json load check", "verify": "read", "class": "methodology"}
]
```

© Cyan Eclipse Technologies LLC — Proprietary · Company Intellectual Property
