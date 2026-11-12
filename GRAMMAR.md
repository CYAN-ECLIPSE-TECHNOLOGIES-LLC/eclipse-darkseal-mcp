# Cyan Eclipse Darkseal — element grammar (published)

**Grammar version:** `darkseal-grammar/1`

Darkseal compares the default-state vector sealed at traversal
start against the charges and terms that resulted, from the
principal's own confirmation and charge artifacts. The
comparison runs under this published grammar: the element
classes, the record shape, the pre-selection rules, and the
verdict rules over them. Any holder of a sealed capture, this
grammar, and the outcome artifacts can recompute the verdict
with no service access.

## Element classes (the bounded v1 set)

| Class | What it is in the rendered flow |
|---|---|
| `checkbox` | A tick-box presented with a default tick state |
| `toggle` | A two-state switch presented on or off |
| `radio/plan selector` | A one-of-many choice presented with one option shown chosen, or none |
| `continuity switch` | A switch governing whether a service, plan, or charge continues by default |

State outside these classes — free-form layouts, canvas-rendered
flows, dynamically injected elements the capture cannot
enumerate — is outside the grammar's coverage. It is named in
the capture's coverage statement, never silently ignored and
never judged.

## Element record shape

An element record is exactly three fields:

- `class` — one of the classes above
- `identity` — the element's identity as presented in the flow
- `default_state` — the state as rendered at traversal start,
  before any principal or agent action

Nothing more is a record. In particular, what a principal typed
into a form field is never part of an element record: Darkseal
seals default *states*, not inputs.

## Rendered-state conventions

| Class | Rendered states | Pre-selected when |
|---|---|---|
| `checkbox` | `checked` · `unchecked` | state is `checked` |
| `toggle` | `on` · `off` | state is `on` |
| `continuity switch` | `on` · `off` | state is `on` |
| `radio/plan selector` | the identity of the option shown chosen, or `none-selected` | state is any option identity other than `none-selected` |

## Outcome artifacts

The diff's outcome side is the principal's own confirmation and
charge artifacts, held as digests. An artifact record is exactly
three fields: `artifact_digest` (the digest of the principal's
artifact), `element_identity` (the element the charge or term
traces to), and `kind` (`charge` or `binding-term`). Records
from any other side are never diff inputs.

## Verdict rules

- **PRESELECTED-AND-CHARGED** — at least one sealed
  pre-selected element produced a charge or binding term in the
  artifacts; the verdict names those elements.
- **PRESELECTED-NOT-CHARGED** — defaults were sealed, and no
  resulting charge or term appears in the principal's artifacts.
- **NO-PRESELECTION** — no grammar-covered element was
  pre-selected in the rendered flow.
- **UNVERIFIABLE** — the capture is below the capture standard
  (the covered elements cannot be enumerated to the record
  standard, or the grammar version is unknown). A state of the
  evidence, never any party's fault.

## Coverage statement

Every capture states the classes the grammar covered in that
flow (`grammar_coverage`), the classes actually enumerated
(`covered_classes`), and the identities of elements outside
coverage (`outside_coverage`). Verdicts run only over covered
elements.

## Separation (the sibling boundary)

A checkout flow whose pre-selected covered elements are all
checkbox-class add-on defaults is the add-on default vector at a
checkout decision — a sibling product's object, marked
`UPSELLSEAL-OBJECT` on the record. Darkseal mints no whole-flow
verdict for that residue. Plan pre-selection, continuity
toggles, and flows with no checkout at all are Darkseal's
object and verdict normally.

## Versioning

Verdicts name their grammar version. A grammar revision adds a
new version; it never retro-alters a minted verdict, and
recomputation under the named version is stable.
