# CMS/zVM Native Git Client — Chat State

Updated: 2026-09-21
Repository: `mostangrymike/ibm-sandbox`, branch `main`

## Workflow/rules
- GitHub canonical; edit there first, then user pulls/transfers/tests on CMS.
- Whenever files must be transferred to CMS for testing, always provide the Mac
  commands needed to fetch/prepare/transfer them, followed by the CMS commands.
  Do not give only the CMS-side test command. Keep both command batches exact and
  small.
- Proven Mac workflow: user works from the local repository `src` directory and
  runs `git pull`, then `./cms-upload.sh FILE1.EXEC FILE2.EXEC ...`. The upload
  script maps each local `.EXEC` file to `NAME EXEC A` on CMS and performs the
  established DFT transfer. Use this exact workflow in future instructions; do
  not substitute raw c3270/nc transfer commands unless the user explicitly asks.
- Exact small CMS command batches. IBM docs first for CMS/zVM; official Git/RFC
  docs for formats. No guessed CMS commands or purchased dependencies.
- No BFS/OpenExtensions runtime dependency. Fixed-80 source <=80 columns.
- CMS file names and file types must each be no longer than 8 characters. Enforce
  this before creating or transferring any CMS-target file.
- c3270 DFT 2048 proven. Preserve target-proven cores; isolate milestones.

## Architecture/environment
z/VM 6.3 Evaluation under Hercules Aethra on AWS EC2 Debian ARM64/aarch64, MP=2.
Current z/VM network is native routed TAP: OSA1 192.168.200.2/24, Linux tap0
192.168.200.1/24, outbound MASQUERADE through ens5. Assembler XF
+ DMSGPI available. REXX orchestrates; assembler for binary/native/performance.
Goal: genuine Git interoperability, eventually smart HTTP with native TLS.

## Completed
M1 SHA-1; M2 object encoding; M3 CMS object DB; M4 trees/commits; M5 refs/HEAD;
M6 protocol/delta through M6N; M7 compression through M7I; M8 complete PACK
ordinary/OFS/REF through M8C; M9A/M9B bounded storage; M9C bounded pack SHA-1;
M9D bounded inflater primitive; M9E bounded general inflater; M9F bounded
ordinary PACK walker; M9G/M9H bounded delta walkers; M9I bounded object store;
M9J streaming DEFLATE/zlib; M9K ordinary streaming PACK; M9L bounded OFS_DELTA;
M9M bounded REF_DELTA; M9N stress; M9O cached performance; M9P consolidated
bounded PACK walker. All completed milestones are target proven.

## M8 complete PACK summary
M8A ordinary complete pack passed including trailer SHA and negative tests.
M8B OFS_DELTA reconstructs abc -> abcd and verifies trailer. M8C REF_DELTA
resolves real base OID, reconstructs abc -> abcd and verifies trailer. M8
regressions all passed after integration.

## M9 scalability

### M9A chunk semantics — DONE/TARGET PROVEN
`GITPBUF` logical byte offsets work across 64-byte CMS records. 80-byte test made
two chunks; boundary and overrun tests passed.

### M9B incremental/selective pack buffer — DONE/TARGET PROVEN
Current `src/GITPBUF.EXEC` blob `47cd29329aed29fa0c99580835a007acf30aee4d`.
M9B adds metadata file `GITPMETA PACK A`, INIT/APPEND/FINAL, and selective READ.
APPEND accepts at most 64 bytes per call, carries a partial tail until a full
64-byte physical record can be emitted, and FINAL emits the last partial record.
READ is forbidden before FINAL and computes only the required CMS record range;
it no longer EXECIO-reads the entire pack file. WRITE remains as compatibility
path and now writes finalized metadata too.

Target results after M9B change:
- existing M9PBUF regression passed fully: 80 bytes -> 2 chunks, normal/boundary/
  stack reads correct, overrun rejected RC=8.
- M9PINC incremental regression passed fully.
- INIT succeeded.
- APPEND fragments of 10, 54, then 16 bytes succeeded (non-aligned calls).
- READ before FINAL rejected RC=8: `GITPBUF: pack buffer not finalized`.
- FINAL flushed partial last record.
- offset 60 count 12 -> `0C0D0E0F0001020304050607` across record boundary.
- READSTACK offset 63 count 3 -> `0F0001`.
- final eight bytes -> `08090A0B0C0D0E0F`.
- final `M9 INCREMENTAL PACK BUFFER TESTS PASSED`.

Known harmless first-run diagnostics: DMSERS002E for absent GITPMETA/GITPBUF when
CLEAR/WRITE removes files before creating them.

