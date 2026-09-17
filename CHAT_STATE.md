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
  `TRANS04 ... records segmented` means the source violated this constraint.
- c3270 DFT buffer 2048 is proven; 16384 caused disconnects.
- Do not modify target-proven core code unnecessarily. Keep milestones isolated.

## Environment and architecture

IBM z/VM 6.3 Evaluation Edition under Hercules Aethra on Raspberry Pi 5/Debian.
TCP/IP works. C89 front end exists but `CBXFINIT` compiler backend is absent; do
not revisit buying XL C/C++ unless user asks. Native assembler is Assembler XF
with DMSGPI. REXX orchestrates; assembler is for binary/native/performance work.
The client must be genuinely Git-compatible and eventually use smart HTTP.

## Completed milestones

M1 SHA-1; M2 Git object encoding; M3 CMS-native object DB; M4 trees/commits;
M5 refs/branches/HEAD; M6A pkt-line; M6B advertisement parser; M6C fetch
negotiation; M6D ACK/NAK; M6E side-band; M6F pack header; M6G packed-object
header; M6H OFS_DELTA offset; M6I delta header; M6J delta application; M6K
REF_DELTA resolution; M6L OFS_DELTA base position; M6M pack-entry context; M6N
OFS_DELTA context/application. M4 onward listed above are target proven.

M6M context currently stores whole `datahex` in a CMS record and is only a small
prototype, not scalable to real pack objects.

## M7 compression

- M7A existing native RFC1950/1951 zlib capability: DONE, none found.
- M7B `GITZLIB` wrapper parser: DONE, target proven.
- M7C `GITSTOR` stored DEFLATE blocks: DONE, target proven.
- M7D `GITFIX` fixed Huffman + LZ77: DONE, target proven.
- M7E `GITDYN` dynamic Huffman + LZ77: DONE, target proven.
- M7F `GITINFL` general/mixed-block inflater: DONE, target proven.
- M7G `GITADLER` Adler-32 calculation/verification: DONE, target proven.
- M7H `GITPINF` Git pack-entry inflate integration: DONE, TARGET PROVEN.

## M7E final result

After REXX compatibility fixes, canonical Huffman next-code correction, and safe
compound-stem indexing, `M7DYN` passed on CMS. Final target output included an
exact match between decoded and expected dynamic-Huffman data, correct truncated
stream rejection RC=8, correct fixed-block rejection RC=8, and:
`M7 DYNAMIC HUFFMAN TESTS PASSED`.

Important CMS REXX lessons from M7E:
- Do not use two-argument `VALUE()` dynamic assignment on this target path.
- Use explicit stems for the known Huffman tables.
- Expressions like `lens.i+1` do not mean compound index `i+1`; compute `k=i+1`
  first and use `lens.k`.
- Canonical next-code recurrence must use previous-length count explicitly:
  `prev=l-1; code=(code+bl.prev)*2`.

## M7F final result

Files include `src/GITINFL.EXEC` and `src/M7INFL.EXEC`. Initial integration found
a REXX loop-variable collision in `bits`; fix `2f170e52...` made `bits` a
PROCEDURE exposing only `data bitpos`. Final target run passed stored, fixed,
dynamic, mixed stored->fixed, reserved-BTYPE rejection, and truncation rejection.
Final line: `M7 GENERAL INFLATER TESTS PASSED`.

## M7G final result

Files: `src/GITADLER.EXEC`, `src/M7ADLER.EXEC`. Target verified `abc` Adler-32
`024D0127`, mismatch RC=8, malformed checksum RC=4. Final line:
`M7 ADLER-32 TESTS PASSED`.

## M7H final result

Files/commits:
- `src/GITINFL.EXEC` stack-return interface commit
  `be9d955a62abce5e710f56de463678d615f9b06c`
- `src/GITPINF.EXEC` integration commit
  `4f79167865ce23ad9eae4d20645f4f1e35c27785`
- `src/M7PINF.EXEC` regression commit
  `73042dfbdc12f56ec8f086fe9e9d80b4ea94e04a`

The existing M7F regression was rerun after touching GITINFL and still passed in
full. M7H CMS target run then passed all gates:
- ordinary blob pack entry: TYPE 3 BLOB, SIZE 3, DATA `616263`, Adler `024D0127`
- wrong Adler rejected RC=8 with expected/actual values
- pack-header size mismatch rejected RC=8
- invalid zlib FCHECK rejected RC=8
- delta entry deliberately deferred to the proven M6 delta path, RC=8
- final line: `M7 PACK-ENTRY INFLATE INTEGRATION TESTS PASSED`

M7H proves an ordinary Git packed-object entry can be parsed, its RFC1950 wrapper
validated, DEFLATE payload reconstructed through GITINFL, Git entry size checked,
and Adler-32 verified. Delta entries are not yet connected to this zlib path.

NEXT ACTION: integrate compressed delta pack entries with the target-proven M6
REF_DELTA/OFS_DELTA machinery. Keep ordinary M7H and all M6 regressions intact.
The likely next isolated milestone should inflate the zlib payload of a delta
entry, then feed the resulting Git delta instruction stream to GITDAPP plus the
existing REF/OFS base resolver, rather than duplicating either subsystem.

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
