# IBM Sandbox

Native IBM platform development experiments.

## CMS Git client

The active project is a native Git client for CMS on z/VM 6.3 Evaluation
Edition under Hercules Aethra on an AWS EC2 Debian ARM64 host.

The Git-format core is target-proven through M10: objects, refs, PACK handling,
bounded inflate/delta reconstruction, pkt-line/side-band transport, and a real
Git upload-pack fixture. M11 native CMS TCP and bounded binary-safe HTTP framing
are also target-proven.

Current practical HTTPS architecture:

- CMS/z/VM: native REXX/SOCKETS TCP and Git smart-HTTP bytes.
- EC2 TAP gateway: `192.168.200.1/24`.
- CMS: `192.168.200.2/24`.
- stunnel listener: `192.168.200.1:8443`, bound only to the TAP interface.
- stunnel establishes verified modern TLS to `github.com:443`, including CA
  chain validation, hostname checking, and SNI.
- The CMS -> EC2 stunnel -> GitHub path is target-proven through live Git
  smart-HTTP discovery and upload-pack. A 340,027-byte live PACK containing
  1,808 objects was received and its PACK SHA-1 verified on CMS. The next work
  is optimizing the bounded object walker for practical large-pack performance.

Native z/VM System SSL work is preserved as an experimental/research path.
Current GitHub uses an ECC Sectigo certificate chain that the old z/VM 6.3
service level cannot currently validate/import with the installed crypto
facilities, so it is no longer the practical blocker for GitHub transport.

See `docs/BUILD.md`, `docs/STATUS.md`, and `CHAT_STATE.md`.

## Native PACK checkpoint: staging and index prototypes

`GITCWALK OPTCHECK` is CMS-proven for the captured 1,808-object PACK:
the optimized and reference SHA-1 implementations agreed on every
reconstructed object, including all 1,117 OFS_DELTA objects.
`OPTSHA` ran in 19.29 s CPU / 19.42 s elapsed on one CMS run.

The original STAGE output FILEDEF error was corrected by specifying
RECFM V and LRECL 80. On September 26, CMS STAGE wrote all 1,808
reconstructed objects; VERIFY independently rehashed every stored
object and BADSTG rejected deliberately altered content. GITCIDX
CHECK validated 1,808 unique indexed OIDs, and first/last GETs
returned independently SHA-1-checked object content on actual CMS.

The canonical compiler wrapper is now `CMSCLNK EXEC`, with the
existing native-inflater link mode as its default and a new `PLAIN`
mode for programs without inflater dependencies. It is prepared for
installation beside GCCCMS on F; see `docs/BUILD.md`. Its F-disk
placement and PLAIN linkage still require CMS validation.

The separate GITCIDX AUDIT mode and experimental ftell/fseek
seek index with direct SGET have passed host C89/CI regressions,
including corrupt stage and truncated-index tests. The faster seek
mode still needs real CMS validation. See docs/NATIVE_STAGE.md and
docs/NATIVE_INDEX.md for the full record and next target gate.
Native forward/external REF_DELTA resolution, safe committed storage
generations, and reboot/restart proof remain outstanding. Issue #2
remains open.

## Performance redesign: native PACK engine

The REXX-per-object pipeline is a correctness reference, not the intended
production architecture. On the captured 1,808-object PACK, a 20-object
prefix took 230.13 seconds initially and 64.44 seconds after bounded I/O
optimizations. Do not extrapolate a full-run time from the prefix: object
sizes and delta costs vary. A 90-minute interactive terminal test is not an
acceptable production workflow.

Target architecture (incremental gates):

1. Keep the existing strict walker and 27-case GITTEST suite as a regression
   oracle. Preserve the captured PACK; ALL overwrites the active buffer.
2. Remove remaining per-record REXX dispatch while retaining bounded file
   access. GIT9CTX SAVE now reads 16 object records per EXECIO directly.
3. Implement a native PACK engine with one CMS entry point: sequential
   buffered PACK input, header and varint decoding, GITNAPI inflation,
   binary object hashing, delta application, and a position/OID index.
   Reuse GITINFA; do not reimplement the inflater. Keep REXX for orchestration.
4. Native gates in order: regular-object fixture; 20-object prefix; delta
   fixture with OFS and REF; 100-object prefix; 500-object prefix; full
   1,808-object PACK with checksum and final boundary verification.
5. Use CPU time and elapsed time for every gate. A sub-five-second 20-object
   run is an engineering target, not an established capability.

Fail closed on malformed headers, short reads, invalid delta bases, wrong
object hashes, missing trailers and out-of-range offsets. No unbounded REXX
strings or repeated network capture. Do not claim native-engine parity until
its implementation and target-side tests demonstrate it.

## GCCCMS native C checkpoint (2026-09-26)

