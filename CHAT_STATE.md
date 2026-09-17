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
M6 protocol/delta through M6N; M7 zlib/DEFLATE/inflate/Adler and compressed
ordinary/REF/OFS through M7I; M8 complete PACK ordinary/OFS/REF through M8C;
M9A chunked pack buffer. All completed milestones target proven.

## M8 complete PACK summary
M8A ordinary complete pack passed including trailer SHA and negative tests.
M8B OFS_DELTA reconstructs abc -> abcd in complete pack and verifies trailer.
M8C REF_DELTA resolves real base OID, reconstructs abc -> abcd and verifies
trailer. M8 regressions all passed after integration.

## M9 scalability

### M9A chunked pack buffer — DONE/TARGET PROVEN
Files/commits:
- `src/GITPBUF.EXEC` commit `0aaaaf281c02854248e210f9455c2539130d79e0`
- `src/M9PBUF.EXEC` commit `96473bc4fe1f6f43a78cdcbcb8cfcbb284eb2607`

GITPBUF establishes a CMS-record-backed logical binary byte stream. WRITE splits
hex input into records of at most 128 hex digits = 64 bytes. READ/READSTACK use
zero-based logical byte offsets/counts independent of physical record boundaries.
M9A deliberately does not modify the target-proven M8 walker.

Target regression:
- wrote 80 bytes -> `CHUNKS 2`
- bytes 0..7 -> `0001020304050607`
- 12-byte read from offset 60 crossed the 64-byte record boundary and returned
  `0C0D0E0F0001020304050607`
- final 8 bytes from offset 72 -> `08090A0B0C0D0E0F`
- READSTACK offset 63 count 3 -> `0F0001`
- offset 79 count 2 correctly rejected RC=8
- final `M9 CHUNKED PACK BUFFER TESTS PASSED`

Initial `DMSERS002E File GITPBUF PACK A not found` came from CLEAR before the
first file existed and is harmless.

Important limitation: M9A's WRITE still accepts one whole REXX hex argument and
READ currently loads all physical records into a REXX stem before extracting the
requested range. It proves logical chunk/boundary semantics, not bounded-memory
I/O yet. Do not overclaim it as streaming.

## NEXT ACTION
M9B should make the pack-buffer API incrementally writable/readable so memory use
can be bounded. Add INIT/APPEND (or equivalent) accepting one bounded chunk at a
time and a reader that retrieves only the CMS record(s) needed for a requested
range rather than EXECIO-reading the entire file. Preserve zero-based logical byte
semantics and 64-byte physical records. Test append fragments that do not align to
64-byte boundaries and reads spanning records. Do not migrate GITPWALK until this
storage primitive is target proven. After M9B, adapt incremental pack SHA-1 and
then inflater consumption to the bounded reader in isolated gates.

## Important implementation facts
Current M8 REXX paths accumulate whole hex strings; GITPCTX stores whole datahex
in one CMS record. Prototype only. Git hash input is exact ASCII
`type + space + decimal size + NUL + binary content`. CMS text strips trailing
EBCDIC record-padding blanks, preserves leading blanks, joins records with ASCII
LF, no final LF. Arbitrary bytes require binary-safe mode. Native GSK/Dynamic SSL
exists; use documented native TLS later rather than implementing TLS ourselves.