### M9C bounded PACK SHA-1 — DONE/TARGET PROVEN
`src/GITPSHA.EXEC` verifies a finalized GITPBUF without assembling the complete
pack in one REXX string. It reads the payload in chunks of at most 64 bytes via
GITPBUF READSTACK, feeds the existing target-proven GITSTRM SHA-1 module, then
reads the final 20-byte trailer separately and compares the digest.

`src/M9CSHA.EXEC` stores the known M8A two-object pack through INIT/APPEND/FINAL.
Target result computed and accepted
`5F1C02695D4BC807AE4A5DD622AD1D28E7659429`. A trailer ending in `...9428`
was rejected RC=8 while the computed payload digest remained `...9429`.
Final target message: `M9C BOUNDED PACK SHA-1 TESTS PASSED`.

A direct GITPSHA VERIFY against the prior M9B arbitrary 80-byte test buffer also
correctly rejected its final 20 bytes as a nonmatching trailer, RC=8. This was an
expected pre-regression sanity check, not a failure of M9C.

### M9D bounded inflater primitive — DONE/TARGET PROVEN
`src/GITPINFL.EXEC` provides an isolated GITPBUF reader-driven inflater path for
the stored-DEFLATE form used by the known M8A ordinary object. It does not first
assemble the complete compressed stream or complete PACK into one REXX hex
string. `src/M9DINF.EXEC` builds the known M8A pack incrementally and exercises
the primitive at the first object's zlib offset.

Target result:
- first ordinary object inflated to `DATA 616263` (`abc`).
- inflater reported `ZLIB BYTES 14`.
- next packed object remained at byte offset 27 with header `33`.
- final `M9D BOUNDED INFLATER TESTS PASSED`.

### M9E bounded general inflater — DONE/TARGET PROVEN
`src/GITPDEF.EXEC` extends bounded GITPBUF DEFLATE consumption to stored, fixed,
dynamic, and mixed blocks. `src/GITPINFL.EXEC` uses it behind the bounded zlib
wrapper. `src/M9EINF.EXEC` exercises the existing M7 fixed/dynamic/mixed vectors.
A REXX variable-scope bug in the first dynamic test was fixed by making the
bounded `bits` routine a PROCEDURE exposing only `base bitpos` (commit
`6f86ae8bb3be01c2708493639d5388ea89b7819b`).

Target results:
- fixed Huffman -> `616263`, `ZLIB BYTES 11`.
- dynamic Huffman -> expected M7 dynamic payload, `ZLIB BYTES 44`.
- stored then fixed -> `616263616263`, `ZLIB BYTES 19`.
- final `M9E BOUNDED GENERAL INFLATER TESTS PASSED`.
- M7INFL and M7DYN regressions passed, including expected negative cases.
- M8PACK, M8OFS, and M8REF regressions passed, including expected negatives.
- M9DINF passed again: `616263`, 14 zlib bytes, next header `33` at offset 27.

The existing general `GITINFL` remains target proven and unchanged. M8 still
uses its whole-pack/whole-string path; M9E has not yet been integrated into the
full pack walker. The bounded inflater still accumulates the complete inflated
object in one REXX hex string.

### M9F bounded ordinary PACK walker — DONE/TARGET PROVEN
`src/GITPBWLK.EXEC` parses PACK and ordinary-object headers directly through
bounded GITPBUF logical offsets and invokes GITPINFL at each zlib offset. It
advances by the inflater's reported consumed-byte count. The initial overlength
name `GITPBWALK` was corrected to CMS-safe `GITPBWLK` before target execution.
`src/M9FWALK.EXEC` builds and verifies the known M8A pack incrementally.

Target result:
- bounded PACK SHA-1 accepted `5F1C02695D4BC807AE4A5DD622AD1D28E7659429`.
- entry 1 at offset 12 reconstructed blob `616263`.
- entry 2 at offset 27 reconstructed blob `78797A`.
- PACK data ended at offset 42.
- offset 42 contained the exact 20-byte PACK trailer.
- final `M9F BOUNDED ORDINARY PACK WALKER TESTS PASSED`.

### M9G bounded OFS_DELTA walker — DONE/TARGET PROVEN
`src/GITPBWLK.EXEC` now parses OFS_DELTA base distances by bounded GITPBUF
offsets, resolves an already reconstructed base by PACK position, inflates the
delta representation through GITPINFL, and applies it with target-proven
GITDAPP. The existing M8 walker remains unchanged.

Target result:
- bounded PACK SHA-1 accepted `8CA36BC28C5A2FDDD0EB9762CA36049A32D114B6`.
- base entry at offset 12 reconstructed `616263` (abc).
- OFS_DELTA entry at offset 24 reconstructed `61626364` (abcd).
- PACK data ended at offset 40.
- final `M9G BOUNDED OFS_DELTA WALKER TESTS PASSED`.

