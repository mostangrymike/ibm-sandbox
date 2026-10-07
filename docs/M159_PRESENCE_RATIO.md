# M159 authenticated first-parent presence ratio

M159 adds:

`GIT HISTORYFIRSTPRESENCERATIO-REF-FULL <commit|ref> <depth> <path>`

It builds on M158 complete-time accounting and reports PRESENT/ABSENT shares
in integer basis points (10000 = 100%). Ratios are emitted only when both
complete-time components are nonnegative and their total is positive.
Otherwise the corresponding AUTHOR/COMMITTER ratio is marked unavailable
instead of inventing a percentage.

## Sealed target fixture

Commit:
`486ADAA5B02080720F4B329C6F68550B13C6AA87`

Depth: 5

Path: `src/GITPBWALK.EXEC`

Expected compact proof:

```text
HFPR P1 S 2 1 1 1
HFPR P1 A 1 50 50 0 10000 0
HFPR P1 C 1 50 50 0 10000 0
```

Meaning:
- complete runs: 2
- incomplete runs: 1
- complete PRESENT runs: 1
- complete ABSENT runs: 1
- author complete total: 50 seconds, all PRESENT
- committer complete total: 50 seconds, all PRESENT
- PRESENT share: 10000 basis points
- ABSENT share: 0 basis points

## Target gate

Transfer `GIT.EXEC`, `GITVREF.EXEC`, and `M159CHK.EXEC`, then run:

`GIT LEVEL`
`M159CHK`

The checker invokes the authenticated history command directly rather than
through a CMS Pipelines command stage. No GITREC rebuild is required.
