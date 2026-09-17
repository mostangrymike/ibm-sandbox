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
- M7E `GITDYN` dynamic Huffman: CURRENT, not yet target proven.
- Planned: M7F general/mixed-block inflater; M7G Adler-32; M7H pack integration.

## M7E detailed state

Files: `src/GITDYN.EXEC`, `src/M7DYN.EXEC`.
Initial commits:
- GITDYN `a62308d79b00cf56112ef3da23a9e11a801b8473`
- M7DYN `3aa4f4afc64a6cc9918df1cce29c41c4e5892483`
80-column fix: `b5190b07b8de5e8034b4b97326248dc15420c4ef`.

First target run returned silent RC 8. Procedure stem exposure was added in
`14d13fb2dedb491ce36cc9895770ffa1d3226cea`.

Next target failure was `call value ...` Error 40. Commit
`4c21a120f6263a34e0c4e32c9aef5ac77c435772` changed it to function form, but
CMS target still produced:

```
m7dyn
M7 DYN TEST 1: dynamic Huffman stream with literals and LZ77 matches
   202 +++     old = value(dst||l||'.'||r,s)
    48 +++ call maketree 'cl.',19,'ct.'
DMSREX475E Error 40 running GITDYN EXEC, line 202: Incorrect call to routine
Ready(20040)
```

Therefore do not use two-argument `VALUE()` for dynamic assignment in this CMS
REXX path. Current GitHub fix removes dynamic VALUE assignment entirely and uses
explicit known stems (`cl.`, `ll.`, `dd.` -> `ct.`, `lt.`, `dt.`), with compound
indices such as `ct.l.r = s`. It also uses `SYMBOL()` only to test whether a
specific generated tree entry exists.

Current GITDYN fix commit:
- `7ad4d21e27513934c2ebffd7e311b456f167148a`

NEXT ACTION: `git pull`, upload only `GITDYN.EXEC`, run `M7DYN`, paste complete
output. Do not mark M7E done until it passes on CMS.

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
