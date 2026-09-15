# CMS Git project status

## Goal

Build a native Git client for CMS/z/VM 6.3 Evaluation Edition without purchasing additional compilers. Preserve Git logical object/protocol compatibility while allowing CMS-native physical storage.

## Proven on target

- Assembler XF is present and functional.
- `DMSGPI` provides CMS preferred macros.
- `LINEWRT` assembles and executes.
- `ASSEMBLE` creates TEXT and LISTING.
- `LOAD` + `GENMOD` creates a native CMS MODULE.
- REXX EXEC can invoke the MODULE and continue after return.
- GITCORE reads the CMS EPLIST from R0 and dispatches `VERSION`.
- GITCORE returns RC 0 for VERSION and RC 4 for bad arguments.
- Exact binary constants including `00` and `FF` assemble successfully with `DC X'...'`.
- Public `GIT EXEC` dispatches VERSION and rejects missing/unknown commands with RC 4.

## Current baseline

`src/GITCORE.ASSEMBLE` is the last target-proven source. It includes the temporary `TESTBYTE DC X'00616263FF'` binary-constant proof.

## Next milestone: M1A SHA-1

Implement a reusable SHA-1 primitive in Assembler XF. First test exact bytes `61 62 63` and require digest:

    A9993E364706816ABA3E25717850C26C9CD0D89D

Then test zero-length and multi-block vectors before using SHA-1 for Git objects.

Do not mix EBCDIC-to-Git byte canonicalization into the initial SHA-1 validation.

## Planned architecture

- REXX: command parsing, repository orchestration, configuration, refs/branches.
- Assembler: byte-oriented operations, hashes, CRC, compression, pack processing, binary I/O, native network/TLS adapters as required.
- Native CMS/TCP-IP/System SSL interfaces; do not implement TLS ourselves.
