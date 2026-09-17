# CMS/zVM Native Git Client — Chat State

Updated: 2026-09-17
Repository: `mostangrymike/ibm-sandbox`, branch `main`

## User workflow and rules

- GitHub is canonical. Make source changes on GitHub first.
- User runs `git pull` on Mac, transfers source to CMS with c3270, runs target
  tests, and pastes complete output.
- Keep CMS command batches small and exact.
- Prefer IBM documentation for CMS/z/VM and official Git/RFC documentation for
  protocol formats. Do not guess CMS commands.
- Use only facilities already available in the z/VM evaluation image. User does
  not want to purchase a compiler or other software.
- Do not depend on BFS/OpenExtensions shell at runtime.
- Fixed-80 CMS transfers require every source line <=80 characters.
- c3270 DFT buffer 2048 is proven; 16384 caused disconnects.
- Do not modify target-proven core code unnecessarily. Keep milestones isolated.

## Environment and architecture

IBM z/VM 6.3 Evaluation Edition under Hercules Aethra on Raspberry Pi 5/Debian.
TCP/IP works. Native assembler is Assembler XF with DMSGPI. REXX orchestrates;
assembler is for binary/native/performance work. Client must be genuinely
Git-compatible and eventually use smart HTTP.

## Completed milestones

M1 SHA-1; M2 object encoding; M3 CMS-native object DB; M4 trees/commits; M5
refs/branches/HEAD; M6 protocol/delta primitives through M6N; M7 RFC1950/DEFLATE
and compressed pack-entry/delta integration through M7I. All listed completion
milestones are target proven.

M6M context stores whole `datahex` in a CMS record and remains a small prototype,
not scalable to real pack objects.

## M7 compression

M7A native zlib investigation DONE none found; M7B wrapper; M7C stored; M7D fixed
Huffman/LZ77; M7E dynamic Huffman/LZ77; M7F general/mixed inflater; M7G Adler-32;
M7H ordinary pack-entry inflate; M7I compressed REF/OFS delta integration: all
DONE and target proven.

CMS REXX lessons: PROCEDURE isolates variables; expose only required state. Do
not use two-argument dynamic VALUE assignment here. Compute compound-stem indices
explicitly. Keep EXEC source lines <=80 chars for fixed-80 transfer.

`GITINFL` has stack-return integration modes. Always rerun `M7INFL` after changing
it because it is now shared pack infrastructure.

## M8 whole-pack integration

### M8A whole-PACK walker — DONE, TARGET PROVEN

Files/commits:
- `src/GITINFL.EXEC` consumed-byte reporting commit
  `edccb52f4cc60db41502d1ae30d2fcfec67f5652`
- `src/GITPWALK.EXEC` commit `efadd73dca8e55027803c73e0c115aa35f6f2c51`
- `src/M8PACK.EXEC` commit `58fa809d1b971455cba1f8eb8ab88b2c98d36d78`

M7F was rerun after changing GITINFL and passed completely.

Final M8A CMS target run on deterministic two-entry PACK:
- entry 1 at byte position 12: BLOB size 3, data `616263` (`abc`)
- entry 2 at byte position 27: BLOB size 3, data `78797A` (`xyz`)
- PACK version 2, object count 2
- trailing PACK SHA-1 verified as
  `5F1C02695D4BC807AE4A5DD622AD1D28E7659429`
- both reconstructed entries retrieved correctly from GITPCTX
- bad trailing pack SHA-1 rejected RC=8 with expected/actual values
- bad declared count rejected RC=8 after the two available entries
- final line: `M8 WHOLE-PACK WALKER TESTS PASSED`

The repeated `DMSSTT002E File GITPCTX PACK A not found` is the known harmless
first-file diagnostic after context clear. In the bad-count test output,
`78797AGITPWALK...` is only adjacent console output; the intended count failure
occurred and RC=8 was observed.

M8A proves the walker can validate a complete PACK header, use inflater consumed
byte counts to advance across adjacent zlib streams, reconstruct ordinary
entries at actual pack positions, populate context, and verify the pack trailer.
It currently covers ordinary entries only; whole-pack REF/OFS delta dispatch is
the next integration gate.

NEXT ACTION: M8B extend GITPWALK to parse REF_DELTA and OFS_DELTA metadata inside
a complete PACK and reconstruct them using the already-proven M6/M7 delta paths.
Use a deterministic complete pack containing an ordinary base plus at least one
delta entry, preserve M8A and M7F regressions, and verify final PACK SHA-1. Avoid
rewriting proven delta/inflater algorithms. After whole-pack delta walking works,
address scalable storage/streaming instead of whole-pack/whole-object REXX hex.

## Important implementation facts

Git object hash input is exact ASCII `type + space + decimal size + NUL + binary
content`. CMS text policy strips trailing EBCDIC record-padding blanks, preserves
leading blanks, joins records with ASCII LF, and adds no final LF. Binary-safe
mode is required for arbitrary bytes.

Known cosmetic first-file diagnostics are accepted where correctness is
unaffected. Do not weaken integrity checks to hide them. Checkout currently means
symbolic HEAD switching only. TLS support exists via native GSK/Dynamic SSL; use
documented native TLS later rather than implementing TLS ourselves.
