# CMS/zVM Native Git Client — Chat State

Updated: 2026-09-17
Repository: `mostangrymike/ibm-sandbox`, branch `main`

## Workflow/rules
- GitHub canonical; edit there first, then user pulls/transfers/tests on CMS.
- Whenever files must be transferred to CMS for testing, always provide the Mac
  commands needed to fetch/prepare/transfer them, followed by the CMS commands.
  Do not give only the CMS-side test command. Keep both command batches exact and
  small.
- Proven Mac workflow: user works from the local repository `src` directory and
  runs `git pull`, then `./cms-upload.sh FILE1.EXEC FILE2.EXEC ...`. The upload
  script maps each local `.EXEC` file to `NAME EXEC A` on CMS and performs the
  established DFT transfer. Use this exact workflow in future instructions; do
  not substitute raw c3270/nc transfer commands unless the user explicitly asks.
- Exact small CMS command batches. IBM docs first for CMS/zVM; official Git/RFC
  docs for formats. No guessed CMS commands or purchased dependencies.
- No BFS/OpenExtensions runtime dependency. Fixed-80 source <=80 columns.
- c3270 DFT 2048 proven. Preserve target-proven cores; isolate milestones.

## Architecture/environment
z/VM 6.3 Evaluation under Hercules Aethra on Raspberry Pi 5/Debian. Assembler XF
+ DMSGPI available. REXX orchestrates; assembler for binary/native/performance.
Goal: genuine Git interoperability, eventually smart HTTP with native TLS.

## Completed
M1 SHA-1; M2 object encoding; M3 CMS object DB; M4 trees/commits; M5 refs/HEAD;
M6 protocol/delta through M6N; M7 compression through M7I; M8 complete PACK
ordinary/OFS/REF through M8C; M9A/M9B bounded storage; M9C bounded pack SHA-1;
M9D bounded inflater primitive; M9E bounded general inflater. All completed
milestones are target proven.

## M8 complete PACK summary
M8A ordinary complete pack passed including trailer SHA and negative tests.
M8B OFS_DELTA reconstructs abc -> abcd and verifies trailer. M8C REF_DELTA
resolves real base OID, reconstructs abc -> abcd and verifies trailer. M8
regressions all passed after integration.

## M9 scalability

### M9A chunk semantics — DONE/TARGET PROVEN
`GITPBUF` logical byte offsets work across 64-byte CMS records. 80-byte test made
two chunks; boundary and overrun tests passed.

### M9B incremental/selective pack buffer — DONE/TARGET PROVEN
Current `src/GITPBUF.EXEC` blob `47cd29329aed29fa0c99580835a007acf30aee4d`.
M9B adds metadata file `GITPMETA PACK A`, INIT/APPEND/FINAL, and selective READ.
APPEND accepts at most 64 bytes per call, carries a partial tail until a full
64-byte physical record can be emitted, and FINAL emits the last partial record.
READ is forbidden before FINAL and computes only the required CMS record range;
it no longer EXECIO-reads the entire pack file. WRITE remains as compatibility
path and now writes finalized metadata too.

Target results after M9B change:
- existing M9PBUF regression passed fully: 80 bytes -> 2 chunks, normal/boundary/
  stack reads correct, overrun rejected RC=8.
- M9PINC incremental regression passed fully.
- INIT succeeded.
- APPEND fragments of 10, 54, then 16 bytes succeeded (non-aligned calls).
- READ before FINAL rejected RC=8: `GITPBUF: pack buffer not finalized`.
- FINAL flushed partial last record.
- offset 60 count 12 -> `0C0D0E0F0001020304050607` across record boundary.
- READSTACK offset 63 count 3 -> `0F0001`.
- final eight bytes -> `08090A0B0C0D0E0F`.
- final `M9 INCREMENTAL PACK BUFFER TESTS PASSED`.

Known harmless first-run diagnostics: DMSERS002E for absent GITPMETA/GITPBUF when
CLEAR/WRITE removes files before creating them.

