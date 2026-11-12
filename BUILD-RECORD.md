PROPRIETARY — CYAN ECLIPSE TECHNOLOGIES LLC · COMPANY INTELLECTUAL PROPERTY

# (INT — INTERNAL) BUILD RECORD — Cyan Eclipse Darkseal v0.1.0

- Built: 2026-11-11 · Build authority: owner commission 2026-11-11 17:08 PT (Argus trio builds, serial per P-2: Routeseal → Grantseal → Darkseal; Routeseal built + bench-filed first — repo eclipse-routeseal-mcp @ 7b351bc, IP §A70; Grantseal second — repo eclipse-grantseal-mcp @ dab0d76, IP §A71). DRK-REQ-001 is satisfied by that commission; the SPEC itself conferred no build slot.
- Spec of record: SPEC-DARKSEAL.md (firm spec store, specs-20261111; summary at SPEC.md in this repo) · Gate: argus-gate-darkseal-20261111.md, PASS-WITH-CONDITIONS, narrowings binding.
- Estate: maintenance home Shard E `/home/witness/app-family/cyan-eclipse-darkseal` · GitHub `CYAN-ECLIPSE-TECHNOLOGIES-LLC/eclipse-darkseal-mcp` (full MIT LICENSE in the first commit).
- Shape: stdlib-only Python MCP server over stdio (`server.py`), pure element-grammar/verdict engine (`logic.py`), store/provenance/receipt layer (`darkseal.py`). Exactly the six §4.1 tools. FREE funnel: no metering anywhere in the build.

## What was built, per requirement

- DRK-REQ-002 — three-part mechanism held jointly: traversal-start element-state sealing in the executing surface · outcome diff under the published element grammar (GRAMMAR.md, `darkseal-grammar/1`) · stateless third-party recomputation (`darkseal_recompute`). No standalone-notary or merchant-audit variant exists.
- DRK-REQ-003 — no listing, pilot, quote, or checkout artefact exists; no metering event exists anywhere in the product; verdict grammar is identical on every call because there is only the free check.
- DRK-REQ-004 — minimum sealed bundle per element class enforced; below-standard captures (malformed rendered states, empty vectors, no grammar-covered elements) mint UNVERIFIABLE only; captures arrive only via the executing-surface channel (source + per-surface HMAC attestation + binding to the flow identity); the record claims the rendered default state only. The counsel-cleared surface list (DK-CQ-2) remains an open counsel item — no surface list is asserted by this build.
- DRK-REQ-005 — the store's capture record field set is exactly the §2 set plus the DK-C10 separation marker (asserted in code + tests); form-field values are refused at the gate (an element carrying any field beyond the grammar's three is rejected, receipted, and nothing is retained); no page bodies, no browsing history, no principal profile.
- DRK-REQ-006 — no cross-principal aggregation code path or tool exists (inventory test); no merchant statistics, feed, or dossier surface.
- DRK-REQ-007 — every verdict names its element-grammar version; a grammar revision registered after minting leaves minted verdicts byte-identical and v1-pinned recomputation unchanged (test).
- DRK-REQ-008 — WATCH.md records both DK-C8 trigger classes (platform terms barring runtime capture · native non-party-verifiable traversal-start receipts); reviewed at build, neither known to have fired.
- DRK-REQ-009 — claim line verbatim in README + seal tool description; §2 verdict vocabulary only; banned-term scan in the suite covers tool descriptions, README, GRAMMAR.md, WATCH.md, the tools manifest, and every output shape the suite produces — and a repo-wide grep at build time is clean outside the test's own scan list.
- DRK-REQ-010 — the separation deliverable is built and fixtured (fixtures/captures.py): Darkseal-only fixtures (plan pre-selection · continuity toggle · signup flow) verdict normally; the Upsellseal-object checkout fixture (add-on defaults only, at a checkout decision) is marked UPSELLSEAL-OBJECT at seal time, mints no whole-flow verdict at diff, and recomputes to the separation marker. The build does NOT collapse into the sibling residue, so the merge rule is not triggered by this build; the bench is asked to test exactly that (ADV-2).
- DRK-REQ-011 — element grammar published (GRAMMAR.md: class rules, record shape, rendered-state conventions, coverage semantics); every capture carries its coverage statement (grammar_coverage · covered_classes · outside_coverage); out-of-grammar elements are named, never judged.
- DRK-REQ-012 — capture provenance enforced: source == executing-surface + registered-surface HMAC attestation bound to the flow identity. Notary, merchant, relay, forged-attestation, wrong-key, and unregistered-surface fixtures are all rejected + receipted with zero witnessed records created (ADV-1).
- DRK-REQ-013 — outcome diff runs only over the sealed default vector + the principal's own artifacts (digest + element identity + kind, exactly); artifact records carrying any extra field are refused as diff inputs; carried defaults verdict PRESELECTED-AND-CHARGED naming the element, sealed-but-uncharged verdict PRESELECTED-NOT-CHARGED, clean controls verdict NO-PRESELECTION.
- DRK-REQ-014 — tool inventory == §4.1 exactly (asserted against tools-manifest.json in the suite); `darkseal_check` reveals the verdict class + charged element names only; recompute runs with no service state.
- DRK-REQ-015 — hash-chained receipt journal, exactly one receipt per default-state capture and per verdict (plus receipted rejections/refusals/separations); exports carry the chain head; tamper + truncation detected; a tampered store fails closed at load.
- DRK-REQ-016 — FREE shape verified by test: the store has no metering structure, the state file and the tool schemas carry no price/amount/tier fields, and no charge event of any kind is created across every event class the suite exercises.
- DRK-REQ-017 — branding applied at creation (branding/BRANDING.md): composite wordmark, canonical theme tokens, server identity surfaces. **Icon: DRAFT candidate only (branding/icon-candidate.svg), NOT approved, NOT shipped, NOT public — owner approval is the outstanding gate.**

