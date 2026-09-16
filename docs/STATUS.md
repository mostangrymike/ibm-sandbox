# CMS Git project status

## Goal

Build a native Git client for CMS/z/VM 6.3 Evaluation Edition without purchasing additional compilers. Preserve Git logical object/protocol compatibility while allowing CMS-native physical storage.

## Proven on target

- Assembler XF is present and functional; native MODULE build and REXX invocation are proven.
- SHA-1 is implemented natively and passes empty, `abc`, multi-block, arbitrary-binary, and padding-boundary vectors.
- Exact Git blob object encoding is implemented: ASCII `blob <size>\0` plus binary payload.
- CMS text canonicalization is target-proven: trailing record blanks are padding, leading blanks are significant, records are joined with ASCII LF, and no final LF is added automatically.
- `GIT INIT`, `HASH-OBJECT`, `WRITE-OBJECT`, `VERIFY-OBJECT`, and `CAT-OBJECT` operate through the public CMS interface.
- `GITSTRM` provides bounded streaming SHA-1 input through the CMS program stack and is target-proven across multi-block and boundary vectors.
- Exact one-entry Git tree bytes are target-proven. Mode `100644`, name `README`, and blob `F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F` produce tree `2030C0B68CCC4116B0CB9990EF04B53EA30140C8`.
- Exact deterministic Git commit bytes are target-proven. The regression commit pointing at that tree produces `54BACE2202BB0C96980CDD0AAE9A752E6188D666`.
- CMS-native TREE and COMMIT storage round-trips preserve their Git object IDs.
- Public `GIT VERIFY-OBJECT` and `GIT CAT-OBJECT` are target-proven for BLOB, TREE, and COMMIT.
- Public `GIT WRITE-TREE 100644 README <blob>` independently reproduces tree `2030C0B68CCC4116B0CB9990EF04B53EA30140C8`, stores it, and passes public verification/retrieval.
- Public `GIT COMMIT-TREE <tree>` independently reproduces deterministic commit `54BACE2202BB0C96980CDD0AAE9A752E6188D666`, stores it, and passes public verification/retrieval.
- Temporary GITSTRM diagnostics have been removed and the clean rebuilt MODULE passes the public TREE/COMMIT regression.

## Current baseline

M3E streaming/multi-block SHA-1 is complete and hardened.

M4's essential logical-object path is now proven end-to-end through the public CMS command interface: blob -> tree -> commit, with exact Git-compatible object bytes and independently known SHA-1 object IDs.

The current `WRITE-TREE` is intentionally a one-entry first implementation. The current `COMMIT-TREE` is intentionally deterministic for the interoperability vector: fixed identity, timestamp/timezone, message, and no parent. These are proof interfaces, not yet the final user-facing semantics.

The current physical object layout is also still a prototype: the filename uses the first eight OID hex digits and the body is stored as hexadecimal DATA in a single record. Prefix collisions and large-object DATA record chunking must be addressed before calling the object database general-purpose.

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
- M3E Streaming / multi-block CMS blobs: DONE + HARDENED
- M4 Trees and commits: IN PROGRESS — public exact tree and initial-commit creation proven
- M5 Refs and branches: NOT STARTED
- M6 Packfiles: NOT STARTED
- M7 TCP/IP: NOT STARTED
- M8 TLS: NOT STARTED
- M9 Smart HTTP / GitHub: NOT STARTED

## Next M4 work

Harden the CMS-native object database before expanding tree/commit semantics. Replace the single DATA record with bounded DATA chunks and explicit size metadata while retaining compatibility with existing prototype objects where practical. Detect first-eight OID filename collisions rather than silently overwriting a different full OID.

Then generalize `WRITE-TREE` to multiple entries with Git tree ordering, and generalize `COMMIT-TREE` to optional parent(s), configurable author/committer identity, timestamp/timezone, and arbitrary commit messages. Keep exact logical Git bytes independent of CMS physical storage.

## Planned architecture

- REXX: command parsing, repository orchestration, configuration, refs/branches.
- Assembler: byte-oriented operations, hashes, CRC, compression, pack processing, binary I/O, native network/TLS adapters as required.
- Native CMS/TCP-IP/System SSL interfaces; do not implement TLS ourselves.
