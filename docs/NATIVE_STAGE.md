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
This code is **not yet compiled or validated on CMS**.

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

## Next CMS test

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

The explicitly specified output LRECL corrects the previous open
error. Do not treat output as proven until `STAGE`, `VERIFY`, and
`BADSTG` all pass on target. If `OBJOUT` still fails, capture the
FILEDEF response, `QUERY FILEDEF`, and complete CMS error code.
If writing stops partway through, `STAGE WRITE STOP OBJ n` identifies
the object; treat any partial file as invalid.

## Later work, not yet claimed

After target-proving the spool and readback gates, implement a
CMS-native indexed content-addressable object store with persistent
OID lookup, restart/readback validation, and atomic or detectable
incomplete writes. Add native REF_DELTA lookup; the captured PACK
uses OFS_DELTA, so the current 1,808-object run does not exercise REF.
Issue #2 remains open.