### M9H bounded REF_DELTA walker — DONE/TARGET PROVEN
`src/GITPBWLK.EXEC` now reads REF_DELTA 20-byte base object IDs through bounded
GITPBUF offsets, computes/stores OIDs for reconstructed blobs, resolves the base
against already reconstructed objects, inflates the delta representation through
GITPINFL, and applies it with target-proven GITDAPP.

Target result:
- bounded PACK SHA-1 accepted `7C95D709D4D46C612315060323DF0B5671650684`.
- base entry at offset 12 reconstructed `616263` (abc).
- REF_DELTA entry at offset 24 reconstructed `61626364` (abcd).
- PACK data ended at offset 59.
- final `M9H BOUNDED REF_DELTA WALKER TESTS PASSED`.

M9F/M9G/M9H now provide an isolated bounded-input PACK path for ordinary blobs,
OFS_DELTA, and REF_DELTA. The existing M8 whole-pack walker remains unchanged.

### M9I bounded reconstructed-object store — DONE/TARGET PROVEN
`src/GITOBUF.EXEC` provides an isolated CMS-backed reconstructed-object buffer
with incremental appends of at most 64 bytes, 64-byte physical records, partial
tail handling, FINAL, and bounded logical-offset reads. `src/M9IOBUF.EXEC`
proved the primitive before integration into the inflater/walker.

Target result:
- 145 bytes appended across multiple physical records.
- pre-FINAL read correctly rejected RC=8.
- cross-record read at offset 60/count 12 returned 4 AA bytes + 8 BB bytes.
- final 17-byte partial record returned all CC bytes.
- overrun correctly rejected RC=8.
- final `M9I BOUNDED OBJECT STORE TESTS PASSED`.

The target-proven M9F/M9G/M9H walker path remains unchanged. GITPINFL/GITPDEF
still return the complete inflated object as one REXX hex string.

## M9J-M9P completion summary
M9J true bounded streaming DEFLATE/zlib writes incrementally to GITOBUF and
passes fixed, dynamic, mixed, and bad-Adler gates. M9K integrates ordinary PACK
objects with bounded OID calculation. M9L and M9M integrate bounded OFS_DELTA
and REF_DELTA reconstruction. M9N proves 4096-byte bounded delta reconstruction
and a 512-byte streaming object. M9O adds bounded input/output caching; the
4096-byte streaming gate passes with Git blob OID
`9D235ED07CD19811A6CEB342DE82F190E49C9F68`.

M9P consolidates ordinary, OFS_DELTA, and REF_DELTA into `GITP9PWK.EXEC`.
`GIT9CTX.EXEC` provides disk-backed multi-object context keyed by PACK position
and OID. Non-immediate OFS/REF bases were target proven, as was a chained delta
where reconstructed `abcd` became the base for reconstructed `abcde`.
The consolidated install path copies one CMS record at a time and does not use
an arbitrary-size EXECIO * stem for reconstructed object data.

Final target regression sweep on 2026-09-17 passed M9JSTRM, M9JZLIB, M9KWALK,
M9LOFS, M9MREF, M9NSTRES, M9NSTRM, M9O4096, M9PCONS, M9PCTX, and M9PCHAIN.
M9P and the M9 scalability milestone are complete/target proven.

## M10 transport progress

M10A side-band to bounded PACK, M10B arbitrary read boundaries, and M10C
upload-pack response framing are DONE/TARGET PROVEN.

M10D real Git upload-pack bytes is DONE/TARGET PROVEN. G10DFIX.EXEC contains
a response captured from Git 2.47.3 upload-pack for a deterministic repository.
M10DREAL.EXEC feeds the unchanged wire bytes through GIT10UP.

The real fixture exposed an ASCII/EBCDIC bug hidden by synthetic tests. Git
pkt-line length fields are ASCII wire bytes. GIT10UP, GIT10BF, and GIT10PK now
decode the four length bytes numerically. GIT10UP recognizes NAK LF by wire hex
4E414B0A.

The real PACK also exposed the old blob-only ordinary-object limit. GITBOID now
hashes COMMIT, TREE, BLOB, and TAG. GITP9PWK walks ordinary types 1 through 4
and carries resolved type through deltas. GIT9CTX stores object type and scans
its index one record at a time.

M10D target result, 2026-09-17:
PACK SHA1 00C20177E759DC5FFD06EA42D0A1D1E1A9F53E7B
COMMIT position 12 size 148 OID 59D72104FBF18B76536A3A99776C7F7930C27CD8
TREE position 124 size 33 OID 747ABC3C651FC0DD12A37E5B5C47E0D02CD0DC4E
BLOB position 168 size 3 OID F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F
PACK version 2, objects 3, data end 180.
Final M10D REAL GIT UPLOAD-PACK FIXTURE TEST PASSED.

