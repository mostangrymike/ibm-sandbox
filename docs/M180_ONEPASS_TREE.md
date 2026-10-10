# M180 — isolated single-pass authenticated tree closure experiment

## October 10, 2026 — source/host CI only; NOT CMS target-proven

The user supplied real M179 results on z/VM 6.3 CMS on
October 9: native `GITPPROF G` returned RC0, CPU
454.92s / elapsed 459.44s; 8 trees, 272 reached
blobs, 279 entries, 280 verified objects, 7736/7736
index, no random seeks. M179 measured exactly
3,864,799 **CMS stage text lines per pass**, for a
total of 7,729,598. All four C `clock()` phase
measurements were UNAVAILABLE. M178 baseline was
455.95s CPU / 460.66s elapsed. The 1.22s difference
is not proof of an optimization.

**M179 target PASS**, but no post-run `QUERY FILEDEF`
was provided for independent hygiene comparison.
No repeat M179 run is required. Include pre/post
FILEDEF comparisons with any later experiment.

## M180 isolated experiment

M180 tests whether avoiding the second 3.86-million-line
sequential stage scan offsets hashing many more blobs.
This trades I/O for hashing; no speedup is presumed.

- `src/GITPONE.C` is a **new**, isolated C89 module
  based on M178's verified native SHA-1/index/tree code.
  It reads M174NET INDEX G read-only, builds the OID
  and object-number maps, then opens M173NET STAGE G
  read-only for exactly **one** forward pass.
- During the pass it parses/position-checks every object,
  SHA1-verifies each unique indexed tree and indexed blob,
  retains only authenticated tree bodies (64 MiB bound),
  and discards each authenticated blob body immediately.
  Commit/tag and duplicate unindexed bodies receive the
  original M178 hex/record-format checks but are not
  themselves SHA1-authenticated by this experiment.
- The root-tree walk then validates all tree modes,
  child types, names, directory depth, cycle and missing
  child rules, and **only permits a blob if it already has
  a matching SHA1 authentication marker**. Duplicated
  child references are counted once. External gitlinks
  are counted but never dereferenced. The walk and
  integrity checks remain fail-closed. Indexed unrelated
  blob corruption now rejects, unlike selective M178.
- It prints `M180 FORWARD SCANS 1 RECORDS N SEEKS 0`.
  RECORDS counts object headers, not CMS text lines.
  `M180 STAGE LINES N` counts successful OBJ/hex/empty
  stage lines read, and `M180 SHA1 BLOBS TOTAL N`
  counts distinct indexed blobs SHA1-checked, including
  unreachable blobs. `M180 AUTHENTICATED BLOBS N`
  counts reachable SHA1-validated blobs only.
- `src/GITPONCE.EXEC` checks explicit non-A 4096B
  G disk, existing protected stage/index, new module,
  no conflicting caller FILEDEF, and a one-pass
  authenticated closure/counters. It manages only
  temporary STGIN and IDXIN definitions and clears
  both on return. No output FILEDEF, import, ERASE,
  FORMAT, CP write or index rebuild.
- Host test `tests/test-m180-onepass-tree.py` is strict
  C89 and checks M178 parity, one-pass counts, exact
  stage lines, SHA of reachable and unrelated indexed
  blobs, malformed OID/hex, truncated index, and
  no mutation of stage/index input. Native-stage CI
  must pass before attempting actual CMS.

**This is a research alternative, not a replacement
for target-proven M178 or M179.** All original modules
and existing `M173NET STAGE G`, `M174NET INDEX G`,
`M171NET PACK/META A` remain unchanged.

## Exact conditional real-CMS test

On the Mac, in the existing `ibm-sandbox/src`:

```sh
git pull
./cms-upload.sh GITPONE.C GITPONCE.EXEC
```

On MAINT CMS, only read-only preflight and new-module build:

```text
QUERY DISK G
STATE M173NET STAGE G
STATE M174NET INDEX G
QUERY FILEDEF
STATE GITPONE C A
CMSCLNK GITPONE PLAIN
STATE GITPONE MODULE A
```

Proceed only on clean 4KB G disk, present stage/index,
no STGIN/IDXIN conflict, and successful new build.

```text
GITPONCE G CCB18BEC067E7886D70B82EF138EE56A8B899A61
QUERY FILEDEF
```

Require RC0 and `M180 TREE CLOSURE PASS`,
`M180 VERIFIED FAST TREE TARGET GATE PASS`,
8 TREES, 272 BLOBS, 0 GITLINKS, 279 ENTRIES,
280 VERIFIED, index 7736 UNIQUE, one forward
scan, 7736 object-header visits, zero seeks,
272 authenticated **reachable** blobs.
Record the new physical `M180 STAGE LINES`,
`M180 SHA1 BLOBS TOTAL`, CPU/elapsed Ready,
and final `QUERY FILEDEF`. Failure preserves
all original data/code: diagnose; do not erase
or reimport the 7736-object stage or index.

Do not use the overlapping VMCOM1 fullpack
`PMAINT 0141` for writes. To compare performance,
compare measured elapsed time with M178 460.66s
and M179 459.44s under otherwise comparable
conditions, while accounting for environmental
variation. The new experiment may be slower.
