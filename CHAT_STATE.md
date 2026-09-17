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
ordinary/REF/OFS integration through M7I; M8 complete PACK integration through
M8C. All completed milestones target proven.

## M8 complete PACK results
M8A ordinary: two blobs positions 12/27, PACK v2 count 2, SHA-1
`5F1C02695D4BC807AE4A5DD622AD1D28E7659429`, negative checksum/count tests pass.

M8B OFS_DELTA: base abc at position 12; OFS delta at position 24 reconstructs
abcd `61626364`; SHA-1 `8CA36BC28C5A2FDDD0EB9762CA36049A32D114B6`;
invalid distance rejected. Existing M8PACK regression preserved.

### M8C REF_DELTA — DONE/TARGET PROVEN
Changes:
- `src/GITPOID.EXEC` commit `4123c0c3c7f40e5e4fed4547f7ea090ca9e58ebb`
  provides reconstructed-object OID -> pack-position index.
- `src/GITPWALK.EXEC` REF support commit
  `6361d0796f3d5b3184cb8af399d3d9e466de034a`.
- `src/M8REF.EXEC` regression commit
  `97da5699286da4ccff9d8b548df9cb489f78895b`.

Regression gate after M8C changes:
- M8PACK passed completely.
- M8OFS passed completely.
- M8REF passed completely.

M8REF target details:
- entry 1 position 12 BLOB size 3 DATA `616263` (abc)
- its real Git blob OID is `F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F`
- entry 2 position 24 REF_DELTA representation size 6 reconstructs inherited
  BLOB DATA `61626364` (abcd)
- PACK v2 count 2
- trailing SHA-1 verified `7C95D709D4D46C612315060323DF0B5671650684`
- unknown base OID `02BA...` rejected RC=8 by GITPOID
- final `M8 WHOLE-PACK REF_DELTA TESTS PASSED`.

Known harmless first-file diagnostics now include GITPCTX/GITPOID PACK A not found
after CLEAR. Initial M8PACK run also showed DMSERS002E for absent GITPOID before
its first creation; functionality passed. Do not weaken correctness to hide these.

## Current boundary / NEXT ACTION
Whole-pack functional prototype is complete for ordinary, OFS_DELTA and REF_DELTA
entries with zlib/DEFLATE, Adler, reconstructed object OIDs/context and trailing
PACK SHA-1. Stop adding whole-hex prototype features now.

NEXT: M9 scalability architecture. Replace whole-pack/whole-object REXX hex and
one-record context with bounded/chunked processing suitable for real Git packs.
First isolated gate should establish a chunked binary-safe CMS pack input/storage
abstraction and incremental byte reader, without changing the proven M8 walker
algorithms yet. It should support reads across CMS record boundaries and bounded
chunks, with deterministic boundary tests. Then adapt incremental SHA/inflate and
object storage in later isolated steps. Preserve exact Git byte semantics.

## Important implementation facts
Current REXX paths accumulate whole hex strings; GITPCTX stores whole datahex in
one CMS record. Prototype only, not scalable. Git hash input is exact ASCII
`type + space + decimal size + NUL + binary content`. CMS text strips trailing
EBCDIC record-padding blanks, preserves leading blanks, joins records with ASCII
LF, no final LF. Arbitrary bytes require binary-safe mode. Native GSK/Dynamic SSL
exists; use documented native TLS later rather than implementing TLS ourselves.