The working GCCCMS toolchain now builds C plus the existing assembler inflater. `GITCAPI` adapts GCCCMS's argument-list calling convention to `GITNAPI`; `GITCLNK` builds the combined CMS module. `GITCINF` passed both a known-good `abc` zlib fixture (3 output bytes, 11 compressed bytes) and the first live PACK object (270 output bytes, 182 compressed bytes, next object at offset 196). The later `GITCWALK` 1,808-object inflation timing and remaining correctness work are recorded in `docs/STATUS.md`. C is the main native-engine implementation path; retain assembler where the existing inflater or CMS interfaces warrant it, and preserve the REXX walker as the correctness reference.

## GCCCMS native C integration (2026-09-26)

GCCCMS now builds a combined C and native assembler CMS module using GITCLNK, GITCAPI, and GITINFA. The adapter corrects GCCCMS argument-list calling convention. GITCINF passed the known abc fixture (3 output bytes, 11 consumed) and the first live PACK object (270 output bytes, 182 consumed; second object at offset 196). GITCWALK subsequently completed the 1,808-object inflation gate; see docs/STATUS.md for its measured time and the remaining delta, OID, checksum, and persistence work. Preserve the REXX implementation as the correctness reference.

## GCCCMS build-tool rename

`CMSCLNK EXEC` supersedes `GITCLNK EXEC` as the build wrapper for
GCCCMS. Default `CMSCLNK GITCWALK` links the native inflater;
`CMSCLNK GITCIDX PLAIN` builds an ordinary C-only module. GitHub
source and host static checks pass. To install the EXEC next to
GCC on CMS F, check `QUERY DISK F`, copy from A to F only if F is
R/W, and validate the newly built module before retiring the
original A-disk GITCLNK. Instructions: `docs/BUILD.md`.

## September 26, 2026 — direct-seek index and native REF progress

On actual CMS, `GITCIDX AUDIT` independently verified all 1,808
staged bodies and 1,808 unique OIDs. Experimental `SBUILD` and
`SCHECK` succeeded; direct `SGET` retrieved both end objects,
confirming ftell/fseek across separate CMS program invocations
on an unchanged stage. Last-object retrieval improved from
7.59 s elapsed via the original V1 sequential GET to 1.77 s
via SGET in the observed runs (4.29x).

The native C PACK walker now also resolves backward, same-PACK
REF_DELTA chains by OID, without changing the proven original
PACK file or index. A deterministic three-object REF PACK has
passed host native parsing, negative tests and independent
`git index-pack`/`git cat-file` interoperability tests.
CMS validation of the updated REF-capable C source remains open.
See `docs/NATIVE_REF.md` for one isolated CMS fixture gate;
do not repeat the live GitHub network capture.

The remaining full-Git gaps include forward/external REF_DELTA
bases and atomic/recoverable content-addressable storage. GitHub
issue #2 remains open. The compiler wrapper has been renamed
`CMSCLNK EXEC` and is intended for the writable GCC F disk;
a command-labeled installation result was not present in the
most recent posted CMS transcript.

## Critical OID interoperability correction: Git ASCII vs CMS EBCDIC

The first CMS backward-REF test exposed a shared native C hash defect:
GCCCMS formatted the Git object header in EBCDIC, not the required
ASCII. As a result, previous 1,808-object C hash parity, staging,
readback and index checks established internal consistency but did
not establish canonical Git OIDs. PACK checksum and object inflation
remained correct. Inspected REXX GITBOID/GITOID already construct
canonical headers explicitly in hexadecimal.

GITCWALK and GITCIDX now construct explicit ASCII headers, and
known Git blob-vector tests detect CMS character-set regressions.
IDX2/SIDX2 index formats reject old incompatible indexes. Full
host CI passes, but the fixed C code needs the next CMS run.
Preserve existing GITSTAGE, GITINDEX and GITSEEK files; rebuild
separately named GITFIX stage/index/seek files from the saved PACK
after the corrected REF test succeeds. See docs/CANONICAL_OIDS.md
for exact safe commands and source of the defect. Issue #2 remains
open for target proof and broader native Git functionality.

## September 26: canonical REF validation on CMS completed

The corrected GITCWALK RTEST and independent GITCIDX SELF now pass
on real CMS with known Git canonical SHA-1 vectors. The saved small
three-object REF fixture passes on the target, reconstructing abc,
abcd and abcde with the correct Git object IDs, and both chained
backward same-PACK REF_DELTA instructions apply correctly in RPACK
and RAPPLY modes. This fixes the confirmed EBCDIC canonical-header
failure exposed in the earlier REF attempt. The four separately
generated malformed PACK fixtures remain host-tested; they were not
part of the latest target transcript.

The earlier 1,808-object staging and seek/index artifacts still have
legacy incompatible IDs. The next required step is to rebuild the
existing captured PACK offline into new GITFIX STAGE, INDEX and SEEK
files and verify every object and both canonical IDX2/SIDX2 indexes.
Do not overwrite the original stage or indexes. Full commands and
success criteria: docs/CANONICAL_OIDS.md. A later optional GITCIDX
PAIR mode is host-tested to compare both new indexes and independently
rehash each indexed body; it may require one new compiler transfer.
