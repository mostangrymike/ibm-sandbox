# Native CMS OID index for staged PACK objects

This experimental `GITCIDX.C` program builds a bounded, sorted
content-addressable index from the separate `GITCWALK STAGE` spool.
It does **not** store Git loose objects. BUILD/CHECK/GET are now
CMS-compiled and the resulting index passed full target CHECK and
first/last GET. The BUILD invocation/timing itself was not included
in the posted terminal output. It is independent of the native PACK inflater and does
not need a live network connection or another GitHub POST.

## Input and guarantees

The source `GITSTAGE DATA A` consists of `OBJ` header records and
uppercase hexadecimal body records as described in
[Native staging](NATIVE_STAGE.md). Run `GITCWALK VERIFY` **before**
building the index; `GITCIDX BUILD` checks the complete staged record
structure, every hex character, object sequence and bounds, but does
not independently recompute the Git SHA-1. The `VERIFY` pass does.

`BUILD` collects exactly 1,808 bounded object descriptors, sorts by
the 20-byte binary OID, collapses duplicate OIDs only when their type
and length agree, and writes `IDX1`, `OID`, and final `END` records
to `IDXOUT`. The final `END 1808 <unique>` trailer is a completeness
marker: interrupted, truncated, unsorted, duplicated, or malformed
index files cannot pass `GITCIDX CHECK`. Never use an index that
has not passed `CHECK`. `FIND` validates the entire index first
and performs binary search in bounded memory. `GET` additionally
opens `STGIN`, retrieves the selected body, recomputes its canonical
Git object SHA-1 independently, rejects mismatches, and reports the
first 16 bytes in hex without displaying unbounded object content.

The source and output records fit CMS variable record length 80.
BUILD, CHECK and FIND retain only 1,808 bounded descriptors in
memory. GET additionally holds one selected decoded body (up to
65,536 bytes) and a bounded canonical-hash scratch buffer.

## Consolidated CMS validation gate

On the Mac, from the repository's `src` directory:

```sh
git pull
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITCWALK.C
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITCIDX.C
```

On CMS, compile both programs **before** defining the DD names:

```text
GITCLNK GITCWALK
GITCLNK GITCIDX
FILEDEF PACKIN DISK GITPBUF PACK A
FILEDEF OBJOUT DISK GITSTAGE DATA A (RECFM V LRECL 80
FILEDEF STGIN DISK GITSTAGE DATA A
FILEDEF IDXOUT DISK GITINDEX DATA A (RECFM V LRECL 80
FILEDEF IDXIN DISK GITINDEX DATA A
GITCWALK STAGE
GITCWALK VERIFY
GITCWALK BADSTG
GITCIDX BUILD
GITCIDX CHECK
GITCIDX FIND 5A81BAF86E7DC7B72377087A8F160CAF8B889B74
GITCIDX FIND BA9F4D66B41352F0D0266090D14AD52F37318FCB
GITCIDX GET 5A81BAF86E7DC7B72377087A8F160CAF8B889B74
GITCIDX GET BA9F4D66B41352F0D0266090D14AD52F37318FCB
```

The first STAGE open attempt with no output LRECL failed
`DMSSOP036E Open error code 4 on OBJOUT`. Explicit
`(RECFM V LRECL 80` on both output FILEDEFs has now been
confirmed on CMS for staging and the index exists and passes CHECK. If
either output open fails, collect the exact FILEDEF and runtime
diagnostics; do not infer the index is valid or silently fall back.

The full run should report `STAGED OBJECTS 1808`,
`STAGE VERIFIED OBJECTS 1808`,
`PASS BADSTG: ALTERED BODY REJECTED`,
`INDEX WRITTEN 1808 UNIQUE N` and
`INDEX VERIFIED 1808 UNIQUE N` with the same N.
The captured real PACK index has been checked on CMS with
**exactly 1,808 unique OIDs**.

`FIND` and `GET` should resolve the first and last displayed OIDs to
object ordinals 1 and 1808, provided those OIDs occur only once
in the captured PACK. If duplicates exist, the index retains the
earliest ordinal.

## Host tests and remaining work

`tests/native_index_host.c` adds 1,808 synthetic descriptors,
duplicate normalization, OID lookups, independently hashed GETs,
valid-hex body tamper rejection, negative lookup, malformed staged
record detection and truncated-index-trailer rejection. The
`tests/run-native-stage-host.sh` runner compiles it under C89 and
independently checks native Git SHA-1 across all four Git object types
and both empty and nonempty bodies. GitHub Actions run
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36271873734
passed the full GET and tamper tests; run
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36271801328
passed the all-types Git cross-check. These are synthetic host tests; the real-PACK CMS target results
are recorded separately below.

This is only the **index and verified retrieval prototype**. Durable content-addressable object
storage still requires safe committed generations or equivalent
recovery, end-to-end restart proof, faster indexed retrieval, and native
REF_DELTA resolution. Indexing the verified spool does not complete
issue #2.

## Target-proven checkpoint: September 26, 2026

CMS compiled GITCWALK and GITCIDX cleanly using GITCLNK. The
explicit output FILEDEF succeeded. GITCWALK STAGE completed
all 1,808 objects and 1,117 OFS_DELTA instructions in
24.89/25.32 s CPU/elapsed. GITCWALK VERIFY independently
read back and hashed all 1,808 staged objects in 22.64/22.84 s;
BADSTG rejected the deliberately altered in-memory first body.
GITCIDX CHECK verified 1,808 unique OIDs in 0.13/0.14 s.
GITCIDX GET returned the known first and last object metadata
and content-hash-checked those bodies on target:

- OBJ 1: commit, 270 bytes, OID
  5A81BAF86E7DC7B72377087A8F160CAF8B889B74;
  GET elapsed 0.14 s.
- OBJ 1808: tree, 5,224 bytes, OID
  BA9F4D66B41352F0D0266090D14AD52F37318FCB;
  GET elapsed 7.59 s.

The terminal transcript does not show the BUILD command/result or
untruncated GET prefixes. CHECK conclusively validates an index
file exists, but BUILD's own timing is not measured in this log.

The time difference is consistent with GET's sequential scan of
all preceding stage records. Next isolated experiment will store
text-stream position cookies returned by ftell during BUILD and
use fseek for direct retrieval, but CMS variable-record seek
semantics are **not yet tested**. Preserve proven CHECK and GET
unchanged; any new seek behavior must be independently validated
on actual target before adoption.
