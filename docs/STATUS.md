# CMS Git project status

Updated: 2026-09-26

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
- M12 practical HTTPS transport: EC2 TLS bridge and live GitHub smart-HTTP
  discovery/upload-pack transport PROVEN. Native z/VM System SSL remains experimental.
- M13 native C live-PACK walker: 1,808-object inflation and native PACK
  SHA-1 verification PASSED; delta reconstruction, OIDs and persistence remain.

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

## Live GitHub smart-HTTP proof — 2026-09-24

CMS successfully performed real GitHub smart-HTTP discovery through the TLS
bridge. GitHub's HTTP/1.1 response used chunked transfer encoding, so
`GIT12CHK EXEC` was added as a bounded chunk decoder. Its FILE-mode replay
decoded the live advertisement correctly.

A live upload-pack POST was then accepted by GitHub. Two request-framing bugs
were found and corrected from target evidence: the want pkt-line length is
`004a`, and the complete HTTP entity length is 87 bytes (74-byte want pkt-line
+ 4-byte flush + 9-byte done pkt-line). With those fixes GitHub returned
348,959 HTTP bytes.

The captured response passed the complete transport integrity path:

- bounded HTTP chunk decoding completed;
- upload-pack and side-band framing reached PACK state cleanly;
- `GITPBUF` finalized a 340,027-byte PACK;
- `GITPSHA VERIFY` accepted PACK SHA1
  `8C92E274ECA84B797F8925A6082915DD6CCDE196`;
- PACK v2 header reports 1,808 objects;
- `GITP9PWK` successfully reconstructed more than 200 live GitHub objects,
  including ordinary COMMIT/TREE/BLOB objects and substantial chained
  OFS_DELTA traffic, with object OIDs computed successfully.

A complete 1,808-object REXX/CMS walk was deliberately stopped because it is
too slow for a practical acceptance gate. The transport is not the bottleneck:
the complete PACK checksum already proves byte-for-byte integrity. The next
engineering problem is PACK/object materialization performance, especially
heavy EXECIO disk traffic and linear context lookup in `GIT9CTX`.

## M13 native C PACK walk — 2026-09-26

GCCCMS builds C modules using GCCE NOASM, IBM ASSEMBLE, PDPCLIB and GENMOD.
A small GITCAPI assembler adapter converts GCCCMS's argument-list convention
to GITINFA's direct six-fullword parameter-block convention. Its known-good
zlib fixture returned RC 0, output 3, consumed 11.

The native GITCWALK C + GITCAPI + GITINFA program walked the captured
340,027-byte, 1,808-object PACK in 2.14 seconds elapsed (2.10 CPU). All
1,808 object headers and zlib streams passed; final data offset 340,007
leaves the expected 20-byte trailing checksum. The live capture's SHA-1
was separately validated in M12; native GITCWALK SHA-1 verification was
subsequently proven in the checkpoint below.

This is a successful *inflation* gate, not yet a full Git object import.
The walker checks inflated delta-instruction sizes but does not apply deltas,
resolve bases, compute object OIDs or persist the resulting objects.

## Next action

After the native PACK checksum gate, implement OFS_DELTA base resolution
and delta application, followed by REF_DELTA and object SHA-1/OID checks. Preserve the existing target-proven REXX implementation
as a correctness reference and the captured PACK as the benchmark. Do not
rerun the network POST for local performance testing.

## 2026-09-26 first-object ABI and live inflate regression

The combined `GITCLNK GITCINF` build completed with three clean Assembler XF assemblies. `GITCAPI` resolves GCCCMS's argument-list ABI versus `GITNAPI`'s direct parameter-block ABI. The known-good `abc` fixture returned `RC 0 OUTPUT 3 USED 11 DATA 61 62 63`. The live PACK first object at byte offset 14 returned `RC 0 OUTPUT 270 USED 182`, establishing the second-object offset at 196; CMS printed `PASS FIRST LIVE OBJECT INFLATE`. These results corroborate the newer 1,808-object `GITCWALK` inflate-only milestone above. Native PACK trailer verification was subsequently proven; OFS/REF delta reconstruction, final object OIDs and persistence remain distinct unfinished acceptance gates.

## Native PACK checksum target proof — 2026-09-26

GITCWALK.C now computes native SHA-1 over the PACK bytes excluding the final
20-byte trailer and rejects a mismatched trailer before inflation. GCCCMS
GITCLNK GITCWALK compiled successfully with three clean Assembler XF passes.
The captured 340,027-byte PACK passed native checksum verification with SHA-1
`8C92E274ECA84B797F8925A6082915DD6CCDE196`. GITCWALK ALL then inflated
all 1,808 objects successfully and ended at offset 340,007, exactly 20 bytes
before the trailer. CMS reported `Ready; T=3.33/3.38` (CPU/elapsed seconds).
This is the checksum-plus-inflation gate; it does not imply delta application,
base resolution, object OID calculation or persistence. The earlier 2.14-second
inflation-only measurement remains a separate proven benchmark. The corrupt-trailer negative test subsequently passed on CMS.

## Next action

Add an isolated negative checksum test without modifying the captured
GITPBUF PACK A. Then implement native OFS_DELTA base resolution and delta
application, followed by REF_DELTA, object OIDs and persistence. Preserve the
REXX walker as the correctness reference and avoid another network POST.

## Corrupt-trailer regression — CMS proven

GITCWALK BADSHA now loads the existing captured PACK into memory, flips the
last trailer byte **only in the in-memory copy**, and expects the native
checksum comparison to reject it. The CMS `GITPBUF PACK A` remains unchanged.
The negative gate returns RC 0 only when the corruption is rejected and RC 8
if the corrupted trailer is incorrectly accepted. After testing BADSHA, rerun
GITCWALK ALL as the positive regression. CMS ran GITCWALK BADSHA and printed
`PASS BADSHA: CORRUPT TRAILER REJECTED`, RC 0, CPU/elapsed 1.81/1.83 seconds.
A subsequent GITCWALK ALL verified SHA-1
`8C92E274ECA84B797F8925A6082915DD6CCDE196`, inflated all 1,808
objects, and ended at offset 340,007, CPU/elapsed 3.30/3.34 seconds.
Both positive and negative checksum regressions are target-proven.

## Native OFS base-position gate — awaiting target test

GITCWALK.C now records each object header's starting PACK byte offset in an
1,808-entry native table. For each OFS_DELTA, it decodes Git's offset distance
relative to that object's header, checks nonzero/bounded distance, and requires
the resulting base position to equal an earlier object's header offset. On a
successful walk it prints `OFS BASE POSITIONS RESOLVED N`. The code has not
yet been built or tested on CMS. It does **not** reconstruct delta output,
calculate object OIDs, or persist objects. Use the existing captured PACK;
rerun BADSHA as a regression after the new ALL gate if needed.