### M9C bounded PACK SHA-1 — DONE/TARGET PROVEN
`src/GITPSHA.EXEC` verifies a finalized GITPBUF without assembling the complete
pack in one REXX string. It reads the payload in chunks of at most 64 bytes via
GITPBUF READSTACK, feeds the existing target-proven GITSTRM SHA-1 module, then
reads the final 20-byte trailer separately and compares the digest.

`src/M9CSHA.EXEC` stores the known M8A two-object pack through INIT/APPEND/FINAL.
Target result computed and accepted
`5F1C02695D4BC807AE4A5DD622AD1D28E7659429`. A trailer ending in `...9428`
was rejected RC=8 while the computed payload digest remained `...9429`.
Final target message: `M9C BOUNDED PACK SHA-1 TESTS PASSED`.

A direct GITPSHA VERIFY against the prior M9B arbitrary 80-byte test buffer also
correctly rejected its final 20 bytes as a nonmatching trailer, RC=8. This was an
expected pre-regression sanity check, not a failure of M9C.

### M9D bounded inflater primitive — DONE/TARGET PROVEN
`src/GITPINFL.EXEC` provides an isolated GITPBUF reader-driven inflater path for
the stored-DEFLATE form used by the known M8A ordinary object. It does not first
assemble the complete compressed stream or complete PACK into one REXX hex
string. `src/M9DINF.EXEC` builds the known M8A pack incrementally and exercises
the primitive at the first object's zlib offset.

Target result:
- first ordinary object inflated to `DATA 616263` (`abc`).
- inflater reported `ZLIB BYTES 14`.
- next packed object remained at byte offset 27 with header `33`.
- final `M9D BOUNDED INFLATER TESTS PASSED`.

### M9E bounded general inflater — DONE/TARGET PROVEN
`src/GITPDEF.EXEC` extends bounded GITPBUF DEFLATE consumption to stored, fixed,
dynamic, and mixed blocks. `src/GITPINFL.EXEC` uses it behind the bounded zlib
wrapper. `src/M9EINF.EXEC` exercises the existing M7 fixed/dynamic/mixed vectors.
A REXX variable-scope bug in the first dynamic test was fixed by making the
bounded `bits` routine a PROCEDURE exposing only `base bitpos` (commit
`6f86ae8bb3be01c2708493639d5388ea89b7819b`).

Target results:
- fixed Huffman -> `616263`, `ZLIB BYTES 11`.
- dynamic Huffman -> expected M7 dynamic payload, `ZLIB BYTES 44`.
- stored then fixed -> `616263616263`, `ZLIB BYTES 19`.
- final `M9E BOUNDED GENERAL INFLATER TESTS PASSED`.
- M7INFL and M7DYN regressions passed, including expected negative cases.
- M8PACK, M8OFS, and M8REF regressions passed, including expected negatives.
- M9DINF passed again: `616263`, 14 zlib bytes, next header `33` at offset 27.

The existing general `GITINFL` remains target proven and unchanged. M8 still
uses its whole-pack/whole-string path; M9E has not yet been integrated into the
full pack walker. The bounded inflater still accumulates the complete inflated
object in one REXX hex string.

## NEXT ACTION
M9F: integrate the target-proven bounded GITPBUF inflater into an isolated
bounded ordinary-object PACK walker path. Parse PACK/object headers by logical
GITPBUF offsets, invoke GITPINFL at the object's zlib offset, advance by its
reported consumed-byte count, and prove both known M8A ordinary objects can be
walked without assembling the complete PACK/compressed stream. Keep the existing
M8 walker unchanged until this new path is target proven. Preserve bounded pack
SHA verification via GITPSHA. Do not tackle bounded inflated-output/object
storage yet; that remains a later scalability step.

## Important implementation facts
M8 walker/general inflater still accumulate whole hex strings; GITPCTX stores
whole object datahex in one record. Git hash input exact ASCII `type + space +
decimal size + NUL + binary content`. CMS text strips trailing EBCDIC padding
blanks, preserves leading blanks, joins records with ASCII LF, no final LF.
Arbitrary bytes require binary-safe mode. Native GSK/Dynamic SSL exists; use
documented native TLS later rather than implementing TLS ourselves.
