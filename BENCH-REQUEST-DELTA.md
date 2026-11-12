PROPRIETARY — CYAN ECLIPSE TECHNOLOGIES LLC · COMPANY INTELLECTUAL PROPERTY

# (INT — INTERNAL) BENCH REQUEST — Cyan Eclipse Darkseal v0.1.0 (build delta)

- Filed: 2026-11-11 · Seat: builder lane (Darkseal build 3 of the Argus trio)
- Subject: Cyan Eclipse Darkseal v0.1.0 — repo `CYAN-ECLIPSE-TECHNOLOGIES-LLC/eclipse-darkseal-mcp`, maintenance home Shard E `/home/witness/app-family/cyan-eclipse-darkseal`
- Spec of record: SPEC-DARKSEAL.md (DRK-REQ-001…017; Loom project 34, req ids 1809–1825, CANDIDATE, verdicts not-run)
- Gate: argus-gate-darkseal-20261111.md — PASS-WITH-CONDITIONS (DK-C1…DK-C10)
- Builder evidence (NOT a verdict): unit suite 42/42 on the droplet + MCP smoke PASS; transcript `evidence/TRANSCRIPT-20261111.txt`

## Claims for independent verification (spec §6, restated)

- **C1 / DK-B1 (DRK-REQ-013):** fixtures where a pre-selected element produces a charge verdict PRESELECTED-AND-CHARGED naming that element; sealed-but-uncharged fixtures verdict PRESELECTED-NOT-CHARGED; clean-flow controls verdict NO-PRESELECTION — 100% of fixtures.
- **C2 / DK-B2 (DRK-REQ-002(iii), DRK-REQ-014):** a verifier holding only the sealed bundle + the published element grammar (GRAMMAR.md) + the outcome artifacts reproduces the verdict with no service access.
- **C3 / DK-B3 (DRK-REQ-004, DRK-REQ-011):** un-enumerable or below-standard capture fixtures verdict UNVERIFIABLE in 100% of cases; no PRESELECTED-AND-CHARGED verdict is mintable from a below-standard bundle; out-of-grammar elements are named in the coverage statement and never judged.
- **C4 / DK-B4 (DRK-REQ-005):** the store, inspected directly, contains only the §2 field set (plus the DK-C10 separation marker) — no form-field values (an element carrying one is refused at the gate, receipted, and nothing is retained), no page bodies, no cross-principal tables.
- **C5 / DK-B5 (DRK-REQ-007, DRK-REQ-010):** verdicts name their grammar version and a revision never retro-alters a minted verdict; the DK-C10 separation fixture set produces Darkseal-only verdicts where the sibling cannot verdict (plan pre-selection · continuity toggle · signup flow), and the reverse fixture is marked, not verdicted (see C7).
- **C6 / ADV-1 (DRK-REQ-012, DK-K1 guard):** default-state bundles submitted by a non-executing third party (a "notary" integration), a merchant, or a relay — carrying plausible element data but no executing-surface attestation — are rejected on provenance, the rejections receipted, zero witnessed records created, and no verdict mintable from submitted material across all API paths.
- **C7 / ADV-2 (DRK-REQ-010, DK-C10):** a checkout fixture whose only pre-selected elements are add-on defaults at a checkout decision — the sibling's exact object — is identified as UPSELLSEAL-OBJECT in the separation set and Darkseal mints no duplicate whole-flow verdict for it, at seal, at diff, and at recompute; the Darkseal-only fixtures verdict normally.
- **C8 (DRK-REQ-015):** the receipt journal verifies end-to-end with exactly one receipt per capture and per verdict; a tampered record and a truncated export (chain-head mismatch) are both detected; a tampered store fails closed at load.
- **C9 (DRK-REQ-016, DRK-REQ-014, DRK-REQ-009):** no metering exists anywhere: across all event classes, zero charge events are created, and no price/amount/tier field exists in the state file or the tool schemas; the verdict grammar is identical on every call. The MCP tool inventory equals SPEC §4.1 exactly; `darkseal_check` reveals verdict class + charged element names only; the gate-banned label appears as a verdict, label, or output string on NO surface (suite scan + build-time repo grep, clean outside the test's own scan list).

## Fences the bench is asked to hold the build to

Buyer-side capture only — no seller-side instrumentation claims, no merchant-facing surface, no notary shape; verdicts name pre-selection states and elements only, never the gate-banned label or any legal conclusion; no form-field value custody; no merchant-aggregate surface; FREE funnel — no metering, no price point. Claims stay **bench-pending** until Verity's verdict lands; builder tests are not evidence.

© Cyan Eclipse Technologies LLC — Proprietary · Company Intellectual Property
