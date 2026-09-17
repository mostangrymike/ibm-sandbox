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
TCP/IP works. C89 front end exists but compiler backend is absent. Native
assembler is Assembler XF with DMSGPI. REXX orchestrates; assembler is for
binary/native/performance work. The client must be genuinely Git-compatible and
eventually use smart HTTP.

## Completed milestones

M1 SHA-1; M2 Git object encoding; M3 CMS-native object DB; M4 trees/commits;
M5 refs/branches/HEAD; M6A pkt-line; M6B advertisement parser; M6C fetch
negotiation; M6D ACK/NAK; M6E side-band; M6F pack header; M6G packed-object
header; M6H OFS_DELTA offset; M6I delta header; M6J delta application; M6K
REF_DELTA resolution; M6L OFS_DELTA base position; M6M pack-entry context; M6N
OFS_DELTA context/application. M4 onward listed above are target proven.

M6M context stores whole `datahex` in a CMS record and remains a small prototype,
not scalable to real pack objects.

## M7 compression

- M7A native RFC1950/1951 zlib capability: DONE, none found.
- M7B `GITZLIB` wrapper parser: DONE, target proven.
- M7C `GITSTOR` stored DEFLATE: DONE, target proven.
- M7D `GITFIX` fixed Huffman + LZ77: DONE, target proven.
- M7E `GITDYN` dynamic Huffman + LZ77: DONE, target proven.
- M7F `GITINFL` general/mixed inflater: DONE, target proven.
- M7G `GITADLER` Adler-32: DONE, target proven.
- M7H `GITPINF` ordinary pack-entry inflate: DONE, target proven.
- M7I compressed REF_DELTA/OFS_DELTA integration: DONE, TARGET PROVEN.

## M7 implementation lessons

CMS REXX `PROCEDURE` isolates variables; expose only required stems/variables.
Do not use two-argument dynamic `VALUE()` assignment on this target path. Use
explicit stems. `lens.i+1` is not compound index `i+1`; calculate an index first.
Canonical Huffman next-code recurrence uses previous bit-length count explicitly.
Keep EXEC source lines <=80 chars for fixed-80 c3270 transfer.

`GITINFL` gained `INFLATESTACK` for integration. Existing `M7INFL` was rerun
after this change and passed completely, preserving the proven inflater path.

## M7H target result

Ordinary blob packed entry inflated to TYPE 3 BLOB, SIZE 3, DATA `616263`, Adler
`024D0127`. Wrong Adler, pack-size mismatch, and invalid FCHECK rejected RC=8.
Delta entries were deliberately deferred. Final line:
`M7 PACK-ENTRY INFLATE INTEGRATION TESTS PASSED`.

## M7I compressed delta final result

Files/commits:
- `src/GITZDREF.EXEC` commit `6e6e9bd4418c6bfafc6d518d8b5e2a788e45ba16`
- `src/GITZDOFS.EXEC` commit `777f61877a93099c95d4d12aa8f0db7ca3a6b8b5`
- `src/M7ZDEL.EXEC` commit `9150519bb1d857a5886bc503dc5bb2c0a8982d14`

M7I inflates and verifies a zlib-compressed Git delta instruction stream, then
hands it to the existing target-proven M6 resolver/application path rather than
duplicating delta logic.

Final CMS target run:
- compressed REF_DELTA reconstructed `abcd` -> `61626364`
- compressed OFS_DELTA reconstructed `abcd` -> `61626364`
- initial `DMSSTT002E File GITPCTX PACK A not found` during context setup is the
  known harmless first-file diagnostic; the OFS test subsequently succeeded
- bad compressed-delta Adler rejected RC=8
- bad OFS base position rejected RC=8 after successful inflation
- final line: `M7 COMPRESSED DELTA INTEGRATION TESTS PASSED`

M7 compression/decompression functionality required for receiving Git pack
objects is now functionally proven in isolated vectors, including ordinary
objects and both Git delta forms. The next gap is no longer a DEFLATE primitive;
it is whole-pack walking/integration and scalability.

NEXT ACTION: begin the next isolated milestone for walking a complete Git PACK
byte stream: validate PACK header/version/count, iterate entries from their byte
positions, parse each entry header and delta base metadata, determine each zlib
stream boundary, inflate/reconstruct it, add reconstructed entries to pack
context, and validate the trailing pack SHA-1. Preserve all M6/M7 target-proven
components. Start with a tiny deterministic multi-entry pack before addressing
streaming/scalability.

## Important implementation facts

Git object hash input is exact ASCII `type + space + decimal size + NUL + binary
content`. CMS text policy strips trailing EBCDIC record-padding blanks, preserves
leading blanks, joins records with ASCII LF, and adds no final LF. Binary-safe
mode is required for arbitrary bytes.

Known cosmetic first-file `DMSSTT002E`/similar messages are accepted where
correctness is unaffected. Do not weaken collision/ref integrity to hide them.
Checkout currently means symbolic HEAD switching only. TLS support exists via
native GSK/Dynamic SSL facilities; use documented native TLS later rather than
implementing TLS ourselves.
