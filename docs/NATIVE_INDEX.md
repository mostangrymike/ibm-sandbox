# Native CMS OID index for staged PACK objects

This experimental `GITCIDX.C` program builds a bounded, sorted
content-addressable index from the separate `GITCWALK STAGE` spool.
It does **not** store Git loose objects and has not yet been compiled
or run on CMS. It is independent of the native PACK inflater and does
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
The code retains only 1,808 descriptors in memory and does not
retain staged body data.

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
`DMSSOP036E Open error code 4 on OBJOUT`. These explicit
`(RECFM V LRECL 80` definitions are a proposed target fix. If
either output open fails, collect the exact FILEDEF and runtime
diagnostics; do not infer the index is valid or silently fall back.

The full run should report `STAGED OBJECTS 1808`,
`STAGE VERIFIED OBJECTS 1808`,
`PASS BADSTG: ALTERED BODY REJECTED`,
`INDEX WRITTEN 1808 UNIQUE N` and
`INDEX VERIFIED 1808 UNIQUE N` with the same N.
The exact unique count is intentionally not assumed until the
captured real PACK is successfully indexed on CMS.

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
passed the all-types Git cross-check. These are synthetic host
proofs, not CMS target tests.

This is only the **index and verified retrieval prototype**. Durable content-addressable object
storage still requires safe committed generations or equivalent
recovery, CMS-verified indexed body retrieval, restart proof, and native
REF_DELTA resolution. Indexing the verified spool does not complete
issue #2.
