# Native CMS object staging: GITCWALK

## Target-proven prerequisites and the initial failure

The captured GitHub PACK is 340,027 bytes, version 2, containing
1,808 objects and 1,117 OFS_DELTA instructions. Its trailer SHA-1 is
`8C92E274ECA84B797F8925A6082915DD6CCDE196`. Native optimized
SHA-1 matched the original reference for **all 1,808 reconstructed
objects** under `GITCWALK OPTCHECK`. Optimized-only `OPTSHA` ran in
19.29 s CPU / 19.42 s elapsed on one CMS run.

The initial `GITCWALK STAGE` test ran the complete verified PACK
processing path but failed while opening the output file:

```text
PASS 1808 OBJECTS NEXT OFFSET 340007
OFS BASE POSITIONS RESOLVED 1117
OFS DELTAS APPLIED 1117
OBJECT OIDS COMPUTED 1808
DMSSOP036E Open error code 4 on OBJOUT
STAGE WRITE FAIL
Ready(00008); T=19.30/19.51
```

No `GITSTAGE DATA A` file was created. IBM FILEDEF documentation
identifies error code 4 on a new output file as missing both LRECL
and BLKSIZE. The former `FILEDEF OBJOUT DISK GITSTAGE DATA A`
omitted these values. [IBM FILEDEF reference](
https://www.ibm.com/docs/en/zvm/7.3.0?topic=commands-filedef).

## Current source and staging format

Commits `fa7052d`, `0806eb0`, and `04be7ee` add buffered
32-byte hex output records, independent readback validation, a
non-destructive negative gate, and progress/error diagnostics.
The updated code is now compiled and **CMS target-validated** for the
captured 1,808-object PACK.

`STAGE` computes the optimized OID for every reconstructed object
and emits CMS **variable-length text records** to FILEDEF `OBJOUT`:

- One header per object: `OBJ <index> <type> <length> <40-hex-OID>`.
- Uppercase body hex in records of at most 32 decoded bytes
  (64 characters) each. Empty object bodies use one blank record.
- The largest header and hex record both fit within LRECL 80.
- 1,808 headers and about 7.9 million body-hex characters are expected
  for the captured PACK. Ensure the A disk has enough free space.

This is a **temporary CMS-native staging file**. It is not yet
a durable content-addressable CMS object database or Git loose-object
storage. Existing `ALL`, `BADSHA`, `OFSAPPLY`, `OID`, `FASTOID`,
`FASTONLY`, `OPTSHA`, and `OPTCHECK` remain available.

`VERIFY` reads only `OBJOUT` (no live network and no PACKIN), strictly
checks record order, type, bounds and all hex bytes, reconstructs each
staged body, and independently recomputes and compares its canonical
Git SHA-1. Successful output: `STAGE VERIFIED OBJECTS 1808`.
`BADSTG` changes the first object **in memory only**, without altering
the file, and must print `PASS BADSTG: ALTERED BODY REJECTED`.

## Completed original CMS staging test

On the Mac, from the repository's `src` directory:

```sh
git pull
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITCWALK.C
```

On CMS, compile first, **then** issue FILEDEFs (language processors
can clear non-permanent FILEDEFs):

```text
GITCLNK GITCWALK
FILEDEF PACKIN DISK GITPBUF PACK A
FILEDEF OBJOUT CLEAR
FILEDEF OBJOUT DISK GITSTAGE DATA A (RECFM V LRECL 80
GITCWALK STAGE
LISTFILE GITSTAGE DATA A
GITCWALK VERIFY
GITCWALK BADSTG
```

Explicit output LRECL 80 corrected the open error. All three
commands passed on CMS with the captured real PACK. If `OBJOUT` still fails, capture the
FILEDEF response, `QUERY FILEDEF`, and complete CMS error code.
If writing stops partway through, `STAGE WRITE STOP OBJ n` identifies
the object; treat any partial file as invalid.

## Later work, not yet claimed

The isolated `GITCIDX` prototype is now committed, host-tested and
documented in [Native index](NATIVE_INDEX.md). It creates a sorted OID
index, detects incomplete index writes, and rehashes selected staged
objects during `GET`. Its original CHECK and first/last GET are now CMS target-proven;
AUDIT and experimental direct-seek modes still need CMS validation.
Remaining work: safe committed storage generations,
restart/readback validation and native REF_DELTA support.
The captured PACK uses OFS_DELTA, so the current 1,808-object test
does not exercise REF. Issue #2 remains open.

## Host-side independent regression gate (2026-09-26)

The host-only test `tests/native_stage_host.c` and its shell runner
`tests/run-native-stage-host.sh` compile `GITCWALK.C` as C89, stage
1,808 synthetic objects, read back and rehash every record, pass a
non-destructive in-memory corruption gate, demonstrate detection of an
actual corrupted disk record, restore the record, and pass readback
again. The runner independently checks Git's native `git hash-object`
result for `blob 3\\0abc`: `f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f`.

GitHub Actions workflow `.github/workflows/native-stage.yml` run
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36271371785
completed successfully. Its job logs show `STAGE VERIFIED OBJECTS 1808`,
`PASS BADSTG: ALTERED BODY REJECTED`, detection of disk tamper, and
`HOST STAGING AND GIT OID TEST PASSED`. Those initial results were HOST tests with synthetic data; the
subsequent real-PACK CMS proof appears in the target result below.

The original staging gate is now complete on CMS. The next new
CMS-only gate is AUDIT and the isolated direct-seek experiment,
documented in [Native index](NATIVE_INDEX.md).

## Combined CMS gate and host-proven index extension

The complete current test procedure is in
[`docs/NATIVE_INDEX.md`](NATIVE_INDEX.md). Host CI also proves
bounded sorted index construction, OID lookup, independently hashed
`GET`, malformed staged-body rejection, and incomplete index trailer
rejection. All four canonical Git type hashes have been cross-checked
against Git using both empty and nonempty synthetic bodies. Latest
expanded run: https://github.com/mostangrymike/ibm-sandbox/actions/runs/36271873734 .
Those host tests preceded the subsequent CMS proof of variable-record
output, full readback and 1,808 unique indexed OIDs.

## Target result: CMS staging and full readback

On September 26, 2026, GITCLNK GITCWALK built cleanly. With
RECFM V and LRECL 80, STAGE wrote all 1,808 reconstructed objects,
including 1,117 OFS_DELTA results, in 24.89 s CPU / 25.32 s elapsed.
Independent disk readback VERIFY recomputed all 1,808 OIDs and
completed in 22.64 / 22.84 s. BADSTG rejected deliberately altered
first-object content without writing it to disk. The full V1 index
passed GITCIDX CHECK (1,808 unique OIDs), and both first and last
GET calls returned correct metadata and independently verified OIDs.
Staging and indexing are thus target-proven for this captured PACK;
they are not a committed generation/recovery mechanism or native
REF_DELTA resolution. New AUDIT and experimental direct-seek index
tests are documented in [Native index](NATIVE_INDEX.md).
