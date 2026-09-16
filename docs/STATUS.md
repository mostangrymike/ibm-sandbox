# CMS Git project status

## Goal

Build a native Git client for CMS/z/VM 6.3 Evaluation Edition without purchasing additional compilers. Preserve Git logical object/protocol compatibility while allowing CMS-native physical storage.

## Proven on target

- Assembler XF is present and functional.
- `DMSGPI` provides CMS preferred macros.
- `LINEWRT` assembles and executes.
- `ASSEMBLE` creates TEXT and LISTING.
- `LOAD` + `GENMOD` creates a native CMS MODULE.
- REXX EXEC can invoke native MODULEs and continue after return.
- GITCORE reads the CMS EPLIST from R0 and dispatches native operations.
- Exact binary constants including `00` and `FF` assemble successfully with `DC X'...'`.
- Public `GIT EXEC` provides the CMS-facing command interface.
- SHA-1 is implemented natively and passes empty, `abc`, two-block, multi-block, and arbitrary-binary vectors.
- Exact Git blob object encoding is implemented: ASCII `blob <size>\0` plus binary payload.
- Dynamic binary blob hashing passes empty, `abc`, and `00 61 62 63 FF` vectors against independently computed Git object IDs.
- CMS text files can be canonicalized to Git blob bytes using the project text policy: trailing CMS record blanks are padding, leading blanks are significant, records are joined with ASCII LF, and no final LF is added automatically.
- `GIT INIT` creates the CMS-native repository metadata prototype.
- `GIT WRITE-OBJECT` writes CMS-native blob objects and receives native object IDs through `CMSSTACK`.
- `GIT VERIFY-OBJECT` detects content corruption by recomputing the Git object ID.
- `GIT CAT-OBJECT` retrieves stored objects.
- Streaming SHA-1 input through the CMS program stack is proven. `GITSTRM` consumes an 8-hex-digit total byte count followed by bounded hex chunks, decodes them incrementally, processes complete 64-byte SHA-1 blocks, retains only the final partial block, finalizes SHA-1, and returns the digest through `CMSSTACK`.
- Streaming regression vector `blob 3\0abc` returns `F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F`.
- Multi-block streaming regression vector `blob 300\0` plus 300 ASCII `a` bytes (309-byte object stream) returns `8EF7A53A7502434FF1BBB9502F5C7A6E66C78BDD`.

## Current baseline

M3E streaming/multi-block SHA-1 is target-proven. The 256-byte hashing limit of the earlier `BLOBHEX` prototype is no longer an architectural limit for hashing: bounded chunks can be streamed through a single native MODULE invocation.

The current streaming protocol is a bring-up interface between REXX and assembler, not the final public Git command syntax. Temporary diagnostic modules `GITRD` and `GITHDR` remain useful regression aids but are not part of the intended public interface.

## Milestone status

- M0 Native CMS toolchain / command interface: DONE
- M1 SHA-1 primitives: DONE
- M2A Fixed Git blob encoding: DONE
- M2B Dynamic binary Git blob encoding: DONE
- M2C CMS text to Git blob prototype: DONE
- M3A Repository initialization: DONE
- M3B CMS-native object writing: DONE
- M3C Object retrieval / verification: DONE
- M3D CMS text canonicalization policy: DONE
- M3E Streaming / multi-block CMS blobs: DONE
- M4 Trees and commits: NOT STARTED
- M5 Refs and branches: NOT STARTED
- M6 Packfiles: NOT STARTED
- M7 TCP/IP: NOT STARTED
- M8 TLS: NOT STARTED
- M9 Smart HTTP / GitHub: NOT STARTED

## Next milestone: M4 trees and commits

Build exact Git tree and commit object byte streams on top of the now-proven object hashing path. Keep logical Git bytes exact while allowing the local physical representation to remain CMS-native. Add independently computed object-ID regression vectors before connecting tree/commit creation to refs.

Before depending on the streaming path for general objects, add boundary regressions around SHA-1 block and padding transitions, especially exact 64-byte and 128-byte object streams and final tails around 55/56/63/64 bytes.

## Planned architecture

- REXX: command parsing, repository orchestration, configuration, refs/branches.
- Assembler: byte-oriented operations, hashes, CRC, compression, pack processing, binary I/O, native network/TLS adapters as required.
- Native CMS/TCP-IP/System SSL interfaces; do not implement TLS ourselves.
