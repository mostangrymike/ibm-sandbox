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

## Completed V1 CMS validation (historical)

The September 26, 2026 target session compiled the original
GITCWALK and GITCIDX modules, defined the variable-length staging
files with LRECL 80, staged and independently verified all 1,808
reconstructed objects, and rejected deliberately corrupted data.
The resulting index passed CHECK with exactly 1,808 unique OIDs;
GET independently rehashed the first and last real objects. The
old compiler wrapper was GITCLNK; the canonical replacement is
now CMSCLNK, intended for the GCC F disk.

These commands do not need to be repeated for the next experiment.
For the only current target-dependent AUDIT and direct-seek test,
use the installation and test commands in the next-gate section
near the end of this document, including the new CMSCLNK EXEC.

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

## M13 next gate: complete AUDIT and experimental direct-seek index

Commit `a838b28` adds `GITCIDX AUDIT`: it loads the proven V1
index, scans all 1,808 staged objects, recomputes every canonical
Git SHA-1, verifies type, length and earliest object ordinal, and
requires complete coverage of all unique index entries. It is a
whole-file integrity reconciliation, not just a selected-object GET.

Commit `6e6b5b3` adds a **separate experimental seek index**.
`GITCIDX SBUILD` records each staged object's `ftell` position
before reading its header, writes a separately versioned sorted
OID index with record positions to FILEDEF `FIDXOUT` and adds a
mandatory `SEND` trailer. `SCHECK` validates this index using
`FIDXIN`. `SGET` uses `fseek` with the stored position to load
and independently hash only the selected object. Original V1
BUILD/CHECK/FIND/GET are retained unchanged as fallback.

IBM's C library documentation describes `ftell` values for
record-oriented text files as encoded positions. The native CMS
GCCCMS runtime must prove that an `ftell` position saved during
SBUILD can be consumed by `fseek` after the file is reopened
in a separate process. Host success does NOT prove this on CMS.
If it fails or returns the wrong record, SGET fails closed rather
than falling back silently. The measured baseline for sequential
V1 GET on captured OBJ 1808 is 7.59 s elapsed.

New host tests exercise 1,808 synthetic objects, full AUDIT
and negative tamper gates, SBUILD and SCHECK, direct SGET on
both ends, stale-body SHA rejection, and truncated seek-index
trailer rejection. GitHub Actions run
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36272574127
completed successfully. Synthetic fixture has 8 unique objects;
real captured PACK has 1,808 unique objects on CMS.

### Completed CMS AUDIT and direct-seek validation (historical commands)

The target-proven `GITSTAGE DATA A` and `GITINDEX DATA A`
already exist. No new PACK download or restaging is necessary.

On the Mac, from `ibm-sandbox/src`, transfer the neutral
compiler EXEC and current GITCIDX C source via the proven uploader:

```sh
git pull
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/CMSCLNK.EXEC
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITCIDX.C
```

On CMS, check whether the existing GCC F disk is writable. If it
reports `R/W`, install the neutral EXEC there and verify the copy.

```text
QUERY DISK F
COPYFILE CMSCLNK EXEC A CMSCLNK EXEC F
STATE CMSCLNK EXEC F
```

**Only after the copy succeeds**, erase `CMSCLNK EXEC A` to force
subsequent commands to resolve from F. If F reports `R/O`, skip the
COPYFILE/ERASE steps and use the uploaded A copy temporarily; an
authorized R/W F-disk access will be required for permanent installation.

For the independent AUDIT/seek gate, build the C-only program with
`CMSCLNK GITCIDX PLAIN`, then issue FILEDEFs. The experiment uses
distinct `GITSEEK INDEX A`; it cannot overwrite the target-proven
V1 `GITINDEX DATA A`.

```text
CMSCLNK GITCIDX PLAIN
FILEDEF STGIN DISK GITSTAGE DATA A
FILEDEF IDXIN DISK GITINDEX DATA A
FILEDEF FIDXOUT DISK GITSEEK INDEX A (RECFM V LRECL 80
FILEDEF FIDXIN DISK GITSEEK INDEX A
GITCIDX AUDIT
GITCIDX SBUILD
GITCIDX SCHECK
GITCIDX SGET 5A81BAF86E7DC7B72377087A8F160CAF8B889B74
GITCIDX SGET BA9F4D66B41352F0D0266090D14AD52F37318FCB
```

Required positive markers: `AUDIT VERIFIED 1808 UNIQUE 1808`,
`SEEK INDEX WRITTEN 1808 UNIQUE 1808`, and
`SEEK INDEX VERIFIED 1808 UNIQUE 1808`. Both SGET results
must return the same validated OIDs, types and sizes as V1 GET.
The last object's elapsed time is the important performance
measurement; do not claim a speedup before observing it on CMS.