Final relevant commits:
GIT10UP af01f6da0a4545d759a7ae15cb2da2eef4529afc
GIT10BF bad7631ee94d388965c00a0d63572dffb40b86eb
GIT10PK 44c554802741129213d96cbcd9aeff05ed991e6f
GITBOID d06512a627e39b0577653a494ee8712bf09aaaad
GIT9CTX 29d16766f2cb48389f8935a1fbdc45909008d574
GITP9PWK 492eb2d25fd9b4e65373e65240ca3a51fe9c6f5d

## 2026-09-18 boundedness hardening closure

Post-reboot recovery and the remaining pre-M11 boundedness work are now target
proven.

GIT9CTX was redesigned to eliminate per-position CMS filenames and their
five-digit position collision. It now uses G9CDATA DATA A plus G9CIDX DATA A
and G9CMETA DATA A, with bounded sequential record access. Commit:
4faf89e073c94b2b4644c2f62b48934cae07651f. M9PCONS, M9PCTX, M9PCHAIN, and
M10DREAL passed after this redesign.

GIT10BF was redesigned as a bounded pkt-line state machine: only a partial
four-byte header and counters are retained; side-band channel 1 is forwarded
incrementally to GITPBUF, channel 2 is discarded incrementally, and channel 3
fails in a controlled way. Final commit:
4a670109244cf18dc297683475ee22544a698ec1. M10BFRAG, M10CRESP, and M10DREAL
passed on target.

GIT10UP was likewise redesigned to avoid retaining an arbitrary incomplete
pkt-line. The final fix preserves the original ASCII pkt-line header across
fragmented PREPAY processing rather than reconstructing it from remaining
bytes. Commit: 5383f2b10b6a376766b24be36b498ee60097feb8.
M10CRESP and M10DREAL passed on target on 2026-09-18.

The final GITBOID strict-boundedness issue is closed. GITBOID no longer uses
EXECIO * DISKR GITHASH DATA A into a REXX stem. GITSTRM now has a CMS-file
input mode and reads GITHASH DATA A sequentially with FSREAD while retaining
the original program-stack interface for PACK SHA regression use. The z/VM
6.3-compatible extended FSCB definition uses FORM=E, RECFM=V, BUFFER, and
BSIZE, with the assembler continuation marker in column 72. Relevant commits:
395dc3bd128ada29329a6e1e661b393ab1ebd564
f2e1804315eb80e82f992ccb70a2df60b3af9105
b387e6c4c6ad4a41a3d058b180b4f40fde86d8e4

Target gates after the final GITSTRM build:
- M9PCONS passed ordinary, OFS_DELTA, and REF_DELTA with exact prior OIDs.
- M9PCHAIN passed abc -> abcd -> abcde; final OID
  6A8165460570531A1247BD99A73B53A5A6E500D5.
- M10DREAL passed the real Git fixture with exact COMMIT, TREE, and BLOB OIDs
  and PACK SHA1 00C20177E759DC5FFD06EA42D0A1D1E1A9F53E7B.

The known pre-M11 unbounded whole-object REXX stem and context-position
collision blockers are therefore closed. M10E then stress-proved transport
boundedness with a maximum normal pkt-line (ffff, 65535 total bytes): a
channel-2 payload of 65530 bytes was delivered in 31-byte fragments through
GIT10BF without retaining the pkt-line payload. M10ESTRS passed on target on
2026-09-18 in T=7.55/9.05. M10B/C/D continue to prove semantics and real-wire
compatibility.

## Persistence / restart point
GitHub main is canonical. M10D is target proven independently of emulator state.
After a target restart, retransmit required source with cms-upload.sh as needed.

Next target regression sweep:
M9PCONS, M9PCTX, M9PCHAIN, M10AFEED, M10BFRAG, M10CRESP, M10DREAL.

M10A-C synthetic fixtures may expose their old EBCDIC header construction after
the correct ASCII parser change. Fix those fixtures, not the production parser.

Before M11, harden GIT9CTX: its G9C plus five-digit PACK-position filenames can
collide above position 99999. Also replace large incomplete pkt-line buffering
with bounded streaming state before real side-band-64k traffic.

## M11 native CMS networking/HTTP progress

M11A is DONE/TARGET PROVEN on 2026-09-18. Native REXX/SOCKETS 3.03 initialized
against TCPIP, resolved EXAMPLE.COM to current IPv4 addresses, connected on
port 80, enabled SO_ASCII for the HTTP-text proof, sent all 56 request bytes,
received 316 response bytes with each RECV bounded to 256 bytes, and closed
cleanly. No BFS/OpenExtensions, Pi proxy, or Mac runtime helper was involved.

