# M161 authenticated first-parent presence coverage frontier

M161 adds:

`GIT HISTORYFIRSTPRESENCEFRONTIER-REF-FULL <commit|ref> <depth> <path>`

It identifies where M160's incomplete structural coverage begins. When history
is depth-truncated, the report names the oldest incomplete presence run, its
state/kind/node count, its start/end step and depth, and—when a complete region
exists immediately before it—the last complete step plus the authenticated
ADDED/DELETED transition edge at the coverage frontier.

This differs from M152 current-presence origin: M152 locates the beginning of
the current run, while M161 locates the boundary between structurally complete
and incomplete bounded history.

## Sealed target fixture

Commit:
`486ADAA5B02080720F4B329C6F68550B13C6AA87`

Depth: 5

Path: `src/GITPBWALK.EXEC`

Expected compact proof:

```text
HFPF P1 S 1 1 3 ABSENT TRUNCATED 1 6 6
HFPF P1 B 5 4 5 ADDED
```

Meaning:
- history is truncated and has a complete/incomplete frontier;
- incomplete run is run 3, ABSENT, TRUNCATED, one node;
- incomplete run occupies step 6 through step 6;
- last complete step is 5 at depth 4;
- frontier edge is edge 5, authenticated status ADDED.

## Target gate

Transfer `GIT.EXEC`, `GITVREF.EXEC`, and `M161CHK.EXEC`, then run:

`GIT LEVEL`
`M161CHK`

The checker invokes the authenticated history command directly. No GITREC
rebuild is required.
