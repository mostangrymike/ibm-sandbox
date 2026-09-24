# CMS Git project status

Updated: 2026-09-24

## Goal

Build a native Git client for CMS/z/VM 6.3 Evaluation Edition with Git logical
object/protocol compatibility and CMS-native physical storage. The practical
GitHub transport may use the EC2 host's TLS layer; Git protocol, HTTP framing,
PACK processing, objects, and refs remain owned by CMS.

## Milestone status

- M0 native CMS toolchain / command interface: DONE
- M1 SHA-1: DONE
- M2 object encoding: DONE
- M3 CMS object database: DONE
- M4 trees and commits: DONE
- M5 refs / HEAD: DONE
- M6 protocol and delta handling through M6N: DONE
- M7 compression through M7I: DONE
- M8 complete PACK ordinary/OFS/REF through M8C: DONE
- M9 bounded/scalable PACK through M9P: DONE
- M10 bounded upload-pack transport / real Git fixture: DONE
- M11 native CMS TCP + bounded binary-safe HTTP: DONE
- M12 practical HTTPS transport: EC2 TLS bridge PROVEN; Git smart-HTTP
  integration is next. Native z/VM System SSL remains experimental.

All completed milestones above are target-proven.

## M9/M10 transport core

M9P is the consolidated bounded PACK walker. GIT9CTX uses disk-backed
`G9CDATA DATA A`, `G9CIDX DATA A`, and `G9CMETA DATA A`; the old
per-position filename scheme is gone. Ordinary objects, OFS_DELTA, REF_DELTA,
non-immediate bases, chained deltas, streaming DEFLATE/zlib, bounded object
storage, and the relevant stress gates are target-proven.

GIT10BF is a bounded pkt-line/side-band state machine. Channel 1 streams into
GITPBUF, channel 2 is discarded incrementally, and channel 3 fails in a
controlled way. M10E passed a maximum `ffff` pkt-line with a 65530-byte
channel-2 payload delivered in 31-byte fragments.

The real Git 2.47.3 M10D upload-pack fixture remains the interoperability gate:

- PACK SHA1 `00C20177E759DC5FFD06EA42D0A1D1E1A9F53E7B`
- COMMIT `59D72104FBF18B76536A3A99776C7F7930C27CD8`
- TREE `747ABC3C651FC0DD12A37E5B5C47E0D02CD0DC4E`
- BLOB `F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F`
- PACK v2, 3 objects, data end 180

## M11 native networking / HTTP

M11A proved native CMS REXX/SOCKETS TCP. M11B proved SO_ASCII OFF and bounded
binary-safe raw send/receive. M11C proved bounded HTTP header framing across a
fragmented CRLFCRLF boundary while preserving binary body bytes. M11D routed
the HTTP body directly through GIT10UP/GIT10BF/GITPBUF and reproduced the real
M10D PACK and object IDs exactly.

Current routed network:

- EC2 ens5: `172.31.14.90/20`
- EC2 tap0: `192.168.200.1/24`
- z/VM OSA1: `192.168.200.2/24`
- gateway: `192.168.200.1`
- DNS: `8.8.8.8`

Native z/VM TN3270 over this path is also proven.

## M12 native System SSL findings

The documented z/VM 6.3 Dynamic SSL client architecture was implemented far
enough to prove VMCF OPENtcp and TLSSCLIENTtcp processing. Target behavior
established these important callcodes: OPENtcp X'6E', open notification X'0B',
TLSSCLIENTtcp X'83', READYforHANDSHAKE X'25',
SECUREhandshakeCOMPLETE X'24', SENDtcp X'76', RECEIVEtcp X'71',
DATAdelivered X'0C', and VMCF RECEIVE function X'0005'.

A clean SSL server trace established the actual blocker:

    DTCSSL022E Handshake failed rc: 8 reason: Certificate validation error

It also reported:

    DTCSSL505W Local client requested use of CERTNOCHECK; Request ignored

Therefore `ValidatePeerCert=No_Check` does not bypass GitHub server
certificate validation.

The target is z/VM 6.3 service level 1302 (2013-era). Current GitHub presents a
Sectigo ECC chain: github.com -> Sectigo Public Server Authentication CA DV E36
-> Sectigo Public Server Authentication Root E46. Importing the E46 root with
GSKKYMAN failed with status `0x03353083`, "ICSF services are not available";
`CP QUERY VIRTUAL CRYPTO` reported no AP Crypto Domains. Further native crypto
archaeology is not on the critical path.

## Practical HTTPS transport — PROVEN

EC2 Debian trixie has stunnel 5.74 with modern OpenSSL. A dedicated client-mode
listener is bound only to `192.168.200.1:8443` and connects to
`github.com:443` with CA-chain validation, hostname validation, SNI, and
TLS >= 1.2.

The EC2-local plaintext HTTP test through the listener returned GitHub
`HTTP/1.1 200 OK`.

CMS then ran M11BRAW against `192.168.200.1 8443`:

- REXX/SOCKETS initialized successfully.
- SO_ASCII was OFF.
- TCP connect succeeded.
- all 56 exact request bytes were sent.
- 176 bytes were received with bounded 256-byte RECV calls.
- prefix was `HTTP/1.1 301 Mov...`.
- final result: `M11B BINARY-SAFE BOUNDED SOCKET TEST PASSED`.

The 301 is expected from that diagnostic because its immutable proof request
uses `Host: example.com`. The important result is that valid decrypted HTTP
returned to CMS through the verified TLS bridge.

A separate `M12PRXY EXEC` was added for the correct `Host: github.com`
probe rather than modifying the target-proven M11B core.

## Next action

Target-prove `M12PRXY 192.168.200.1 8443`. Then build the isolated real GitHub
smart-HTTP integration gate: CMS sends the correct Git smart-HTTP request
through the stunnel endpoint, bounded HTTP response bytes feed GIT11HTP, and
the existing M10/M9 pipeline handles pkt-lines, PACK data, objects, and refs.

Preserve M12TLS4 as native-System-SSL research. Do not spend the next milestone
trying to make the 2013 System SSL stack validate GitHub's modern ECC chain.