After reboot, TCP/IP client commands/configuration required linking TCPMAINT 592
read-only and accessing it as T. This exposed PING/NETSTAT and TCPIP DATA.
NETSTAT showed IPv4 home 192.168.1.223/24 on OSA1 and default gateway
192.168.1.254. PING to the gateway and 8.8.8.8 succeeded. The earlier timeout
to 93.184.216.34 was destination-specific, not a native socket/routing failure.

M11B is DONE/TARGET PROVEN. SO_ASCII was confirmed OFF; 56 exact ASCII wire
bytes were sent, raw RECV was bounded to 256 bytes, 828 bytes were received,
and the exact raw prefix was 485454502F312E3120323030204F4B0D.

M11C is DONE/TARGET PROVEN. GIT11HTP bounded HTTP header framing preserved a
binary body containing 00, FF, and PACK bytes exactly across a deliberately
fragmented CRLFCRLF boundary.

M11D is DONE/TARGET PROVEN. GIT11HTP routed the bounded HTTP body directly into
GIT10UP/GIT10BF/GITPBUF. The real Git 2.47.3 upload-pack fixture reproduced
PACK SHA1 00C20177E759DC5FFD06EA42D0A1D1E1A9F53E7B, COMMIT OID
59D72104FBF18B76536A3A99776C7F7930C27CD8, TREE OID
747ABC3C651FC0DD12A37E5B5C47E0D02CD0DC4E, BLOB OID
F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F, and PACK data end 180.


## M12 SSL/TLS rediscovery guard — 2026-09-18
Do not repeat the early-project SSL configuration investigation. Prior work
already established these facts for the z/VM 6.3 target:

- z/VM 6.3 SSL/System SSL support on this installation is the native TLS path;
  TLS 1.2 was established as the relevant/highest target SSL-server protocol.
- Dynamic SSL/TLS is the intended application architecture. Ordinary native
  sockets handle TCP; a native Dynamic SSL adapter handles TLS. Do not attempt
  to make REXX/SOCKETS itself implement TLS, and do not add a Pi/Mac proxy,
  BFS/OpenExtensions dependency, or custom TLS implementation.
- Earlier inspection found Dynamic SSL material including TCPSSL PASCAL and
  routines such as SkSslAcc and SkSslBnd. TCSSLSRV in ALLMACRO was also found,
  but it is an internal SSL-server DSECT and is not the application API.
- The normal socket headers did not expose SSL extensions.
- SYSTEM DTCPARMS belongs on TCPIP 198, not TCPMAINT 198. Do not search
  TCPMAINT 198 for that configuration again.
- Current post-reboot inspection confirms TCPMAINT 592 (accessed as T) contains
  GSKCMS31, GSKC31, GSKC31F, GSKSSL, GSKSUS31, GSKS31, and GSKS31F modules.
- TCPMAINT 591 (accessed as U) contains GSKSSLDB LOADBFS, SSLADMIN EXEC,
  SSLIDCSS EXEC, SSLPOOL EXEC, SSLSERV LOADBFS/MODULE, VMSSL EXEC,
  GSKKYMAN EXEC/MODULE, GSKMSGA/GSKMSGS catalogs, and GSKTRACE EXEC/MODULE.
- No matching SSL/GSK MACLIB or COPY files were found on TCPMAINT 591/592.
- Q SSL00001 and Q SSLDCSSM returned HCPCQU045E not logged on. This proves
  only that those users were not logged on; it does not prove they are absent
  from the directory or that SSL requires reconfiguration.

M12 must resume from the programming-interface question, not SSLPOOL setup:
recover and verify the exact IBM z/VM 6.3 Dynamic SSL application API from IBM
documentation/source material, especially the TCPSSL PASCAL interface and the
assembler-callable contract for an outbound TLS client. IBM documentation is
the first source of truth; observed target behavior is second. Do not guess API
entry points or configuration commands.

The desired M12 adapter must preserve the raw bounded-byte interface already
proven above GIT11HTP: establish outbound native TLS, perform certificate and
hostname/SNI handling as supported/required by the documented target API, and
deliver bounded binary-safe decrypted HTTP bytes to the existing M11/M10 path.



## M12 Dynamic SSL interface findings — 2026-09-18
The new `src/cms-download.sh` helper (commit
4bad2c8f9f8da05f7ca23f2ddb3da9dce9cda0bf) is target proven by downloading
`ALLMACRO MACLIB T` (~3.9 MB) from CMS to the Mac through the existing c3270
DFT path. Use this helper for future CMS-to-Mac source/interface inspection.

Direct inspection of the downloaded IBM-supplied ALLMACRO plus the IBM
Programmer's Reference corrected the earlier partial recollection:
- TCSOCKC explicitly says SkSsl procedures are implemented in TCPSSL PASCAL.
- Verified declarations include SkSslSoc, SkSslBnd, SkSslCon, SkSslLis,
  SkSslAcc, and DoIoctlSSL. SkSslCon DOES exist; an earlier XEDIT search simply
  missed it.
