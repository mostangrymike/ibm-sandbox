# Canonical Git object IDs on EBCDIC CMS

## Confirmed September 26, 2026 failure

The user ran the updated native REF-capable GITCWALK on real CMS.
Its compiler succeeded, and its REFPACK trailer checksum matched
`9CD9B4CCFA5D5371C608230D3157F4766248355F`.
But the first blob, whose decompressed bytes are ASCII `abc`, was
reported with OID `5492DC378EC7097F3437B18BE17F4C58D0923A03`.
The fixture's subsequent REF_DELTA correctly references Git's real
blob ID `F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F`.
Thus RPACK/RAPPLY both failed locating the second object's base.
The old in-memory RTEST printed an unrelated
`0414AADE456A43A390C3A0E689DD2CDE0439DAA7` but declared
success, because it never checked a known external Git OID.

The root cause is now verified, not a suspected inflater problem.
Before this correction, GITCWALK object_oid/fast_oid and GITCIDX
idx_hash constructed Git's binary `type size NUL body` input with
`sprintf` over CMS-native EBCDIC type names, space and digits.
For `blob 3\0abc`, CMS produced this incorrect preimage:

```text
82 93 96 82 40 F3 00 61 62 63
```

SHA-1 of these exact bytes is the incorrect `5492DC37...`.
Git requires ASCII header bytes:

```text
62 6C 6F 62 20 33 00 61 62 63
```

SHA-1 of these bytes is `F2BA8F84...`, independently validated
by Git `hash-object`. For `blob 5\0abcde`, the correct Git
OID is `6A8165460570531A1247BD99A73B53A5A6E500D5`.
The selftest's body bytes were also CMS-native before the fix;
they are now explicit hexadecimal ASCII.

## Committed correction and compatibility boundary

The current GitHub main branch changes both programs:

- `src/GITCWALK.C` has `canonical_head`, constructing the raw
  ASCII type, space (0x20), decimal digits (0x30–0x39) and NUL
  using explicit byte values. Both object_oid and fast_oid use it.
  RTEST now checks the known raw `blob 3 NUL` header plus the
  actual Git SHA-1 results for `abc` and `abcde`.
- `src/GITCIDX.C` uses its own explicit ASCII `idx_head` in
  every OID calculation. `GITCIDX SELF` checks `blob 3\0abc`
  against Git's known hash, without accessing any stage file.
  The index formats are bumped from `IDX1` to `IDX2`, and
  `SIDX1` to `SIDX2`, with new matching END2/SEND2 markers.
  New code fails closed on old index formats.
- `GITCIDX SVAUDIT` additionally independently reopens and
  SHA-1-checks **every** stored direct-seek cookie in the new
  index. It prints progress every 256 unique objects.
- CI guards reject any reintroduction of native-text sprintf
  for canonical object headers. Synthetic host regression tests
  check full stage/index, REF chains, malformed and legacy index
  version rejection, independently accepted Git PACK, and
  direct-seek audit including corruption rejection.

Both old and optimized C SHA-1 compression algorithms were
previously byte-for-byte equal on 1,808 target objects, but
they shared the same **incorrect EBCDIC canonical header**.
Consequently, prior positive CMS STAGE/VERIFY/AUDIT results
proved file integrity and consistency, not Git interoperability.
The old GITSTAGE DATA A and GITINDEX DATA A / GITSEEK INDEX A
contain incorrect OIDs and must **not** be used as a production
Git object database. Their unpacked object body bytes and
verified raw PACK are still useful. They are preserved as
historical artifacts until a correct, independently checked
replacement is target-validated.

The inspected REXX `GITBOID.EXEC` and `GITOID.EXEC` already
construct ASCII type/space/decimal/NUL **in hexadecimal**;
they do not use this C-specific native-text header path.
This does not establish every other REXX path independently.

## Target validation and safe rebuild (not yet completed)

The next target test requires no live network download. Use the
existing positive REFPACK PACK A, the already saved
GITPBUF PACK A and new *separate* output file names. Do not
overwrite old GITSTAGE or either legacy index.

On the Mac, in `ibm-sandbox/src`:

```sh
git pull
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITCWALK.C
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITCIDX.C
```

Compile both programs before defining file DD names:

```text
CMSCLNK GITCWALK
CMSCLNK GITCIDX PLAIN
GITCWALK RTEST
GITCIDX SELF
FILEDEF PACKIN CLEAR
FILEDEF PACKIN DISK REFPACK PACK A
GITCWALK RPACK
GITCWALK RAPPLY
```

Expected: RTEST prints `CANONICAL ABC OID` equal to the correct
F2BA... OID and `REFTEST OID` equal to the correct 6A816... OID.
GITCIDX SELF prints `INDEX CANONICAL ASCII ABC PASSED`.
RPACK must produce exactly 3 objects, 2 REF_DELTA applications,
and the expected Git OIDs of abc, abcd and abcde. RAPPLY must
also resolve both REF bases. An unexpected RC 8 is a stop gate.

If all the preceding pass, the independent offline rebuild can
use the existing 340,027-byte PACK but **new files**:

```text
FILEDEF PACKIN CLEAR
FILEDEF PACKIN DISK GITPBUF PACK A
FILEDEF OBJOUT CLEAR
FILEDEF OBJOUT DISK GITFIX STAGE A (RECFM V LRECL 80
GITCWALK STAGE
GITCWALK VERIFY
FILEDEF STGIN CLEAR
FILEDEF STGIN DISK GITFIX STAGE A
FILEDEF IDXOUT CLEAR
FILEDEF IDXOUT DISK GITFIX INDEX A (RECFM V LRECL 80
FILEDEF IDXIN CLEAR
FILEDEF IDXIN DISK GITFIX INDEX A
GITCIDX BUILD
GITCIDX CHECK
GITCIDX AUDIT
FILEDEF FIDXOUT CLEAR
FILEDEF FIDXOUT DISK GITFIX SEEK A (RECFM V LRECL 80
FILEDEF FIDXIN CLEAR
FILEDEF FIDXIN DISK GITFIX SEEK A
GITCIDX SBUILD
GITCIDX SCHECK
GITCIDX SVAUDIT
```

The corrected real-PACK commit/tree OIDs will be **different**
from the previously printed legacy `5A81...` and `BA9F...`.
Do not write down hypothetical replacements. The target
GITCWALK STAGE output supplies the actual first/last values,
which can then be compared with independent Git data if the
corresponding raw object bytes are available. Never promote or
erase legacy files before all new gates succeed.

Remaining milestones: target-proven canonical headers and backward
REF_DELTA, correct fresh stage/index, persisted external and forward
REF_DELTA support, and safe committed/recoverable storage. GitHub
issue #2 remains open. Follow maximum-work-per-turn rule; CMS
runtime behavior requires actual target validation.
