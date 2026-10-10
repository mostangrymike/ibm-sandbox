## October 10, 2026 — M180 ACTUAL CMS PASS, PERFORMANCE REGRESSION

**Real z/VM 6.3 MAINT terminal positive-path PASS.** `GIT600 600 G R/W`
3390, 1600 cylinders, 4096-byte blocks, 2 protected files
(62526 blocks used, 225474 free). Both original `M173NET STAGE G`
and `M174NET INDEX G` STATE RC0. Before/after `QUERY FILEDEF`
reported **No user defined FILEDEF in effect**.

`STATE GITPONE C A` RC0; `CMSCLNK GITPONE PLAIN` completed
`ASSEMBLER (XF) DONE`, no flagged assembly statements,
`built GITPONE MODULE mode PLAIN` in 2.05s elapsed.
`STATE GITPONE MODULE A` RC0. Actual command:
`GITPONCE G CCB18BEC067E7886D70B82EF138EE56A8B899A61`.

```text
TREE CLOSURE ROOT CCB18BEC067E7886D70B82EF138EE56A8B899A61
TREE CLOSURE TREES 8 BLOBS 272 GITLINKS 0
TREE CLOSURE ENTRIES 279 VERIFIED 280
TREE CLOSURE MAX OBJECT 393767 RESIDENT PEAK 6486786
TREE CLOSURE INDEX TOTAL 7736 UNIQUE 7736
M180 FORWARD SCANS 1 RECORDS 7736 SEEKS 0
M180 STAGE LINES 3864799
M180 SHA1 BLOBS TOTAL 2220
M180 AUTHENTICATED BLOBS 272
M180 TREE CLOSURE PASS
M180 VERIFIED FAST TREE TARGET GATE PASS CCB18BEC067E7886D70B82EF138EE56A8B899A61 G
```

Terminal `Ready; T=704.95/708.52 10:13:31` (CPU 704.95s,
elapsed **708.52s**) and later `QUERY FILEDEF` at 10:16:35
still `No user defined FILEDEF in effect`. No persistent input
was modified. Peak resident 6,486,786 bytes.

**The single-scan approach IS FUNCTIONALLY TARGET-PROVEN, but is
NOT a performance win.** M179 elapsed 459.44s, M178 460.66s;
M180 is **249.08s / approximately 54.2% slower than M179**.
One-pass avoids 3,864,799 text-line reads but authenticates
2,220 indexed blobs rather than only the 272 reachable blobs
(1,948 additional blobs). This is an observed tradeoff, not
precise attribution of CPU time to either stage or SHA operation.
Keep the established M178/M179 two-pass readers as performance
baselines. Do not rerun completed M180 test or rebuild G data.
Follow-up experiment must isolate a bounded optimization and
prove parity/corruption behavior before a single native target run.

---

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