- SockAddrSslType is the internal SOCKE_SSL address structure and includes real
  server address/port, connection number, certificate label, and Ssl_OrigTcb
  for Dynamic SSL. These SkSsl routines/structures are stack internals, not the
  application-level interface to implement directly.
- The documented application API for an outbound secure connection is
  TcpSClient for Pascal. It takes a connection returned by TcpOpen/TcpWaitOpen,
  a Wait flag, SecureDetailType, handshake result, and return code.
- SecureDetailType contains TLSLabel, TLSTimeout, RequestClientCert,
  ValidatePeerCert, CipherRequest, Reserved1, Keyring, and Buffer. The IBM
  reference states TLSTimeout=0, RequestClientCert=0, Reserved1=0, and an empty
  Keyring for this level; ValidatePeerCert=Full_Check requests certificate
  validation.
- The documented assembler/VMCF equivalent is CALLCODE TLSSCLIENTtcp. It uses
  SEND/RECV, VADA=address of SecureDetailType, LENA=its length, VADB=0, LENB=1,
  and CONN=the connection number from OPENtcp. Preprocessing status is returned
  by VMCF REJECT; handshake completion arrives as SECUREhandshakeCOMPLETE.
- TLSQuery CALLCODE 128 is the documented prerequisite probe for SSL-server
  availability/label recognition. QUERYtlsCOMPLETE is notification 33;
  SECUREhandshakeCOMPLETE is 34; READYforHANDSHAKE is 35.
- Critical architecture consequence for z/VM 6.3: Dynamic SSL is tied to the
  TCP connection number owned by the Pascal/VMCF TCP/IP API. The M11
  REXX/SOCKETS descriptor does not expose that documented connection-number
  contract. Therefore M12 should not try to wrap the M11 REXX socket. The
  native assembler adapter should own OPENtcp/SENDtcp/RECEIVEtcp plus
  TLSSCLIENTtcp, then present the same bounded raw-byte interface upward.
- Do not confuse this with the later z/VM 6.4 client/server TLS ioctl support;
  the 6.3 design must use the documented Dynamic SSL VMCF/Pascal API.

Next M12 subgate: build the smallest assembler/VMCF TLSQuery capability probe,
using the IBM VMCF parameter-list definitions/equates from the supplied
ALLMACRO and Programmer's Reference. Once TLS availability is proven, extend
that same adapter to OPENtcp + TLSSCLIENTtcp and bounded SEND/RECEIVE.

## 2026-09-21 EC2 TCP/IP and native TN3270 recovery

The old Raspberry Pi 192.168.1.223/24 configuration was stale on the EC2 host.
EC2 Debian has ens5 172.31.14.90/20 and tap0 192.168.200.1/24. IPv4 forwarding
is enabled. iptables POSTROUTING has MASQUERADE for 192.168.200.0/24 out ens5.

IBM IPWIZARD was made available to MAINT by linking/accessing MAINT 193 (2CC was
already accessed). IPWIZARD reconfigured TCPIP successfully:
- TCPIP VM: TCPIP
- host TACOTICO, domain MIKE.LCL
- OSA1 / DEV@0600, QDIO layer 2, MTU 1500, PMTU enabled
- z/VM address 192.168.200.2/24
- gateway 192.168.200.1
- DNS 8.8.8.8
IPWIZARD successfully pinged the interface, gateway, and DNS and regenerated
PROFILE TCPIP and SYSTEM DTCPARMS on TCPIP 198 plus TCPIP DATA on TCPIP 592.
NETSTAT DEVLINKS showed DEV@0600 OSD Ready and OSA1 QDIOETHERNET.

MAINT PROFILE EXEC A was updated to persist TCP/IP client commands with:
'CP LINK TCPMAINT 592 592 RR'
'ACCESS 592 T'
This restores PING/NETSTAT after login/profile execution.

Native z/VM TN3270 is now proven. NETSTAT CONN showed INTCLIEN listening on
TELNET port 23. From EC2 Debian, nc -vz 192.168.200.2 23 succeeded. The Mac uses
an SSH local forward through EC2 to z/VM port 23, and c3270 connects through
that path. 3270 oversize is confirmed working over the native z/VM TCP/IP/TN3270
path. This is now the preferred ordinary network-login path; Hercules CNSLPORT
remains useful for the system/operator console.

## NEXT ACTION
Build M12A as a minimal assembler/VMCF TLSQuery probe from the documented z/VM
6.3 CALLCODE interface. Do not wrap the REXX/SOCKETS descriptor. After TLSQuery
is target proven, extend the same native adapter to OPENtcp + TLSSCLIENTtcp +
bounded SENDtcp/RECEIVEtcp, preserving the raw bounded-byte interface expected
by GIT11HTP.

