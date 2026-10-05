# M156 authenticated closed presence duration

M156 adds:

`GIT HISTORYFIRSTPRESENCEDURATION-REF-FULL <commit|ref> <depth> <path>`

The command reuses the authenticated first-parent presence runs from M151-M154.
It reports duration only for a presence run that is bounded by authenticated
ADDED/DELETED transitions on both sides. Current/open and oldest/truncated runs
are not treated as fully closed durations.

For each closed run, the duration is the signed time difference between the
child commit that begins the run and the newer child commit that ends it.
Author and committer clocks are tracked independently. A PRESENT closed run
must begin at ADDED and end at DELETED; an ABSENT closed run must begin at
DELETED and end at ADDED. Violations fail closed.

## Sealed target fixture

Commit:
`486ADAA5B02080720F4B329C6F68550B13C6AA87`

Depth: 5

Path: `src/GITPBWALK.EXEC`

Expected presence states are ABSENT, PRESENT across four commits, ABSENT.
Therefore there are three presence runs and exactly one closed run:

- run 2 state PRESENT
- begin edge 5 status ADDED
- end edge 1 status DELETED
- author duration 50 seconds
- committer duration 50 seconds

## Compact real-CMS gate

Upload `GITVREF.EXEC`, `GIT.EXEC`, and `M156CHK.EXEC`, then run only:

`M156CHK`

Success output is three lines:

```text
M156 LEVEL PASS M156/M156
M156 DURATION PASS RUN 2 PRESENT 50/50
M156 COMPACT TARGET GATE PASS
```

followed by plain `Ready;`. Full verbose output is needed only if this compact
gate fails.
