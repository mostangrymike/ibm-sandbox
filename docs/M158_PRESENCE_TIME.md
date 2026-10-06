# M158 authenticated first-parent presence time

M158 adds:

`GIT HISTORYFIRSTPRESENCETIME-REF-FULL <commit|ref> <depth> <path>`

It composes the authenticated presence-run, chronology, closed-duration and
current-age machinery into a per-run time ledger. Every run is classified as
CURRENT, CLOSED, ROOT, or TRUNCATED.

Complete runs contribute signed author/committer seconds to PRESENT or ABSENT
totals. A truncated oldest run is explicitly incomplete and contributes only
observed span to its own run record; it is never included in complete-time
totals.

## Sealed target fixture

Commit:

`486ADAA5B02080720F4B329C6F68550B13C6AA87`

Depth: 5

Path: `src/GITPBWALK.EXEC`

Expected accounting:

- presence runs: 3
- complete runs: 2
- incomplete runs: 1
- complete PRESENT runs: 1
- complete ABSENT runs: 1
- complete PRESENT author/committer seconds: 50 / 50
- complete ABSENT author/committer seconds: 0 / 0
- run 1: ABSENT CURRENT complete, 0 / 0 seconds
- run 2: PRESENT CLOSED complete, 50 / 50 seconds
- run 3: ABSENT TRUNCATED incomplete, 0 / 0 observed seconds

Compact proof records:

```text
HFPT P1 S 3 2 1 1 1
HFPT P1 T 50 50 0 0
HFPT P1 R 1 ABSENT CURRENT 1 0 0
HFPT P1 R 2 PRESENT CLOSED 1 50 50
HFPT P1 R 3 ABSENT TRUNCATED 0 0 0
```

## Target gate

Transfer `GIT.EXEC`, `GITVREF.EXEC`, and `M158CHK.EXEC`, then run:

`M158CHK`

The checker intentionally executes the authenticated history command directly,
not as a CMS Pipelines stage. Its full report remains visible so target proof
cannot be distorted by the pipeline-capture behavior isolated during M155-M157.
No GITREC rebuild is required.
