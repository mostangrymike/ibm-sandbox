# CMS/zVM Native Git Client — Chat State

Updated: 2026-09-17
Repository: `mostangrymike/ibm-sandbox`, branch `main`

## User workflow and rules

- GitHub is the canonical source. Make source changes on GitHub first.
- User runs `git pull` on Mac, transfers source to CMS with c3270, runs target tests,
  and pastes complete output.
- Keep CMS command batches small and exact.
- Prefer IBM documentation for CMS/z/VM questions and official Git/RFC documentation
  for protocol formats. Do not guess CMS commands.
- Use only software/facilities already available in the z/VM evaluation image; user
  does not want to purchase a compiler or other software.
- Do not depend on BFS/OpenExtensions shell at runtime.
- Source transferred as fixed 80-byte CMS records must have every source line <=80
  characters. `TRANS04 File transfer complete, with records segmented` is a failure
  indicating an over-80 source line.
- c3270 DFT buffer 2048 is proven; 16384 caused disconnects.
- Do not modify target-proven core code unnecessarily. Keep new milestones isolated.

## Environment

- IBM z/VM 6.3 Evaluation Edition under Hercules Aethra.
- Hercules host: Raspberry Pi 5/Debian.
- z/VM TCP/IP works.
- C89 front end exists but compiler backend `CBXFINIT` is absent. Do not revisit
  buying XL C/C++ unless user asks.
- Native assembler toolchain is Assembler XF (`ASSEMBLE`), with DMSGPI macros.
- REXX orchestrates; assembler is for binary/native/performance primitives.

## Proven transfer workflow

Interactive c3270 can be started with script port 3271. Generic uploader uses:

`Transfer(Direction=send,"HostFile=NAME TYPE A",LocalFile=file,Host=vm,Mode=ascii,Exist=replace,Recfm=fixed,Lrecl=80,BufferSize=2048)`

Uploader retries after `Clear()` on timeout. Source lines must be <=80 characters.

## Project architecture

Native CMS Git client with exact Git logical object compatibility. Physical local
storage is CMS-native. REXX handles command/repository orchestration; assembler
handles binary/network/hash/native primitives. Remote interoperability must use
real Git smart HTTP protocol, not REST pretending to be Git.

## Completed milestones

- M1 SHA-1 primitives — DONE.
- M2 Git object encoding — DONE.
- M3 CMS-native object DB — DONE.
- M4 trees/commits — DONE, target proven.
- M5 refs/branches/HEAD — DONE, target proven.
- M6A pkt-line framing — DONE, target proven.
- M6B ref advertisement parsing — DONE, target proven.
- M6C fetch negotiation request construction — DONE, target proven.
- M6D ACK/NAK parser — DONE, target proven.
- M6E side-band demultiplexing — DONE, target proven.
- M6F pack header parsing — DONE, target proven.
- M6G packed-object entry header — DONE, target proven.
- M6H OFS_DELTA offset decoding — DONE, target proven.
- M6I delta header parsing — DONE, target proven.
- M6J delta instruction application — DONE, target proven.
- M6K REF_DELTA base resolution — DONE, target proven.
- M6L OFS_DELTA base-position resolution — DONE, target proven.
- M6M pack-entry context/indexing — DONE, target proven (prototype stores whole
  datahex in a record; not scalable for real packs).
- M6N OFS_DELTA context/application — DONE, target proven.

## M7 compression status

Native zlib capability investigation found no usable RFC1950/1951 inflater on the
accessible evaluation disks. IBM CMPSC is not DEFLATE. Therefore implementing a
native inflater incrementally.

### M7A
Existing native zlib capability — DONE, none found.

### M7B
`GITZLIB.EXEC` / `M7ZLIB.EXEC`: RFC1950 wrapper parser — DONE, target proven.
Proven: CM=8, CINFO, FCHECK, FDICT/DICTID, FLEVEL, DEFLATE payload extraction,
Adler trailer extraction, malformed/truncated rejection.

### M7C
`GITSTOR.EXEC` / `M7STOR.EXEC`: DEFLATE stored blocks — DONE, target proven.
Proven: empty/data blocks, alignment, multiple stored blocks, LEN/NLEN,
truncation, BTYPE validation.

### M7D
`GITFIX.EXEC` / `M7FIX.EXEC`: fixed Huffman + LZ77 — DONE, target proven.
Proven: literals, length/distance, overlapping LZ77 copies, truncation and BTYPE
rejection.

### M7E — CURRENT
`GITDYN.EXEC` / `M7DYN.EXEC`: dynamic Huffman decoder. Intended coverage:
HLIT/HDIST/HCLEN, code-length permutation, repeat symbols 16/17/18, canonical
runtime trees, literals/end-of-block, length/distance reconstruction.

Initial commits:
- GITDYN: `a62308d79b00cf56112ef3da23a9e11a801b8473`
- M7DYN: `3aa4f4afc64a6cc9918df1cce29c41c4e5892483`

80-column source fix:
- `b5190b07b8de5e8034b4b97326248dc15420c4ef`

First target run returned RC 8 silently at test 1. A REXX procedure-scope fix was
attempted:
- `14d13fb2dedb491ce36cc9895770ffa1d3226cea`

Next target run produced:

```
m7dyn
M7 DYN TEST 1: dynamic Huffman stream with literals and LZ77 matches
   202 +++     call value dst||l||'.'||r,s
    48 +++ call maketree 'cl.',19,'ct.'
DMSREX475E Error 40 running GITDYN EXEC, line 202: Incorrect call to routine
Ready(20040)
```

Root cause: REXX `VALUE()` is a function, not a CALL-able subroutine for assignment.
The current GitHub fix changes:

`call value dst||l||'.'||r,s`

to:

`old = value(dst||l||'.'||r,s)`

while retaining explicit stem exposure in `maketree` and `getsym`.
Current fix commit:
- `4c21a120f6263a34e0c4e32c9aef5ac77c435772`

**NEXT ACTION:** user should `git pull`, upload only `GITDYN.EXEC`, then run
`M7DYN` and paste complete output. Do not mark M7E done until target passes.

Planned after M7E:
- M7F general/mixed-block inflater.
- M7G Adler-32 verification.
- M7H Git pack-entry inflate integration.

## Important implementation facts

Git object hash input is exact ASCII `type + space + decimal size + NUL + binary
content`. CMS text policy strips trailing EBCDIC record-padding blanks, preserves
leading blanks, joins records with ASCII LF, and adds no final LF. Binary-safe
mode is required for arbitrary bytes.

Known cosmetic first-file messages such as `DMSSTT002E File ... not found` are
accepted where correctness is unaffected. Do not weaken collision/ref integrity
to hide them.

Checkout currently means symbolic HEAD switching only; working-tree
materialization is later work.

TLS exists on the evaluation system (`GSK*` modules and Dynamic SSL interfaces).
Use documented native TLS later; do not implement TLS ourselves.
