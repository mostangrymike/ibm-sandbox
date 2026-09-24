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
- The CMS -> EC2 stunnel -> GitHub path is target-proven with M11BRAW; CMS
  received a valid HTTP response through the bridge.

Native z/VM System SSL work is preserved as an experimental/research path.
Current GitHub uses an ECC Sectigo certificate chain that the old z/VM 6.3
service level cannot currently validate/import with the installed crypto
facilities, so it is no longer the practical blocker for GitHub transport.

See `docs/BUILD.md`, `docs/STATUS.md`, and `CHAT_STATE.md`.