## 2026-09-21 workflow rule and M12A execution diagnostic

Workflow rule: proceed independently through all host-side research, source
inspection, GitHub edits, and preparation. Do not stop to ask the user to
perform intermediate work. Stop only when an action on the z/VM/CMS target is
actually required; then provide the exact Mac transfer commands first (when a
transfer is needed) and the smallest exact CMS command batch. Continue again
independently as soon as the target output is returned.

The native c3270 DFT control path is recovered and target proven. A single
interactive c3270 session is launched with local script port 3271; transfer
helpers send c3270 Transfer() actions to that port. The running c3270 resolves
LocalFile relative to its own launch directory, not the helper shell's current
directory. An absolute LocalFile path was proven by successfully uploading
GIT12Q ASSEMBLE A. Preserve CMS filename/type limits of eight characters.

GIT12Q assembled, LOADed, and GENMODed cleanly, but its first execution blocked
until HX. Do not run GIT12Q again in that form. Inspection of the existing
canonical M12 diagnostics shows the missing target mechanics: M12ABEG selects
the base VCPU, installs HNDEXT X'4001', ENABLEs interrupts, enables CR0 bit 31,
AUTHORIZEs TCPIP, and uses bounded polling for BEGINtcpIPservice rather than an
unbounded WAITECB. M12ATLS contains the fuller TLSQuery sequence. Use the
existing bounded diagnostic path to localize VMCF completion before resuming
TLSQuery; do not introduce another unbounded wait.

## M12C target proof — 2026-09-23
- Direct VMCF OPENtcp to GitHub IPv4 140.82.114.3:443 succeeds.
- OPENtcp CALLCODE X'6E' returned connection X'03E8', RC X'00'.
- OPEN notification on this z/VM 6.3 RSU is CALLCODE X'0B'.
- SSL pool VMSSL startup parameters belong in SYSTEM DTCPARMS under
  the SSL* stanza; :parms. PROTOCOL TLSV1_2 enabled TLS 1.2.
- SSLADMIN QUERY STATUS DETAILS then showed TLSV1_2 enabled on all
  five SSL servers and SHA-256 cipher suites included.
- M12TLS3 target-proved TLSSCLIENTtcp preprocessing: CALLCODE X'83',
  connection X'03E8', return X'00'.
- CALLCODE X'25' on this target is READYforHANDSHAKE, not handshake
  completion. CALLCODE X'24' is SECUREhandshakeCOMPLETE.
- M12TLS4 target-proved X'25' followed by X'24', SENDtcp X'76' RC 0,
  RECEIVEtcp X'71' RC 0, DATAdelivered X'0C', and VMCF RECEIVE X'0005'.
- The X'24' notification carries a four-byte SecureHSCompleteDetail
  through VADB. M12TLS4 must receive and validate that detail before
  treating the TLS handshake as successful.
- Next milestone: validate SecureHSCompleteDetail and prove that
  received application bytes are decrypted HTTP before routing HTTPS
  Git smart-HTTP through the bounded pack/object pipeline.


## M12D checkpoint — 2026-09-23 chat rollover
- Continue independently on host/GitHub until actual z/VM/CMS action is
  required. Then give exact Mac transfer commands followed by the
  smallest exact CMS command batch.
- Current source is src/M12TLS4.ASSEMBLE. GitHub main commit
  9ec2a249985596711c26710b942a9c27df125a49 added bounded repeated
  RECEIVEtcp testing for decrypted HTTP.
- Target-proven sequence before that commit:
  OPENtcp X'6E' RC 00; OPEN notice X'0B'; TLSSCLIENTtcp X'83' RC 00;
  READYforHANDSHAKE X'25'; SECUREhandshakeCOMPLETE X'24';
  SecureHSCompleteDetail received from VADB and equals 00000000;
  SENDtcp X'76' RC 00 for the 75-byte HTTP request; RECEIVEtcp X'71'
  RC 00; DATAdelivered X'0C'; VMCF RECEIVE function X'0005' succeeds.
- First delivered data was 9 bytes:
  16030300040E000000. It is a TLS handshake record, not decrypted HTTP.
  Therefore HTTPS application receive is NOT yet proven.
- X'25' is READYforHANDSHAKE. X'24' is SECUREhandshakeCOMPLETE.
  Do not regress to the earlier incorrect interpretation.
- X'24' notification VADB/LENB contains the four-byte
  SecureHSCompleteDetail. The target detail was 00000000.
- DATAdelivered data is collected with VMCF RECEIVE X'0005'; X'0004'
  is not the RECEIVE function.