## Verification (builder-side; bench verdict is Verity's)

- Unit suite: **42/42 PASS** on the droplet (python3 -m unittest, tests/test_darkseal.py; each test names its requirement / bench claim).
- MCP smoke over real stdio JSON-RPC: **PASS** (tools list · PRESELECTED-AND-CHARGED · PRESELECTED-NOT-CHARGED · notary rejected · below-standard UNVERIFIABLE · UPSELLSEAL-OBJECT separation · check · export · recompute reproduced · form-value refused). Transcript: evidence/TRANSCRIPT-20261111.txt.

## What this build does NOT do (gate narrowings, honored by construction)

Buyer-side capture only — no seller-side instrumentation and no merchant-facing surface of any kind · no standalone-notary shape (non-executing submissions are rejected, never sealed) · the gate-banned label appears as a verdict, label, or marketing claim on NO surface (verdicts name pre-selection states and elements only) · no claim that a sealed default state proves what any person saw, understood, or agreed to · no form-field value custody · no merchant-aggregate statistics, feeds, or dossiers · no metering, no per-check price, no paid verdict tier (FREE funnel) · no listing, directory submission, public launch, or pricing/checkout wiring.

## Open items / gaps

- Icon owner approval outstanding (draft candidate only).
- TM screen for the name (DK-CQ-3), evidentiary-weight question (DK-CQ-1), and the capture posture + v1 cleared-surface list (DK-CQ-2) remain open counsel items; name stays provisional and no cleared-surface list is asserted.
- Slate ETO-13: this seat's Slate API route is the build-lane route whose probes are rejected ("no valid directory session"); no transition was forced. Comment text for ETO-13, ready for the main seat to post verbatim:
  - Progress: "Darkseal build started 2026-11-11 under owner commission 17:08 PT (Argus trio serial order: Routeseal → Grantseal → Darkseal). Building to SPEC-DARKSEAL DRK-REQ-001…017 on Shard E; GitHub repo eclipse-darkseal-mcp."
  - Completion: "Darkseal v0.1.0 build complete 2026-11-11: suite 42/42 + MCP smoke PASS on droplet; GitHub == droplet; BENCH-REQUEST-DELTA filed (claims C1–C9 ← DK-B1…B5 + ADV-1/2), bench-pending; buyer-side-only + banned-verdict-language + DK-C10 separation + FREE-funnel narrowings honored; icon draft candidate only (owner approval outstanding); no listing/launch. Record: BUILD-RECORD.md in repo."
- Loom verifications for req 1809–1825 remain not-run (bench will move them; nothing fabricated here).

© Cyan Eclipse Technologies LLC — Proprietary · Company Intellectual Property
