# CMS/zVM Native Git Client — Chat State

Updated: 2026-09-17
Repository: `mostangrymike/ibm-sandbox`, branch `main`

## Workflow/rules
- GitHub canonical; edit there first, then user pulls/transfers/tests on CMS.
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
ordinary/OFS/REF through M8C; M9A/M9B bounded pack storage. All target proven.

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

M9B is materially bounded at the storage API: callers can append bounded chunks,
and READ loads only records intersecting the requested range. Metadata tail is
bounded below one physical record. It is not yet an end-to-end streaming Git pack
pipeline because the M8 walker/inflater still consume large REXX hex strings.

## NEXT ACTION
M9C: incremental PACK SHA-1 over GITPBUF. Build a bounded reader-driven hashing
path that hashes the pack payload (all bytes except the final 20-byte trailer) in
small chunks and compares against the trailer without assembling the whole pack
hex string. Reuse proven SHA implementation, adding an incremental interface only
if required; preserve existing SHA regressions. Use the known M8A pack checksum
`5F1C02695D4BC807AE4A5DD622AD1D28E7659429` as deterministic vector stored via
INIT/APPEND/FINAL. Test a corrupted trailer. Do not migrate the full walker yet.
After M9C, make inflater consumption incremental from GITPBUF.

## Important implementation facts
M8 walker/inflater still accumulate whole hex strings; GITPCTX stores whole
object datahex in one record. Git hash input exact ASCII `type + space + decimal
size + NUL + binary content`. CMS text strips trailing EBCDIC padding blanks,
preserves leading blanks, joins records with ASCII LF, no final LF. Arbitrary
bytes require binary-safe mode. Native GSK/Dynamic SSL exists; use documented
native TLS later rather than implementing TLS ourselves.
