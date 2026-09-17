# CMS/zVM Native Git Client — Chat State

Updated: 2026-09-17
Repository: `mostangrymike/ibm-sandbox`, branch `main`

## Workflow/rules
- GitHub is canonical; edit there first, then user git-pulls/transfers/tests CMS.
- Exact small CMS command batches. IBM docs first for CMS/z/VM; official Git/RFC
  docs for formats. Do not guess CMS commands or require purchased software.
- No BFS/OpenExtensions runtime dependency. Fixed-80 transfers: source <=80 cols.
- c3270 DFT 2048 proven. Preserve target-proven cores; isolate milestones.

## Environment/architecture
z/VM 6.3 Evaluation under Hercules Aethra on Raspberry Pi 5/Debian. Assembler XF
+ DMSGPI available. REXX orchestrates; assembler for binary/native/performance.
Goal is genuine Git interoperability and later smart HTTP/native TLS.

## Completed
M1 SHA-1; M2 object encoding; M3 CMS object DB; M4 trees/commits; M5 refs/HEAD;
M6 protocol/delta primitives through M6N; M7 zlib/DEFLATE/inflate/Adler and
compressed ordinary/REF/OFS delta integration through M7I: target proven.

Important limitation: current REXX paths accumulate whole hex strings and M6M
GITPCTX stores whole datahex in one CMS record. Prototype only, not scalable.

## M8 whole-pack integration

### M8A ordinary complete PACK — DONE/TARGET PROVEN
GITINFL consumed-byte mode + GITPWALK. Two ordinary blobs at positions 12 and 27
walked correctly; PACK v2 count 2; SHA-1
`5F1C02695D4BC807AE4A5DD622AD1D28E7659429` verified. Bad checksum and bad count
rejected RC=8. `M8 WHOLE-PACK WALKER TESTS PASSED`.

### M8B OFS_DELTA complete PACK — DONE/TARGET PROVEN
Changes:
- GITDAPP stack-return mode commit `066aab7a8aed338ad9fc328549a2c087fa241b73`
- GITPCTX stack-return lookup commit `2149f4a0594c275e67596050741a52690c9a0752`
- GITPWALK OFS support/fix commits `79bd7c7f29f8a88bb7f61cc581480155197ab059`
  and `250848b1e9ba0b754372a6e6a9cd48da00b9357a`
- regression `src/M8OFS.EXEC` commit
  `85ca25480b0238d11335adea0f5e2218a39b020b`

Existing `M8PACK` regression rerun after shared-component edits and passed fully.
M8B target pack:
- entry 1 position 12 BLOB size 3 DATA `616263`
- entry 2 position 24 OFS_DELTA representation size 6, reconstructed/inherited
  BLOB DATA `61626364` (`abcd`)
- PACK v2 count 2, SHA-1 `8CA36BC28C5A2FDDD0EB9762CA36049A32D114B6`
  verified
- context position 12 = abc BLOB; position 24 = abcd BLOB
- invalid OFS distance 0 rejected RC=8
- final: `M8 WHOLE-PACK OFS_DELTA TESTS PASSED`

Known `DMSSTT002E File GITPCTX PACK A not found` after CLEAR remains harmless.
Note pack entry SIZE for a delta is the uncompressed delta representation size,
not reconstructed object size; current walker correctly checks reconstructed size
inside GITDAPP's delta header rather than against packed-entry objsize.

NEXT ACTION: M8C complete whole-pack REF_DELTA support. Need parse the 20-byte base
OID after type-7 entry header, resolve that OID to an object available from earlier
pack entries and/or CMS object DB, inflate the delta representation, apply through
proven GITDAPP, inherit base type, store reconstructed entry in GITPCTX, advance
correctly, and verify final PACK SHA-1. Use deterministic complete pack test and
rerun M8PACK/M8OFS as regressions after touching shared walker/context. Prefer
adding OID metadata/index capability cleanly rather than duplicating resolution.
After REF_DELTA whole-pack support is proven, prioritize scalable chunked/streaming
pack/object storage instead of adding more whole-hex prototype features.

## Implementation facts
Git hash input: exact ASCII `type + space + decimal size + NUL + binary content`.
CMS text strips trailing EBCDIC record-padding blanks, preserves leading blanks,
joins records with ASCII LF, no final LF. Arbitrary bytes require binary-safe mode.
Known cosmetic first-file diagnostics accepted if correctness unaffected. Native
GSK/Dynamic SSL exists; use documented native TLS later, do not implement TLS.
