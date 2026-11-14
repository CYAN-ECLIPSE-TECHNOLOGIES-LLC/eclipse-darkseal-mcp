PROPRIETARY — CYAN ECLIPSE TECHNOLOGIES LLC · COMPANY INTELLECTUAL PROPERTY

# (INT — INTERNAL) BENCH REQUEST — Cyan Eclipse Darkseal cure-of-cure delta (F-1) for VERDICT-DELTA-DARKSEAL-CURE-20261113 FAIL

- Subject: Cyan Eclipse Darkseal v0.1.0 — narrow cure delta against VERDICT-DELTA-DARKSEAL-CURE-20261113.md (CONTRACT: FAIL, fixture scope; F-1 HIGH blocking on DC2/C8′; DC1 and DC3 PASSED and are NOT re-claimed beyond regression, per the verdict's own path to re-sitting)
- Filed: 2026-11-13 · Lane: Darkseal cure-of-cure lane (main-seat commission)
- Subject build / artefact: repo `CYAN-ECLIPSE-TECHNOLOGIES-LLC/eclipse-darkseal-mcp`, maintenance home Shard E `/home/witness/app-family/cyan-eclipse-darkseal`, HEAD 2ae9f55 (GitHub main == Shard E, ff-merge verified). Cure commit: 2ae9f55 (one commit, on top of the judged cure HEAD 49b1af2; diff = darkseal.py + tests/test_darkseal.py only).
- Claims: 1 (claim sheet appended below, standard form) — C8′ only.
- User-facing surface: YES — MCP tools (six tools, SPEC §4.1 inventory unchanged)

## What is being benched

The one residual the cure verdict found, cured in the judge's named shape:

- F-1 (was DC2/C8′ FAIL) — `Store._verify_record` applied the journal verdict-receipt binding only when `capture_standard == "full"`. A below-standard record's minted verdict (UNVERIFIABLE) and charged_elements were bound to nothing: a state-file edit flipping the verdict to PRESELECTED-AND-CHARGED with charged_elements ["newsletter-opt-in"] loaded without error and `check` served the flipped verdict (judge-reproduced; cure lane re-reproduced pre-cure against 49b1af2, both the verdict flip and a charged_elements-only flip).
- Cure, load side: the "full" guard is dropped — EVERY non-null minted verdict (digest over capture_id + verdict + charged_elements + grammar_version) must match a journal verdict receipt at load, for every capture_standard.
- Cure, mint side (named plainly, because the load binding must have something to bind): at 49b1af2 the below-standard UNVERIFIABLE verdict was minted inside `seal_defaults` with NO journal verdict receipt — the diff path that journals full-standard verdicts is never reached for that class (already_minted short-circuit). `seal_defaults` now appends the verdict receipt for the below-standard mint at seal time, payload exactly {capture_id, verdict, charged_elements, grammar_version}. Full-standard and separation mint paths are byte-unchanged in behaviour.
- Compatibility, stated plainly: stores minted under the cured code (all classes) reload and serve their original verdicts; full-standard and separation stores minted under pre-cure code load unchanged under the cured code (probe-verified, incl. the live Shard E store, 1 capture / full / PRESELECTED-AND-CHARGED). A below-standard store minted under PRE-cure code carries no verdict receipt and now FAILS CLOSED at load rather than serving a verdict nothing binds; migration is to re-seal the capture under cured code. No such store is known live (the only live store is the full-standard one above).

Post-cure probes (cure lane, against 2ae9f55): the judge's below-standard tamper set — verdict flip and charged_elements-only flip — both RAISE at load naming the unbound record; the untouched below-standard store loads and serves UNVERIFIABLE with charged_elements []. Product suite 51/51 OK (48 + 3 new: tamper-at-load on a below-standard record ×2 + untouched below-standard reload); MCP stdio smoke PASS.

A PASS on this delta re-sits C8′ only; fixture scope stays fixture scope — no arming, listing, or external claim rides it. Fences held: buyer-side capture only remains the only capture shape; the gate-banned label appears on no surface; no metering added.

## Re-filed claim (C8′ only, superseding the DC2 wording that failed)

- C8′ (DRK-REQ-015): the receipt journal verifies end-to-end with exactly one receipt per capture and per verdict; a tampered journal record and a truncated export are detected; and a tampered store — journal OR capture record (including a flipped minted verdict or a flipped sealed element state, on a record of ANY capture_standard, full or below-standard) — fails closed at load, serving nothing. Scope note carried from the cure: this claim covers stores minted under the cured code, plus pre-cure full-standard and separation stores; a pre-cure below-standard store fails closed at load as unbound (see compatibility note above) rather than serving.

## Evidence pack

- Verdict cured against: `VERDICT-DELTA-DARKSEAL-CURE-20261113.md` (this home; F-1 cure shape followed).
- Cure-lane reproduction: judge-shape probe (seal below-standard → flip verdict / flip charged_elements in the state file → load + check), pre-cure against 49b1af2 = LOADED+SERVED both flips; post-cure against 2ae9f55 = RAISED at load both flips, untouched control served original verdict.
- Cross-version probe: stores minted end-to-end under 49b1af2 code (full / separation / below-standard) loaded under 2ae9f55 — full and separation load and serve originals; pre-cure below-standard raises (disclosed above).
- Product suite at 2ae9f55: 51/51 OK (48 pre-existing incl. the full-standard tamper-at-load tests + 3 new below-standard tests in TestReceiptChain), re-run green on Shard E as well.
- MCP stdio smoke at 2ae9f55: PASS (6 tools · below-standard UNVERIFIABLE · separation · recompute reproduced).
- Live data store regression check: Shard E `data/darkseal-state.json` (1 capture, full-standard, PRESELECTED-AND-CHARGED) loads clean under the cured load path at 2ae9f55.
- Commit 2ae9f55 in the repo of record (GitHub main == Shard E).

## (INT — INTERNAL) QA-pattern conformance

| Pattern | Verdict (CLEAR / HIT / N-A) | Evidence or N-A reason |
|---|---|---|
| P1 — Content-free modes close every ingress | N-A | No content-free mode, tier, or setting exists. The custody rule is a field-set refusal at the single seal ingress (FIELD_OUTSIDE_GRAMMAR, receipted), covered by TestCustody, unchanged by this delta. |
| P2 — Disclosure matches build | CLEAR | This delta re-files C8′ only, restated to the cured behaviour with its scope note attached (pre-cure below-standard stores fail closed as unbound — disclosed in the claim itself, not buried); DC1/DC3 are not re-claimed beyond regression, per the verdict's path to re-sitting. |
| P3 — Save/close basics | N-A | No save concept and no window: headless MCP server; state persists atomically per operation (os.replace in _save). |
| P4 — AI-applied content is attributed | N-A | The product applies no content — it seals presented element states and diffs artifacts; there is no AI-applied content surface. |
| P5 — Version discipline | HIT | The cure changes shipped code (darkseal.py) with no version bump: TOOL_VERSION and VERSION still read 0.1.0 — the same HIT the cure verdict recorded as F-2 (LOW), carried openly. No artefact is released under this delta; the bump belongs to the next release cut. |
| P6 — Integrity warnings are prominent | CLEAR | The delta is the P6 test shape applied to a headless surface, now covering the record class that escaped it: divergence is refused at the point of use, by name — load raises naming the record and the failed binding and serves nothing, for below-standard records exactly as for full (cure-lane probes + TestReceiptChain.test_store_fails_closed_on_tampered_below_standard_verdict / _charged). |
| P7 — Erasure-class operations | N-A | No erasure story: the product makes no history-erasure claim and offers no erasure operation; nothing in its copy credits any action with erasure. |
| P8 — Preview equals apply | N-A | No preview, dry-run, plan, or proposal surface exists. Recompute is a verification path over the sealed record, not a preview of an apply (unchanged; DC1 not re-claimed). |

## Claim sheet (standard form, added 2026-11-04 — bench efficiency lever 1)

Form only: statements extracted from this request; no claim substance changed.

```claims
[
  {"id": "DC2-CURE2", "statement": "Store load binds EVERY non-null minted verdict (digest over capture_id + verdict + charged_elements + grammar_version) to a journal verdict receipt at every capture_standard; a tampered below-standard record (flipped minted verdict or flipped charged_elements) fails closed at load and is never served, and an untouched below-standard store reloads and serves its original UNVERIFIABLE verdict", "evidence": "darkseal.py Store._verify_record + seal_defaults verdict receipt at 2ae9f55; tests TestReceiptChain.test_store_fails_closed_on_tampered_below_standard_verdict/_charged + test_below_standard_store_reloads_and_serves; cure-lane judge-shape probe pre/post cure; suite 51/51", "verify": "recompute", "class": "chain"}
]
```

© Cyan Eclipse Technologies LLC — Proprietary · Company Intellectual Property