- Latest target action was only ASSEMBLE of commit 9ec2a249... and it
  failed at source line 416:
      XC    RECVBUF(1024),RECVBUF
  with IFO224 LENGTH ERROR. IBM XC SS-format length is limited to 256
  bytes. No LOAD/GENMOD/run occurred after this assembly failure.
- NEXT HOST-SIDE ACTION: fix the 1024-byte RECVBUF clear using legal
  <=256-byte operations (or MVI + overlapping MVC), check every source
  line <=71 columns and every assembler symbol <=8 characters, commit
  to GitHub, then give Mac upload and CMS ASSEMBLE/LOAD/GENMOD/run.
- The purpose of the repeated-receive diagnostic is to distinguish a
  residual TLS handshake record from subsequent decrypted HTTP. It
  should only claim success when received bytes actually begin with
  ASCII HTTP (X'48545450'); otherwise inspect up to the bounded number
  of chunks and fail clearly.
- Important assembler hygiene: CMS assembler symbols <=8 chars;
  fixed-card source lines <=71 chars unless intentionally continued;
  MVC/XC explicit lengths cannot exceed 256.
- Recent commits:
  4c095778a8a5248bd10821a7a66c3989ec75127a receive/validate X'24'
  detail; 058c79c2cbd087eb10c305e21ecec90cee798cd6 fixed 9-char symbol;
  9ec2a249985596711c26710b942a9c27df125a49 repeated receive diagnostic.


## 2026-09-24 current checkpoint — EC2 TLS bridge

Native z/VM System SSL investigation reached a definitive certificate-validation
blocker. SSL server trace reported `DTCSSL022E Handshake failed rc: 8 reason:
Certificate validation error` and `DTCSSL505W Local client requested use of
CERTNOCHECK; Request ignored`. Current GitHub presents a Sectigo ECC chain
(github.com -> CA DV E36 -> Root E46). The target is z/VM 6.3 service level
1302. Import of the E46 root with GSKKYMAN failed status `0x03353083` because
ICSF services are unavailable; `CP QUERY VIRTUAL CRYPTO` reports no AP Crypto
Domains. Preserve M12TLS4 for research, but native System SSL is no longer on
the practical transport critical path.

The practical HTTPS architecture now uses stunnel on the existing EC2 Debian
host. stunnel 5.74 listens only on tap0 `192.168.200.1:8443` in client mode and
connects to `github.com:443` with CA-chain verification, hostname checking,
SNI, and TLS >= 1.2. EC2-local plaintext through that listener returned GitHub
HTTP/1.1 200 OK.

CMS-to-GitHub bridge proof is target-proven. `M11BRAW 192.168.200.1 8443`
initialized REXX/SOCKETS, confirmed SO_ASCII OFF, connected, sent all 56 raw
request bytes, received 176 bytes in bounded receives, and saw prefix
`485454502F312E3120333031204D6F76` = `HTTP/1.1 301 Mov`. The 301 is expected
because the preserved M11B diagnostic sends `Host: example.com`; valid HTTP
returning to CMS proves CMS -> TAP -> stunnel -> verified TLS -> GitHub -> CMS.

`src/M11BRAW.EXEC` was fixed to accept dotted numeric IPv4 destinations; latest
fix commit before this documentation update is
`fdcf997b60f6c95fec6322002b72e7da35c19f89`. A separate
`src/M12PRXY.EXEC` was added in commit
`197c61577dced36226f4f303ed2ee113bef066fb` with `Host: github.com`, preserving
the target-proven M11B core.

NEXT ACTION: transfer/run `M12PRXY 192.168.200.1 8443`. After that gate passes,
move directly to a real GitHub smart-HTTP request through the bridge and feed
the bounded response into GIT11HTP -> GIT10UP/GIT10BF/GITPBUF -> M9 PACK/object
pipeline. Do not resume crypto-level archaeology unless explicitly revisiting
the native System SSL research path.


## 2026-09-24 M12PRXY target proof

`M12PRXY 192.168.200.1 8443` is TARGET PROVEN. CMS REXX/SOCKETS initialized,
SO_ASCII was OFF, connect to the EC2 TAP listener succeeded, all 55 exact request
bytes were sent, and bounded 256-byte receives returned 582167 bytes. Wire prefix
`485454502F312E3120323030204F4B0D` is `HTTP/1.1 200 OK\r`. Final target message:
`M12 PROXY PATH TEST PASSED`. This closes the generic HTTPS bridge gate with the
correct `Host: github.com` header.

NEXT ACTION: build an isolated Git smart-HTTP discovery/fetch integration gate
through `192.168.200.1:8443`, preserving M11BRAW/M12PRXY. Feed bounded HTTP
response bytes through GIT11HTP and the existing M10/M9 transport/PACK pipeline.
