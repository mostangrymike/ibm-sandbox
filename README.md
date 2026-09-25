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
