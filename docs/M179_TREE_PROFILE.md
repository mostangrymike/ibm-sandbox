# M179 — isolated read-only tree closure CPU profiler

## Why

On October 9, 2026, M178 passed real z/VM 6.3 CMS verification
over the retained 7736-object M173/M174 G stage/index.
It reported CPU 455.95s, elapsed 460.66s, two complete
forward scans, 15472 object visits and zero random seeks.
**The M178 RECORDS counter counts object headers, not
physical CMS stage records.** M177 TREE had overflowed
timing counters; no comparative speedup has been proven.

M179 is a **separate diagnostic module**, not a production
replacement and not yet target-proven. It retains the full
M178 SHA1, index, graph, type/mode/depth, resident cap,
count, two-scan, fail-closed checks and stages without writes.
The target-proven `GITPFST`, `GITPFAST`, `GITPTRE`,
`GITPVIEW` and saved PACK remain unchanged.

- `src/GITPPRF.C` is a C89 copy of M178's authenticated
  walker, with an extra counter of actual successfully
  read stage text records (OBJ header and hex body).
  Counter lines: `M179 STAGE LINES PASS1 N PASS2 N`.
- Additional C89 `clock()` instrumentation separates
  INDEX (read index/map), TREE_SCAN (pass 1), GRAPH
  (closure traversal), BLOB_SCAN (pass 2).
  Each phase reports CPU seconds, or `UNAVAILABLE`
  if the target C library clock is unsupported.
  Diagnostic timers do not change verification decisions.
- `src/GITPPROF.EXEC` requires a 4 KB explicit non-A
  input disk, preexisting M173/M174 files and module,
  rejects caller STGIN/IDXIN FILEDEF, binds only its
  own read inputs and clears only its own definitions.
  It requires the existing native two-scan count,
  OID, closure and authenticated-blob markers.
  It performs no ERASE, FORMAT, output FILEDEF,
  data copy, CP change or PACK/index build.
- Host regression: `tests/test-m179-tree-phase.py`
  compares real-format C89 stdout/closure with proven
  M178 and rejects bad OID, corrupt reached blob,
  malformed skipped body and truncated index.
  It checks physical line totals and all four CPU tags.

## Target run, only after host CI passes

On the Mac from the current `ibm-sandbox/src` directory:

```sh
git pull
./cms-upload.sh GITPPRF.C GITPPROF.EXEC
```

Then on CMS MAINT, read-only preflight:

```text
QUERY DISK G
STATE M173NET STAGE G
STATE M174NET INDEX G
QUERY FILEDEF
STATE GITPPRF C A
CMSCLNK GITPPRF PLAIN
STATE GITPPRF MODULE A
GITPPROF G CCB18BEC067E7886D70B82EF138EE56A8B899A61
QUERY FILEDEF
```

Proceed to the walk only after a successful native build
and a G preflight that still shows a 4096-byte R/W disk,
both original stage/index files, and no conflicting DDs.
Expected closure: 8 trees, 272 blobs, 279 entries,
280 verified objects, 7736 unique index, 2 forward
scans, 0 seeks, 272 authenticated reachable blobs,
`M179 TREE CLOSURE PASS`, and
`M179 VERIFIED FAST TREE TARGET GATE PASS`.
Capture the new `M179 STAGE LINES` and all four
`M179 CPU` rows, and final CMS Ready CPU/elapsed.
Compare post-run `QUERY FILEDEF` to pre-run state.
The timers may be unavailable and are not an
authenticated data input.

Do not rerun M173/M174 import/index audits for the
profiler. Do not replace production module names.
No reformat, ERASE, G stage/index write, directory
edit, or write access through the physically
overlapping PMAINT0141 fullpack. M179 is diagnostic
only until actual CMS target validation.
