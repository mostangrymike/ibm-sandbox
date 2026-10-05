# M157 authenticated current presence age

M157 adds:

`GIT HISTORYFIRSTPRESENCEAGE-REF-FULL <commit|ref> <depth> <path>`

It reuses the authenticated current-presence origin machinery. If the beginning
of the current presence run is known as an ADDED/DELETED change or repository
root, the command reports complete signed author and committer age from that
beginning to the newest commit. If bounded history is truncated before the
beginning, it reports observed spans rather than claiming a complete age.

## Sealed target fixture

Commit:
`6EF11911449C184457F3958ABE4CA7A0692CE8C9`

Depth: 6

Path: `src/GITPBWALK.EXEC`

Expected result:

- current state ABSENT
- current run nodes 6, exact runs 1
- begin known 1
- begin kind CHANGE
- begin edge 6 status DELETED
- author age 268 seconds
- committer age 268 seconds

## Compact target gate

After transferring the M157 wrappers and `M157CHK.EXEC`, run only:

`M157CHK`

Expected output:

```text
M157 LEVEL PASS M157/M157
M157 AGE PASS ABSENT EDGE 6 DELETED 268/268
M157 COMPACT TARGET GATE PASS
```

followed by plain `Ready;`. The checker accepts any synchronized GIT/GITVREF level M157 or newer.


## Combined compact gate through M157

`M157GATE EXEC` runs M155CHK, M156CHK, and M157CHK internally and suppresses
their successful detail. This is the preferred real-CMS acceptance command.

Expected output:

```text
M157GATE M155 PASS
M157GATE M156 PASS
M157GATE M157 PASS
M157GATE COMBINED TARGET GATE PASS
```

followed by plain `Ready;`. If it fails, run only the named compact checker
reported by the failure line; use a verbose history command only if that compact
checker also fails.
