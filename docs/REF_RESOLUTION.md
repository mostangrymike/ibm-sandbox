# M13 next isolated CMS gate: external and forward REF_DELTA

## Verified baseline

On September 26, 2026, z/VM CMS compiled the corrected native C
walker and indexer. The positive three-object backward chained REF
fixture passed with Git-compatible OIDs and two REF_DELTA applications.
The original 1,808-object saved PACK was then rebuilt offline into
`GITFIX STAGE A`, `GITFIX INDEX A` (IDX2), and
`GITFIX SEEK A` (SIDX2). Independent VERIFY, AUDIT, SFAST and PAIR
all passed with 1,808 unique canonical OIDs. Original PACK checksum:
`8C92E274ECA84B797F8925A6082915DD6CCDE196`.

The canonical first commit is
`00D8D63229305230C8D37F884CE87F9E1A89468C`, size 270.
The canonical last tree is
`EB37E3F23FF4FC137D715D71A711D3B7632D75F2`, size 5,224.
Both were retrieved via target SGET. Do not repeat full PACK capture,
reconstruction or indexing for this experiment. Preserve historical
IDX1/SIDX1 as legacy and the new GITFIX generation as validated.

## Independent implementation and host results

The updated `GITCWALK.C` adds two **isolated, optional** modes:
`XPACK`/`XAPPLY` resolve a missing REF base by scanning bounded
CMS text records from FILEDEF `EXTIN`. They require a matching
40-byte canonical Git OID and recompute the selected external
object's SHA-1 over the actual body before using it. Malformed,
duplicated, unprovided and altered external bases fail closed.
`FPACK` defers unresolved forward same-PACK REF_DELTA instructions,
then completes multi-pass dependency resolution once later objects
have been inflated and hashed. A three-object fixture contains
two chained forward deltas followed by their ordinary base.

Separate host fixtures are generated with
`tests/make-native-ref-pack.py`. They cover chained forward
dependencies, previously proven backward deltas, absent/forward
negative resolution, external single/multiple staged records,
duplicated/altered/missing staged base OIDs, and a real target
first-commit no-op copy delta. The host adapter substitutes zlib
only for the native CMS inflater. Git itself independently
accepts the backward and forward PACKs via `git index-pack`
and reconstructs all three blobs with `git cat-file`.
All host regressions passed in
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36282246527 .

These new modes are **not yet CMS validated**. They do not replace
the target-proven original STAGE, RPACK, RTEST, IDX2 or SIDX2 paths.

## Exact isolated target test

Mac commands from `/Users/mikewommack/ibm-sandbox/src`; use
the already running single c3270 through the existing uploader:

```sh
git pull
python3 ../tests/make-native-ref-pack.py .
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITCWALK.C
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/FCHAIN.PACK
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/XPACK.PACK
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/XBAD.PACK
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/XREAL.PACK
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/EXTBASE.DATA
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/EXTMULT.DATA
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/EXTBAD.DATA
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/EXTMISS.DATA
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/EXTDUP.DATA
```

On CMS, compile **before** FILEDEF; none of these tests writes
to GITFIX or the historical stage/index/seek files.

```text
CMSCLNK GITCWALK
FILEDEF PACKIN DISK FCHAIN PACK A
GITCWALK FPACK
FILEDEF PACKIN CLEAR
FILEDEF PACKIN DISK XPACK PACK A
FILEDEF EXTIN DISK EXTBASE DATA A
GITCWALK XPACK
GITCWALK XAPPLY
FILEDEF EXTIN CLEAR
FILEDEF EXTIN DISK EXTMULT DATA A
GITCWALK XPACK
FILEDEF PACKIN CLEAR
FILEDEF PACKIN DISK XREAL PACK A
FILEDEF EXTIN CLEAR
FILEDEF EXTIN DISK GITFIX STAGE A
GITCWALK XPACK
```

Expected positive markers for FCHAIN: `FORWARD REF OBJ 2`
(type 3, 4 bytes, `85DF50785D62D3B05AB03D9CBF7E4A0B49449730`),
then `FORWARD REF OBJ 1` (type 3, 5 bytes,
`6A8165460570531A1247BD99A73B53A5A6E500D5`), ending
`PASS 3 OBJECTS` and `REF DELTAS APPLIED 2`.

Both XPACK and XAPPLY with EXTBASE must verify an external
blob of 3 bytes and reconstruct Git blob `abcd`, OID
`85DF50785D62D3B05AB03D9CBF7E4A0B49449730`.
The EXTMULT stage stores the matching base as record #2;
it must produce the same result. The XREAL fixture is a
single REF_DELTA copy of the already-validated first commit
from the full GITFIX stage, proving actual persisted external
lookup. Expected output: `EXTERNAL REF BASE VERIFIED TYPE 1
SIZE 270` and an ordinary reconstructed type 1 / 270-byte
object with the *same* commit OID
`00D8D63229305230C8D37F884CE87F9E1A89468C`.

### Negative CMS fixtures

Only after the positive gates pass, keep changes isolated by
redefining existing FILEDEFs between tests:

```text
FILEDEF PACKIN CLEAR
FILEDEF PACKIN DISK XPACK PACK A
FILEDEF EXTIN CLEAR
FILEDEF EXTIN DISK EXTBAD DATA A
GITCWALK XPACK
FILEDEF EXTIN CLEAR
FILEDEF EXTIN DISK EXTMISS DATA A
GITCWALK XPACK
FILEDEF EXTIN CLEAR
FILEDEF EXTIN DISK EXTDUP DATA A
GITCWALK XPACK
FILEDEF EXTIN CLEAR
FILEDEF EXTIN DISK EXTBASE DATA A
FILEDEF PACKIN CLEAR
FILEDEF PACKIN DISK XBAD PACK A
GITCWALK XPACK
```

All four negative invocations must return RC 8. The corrupted
and duplicated stage cases must report `INVALID EXTERNAL
STAGE RECORD`; absent or unmatched OIDs must report
`UNRESOLVED REF BASE OBJ 1`. A malformed or absent external
source must never be silently accepted.

## Scope and remaining gaps

FPACK currently resolves forward **REF_DELTA** chains when their
base objects are available later in the same PACK. An OFS_DELTA
that depends on a still-deferred REF object is not yet supported;
neither is a cyclic unresolved dependency. XPACK uses a verified
separate stage for external bases but does not yet perform a
content-addressed indexed lookup; it scans the external stage.
These are optional test modes, not a complete production Git
receive-pack implementation.

Full canonical stage/index consistency is target-proven. A
transactional commit marker, restart/reboot readback and safe
generation recovery remain separate work under GitHub issue #2.
