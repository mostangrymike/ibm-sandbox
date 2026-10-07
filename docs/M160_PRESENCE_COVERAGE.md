# M160 authenticated first-parent presence coverage

M160 adds:

`GIT HISTORYFIRSTPRESENCECOVERAGE-REF-FULL <commit|ref> <depth> <path>`

It reports structural completeness of the bounded first-parent presence history
used by M158/M159. Coverage is deliberately based on authenticated run and node
counts, not elapsed time, so commit density is not misrepresented as time
coverage.

The report reconciles:
- complete + incomplete presence runs = all presence runs;
- complete + incomplete first-parent nodes = the chain node count;
- each complete/incomplete basis-point pair sums to 10000.

## Sealed target fixture

Commit:
`486ADAA5B02080720F4B329C6F68550B13C6AA87`

Depth: 5

Path: `src/GITPBWALK.EXEC`

Expected compact proof:

```text
HFPC P1 S 3 2 1 6 5 1
HFPC P1 B 6666 3334 8333 1667
```

Meaning:
- 3 presence runs: 2 complete, 1 incomplete;
- 6 chain nodes: 5 in complete runs, 1 in the truncated run;
- run completeness: 6666 basis points;
- node completeness: 8333 basis points.

## Target gate

Transfer `GIT.EXEC`, `GITVREF.EXEC`, and `M160CHK.EXEC`, then run:

`GIT LEVEL`
`M160CHK`

The checker invokes the authenticated history command directly. No GITREC
rebuild is required.
