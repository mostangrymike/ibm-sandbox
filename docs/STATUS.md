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
- Public `GIT WRITE-TREE` supports multiple entries and exact Git ordering. Reverse input `README`, `BIGFILE` produces independently known tree `E11636C5C257E21ADBBE98AE3EBB677E81AF94EB`.
- Argument parsing preserves case-sensitive Git data while normalizing only command verbs, CMS file identifiers, modes, and OIDs where appropriate. Mixed-case tree entry `ReadMe` produces independently known tree `B9E7816426B28421D7050FF4F501E7E796BC244A`.
- Git's directory comparison rule is target-proven. Subtree `A/x` produces `C2421DE5E21D352FCC0CA2F81FD2D06D7B68FD72`; reverse input file `A` and directory `A` sorts correctly and produces `16202BB74533B0AA9E941E3C1D22ACCA53A2B72B`.
- `GIT COMMIT-TREE` retains the deterministic one-argument interoperability form and supports proof-level explicit parent(s), author, committer, timestamp, timezone, and message options.
- A one-parent mixed-case metadata commit is target-proven at `1E99ED02563737B793C60359F94BA587F6C1B8BD`.
- Multiple-parent commit serialization and parent order are target-proven. The two-parent merge regression produces independently known commit `C72FFDE0A46ED667E494842150FA4011C99BC9A0`.
- The CMS object database writes `OID`, `TYPE`, `SIZE`, then bounded DATA records of at most 128 hex characters while retaining reads of the original three-record layout.
- A 303-byte canonical CMS text blob is target-proven through public WRITE/VERIFY. It produces `F96567C0F557CCE820219AE6483F2171A106810B` and is physically stored in five DATA records.
- Object writes inspect an existing first-eight-character CMS filename and reject a different stored full OID instead of silently overwriting it.

## Current baseline

M3E streaming/multi-block SHA-1 is complete and hardened.

M4 trees and commits is complete. Blob -> ordered/nested tree -> initial, parented, and merge commit construction is proven end-to-end through the public CMS command interface with exact Git-compatible object bytes and independently known SHA-1 object IDs.

The physical object layout supports bounded DATA records with explicit byte size and backward-compatible reads. It still uses the first eight OID hex digits as the CMS filename; collisions are detected rather than overwritten, but a scalable collision-resolution/catalog scheme remains future work.

`COMMIT-TREE`'s underscore-for-space option encoding is a proof-level interface, not final porcelain syntax. A later command-input layer should provide natural quoted and multiline commit messages without changing the proven object serializer.

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
- M4 Trees and commits: DONE
- M5 Refs and branches: IN PROGRESS
- M6 Packfiles: NOT STARTED
- M7 TCP/IP: NOT STARTED
- M8 TLS: NOT STARTED
- M9 Smart HTTP / GitHub: NOT STARTED

## Next M5 work

Implement CMS-native refs without changing Git logical ref semantics. Start with symbolic `HEAD`, `refs/heads/<name>`, exact 40-hex commit targets, branch creation/listing, and ref resolution. Validate that branch refs can point only at existing COMMIT objects. Then add safe ref updates and checkout/HEAD switching semantics before using refs as the parent source for higher-level commits.

The expected-missing-file probe currently emits a CMS `DMSSTT002E` diagnostic even though the write succeeds. This is cosmetic but should be replaced with a quiet existence mechanism once the appropriate documented CMS interface is selected; do not weaken collision detection merely to suppress the message.

## Planned architecture

- REXX: command parsing, repository orchestration, configuration, refs/branches.
- Assembler: byte-oriented operations, hashes, CRC, compression, pack processing, binary I/O, native network/TLS adapters as required.
- Native CMS/TCP-IP/System SSL interfaces; do not implement TLS ourselves.
