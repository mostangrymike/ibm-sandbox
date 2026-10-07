# M163 authenticated first-parent complete presence horizon

M163 adds:

`GIT HISTORYFIRSTPRESENCEHORIZON-REF-FULL <commit|ref> <depth> <path>`

It reports the fully complete prefix of the authenticated bounded first-parent
presence history. M161/M162 describe where incomplete history begins; M163
reports how far back from HEAD the history remains structurally complete.

When a complete prefix exists, the report includes:
- complete-through step and depth;
- step and depth distance from HEAD;
- signed author/committer span from HEAD to the last complete node;
- the next incomplete step and authenticated frontier edge when truncation
  follows the complete prefix.

The complete-node count is reconciled with the complete-through step so the
reported horizon cannot silently skip or include incomplete nodes.

## Sealed target fixture

Commit:
`486ADAA5B02080720F4B329C6F68550B13C6AA87`

Depth: 5

Path: `src/GITPBWALK.EXEC`

Expected compact proof:

```text
HFPH P1 S 1 5 4 4 4 50 50
HFPH P1 F 1 6 5 5 ADDED
```

Meaning:
- complete horizon is available;
- complete history runs through step 5 at depth 4;
- complete horizon is 4 first-parent steps / 4 depths from HEAD;
- HEAD-to-horizon author and committer span: 50 / 50 seconds;
- the next node is incomplete step 6 at depth 5;
- frontier edge is edge 5, authenticated status ADDED.

## Target gate

Transfer `GIT.EXEC`, `GITVREF.EXEC`, and `M163CHK.EXEC`, then run:

`GIT LEVEL`
`M163CHK`

The checker invokes the authenticated history command directly. No GITREC
rebuild is required.
