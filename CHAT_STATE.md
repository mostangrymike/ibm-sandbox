# CMS/z/VM Native Git Client — Chat State

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
- M7E `GITDYN` dynamic Huffman + LZ77: DONE, TARGET PROVEN.
- M7F `GITINFL` general/mixed-block inflater: CURRENT, awaiting CMS target test.
- Planned: M7G Adler-32 verification; M7H Git pack-entry inflate integration.

## M7E final result

After REXX compatibility fixes, canonical Huffman next-code correction, and safe
compound-stem indexing, `M7DYN` passed on CMS. Final target output included an
exact match between decoded and expected dynamic-Huffman data, correct truncated
stream rejection RC=8, correct fixed-block rejection RC=8, and:

`M7 DYNAMIC HUFFMAN TESTS PASSED`

Last M7E source fix before target proof:
`1aa209f01ac463d77ab371256f3664ff3c8aec12`.

Important CMS REXX lessons from M7E:
- Do not use two-argument `VALUE()` dynamic assignment on this target path.
- Use explicit stems for the known Huffman tables.
- Expressions like `lens.i+1` do not mean compound index `i+1`; compute `k=i+1`
  first and use `lens.k`.
- Canonical next-code recurrence must use previous-length count explicitly:
  `prev=l-1; code=(code+bl.prev)*2`.

## M7F current state

New files:
- `src/GITINFL.EXEC`, commit `f2eb9f0b043476e0f111474d801ce017fd4422bc`
- `src/M7INFL.EXEC`, commit `5ca6a6b6630171aa63e0d83cf8bb4a373530db7f`

`GITINFL` consolidates stored, fixed, and dynamic DEFLATE decoding under one
bit position and one output history. It loops across blocks until BFINAL=1, so
LZ77 history is preserved across block boundaries. `M7INFL` tests final stored,
final fixed, final dynamic, a stored-then-fixed mixed stream, reserved BTYPE
rejection, and truncated mixed-stream rejection.

NEXT ACTION: user should `git pull`, upload `GITINFL.EXEC` and `M7INFL.EXEC`, run
`M7INFL`, and paste complete CMS output. Do not mark M7F done until target passes.

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
