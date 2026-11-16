PROPRIETARY — CYAN ECLIPSE TECHNOLOGIES LLC · COMPANY INTELLECTUAL PROPERTY

# (INT — INTERNAL) BENCH REQUEST — Cyan Eclipse Darkseal cure-3 delta (F-1 verdict-presence binding + F-2 version bump) for VERDICT-DELTA-DARKSEAL-CURE2-20261113 PASS-WITH-FINDINGS

- Subject: Cyan Eclipse Darkseal v0.1.1 — narrow cure delta against VERDICT-DELTA-DARKSEAL-CURE2-20261113.md (CONTRACT: PASS-WITH-FINDINGS, fixture scope; F-1 MED non-blocking + F-2 LOW; DC2-CURE2/C8′ PASSED there and DC1/DC3 stand passed — none re-claimed beyond regression, per that verdict's disposition: "at the lane's next delta rather than a re-sitting of this one")
- Filed: 2026-11-16 · Lane: production-readiness L19 (Slate OPS-90, tkt-ac69fb1d3944), owner directive 2026-11-16
- Subject build / artefact: repo `CYAN-ECLIPSE-TECHNOLOGIES-LLC/eclipse-darkseal-mcp`, maintenance home Shard E `/home/witness/app-family/cyan-eclipse-darkseal`. Cure commit on top of judged HEAD 814953c (code 2ae9f55); commit hash recorded in the lane evidence + Slate OPS-90 comment at filing (hash known only after commit).
- Claims: 1 (claim sheet appended below) — the presence leg of C8′ (DRK-REQ-015) only, plus the F-2 version-discipline discharge, which is a QA-pattern item, not a claim.
- User-facing surface: YES — MCP tools (six tools, SPEC §4.1 inventory unchanged)

## What is being benched

The two findings the cure-2 verdict left open, cured in the judge's named shape:

- F-1 (MED) — verdict erasure was not bound: at 2ae9f55, `Store._verify_record` bound verdict CONTENT only when the verdict was non-null, so setting a minted record's verdict to null in the state file loaded without error and `check` served verdict None (judge probes J-E below-standard, J-E2 full-standard). Cure lane re-reproduced pre-cure at 814953c: both classes LOAD_OK, served None; untouched controls served their original verdicts.
- Cure, per-record leg (`Store._verify_record`): verdict PRESENCE is bound as well as content. A null verdict is legitimate only on an unminted full-standard record (including the DK-C10 separation class, which mints no verdict). Every other class mints — below-standard at seal, full at diff, and a diff mint always sets grammar_basis (and charged_elements when charged) — so a null verdict on a record carrying a minted basis raises ValueError at load naming the record and the erasure; the store fails closed and serves nothing (the product's existing typed load refusal).
- Cure, aggregate leg (`Store.__init__`): the judge's second clause — an unminted (verdict-null) record must present no verdict receipt. The journal appends exactly one verdict receipt per minted verdict and no other path appends one, so at load the verdict-receipt count must equal the count of records presenting a non-null verdict. An erasure that also scrubs the minted-state fields (grammar_basis / charged_elements / outcome_artifacts) leaves an orphan receipt and fails closed on the count. Scope stated plainly: this leg binds presence against the journal as presented; deleting the receipt itself is journal tampering, a class the chain verification and the C8′ tamper legs already cover.
- Compatibility, stated plainly: genuine stores of every legitimate shape reload — untouched minted full (live Shard E store: 1 capture, full, PRESELECTED-AND-CHARGED, loads clean under the cured code), untouched minted below-standard, unminted full (verdict None, no receipt), and separation (verdict None after a diff attempt; the diff_separation receipt is not a verdict receipt). Pre-cure below-standard stores already failed closed under cure-2 (no verdict receipt exists to bind) and still do — unchanged, disclosed in the cure-2 request.
- F-2 (LOW) — version bump discharged in the same cut: 0.1.0 → 0.1.1 in VERSION, darkseal.TOOL_VERSION, pyproject.toml, server.json (both version fields), tools-manifest.json, and the README status line. Historical bench/build records keep their 0.1.0 text — they are dated records of judged builds, not version surfaces.

Post-cure probes (cure lane, against the cure commit): judge-shape repro — verdict erased to null on a below-standard record and on a full-standard PRESELECTED-AND-CHARGED record — both RAISE at load with the presence error; untouched controls serve original verdicts. Product suite 56/56 OK (51 pre-existing + 5 new in TestReceiptChain: erased-verdict full, erased-verdict below-standard, scrubbed-erasure aggregate leg, + unminted-full and separation legitimate-null reload controls). The 3 erasure tests FAIL against pre-cure code (ValueError not raised) and pass post-cure; the 2 controls pass both sides. MCP stdio smoke PASS. Live Shard E store reload PASS.

A PASS on this delta judges the presence leg of C8′ only; fixture scope stays fixture scope — no arming, listing, or external claim rides it. Fences held: buyer-side capture only remains the only capture shape; the gate-banned label appears on no product surface; no metering added; DK-C3 listing fence untouched (listing waits on counsel written answers + owner review — this lane does not touch it).

## Re-filed claim (presence leg of C8′ only)

- C8′-PRESENCE (DRK-REQ-015): in addition to the content binding already passed, verdict presence is bound at load — a record whose class mints a verdict (every below-standard record; any record carrying a minted grammar basis) must present a non-null verdict matching a journal verdict receipt, and the journal's verdict-receipt count must equal the number of records presenting a verdict; a minted verdict erased to null (with or without scrubbing the minted-state fields) fails closed at load and is never served, while unminted full-standard and DK-C10 separation records legitimately present verdict null and reload.

## Evidence pack

- Verdict cured against: `VERDICT-DELTA-DARKSEAL-CURE2-20261113.md` (F-1 shape + F-2, both followed as written).
- Cure-lane reproduction: judge-shape probe (seal → erase verdict to null in the state file → load + check), pre-cure at 814953c = LOAD_OK + served None on both classes; post-cure = RAISED at load on both classes, untouched controls served originals. Lane evidence: production-readiness-20261116/lanes/L19/evidence/ (repro-precure.txt, postcure-first-run.txt, precure-test-fail.txt, suite-smoke-live.txt).
- Regression tests: TestReceiptChain.test_store_fails_closed_on_erased_verdict_full / _below_standard / test_store_fails_closed_on_scrubbed_erased_verdict (fail pre-cure, pass post-cure) + test_unminted_full_store_reloads_with_null_verdict / test_separation_store_reloads_with_null_verdict (legitimate-null controls).
- Product suite at the cure commit: 56/56 OK, run on Shard E. MCP stdio smoke PASS (6 tools).
- Live data store regression check: Shard E `data/darkseal-state.json` (1 capture, full-standard, PRESELECTED-AND-CHARGED) loads clean under the cured load path.
- Version surfaces at 0.1.1: VERSION · TOOL_VERSION · pyproject.toml · server.json · tools-manifest.json · README status line (grep-verified in lane evidence).

## (INT — INTERNAL) QA-pattern conformance

| Pattern | Verdict (CLEAR / HIT / N-A) | Evidence or N-A reason |
|---|---|---|
| P1 — Content-free modes close every ingress | N-A | No content-free mode, tier, or setting exists. The custody rule is a field-set refusal at the single seal ingress (FIELD_OUTSIDE_GRAMMAR, receipted), covered by TestCustody, unchanged by this delta. |
| P2 — Disclosure matches build | CLEAR | This delta re-files the presence leg of C8′ only, restated to the cured behaviour with its scope note attached (aggregate leg binds against the journal as presented; receipt deletion is the journal-tamper class, named in the request, not buried); DC1/DC3/DC2-CURE2 are not re-claimed beyond regression. |
| P3 — Save/close basics | N-A | No save concept and no window: headless MCP server; state persists atomically per operation (os.replace in _save). |
| P4 — AI-applied content is attributed | N-A | The product applies no content — it seals presented element states and diffs artifacts; there is no AI-applied content surface. |
| P5 — Version discipline | CLEAR | The F-2 HIT carried through two verdicts is discharged in this cut: shipped code changed AND the version bumped 0.1.0 → 0.1.1 on every version surface in the same commit, named in the commit message. |
| P6 — Integrity warnings are prominent | CLEAR | The delta is the P6 test shape applied to the presence leg: divergence is refused at the point of use, by name — load raises naming the record and the erased verdict and serves nothing, for both record classes (cure-lane probes + the 3 new erasure tests). |
| P7 — Erasure-class operations | N-A | No erasure story: the product makes no history-erasure claim and offers no erasure operation. (This finding was about tamper-by-erasure of a sealed verdict, cured as an integrity binding — not a product erasure feature.) |
| P8 — Preview equals apply | N-A | No preview, dry-run, plan, or proposal surface exists. Recompute is a verification path over the sealed record, not a preview of an apply (unchanged). |

## Claim sheet (standard form, added 2026-11-04 — bench efficiency lever 1)

```claims
[
  {"id": "DC2-CURE3", "statement": "Store load binds verdict PRESENCE as well as content: a minted record (every below-standard record; any record carrying a minted grammar basis) presenting verdict null fails closed at load, the journal verdict-receipt count must equal the number of records presenting a verdict, and unminted full-standard and DK-C10 separation records legitimately present verdict null and reload", "evidence": "darkseal.py Store._verify_record presence leg + Store.__init__ aggregate count at v0.1.1 cure commit; tests TestReceiptChain.test_store_fails_closed_on_erased_verdict_full/_below_standard/test_store_fails_closed_on_scrubbed_erased_verdict + test_unminted_full_store_reloads_with_null_verdict + test_separation_store_reloads_with_null_verdict; cure-lane judge-shape probe pre/post cure; suite 56/56; live-store reload", "verify": "recompute", "class": "chain"}
]
```

© Cyan Eclipse Technologies LLC — Proprietary · Company Intellectual Property