Do not clear or overwrite target-proven `GITINDEX DATA A`
during this experiment. Failure of the seek experiment leaves
V1 CHECK/GET available.

### Live F-disk result

On 2026-09-26 the user's `Q DISK` showed GCCLIB VDEV 29D accessed
as **F R/W**, with 2,055 free blocks. The neutral compiler may
therefore be copied directly from its uploaded A copy into F.
Copy and verify before erasing the temporary CMSCLNK EXEC A,
and preserve the existing old GITCLNK EXEC A for rollback until
the new CMSCLNK PLAIN build passes. The actual transfer, copy,
compile and seek-index run remain CMS-validation pending.

### Compiler EXEC rename

`GITCLNK` is the historical build utility used for the target-proven
C/assembler modules; `CMSCLNK` is now the canonical GCCCMS build
utility intended to reside on F. Its default NAPI mode retains the
legacy build sequence. The new optional PLAIN mode omits the native
inflater adapter for GITCIDX and other ordinary C programs. Host
static-source checks passed; CMS F-disk placement and PLAIN-mode
module linking still require target validation. See [Build](BUILD.md).

## Latest result: target-proven direct seek

September 26, 2026 CMS transcript:

| Mode | Result | CPU / elapsed |
|---|---|---|
| AUDIT | 1,808 staged bodies, 1,808 unique OIDs | 20.96 / 21.09 s |
| SBUILD | 1,808-unique separate seek index written | 7.13 / 7.21 s |
| SCHECK | 1,808-unique seek index verified | 0.14 / 0.15 s |
| SGET first | commit #1, 270 bytes, expected OID | 0.15 / 0.15 s |
| SGET last | tree #1808, 5,224 bytes, expected OID | 1.72 / 1.77 s |

The last-object sequential V1 GET previously took 7.59 seconds
elapsed. The single observed direct-seek run reduced this to
1.77 seconds, a 4.29x ratio and approximately 76.7% less time.
The SBUILD/SCHECK and first/last SGET success on actual CMS prove
that this GCCCMS runtime can reuse saved ftell positions after
closing and reopening the **unchanged** CMS staging file. They do
not prove index-cookie portability after stage modification or
system reboot. Retain V1 index/GET as fallback. The user's
log begins after an unlabeled command's Ready line, so actual
F-disk CMSCLNK installation is not independently confirmed by
that excerpt.

The next functional gate is native backward REF_DELTA, now
implemented and independently validated with Git on the host.
See [Native REF_DELTA](NATIVE_REF.md) for generated positive and
negative PACK fixtures, exact Mac upload/CMS execution commands,
and the limits of this first native REF milestone. No real-PACK
restaging or separate seek-index retest is needed.

## EBCDIC canonical OID correction

The first CMS REF fixture revealed that native C code formatted the Git
object header using EBCDIC, producing consistent but noncanonical
hashes. The original staging/index tests proved reconstruction and
readback consistency, not Git object-ID correctness. Original IDX1
and SIDX1 indexes must not be promoted. Current GITCIDX uses explicit
ASCII for the type, separator, decimal length and zero byte;
SELF checks the known Git blob ABC vector. New IDX2/SIDX2 formats
reject the old indexes, and SVAUDIT independently rehashes every
saved direct-seek entry. Preserve existing GITSTAGE, GITINDEX and
GITSEEK files. Regenerate into GITFIX STAGE, GITFIX INDEX and
GITFIX SEEK only after the corrected RTEST/RPACK pass on CMS.
Exact commands: docs/CANONICAL_OIDS.md. The previously measured
1.77-second SGET run proved seek mechanics, but its legacy stored
OID is not a canonical Git ID.

## New optional IDX2 and SIDX2 PAIR gate

Following the on-target Git-compatible RTEST, SELF, RPACK and RAPPLY
success on September 26, 2026, GITCIDX gained a separate PAIR mode.
It loads both newly generated IDX2 and SIDX2 formats, compares every
sorted canonical OID, object ordinal, type and size, and then invokes
SVAUDIT to independently reopen/re-hash every staged object via the
seek cookies. It detects stale or mismatched index generations,
corrupt stage bytes and invalid offsets without modifying source or
index files. The 1,808-synthetic-object host suite passed including
mismatch injection and restoration in GitHub Actions run
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36280431393 .

PAIR is additional verification, not required before the first
canonical 1,808-object GITFIX migration. After uploading/building the
latest GITCIDX.C with the known CMSCLNK GITCIDX PLAIN sequence and
binding STGIN, IDXIN and FIDXIN to the three new GITFIX files,
`GITCIDX PAIR` must report `PAIR VERIFIED UNIQUE 1808` before
regarding the two indexes as a mutually attested candidate. The
original IDX1/SIDX1 files must remain historical, not be mixed with
new IDX2/SIDX2 files.
