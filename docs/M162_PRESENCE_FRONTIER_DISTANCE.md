# M162 authenticated first-parent presence frontier distance

M162 adds:

`GIT HISTORYFIRSTPRESENCEFRONTIERDISTANCE-REF-FULL <commit|ref> <depth> <path>`

It extends M161's structural coverage frontier with distance and chronology.
When a complete/incomplete frontier exists, it reports:
- first-parent step distance from HEAD to the first incomplete node;
- first-parent depth distance;
- author/committer span from HEAD to that incomplete node;
- author/committer delta across the frontier edge itself.

Signed chronology is preserved; unlike the M159 ratio, these values are not
suppressed merely because a clock delta is negative.

## Sealed target fixture

Commit:
`486ADAA5B02080720F4B329C6F68550B13C6AA87`

Depth: 5

Path: `src/GITPBWALK.EXEC`

Expected compact proof:

```text
HFPG P1 S 1 5 5 105 105
HFPG P1 E 5 ADDED 55 55
```

Meaning:
- frontier distance is available;
- incomplete history starts five first-parent steps / five depths from HEAD;
- HEAD-to-frontier author and committer span: 105 / 105 seconds;
- frontier edge 5 is ADDED;
- edge author and committer delta: 55 / 55 seconds.

## Target gate

Transfer `GIT.EXEC`, `GITVREF.EXEC`, and `M162CHK.EXEC`, then run:

`GIT LEVEL`
`M162CHK`

The checker invokes the authenticated history command directly. No GITREC
rebuild is required.
