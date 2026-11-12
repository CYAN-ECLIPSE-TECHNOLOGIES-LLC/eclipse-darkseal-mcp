# Cyan Eclipse Darkseal

**Powered by Cyan Eclipse Technologies** — https://cetech.ai

![Cyan Eclipse Darkseal icon](branding/icon.svg)

*Icon: `branding/icon.svg` — owner-elected 2026-11-12 (class MARGINAL: legible at 48 px, marginal at 32 px).*

Darkseal seals the state the flow started in — every pre-ticked
add-on, pre-chosen plan, and continuity toggle, element by
element — at the moment your agent entered it. If a charge
began as a default you never chose, the sealed record names the
element it began as, and anyone can recompute the verdict from
the record itself.

Cyan Eclipse Darkseal is a Model Context Protocol (MCP) server.
It witnesses the default state of agent-traversed flows from the
buyer's side of the seam: the capture happens in the executing
surface — the buying agent's own runtime, or a
Checkout-Hands-class surface — at traversal start, before any
principal or agent action. The sealed vector is diffed against
the charges and terms that resulted, from the principal's own
confirmation and charge artifacts, held as digests.

Verdicts, from a fixed grammar:

- **PRESELECTED-AND-CHARGED** — names the pre-selected elements
  that produced charges or binding terms.
- **PRESELECTED-NOT-CHARGED** — defaults were sealed; no
  resulting charge or term appears in the principal's artifacts.
- **NO-PRESELECTION** — no grammar-covered element was
  pre-selected in the rendered flow.
- **UNVERIFIABLE** — the capture is below the capture standard;
  a state of the evidence, never any party's fault.

The element grammar (`GRAMMAR.md`, `darkseal-grammar/1`) covers
four classes in v1: checkboxes, toggles, radio/plan selectors,
and continuity switches. Elements outside the grammar are named
in the capture's coverage statement and never judged. A
checkout flow whose pre-selected elements are all checkbox
add-on defaults is a sibling product's object — the record is
marked `UPSELLSEAL-OBJECT` and Darkseal mints no duplicate
whole-flow verdict for it.

Darkseal is a witness, not an auditor and not a notary: it
accepts captures only from the executing surface's own witness
module — bundles submitted by any other party are rejected on
provenance — and it renders no finding about what any person
saw, understood, or agreed to. The record names the state the
flow started in and what that state produced. Nothing more.

## Tools

| Tool | What it does |
|---|---|
| `darkseal_seal_defaults` | Seal a traversal-start default-state vector from the executing surface's witness module. Free. |
| `darkseal_diff_outcome` | Diff the principal's own confirmation/charge artifacts against the sealed defaults and mint the verdict. Free. |
| `darkseal_get_verdict` | The full verdict record: verdict, charged element names, grammar version, coverage statement, receipt refs. Free. |
| `darkseal_check` | Counterparty view: verdict class and the names of charged elements only. Free. |
| `darkseal_recompute` | Recompute a verdict from an exported capture + the grammar version + the outcome artifacts, with no service state. Free. |
| `darkseal_export_captures` | Export a sealed capture with the receipt-chain head for independent recomputation. Free. |

The check is free at every tier — there is no metering anywhere
in this product, and no paid tier changes verdict wording.

## Custody

The store carries only the sealed element field set: element
class and identity as presented, default state as rendered,
flow identity, timestamps, seals, outcome-artifact digests, and
the verdict with its named grammar basis. Form-field values are
never captured, held, or sealed — Darkseal seals default
states, not inputs. No page bodies beyond the grammar-named
elements, no browsing history, no principal profile. Records
serve the principal whose side sealed them; there is no
cross-principal aggregation surface. Every capture and verdict
appends one record to a hash-chained receipt journal, verified
at load; a store that fails verification fails closed.

## Status

v0.1.0 · built · **bench-pending** (independent bench requested;
builder tests are not a bench verdict) · name "Cyan Eclipse
Darkseal" is provisional pending trademark screen · not listed,
not offered for sale — review-first standing posture.

## Run

```sh
python3 server.py   # MCP over stdio
```

Environment: `ECLIPSE_DARKSEAL_STATE` (record store path),
`ECLIPSE_DARKSEAL_SURFACE_KEYS` (executing-surface channel keys,
JSON — surface-held in production; the keys in `keys/` are test
fixtures only).

## License

MIT — see `LICENSE`.
