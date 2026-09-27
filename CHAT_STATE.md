# CMS/zVM Native Git Client — Chat State

Updated: 2026-09-26
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


## M12 practical GitHub smart-HTTP closure — 2026-09-24
- EC2 stunnel practical HTTPS path is target proven end-to-end for real Git.
- M12GDISC fetched the real ibm-sandbox upload-pack advertisement through the
  bridge. GitHub HTTP/1.1 uses chunked transfer encoding on this path.
- GIT12CHK is the bounded HTTP chunk decoder; live advertisement replay passed.
- M12JPOST live upload-pack request required pkt-line length 004a and total HTTP
  Content-Length 87 (74-byte want pkt-line + 4-byte flush + 9-byte done).
- Corrected POST returned 348959 HTTP bytes.
- M12KPACK decoded the response through GIT12CHK -> GIT10UP -> GIT10BF ->
  GITPBUF. Final PACK length is 340027 bytes and GITPSHA verified SHA1
  8C92E274ECA84B797F8925A6082915DD6CCDE196.
- PACK v2 contains 1808 objects. GITP9PWK successfully reconstructed >200 live
  objects before the verbose diagnostic was stopped, including ordinary
  COMMIT/TREE/BLOB and chained OFS_DELTA objects with computed Git OIDs.
- Full 1808-object walk is not a useful M12 gate: current bounded REXX/CMS
  implementation is too slow. The prior interrupted run consumed ~415 seconds
  virtual CPU and a subsequent quiet run confirmed 1808 objects.
- M12 transport is therefore closed/proven. Do not rerun network POST merely to
  benchmark local processing; M11BODY/GITPBUF capture is the benchmark while
  present on target.
- NEXT: M13 PACK/object performance. Preserve bounded storage semantics. Focus
  first on GIT9CTX linear index lookup and repeated EXECIO/file open-close work.


## M13N native DEFLATE checkpoint — 2026-09-25
- Target z/VM Assembler XF assembled src/GITINFA.ASSEMBLE without flagged statements; LOAD, GENMOD and M13NTEST all succeeded at 08:35:53.
- Native 32 KiB history, fixed Huffman literals and LZ77, dynamic Huffman with full 5400-byte output comparison, stored blocks, mixed multiblock, zlib CMF/FLG and Adler-32, and malformed-stream tests all passed.
- Malformed tests reject truncated DEFLATE, insufficient output capacity, invalid stored LEN/NLEN, and reserved BTYPE. zlib negative tests reject invalid FCHECK and checksum.
- Source checkpoint: commit f47289d7c6ac82eba7cbba0cf5d06d944391ebaf. Two code bases (R12 initial 4K, R1 second 4K), local LTORG pools, and R13 DATAORG base are required to assemble the expanded module.
- Current GITINFA is a standalone self-test MODULE, not yet a callable PACK inflater. GITPBUF READSTACK returns hexadecimal text and GITINFA consumes native binary bytes. The integration needs an explicit binary-safe bridge and bounded output contract; do not substitute an unbounded REXX hex string for a 340027-byte PACK.
- NEXT: inspect M13M/M13N and bounded GITPBUF callers, design a native callable interface and an isolated CMS integration test on small real PACK/zlib objects. Retain target-proven REXX fallback and existing M13NTEST. Do not claim live PACK acceleration until it is tested on CMS.


## M13 production native PACK milestone — 2026-09-25
- CMS GITTEST ALL passed 27 PASSED, 0 FAILED after promotion.
- Production GITP9PWK defaults WALK / WALK QUIET to native STRICT; WALK REXX / WALK QUIET REXX retains original implementation.
- Consolidated GITTEST tests malformed streams, PACK headers, deltas, SHA1/trailer and boundary validation, production routing, and a Git-generated five-object PACK through both routes.
- This does not establish performance or full traversal of captured 340027-byte / 1808-object live GitHub PACK.
- NEXT: benchmark and validate native-default walker against already captured live PACK in GITPBUF if still available. Do not repeat network POST just to benchmark. Record progress, object count, time and failures; retain REXX fallback. Investigate GIT9CTX indexing and per-object CMS I/O if throughput inadequate.

## 2026-09-26 GCCCMS/native inflater checkpoint

GCCCMS on CMS F is operational. `GITCLNK` builds a C program with the `GITCAPI` assembler adapter and `GITINFA`; `GITCAPI` converts GCCCMS's R1 argument-list pointer into `GITNAPI`'s direct six-fullword parameter-block pointer. On CMS, `GITCINF` passed its binary `abc` fixture (`RC 0`, 3 output bytes, 11 zlib bytes consumed; `61 62 63`) and decoded the first live object of `GITPBUF PACK A` (`RC 0`, 270 output bytes, 182 zlib bytes consumed, next object offset 196). The live stream prefix was `78 9C A5 8C 5B 6A C3 30 10 45 FF BD 8A D9 40 82`. The initial direct C call and 1 KB input tests returned RC 8; the ABI adapter fixed the call. Preserve these target results and the later 1,808-object GITCWALK result documented in `docs/STATUS.md`. Next native-engine work is checksum, delta/base reconstruction, object OIDs, and persistence, not re-proving first-object inflation.

## 2026-09-26 native C/assembler integration checkpoint

GCCCMS is operational on CMS F. GITCLNK builds C with GITCAPI and GITINFA. GITCAPI converts GCCCMS's argument-list calling convention to GITNAPI's direct six-fullword parameter-block ABI. GITCINF passed its abc fixture (RC 0, output 3, consumed 11; data 61 62 63) and first live PACK object (RC 0, output 270, consumed 182; next object offset 196). The initial RC 8 was caused by the ABI mismatch, not proof of invalid zlib input. Preserve the newer 1,808-object GITCWALK inflate-only gate recorded in docs/STATUS.md. Next: native PACK checksum, OFS/REF delta resolution, object OIDs and persistence; retain the target-proven REXX fallback.

## 2026-09-26 native PACK SHA-1 closure and next gate

Repository `main` is canonical. Target z/VM 6.3 GCCCMS `GITCLNK GITCWALK`
built successfully with three clean Assembler XF passes. Existing live capture
`GITPBUF PACK A` is 340,027 bytes, PACK v2, 1,808 objects. Native GITCWALK
verified PACK SHA-1 `8C92E274ECA84B797F8925A6082915DD6CCDE196`
and inflated all 1,808 streams to final offset 340,007 in 3.33 CPU /
3.38 elapsed seconds. A separate in-memory corrupt-trailer mode,
`GITCWALK BADSHA`, returned `PASS BADSHA: CORRUPT TRAILER REJECTED`, RC 0,
in 1.81 CPU / 1.83 elapsed seconds. The subsequent unmodified `GITCWALK ALL`
passed again in 3.30 CPU / 3.34 elapsed seconds. Both positive and negative
native PACK SHA-1 tests are target-proven; never mutate the captured PACK or
repeat the network POST for local gates. Earlier inflation-only benchmark
was 2.10 CPU / 2.14 elapsed seconds, not comparable as checksum-inclusive.

Next: native OFS_DELTA base-position resolution, then bounded delta application
and reconstructed object OIDs. Native C currently only inflates delta instruction
streams; REXX `GITP9PWK` remains the correctness reference. Preserve known-good
GITCAPI/GITINFA and the single c3270 transfer workflow. The GCCCMS source
transfer translated C caret XOR badly; native SHA-1 uses `bxor` instead.
All new target C source must fit 80-column CMS records. For target testing,
provide Mac `git pull` plus absolute-path `./cms-upload.sh` first, then
`FILEDEF PACKIN DISK GITPBUF PACK A`, `GITCLNK GITCWALK`, and specific
`GITCWALK` gate. No BFS/OpenExtensions dependency.

## 2026-09-26 OFS base-position target proof

GITCWALK ALL on z/VM 6.3 passed native PACK SHA-1, inflated all 1,808
objects, resolved 1,117 OFS_DELTA base header positions, and ended at
PACK data offset 340,007. CMS CPU/elapsed: 3.44/3.49 seconds. This
proves base-position resolution, not delta application, OID calculation,
or persistence. Next milestone: native bounded delta reconstruction.

## Native OFS_DELTA application gate — prepared, not target-proven

Commit `9a0453d` adds isolated `GITCWALK OFSAPPLY` mode. The existing
`GITCWALK ALL` and `BADSHA` modes retain their previous behavior. OFSAPPLY
uses a bounded Git delta varint/copy/insert parser, retains prior reconstructed
objects by PACK index, inherits the base object's type, and applies OFS_DELTA
instructions to the resolved base. It checks base and result lengths and
copy/insert bounds with a 65,536-byte per-object cap. It prints
`OFS DELTAS APPLIED N` on success. REF_DELTA reconstruction and object OIDs
remain unimplemented in native C; OFSAPPLY stops explicitly if it encounters
a REF_DELTA. This code awaits CMS compile and target execution; do not mark
it proven before the user returns output. Test with existing captured PACK,
without repeating the network POST. First rerun ALL to ensure no regression,
then OFSAPPLY. Mac: git pull, cms-upload.sh absolute GITCWALK.C; CMS:
FILEDEF PACKIN DISK GITPBUF PACK A, GITCLNK GITCWALK, GITCWALK ALL,
GITCWALK OFSAPPLY.

## 2026-09-26 native OFS_DELTA application — TARGET PROVEN

CMS `GITCWALK ALL` verified SHA-1
`8C92E274ECA84B797F8925A6082915DD6CCDE196`, inflated all 1,808
objects, resolved all 1,117 OFS_DELTA base positions, and ended at PACK
offset 340,007 (CPU/elapsed 3.49/3.55 seconds). The separate
`GITCWALK OFSAPPLY` mode then passed the same integrity and inflation
gates and reported `OFS DELTAS APPLIED 1117`, with final offset 340,007
(CPU/elapsed 5.19/5.27 seconds). The native OFS_DELTA application gate is
now target-proven. Native REF_DELTA support, independent reconstructed-object
OID verification, and object persistence are not yet implemented. Continue
using the unchanged captured PACK and preserve existing ALL/BADSHA gates.

## Native reconstructed-object OID gate — awaiting CMS test

Commit `3e77538` adds isolated `GITCWALK OID` mode. It retains and
reconstructs ordinary/OFS_DELTA objects exactly as target-proven OFSAPPLY,
then hashes Git's canonical `<type> <size>\\0` prefix and reconstructed
bytes with the native SHA-1 implementation. It prints OIDs for the first
three and last objects, and `OBJECT OIDS COMPUTED 1808` on success.
The OID mode has not yet been compiled or run on CMS, and its output
must be compared with an independent Git/REXX reference before claiming
OID correctness. `ALL`, `BADSHA`, and `OFSAPPLY` remain separate gates.
Native REF_DELTA resolution and CMS persistence remain future work.

## 2026-09-26 OID target proof and profiling next gate

CMS `GITCWALK OID` verified PACK SHA-1
`8C92E274ECA84B797F8925A6082915DD6CCDE196`, inflated 1,808
objects, applied all 1,117 OFS_DELTA programs, computed 1,808 Git object
IDs and ended at byte offset 340,007 (CPU/elapsed 20.70/20.83 seconds).
Sample IDs: obj 1 COMMIT 270 bytes
`5A81BAF86E7DC7B72377087A8F160CAF8B889B74`; obj 2 BLOB 1841 bytes
`030E4837F28336A89B785202BC84B00E934F7C94`; obj 3 TREE 139 bytes
`450532795889EE54C540AC1AE9581E0FA98C7866`; obj 1808 TREE 5224 bytes
`BA9F4D66B41352F0D0266090D14AD52F37318FCB`. All OIDs were computed
on CMS, but independent comparison remains pending. OFSAPPLY previously took
5.19/5.27 seconds and ALL 3.49/3.55 seconds; do not attribute the difference
to SHA-1 until separately measured.

Commit `e5001c1` adds `GITCWALK PROFILE` as an isolated OID-equivalent mode
using C `clock()` around delta application and object hash calls. It prints
`PROFILE CLOCKS PER SEC`, `PROFILE DELTA TICKS ... BYTES ...` and
`PROFILE HASH TICKS ... BYTES ...`. PROFILE has not yet been compiled or
run on CMS. Preserve ALL, BADSHA, OFSAPPLY and OID modes. Next target gate:
Mac git pull and absolute-path cms-upload.sh GITCWALK.C; CMS FILEDEF PACKIN,
GITCLNK GITCWALK, then GITCWALK PROFILE. Do not repeat network POST.

## 2026-09-26 CMS PROFILE result and FASTOID gate

`GITCWALK PROFILE` passed PACK SHA-1, all 1,808 inflations, all 1,117
OFS_DELTA applications, and all 1,808 OID computations. The sample OIDs
matched the prior OID run. CPU/elapsed: 20.70/20.83 seconds. It reported
`CLOCKS PER SEC 1000`, `DELTA TICKS 0 BYTES 3406774`, and
`HASH TICKS 0 BYTES 3936764`. CMS `clock()` did not yield usable
per-call timing; the prior 5.27-second OFSAPPLY and 20.83-second OID
whole-run comparison suggests about 15.56 seconds additional OID-mode
work, not exclusively proven to be SHA-1.

Commit `950b199` (diagnostic fix `8ac152f`) adds isolated
`GITCWALK FASTOID` mode. Its streaming SHA-1 hashes the canonical Git
object header and reconstructed body without copying the entire body to
a contiguous hash buffer. FASTOID independently computes the existing
reference OID for every object and fails on any byte mismatch. It reports
`FAST OIDS MATCH REFERENCE 1808` only after all 1,808 match. This is
awaiting CMS compile/run; it deliberately performs both hash paths, so
FASTOID total runtime is not an optimization benchmark. Once parity
passes, a separate fast-only benchmark can measure speed. Keep ALL,
BADSHA, OFSAPPLY, OID, and PROFILE unchanged. Mac git pull and upload
absolute-path GITCWALK.C; CMS FILEDEF PACKIN, GITCLNK GITCWALK,
GITCWALK FASTOID. No network POST needed.

## 2026-09-26 FASTOID parity target proof; FASTONLY benchmark pending

CMS `GITCWALK FASTOID` passed native PACK SHA-1, inflated all 1,808
objects, applied all 1,117 OFS_DELTA programs, and computed 1,808 OIDs.
Its independent streaming SHA-1 output matched the original OID hash
byte-for-byte for every object: `FAST OIDS MATCH REFERENCE 1808`.
CPU/elapsed was 36.45/36.63 seconds, expected to include both hash
paths and therefore not a streaming-only benchmark.

Commit `9ffbbf3` adds isolated `GITCWALK FASTONLY` mode: same PACK
integrity, reconstruction and sample OID output, but hashes each object
only with the target-proven streaming implementation. FASTOID remains
available as the byte-for-byte parity regression. FASTONLY is not yet
compiled/tested on CMS. Next: Mac git pull and absolute-path upload
GITCWALK.C; CMS FILEDEF PACKIN, GITCLNK GITCWALK, GITCWALK FASTONLY.
Compare its CPU/elapsed to prior OID 20.70/20.83 seconds. No network
POST needed. Independent Git/REXX sample-OID comparison still pending.

## 2026-09-26 FASTONLY benchmark and next OPTSHA gate

CMS `GITCWALK FASTONLY` passed SHA-1, 1,808 inflations and OIDs,
1,117 OFS_DELTA applications, and final PACK offset 340,007. Sample
OIDs matched OID/FASTOID. CPU/elapsed 20.98/21.11 seconds versus
original OID 20.70/20.83 and OFSAPPLY 5.19/5.27. Streaming alone did
not demonstrate a speedup in this single run; do not claim it did.

Commit `154509c` adds isolated `GITCWALK OPTSHA` mode, using a second
SHA-1 compression routine with macro-expanded XOR rather than repeated
`bxor()` calls. Existing PACK checksum and original SHA-1 gates remain
unchanged; OPTSHA selects the alternate compression routine only while
computing object OIDs. This is an experimental benchmark, not yet CMS
compiled/tested or independently Git-verified. Mac: git pull and upload
absolute-path GITCWALK.C. CMS: FILEDEF PACKIN DISK GITPBUF PACK A,
GITCLNK GITCWALK, GITCWALK OPTSHA. Compare sample IDs and timings to
original OID 20.70/20.83 seconds; run FASTOID for established parity if
needed. Preserve prior target-proven modes and captured PACK.

## 2026-09-26 OPTSHA result, OPTCHECK parity, issue review

CMS `GITCWALK OPTSHA` passed PACK checksum, 1,808 inflations,
1,117 OFS_DELTA applications, and 1,808 OID computations, with the
four displayed sample OIDs unchanged and final offset 340,007.
CPU/elapsed 19.29/19.42 seconds versus original OID 20.70/20.83;
one-run elapsed improvement 1.41 seconds (~6.8%), not a repeated
benchmark or full optimized/reference OID comparison.

Commit `688244a` adds isolated `GITCWALK OPTCHECK`: computes optimized
and original SHA-1 OIDs for each reconstructed object, compares all
20 bytes per object, and fails immediately on mismatch. It prints
`OPT OIDS MATCH REFERENCE 1808` only on full success. OPTCHECK has not
yet been compiled or run on CMS. Test via Mac git pull, absolute-path
cms-upload.sh GITCWALK.C; CMS FILEDEF PACKIN, GITCLNK GITCWALK,
GITCWALK OPTCHECK. Its double-hash runtime is not a speed benchmark.

GitHub open-issue review: closed #4 as not planned because direct legacy
z/VM System SSL certificate-chain research is not on the practical
Git-client critical path (working validated stunnel bridge exists).
Closed #3 as not planned because interrupted long REXX-walker timing is
superseded for current native PACK benchmarks by normal completed CMS
runs. Kept #2 open: native PACK persistence/REF_DELTA and production
readiness remain unfinished despite substantial speed improvements.
Kept #5 open: automatic stunnel startup/reboot persistence is still
unproven. Do not claim these remaining tasks completed.

## 2026-09-26 OPTCHECK target result

CMS GITCWALK OPTCHECK passed: native PACK checksum
8C92E274ECA84B797F8925A6082915DD6CCDE196, 1,808 objects,
1,117 OFS_DELTA applications, all 1,808 optimized SHA-1 OIDs
byte-for-byte equal to the original implementation, final offset
340007. Reported `OPT OIDS MATCH REFERENCE 1808`; CPU/elapsed
34.50/34.66 seconds (dual hashing, not a speed benchmark).
Separate optimized-only OPTSHA baseline remains 19.29/19.42 seconds.
Next: isolated native object persistence staging, preserving all
existing gates. Do not claim Git loose-object storage exists yet.

## Mandatory execution rule (2026-09-26)

Maximize useful autonomous work in every turn. Do not pause, request permission, or stop after an intermediate documentation/code step when more repository work can be completed independently. Stop only when actual CMS target validation is required; at that point provide exact Mac transfer and CMS test commands. Document completed work and target results in CHAT_STATE.md and docs/STATUS.md, follow all existing project rules, and never claim untested code is target-proven.

## 2026-09-26 Native STAGE gate prepared (CMS validation pending)

Commit `a2d1743` adds isolated `GITCWALK STAGE`. It runs the proven
PACK integrity, inflation, OFS reconstruction and optimized SHA-1
OID path, then writes all reconstructed objects to FILEDEF `OBJOUT`
as CMS text records. Each object has a header `OBJ index type length
40-hex-OID`, followed by uppercase hex body lines of up to 32 bytes
(64 characters) per record; empty bodies get a blank record. This is
an intermediate validated staging format, NOT Git loose-object storage.
All prior GITCWALK modes remain available. C source max line 72 chars.
CMS compilation, FILEDEF record behavior, and spool correctness have
NOT yet been target-validated. To test: Mac git pull; upload absolute
path `/Users/mikewommack/ibm-sandbox/src/GITCWALK.C` using existing
cms-upload.sh. CMS: `FILEDEF PACKIN DISK GITPBUF PACK A`,
`FILEDEF OBJOUT DISK GITSTAGE DATA A`, `GITCLNK GITCWALK`,
`GITCWALK STAGE`. Expected final `STAGED OBJECTS 1808`; inspect
`LISTFILE GITSTAGE DATA A` and first/last records after success.
Keep #2 open until persistence and REF_DELTA support are addressed.

## 2026-09-26 STAGE open failure and next isolated CMS gate

User's initial CMS `GITCWALK STAGE` successfully checked PACK SHA-1
`8C92E274ECA84B797F8925A6082915DD6CCDE196`, inflated all
1,808 objects, applied all 1,117 OFS_DELTA instructions, computed
all 1,808 OIDs, and reached the expected final offset 340,007.
Writing failed: `DMSSOP036E Open error code 4 on OBJOUT`,
`STAGE WRITE FAIL`, CMS RC 8, CPU/elapsed 19.30/19.51 seconds.
`LISTFILE GITSTAGE DATA A` confirmed no file exists. No staging
persistence was demonstrated.

IBM FILEDEF documentation confirms open error 4 on new output if both
LRECL and BLKSIZE are unspecified. Initial FILEDEF lacked both.
For the next test, compile FIRST and then define the output:
`FILEDEF OBJOUT DISK GITSTAGE DATA A (RECFM V LRECL 80`.
Reissue `FILEDEF PACKIN DISK GITPBUF PACK A` after compilation.
Reference: https://www.ibm.com/docs/en/zvm/7.3.0?topic=commands-filedef

Commits `fa7052d` (buffer hex into <=64-char body records),
`0806eb0` (independent `VERIFY` and memory-only `BADSTG` gates),
and `04be7ee` (stage progress every 256 objects and error position)
are committed to main. Source is <=72 columns; CMS compile and the
new write/readback modes have not yet been target-tested. Details
and exact commands are in `docs/NATIVE_STAGE.md` (commit `faf7b05`).
Next target test: git pull and transfer absolute-path GITCWALK.C,
`GITCLNK GITCWALK`, FILEDEFs above, `GITCWALK STAGE`,
`LISTFILE GITSTAGE DATA A`, `GITCWALK VERIFY`,
`GITCWALK BADSTG`. Expected: `STAGED OBJECTS 1808`,
`STAGE VERIFIED OBJECTS 1808`, and
`PASS BADSTG: ALTERED BODY REJECTED`.

GitHub issue #2 was retitled to native PACK object persistence and
REF_DELTA support, remains open. Issue #5 remains open for durable
stunnel startup. Do not pause for permission when repository work can
proceed; stop for necessary CMS validation only.

Source review caught an EBCDIC portability hazard in the new stage
code: literal numeric byte 10 is not a portable C newline on CMS.
Commit `f895939` replaces numeric delimiter constants with proper
`'\\n'`/`'\\r'` character escapes before any CMS write/readback test.

## Host-side independent regression gate (2026-09-26)

The host-only test `tests/native_stage_host.c` and its shell runner
`tests/run-native-stage-host.sh` compile `GITCWALK.C` as C89, stage
1,808 synthetic objects, read back and rehash every record, pass a
non-destructive in-memory corruption gate, demonstrate detection of an
actual corrupted disk record, restore the record, and pass readback
again. The runner independently checks Git's native `git hash-object`
result for `blob 3\\0abc`: `f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f`.

GitHub Actions workflow `.github/workflows/native-stage.yml` run
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36271371785
completed successfully. Its job logs show `STAGE VERIFIED OBJECTS 1808`,
`PASS BADSTG: ALTERED BODY REJECTED`, detection of disk tamper, and
`HOST STAGING AND GIT OID TEST PASSED`. These are HOST tests with
synthetic data, NOT CMS target proof or real-PACK staging proof.

Source code and stage test commands in `docs/NATIVE_STAGE.md` remain
a CMS validation gate. Do not stop for non-CMS repository tasks; only
request the real CMS compile/run when needed.

## 2026-09-26 max-autonomy follow-on: native staged OID index and GET

Mandatory work rule: maximize independent repository work each turn;
do NOT stop after intermediate implementation or docs if other repo
work remains. Stop only for actual CMS target validation. No background
work is promised. This rule and all prior project rules remain active.

After the failed CMS STAGE attempt (`DMSSOP036E` output open error 4),
the staging code got explicit CMS-output FILEDEF guidance and HOST
verification; target STAGE/VERIFY/BADSTG still require a CMS run.
Additional independent work completed before stopping:

- `src/GITCIDX.C` is a separate bounded C89 program; BUILD reads
  exactly 1,808 staged descriptors and checks every bounded hex body,
  sorts binary 20-byte OIDs, normalizes matching duplicates, rejects
  conflicting duplicates and writes a versioned CMS text OID index
  with a mandatory END trailer.
- CHECK rejects malformed, unsorted, duplicated, truncated and extra
  index records. FIND validates the index and binary-searches an OID.
- GET validates the index, walks STGIN to the indexed object, strictly
  parses records, recomputes canonical Git SHA-1 over the selected
  staged body with its own C89 implementation and rejects a mismatch.
  Success reports metadata and a bounded 16-byte hex prefix. This is
  a prototype retrieval path, NOT a committed loose-object database.
- `tests/native_index_host.c` exercises 1,808 synthetic objects,
  duplicate normalization (8 unique synthetic OIDs), positive/negative
  indexed lookup, independently hashed GET, valid-hex body corruption,
  malformed stage hex, malformed index entry, incomplete trailer and
  restoration. The host runner compares C SHA-1 to Git's own
  `git hash-object` for commit/tree/blob/tag on both empty and
  three-byte bodies.
- CI passed https://github.com/mostangrymike/ibm-sandbox/actions/runs/36271873734
  for expanded GET/tamper tests and
  https://github.com/mostangrymike/ibm-sandbox/actions/runs/36271801328
  for all-four-type Git OID cross-check.
- The procedures and source format are documented in
  `docs/NATIVE_STAGE.md` and `docs/NATIVE_INDEX.md`; README updated;
  issue #2 updated but must remain open. Issue #5 also remains open.

Next ONLY CMS-dependent gate: Mac git pull and existing cms-upload.sh
absolute-path upload BOTH `src/GITCWALK.C` and `src/GITCIDX.C`.
On CMS compile `GITCLNK GITCWALK` and `GITCLNK GITCIDX`
BEFORE output FILEDEFs; define PACKIN, OBJOUT with
`FILEDEF OBJOUT DISK GITSTAGE DATA A (RECFM V LRECL 80`,
STGIN, IDXOUT with
`FILEDEF IDXOUT DISK GITINDEX DATA A (RECFM V LRECL 80`,
and IDXIN. Run GITCWALK STAGE, VERIFY, BADSTG; GITCIDX BUILD, CHECK,
FIND and GET against known first/last captured OIDs. Full commands
are in docs/NATIVE_INDEX.md. No new live GitHub POST needed.
Do NOT claim CMS staging, CMS indexing, or real-PACK GET proven until
user sends successful actual target output.

## 2026-09-26 CMS target proof: staged readback and full unique index

Target logs from user, no repeated live POST:
`GITCLNK GITCWALK` built with no assembler flags (4.78/5.01 s).
`GITCLNK GITCIDX` built with no assembler flags (2.47/2.59 s).
Issuing `FILEDEF OBJOUT DISK GITSTAGE DATA A (RECFM V LRECL 80`
after compilation fixed the original OBJOUT open error 4.
`GITCWALK STAGE` verified PACK SHA-1
`8C92E274ECA84B797F8925A6082915DD6CCDE196`;
1,808 PACK objects, 1,117 OFS_DELTA applied and all 1,808 optimized
OIDs computed; final offset 340,007. `STAGE WRITTEN` checkpoints
256,512,768,1024,1280,1536,1792; `STAGED OBJECTS 1808`.
CPU/elapsed 24.89/25.32 s. `GITCWALK VERIFY`: independent readback
and rehash of all 1,808 staged bodies passed, including first
5A81BAF86E7DC7B72377087A8F160CAF8B889B74 and last
BA9F4D66B41352F0D0266090D14AD52F37318FCB; 22.64/22.84 s.
`GITCWALK BADSTG`: `PASS BADSTG: ALTERED BODY REJECTED`,
0.01/0.01 s, stages unaffected. `GITCIDX CHECK` printed
`INDEX VERIFIED 1808 UNIQUE 1808`, 0.13/0.14 s. The posted
log did not include `GITCIDX BUILD` itself; CHECK establishes
that a complete and valid 1,808-unique-object index exists, without
claiming BUILD timing. `GITCIDX GET` successfully rehashed first
OID, returning OBJ 1 TYPE 1 SIZE 270 (0.13/0.14 s), and last OID,
returning OBJ 1808 TYPE 2 SIZE 5224 (7.49/7.59 s). Console
line for PREFIX was truncated on capture; full prefix not asserted.
GET cost grows with the target's staging-file ordinal because
GITCIDX scans staged preceding records. Next optimization:
experiment with separate offset/seek index mode without replacing
the target-proven original; target CMS `ftell/fseek` on variable
records MUST be validated before trusting random access.

This is real CMS target proof for reconstructed staging, independent
readback, non-destructive negative gate, valid unique index and
GET from both ends of the real captured PACK. It is NOT committed
generation/restart proof, full per-OID independent cross-Git hash
verification of actual captured data, or native REF_DELTA support.
Keep issue #2 open and continue autonomous repository work until
actual CMS validation of next isolated experiment.

## 2026-09-26 follow-on: host-verified AUDIT and experimental SGET

Actual CMS STAGE, VERIFY, BADSTG, INDEX CHECK and first/last GET
passed on the captured real PACK as recorded immediately above.
The record is **1,808 unique native-indexed OIDs**, all reconstructed
bodies independently rehashed on CMS. Last sequential GET elapsed
7.59 s versus first GET 0.14 s; GET walks preceding staged records.

Autonomous follow-on committed:
- `GITCIDX AUDIT`: read proven V1 index, scan all 1,808 staged
  bodies, independently recompute each Git OID, reconcile header
  type/size/index earliest ordinal and check all unique index OIDs
  are represented; fails on malformed/stale/truncated data.
- Separate experimental `GITCIDX SBUILD` / `SCHECK` / `SGET`.
  SBUILD collects ftell tokens for each staged header and stores a
  binary-OID-sorted index with an SIDX1/SEND version and completeness
  trailer. SCHECK validates entire seek index. SGET uses fseek on a
  freshly reopened STGIN and hashes the actual selected body before
  returning. Old V1 BUILD/CHECK/GET remain unchanged. New file is
  `GITSEEK INDEX A` through FIDXOUT/FIDXIN, never overwrite V1
  `GITINDEX DATA A`. CMS ftell/fseek across file reopen is NOT
  target-proven; fail closed if unavailable.
- Host tests for 1,808 synthetic objects, AUDIT, negative stage
  corruption, synthetic duplicate normalization, direct SGET,
  stale-body hash rejection, and incomplete seek trailer passed:
  https://github.com/mostangrymike/ibm-sandbox/actions/runs/36272574127
  . All four canonical type hashes against Git on empty and
  nonempty fixtures were already CI-proven.

Current only target-dependent checkpoint, without rerunning STAGE:
Mac `git pull` then upload absolute-path `src/GITCIDX.C` with
existing `cms-upload.sh`. CMS `GITCLNK GITCIDX` BEFORE FILEDEFs;
`FILEDEF STGIN DISK GITSTAGE DATA A`;
`FILEDEF IDXIN DISK GITINDEX DATA A`;
`FILEDEF FIDXOUT DISK GITSEEK INDEX A (RECFM V LRECL 80`;
`FILEDEF FIDXIN DISK GITSEEK INDEX A`.
Run `GITCIDX AUDIT`, `GITCIDX SBUILD`,
`GITCIDX SCHECK`, then `GITCIDX SGET` for first OID
5A81BAF86E7DC7B72377087A8F160CAF8B889B74 and last OID
BA9F4D66B41352F0D0266090D14AD52F37318FCB. Compare latter
elapsed with old sequential GET 7.59 s. Commands fully documented
in `docs/NATIVE_INDEX.md`. Next native REF_DELTA and recoverable
generation storage not yet implemented; issue #2 remains open.

Mandatory user rule remains: maximize independent work every turn,
pause only for actual CMS validation, follow all project rules.

## 2026-09-26 CMS compiler EXEC migration: neutral name and GCC F

User requested no unnecessary pauses and the existing C compiler
wrapper renamed to a non-Git name on the same F disk as GCCCMS.
Canonical repository build wrapper is now `src/CMSCLNK.EXEC`
(commit `6dbc8a4`); original `src/GITCLNK.EXEC` removed from
the repository in commit `83c1e419`, while existing CMS A-disk
`GITCLNK EXEC A` is preserved as a target-proven rollback until
the replacement is actually installed and tested. Do NOT erase the
existing old A-disk wrapper before verifying the new F-based build.

`CMSCLNK name [NAPI|PLAIN]`: defaults to NAPI and preserves
the proven GCCE C A NOASM STD380, generated source ASSEMBLE,
GITCAPI/GITINFA assembly, PDPCLIB LOAD, and GENMOD sequence.
New optional PLAIN compiles/assembles/loads ordinary C modules
without Git-specific native inflater adapters. This is designed
as a reusable GCCCMS build tool, unlike the historical name.
It uses source files on A even when CMSCLNK resides on F.
Source fixed-card max 63 columns, filename under eight chars.
CI static validation of script structure, preserved native
link sequence and documented F installation passed
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36273033118
. The CI cannot validate the REXX script on actual CMS.

F writability has not been observed. IBM-documented `QUERY DISK F`
reports R/W or R/O, and `COPYFILE CMSCLNK EXEC A CMSCLNK EXEC F`
moves a copy only if F is R/W. Canonical Mac upload uses the one
existing c3270: git pull, then cms-upload.sh absolute paths for
CMSCLNK.EXEC and current GITCIDX.C. If F is writable, use COPYFILE
and STATE CMSCLNK EXEC F, then erase only CMSCLNK EXEC A after
successful copy (so program search resolves F). If F is R/O, leave
the new A-disk copy usable temporarily: do not attempt unauthorized
remount or modify GCC disk; authorized write access is required
for requested final F placement.

Actual next CMS validation combines F placement, a new PLAIN build
of GITCIDX, and host-proven AUDIT and experimental SBUILD/SCHECK/
SGET using previously target-proven GITSTAGE DATA A and existing
GITINDEX DATA A. The experimental seek index is a DIFFERENT
GITSEEK INDEX A file; never overwrite the proven V1 index.
Compare last-object SGET elapsed to V1 GET 7.59 s.
Detailed exact Mac and CMS commands are in docs/NATIVE_INDEX.md
and docs/BUILD.md. No new network PACK POST or restaging needed.
Maintain all other project rules and maximize independent work;
pause only for genuine CMS target validation.

## 2026-09-26 F-disk status supplied by user

Live CMS `Q DISK` result: GCCLIB virtual disk 29D is accessed as
F **R/W**, with 20 cylinders, 4,096-byte blocks, 38 files,
1,545 blocks used and **2,055 blocks free** (3,600 total).
No ACL/minidisk remount or permission request is needed for
neutral GCC compiler EXEC placement. After uploading canonical
src/CMSCLNK.EXEC to A using the existing Mac c3270 uploader,
run `COPYFILE CMSCLNK EXEC A CMSCLNK EXEC F`, verify with
`STATE CMSCLNK EXEC F`, then `ERASE CMSCLNK EXEC A` only on
successful copy/verification. Keep existing `GITCLNK EXEC A`
rollback until `CMSCLNK GITCIDX PLAIN` builds on actual CMS.
After compiling, independently run GITCIDX AUDIT and isolated
SBUILD/SCHECK/SGET with existing GITSTAGE DATA A, GITINDEX DATA A
and separate GITSEEK INDEX A. Existing index must not be overwritten.
Target validation has not yet been reported; do not claim installation,
PLAIN compiler execution, AUDIT or the seek experiment passed.

## 2026-09-26 CMS target proof: AUDIT and direct seek

User CMS output: `GITCIDX AUDIT` printed `AUDIT VERIFIED 1808 UNIQUE 1808`, CPU/elapsed 20.96/21.09 seconds. `GITCIDX SBUILD` wrote 1,808 unique entries in 7.13/7.21 seconds. `GITCIDX SCHECK` verified all 1,808 unique entries in 0.14/0.15 seconds. `GITCIDX SGET` on OID `5A81BAF86E7DC7B72377087A8F160CAF8B889B74` returned object #1, commit (type 1), 270 bytes, in 0.15/0.15 seconds. `SGET` on OID `BA9F4D66B41352F0D0266090D14AD52F37318FCB` returned object #1808, tree (type 2), 5224 bytes, in 1.72/1.77 seconds. Previous original indexed sequential GET for last object elapsed 7.59 seconds; direct SGET last object was 4.29x faster, elapsed reduction ~76.7%, single runs. The source output prefix is truncated by terminal capture and not independently asserted. The successful separate runs establish CMS `ftell` positions saved during SBUILD can be reused by `fseek` after reopening STGIN from another invocation for this unchanged staging file. NO reboot or modified-stage cookie lifetime proof. The leading `Ready; T=3.41/3.56` in user's paste has no associated preceding command. Therefore CMSCLNK F installation and PLAIN mode may have succeeded, but the visible transcript does not independently identify or prove that command. Do not mark F-based compiler placement proven until explicit `STATE CMSCLNK EXEC F` and a labeled build result are available.

Full stage + original index + new AUDIT + direct seek are target-proven for the captured PACK. Next independent development: native backward REF_DELTA resolution and bounded synthetic tests, while preserving current target-proven modes and staging/index files. User rule: maximize work per turn; only pause when actual CMS validation becomes necessary.

## 2026-09-26 target-proven direct seek; host-proven backward REF_DELTA

Latest user CMS output: `GITCIDX AUDIT` verified 1,808 stored objects and
1,808 unique index entries (20.96 CPU/21.09 elapsed seconds).
`SBUILD` wrote an independent 1,808-unique seek index
(7.13/7.21 seconds); `SCHECK` passed (0.14/0.15 seconds).
`SGET` succeeded across separate CMS invocations and file reopen:
first captured commit OID `5A81BAF86E7DC7B72377087A8F160CAF8B889B74`,
object 1/type 1/270 bytes at 0.15/0.15 seconds; last captured tree
OID `BA9F4D66B41352F0D0266090D14AD52F37318FCB`,
object 1808/type 2/5,224 bytes at 1.72/1.77 seconds.
Original V1 sequential `GET` took 7.49/7.59 seconds for that last
object. The one-run last-object direct-seek improvement is 4.29x,
about 76.7% lower elapsed time. This proves ftell/fseek cookies
persist across a new invocation on the **unchanged** STGIN file;
not across disk mutation or reboot. Console output prefixes were
truncated, so no complete prefix was asserted. Leading user
`Ready T=3.41/3.56` has no associated command; do not assume
CMSCLNK F installation/PLAIN build was proven. F disk was already
confirmed R/W in earlier `Q DISK` output.

Continued autonomous development after these target results.
`src/GITCWALK.C` now supports bounded backward same-PACK native
REF_DELTA resolution by reconstructed base OID and proper inherited
object type, including chained REF_DELTA. In OFSAPPLY path, base OIDs
are computed on demand when first needed; zero-REF captured PACK
retains its existing behavior. Unresolved, forward or external
bases fail closed rather than accessing uninitialized objects.
New `RTEST` in-memory chain/negative gate, `RPACK` bounded
variable-length synthetic PACK integration mode, and `RAPPLY`
no-prehash gate; no change to saved GITPBUF/STAGE/IDX files.
`tests/make-native-ref-pack.py` creates CMS 64-char ASCII hex
positive REFPACK plus REFBAD/REFFWD/REFSIZE/REFSHA negatives.
`tests/native_ref_pack_host.c` substitutes zlib only for CMS
inflater. Git's own `git index-pack --stdin` and `git cat-file`
independently accept/reconstruct all 3 reference fixture blobs
(abc, abcd, abcde); expected OIDs match Git hash-object.
Positive fixture ends at offset 94, 2 REF deltas; negative missing,
forward, malformed delta base size and bad trailer all rejected.
Full latest host CI passed:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36274025088 .
Actual updated REF C code and fixture tests NOT YET CMS-validated.
Complete concise Mac/CMS test instructions in `docs/NATIVE_REF.md`.
Do not rerun network POST or overwrite 1,808-object real PACK.
Still missing native external/forward REF base resolution and
recoverable store/restart proof; leave GitHub issue #2 open.

Rule: maximize independent work each turn; pause only for genuine
CMS validation. Preserve source max 80 columns, current compiled
CMS modules, single Mac c3270 uploader, and protected stage/index.

## 2026-09-26 confirmed CMS EBCDIC canonical OID bug and fix

User target: `CMSCLNK GITCWALK` NAPI compiled cleanly (5.10 CPU /
5.33 elapsed seconds). Original `GITCWALK RTEST` printed a false-pass
non-Git SHA-1 of `0414AADE456A43A390C3A0E689DD2CDE0439DAA7`.
The valid transferred synthetic REF PACK (114 bytes, checksum
9CD9B4CCFA5D5371C608230D3157F4766248355F) decoded blob ABC
with correct zlib return and 11 consumed bytes, but computed OID
5492DC378EC7097F3437B18BE17F4C58D0923A03 rather than Git's
F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F; both RPACK/RAPPLY
failed `UNRESOLVED REF BASE OBJ 2` with RC8. Verified exactly:
CMS code's sprintf built a **CP037 EBCDIC** header
`8293968240F300` for blob3; SHA-1 of that header plus ASCII
`616263` exactly equals erroneous 5492DC... . Git requires
raw ASCII header `626C6F62203300`; SHA-1 of header plus
`616263` is F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F.
Old RTEST also used native EBCDIC character constants for its body,
explaining old 0414AA... rather than Git's correct ABCDE SHA-1
6A8165460570531A1247BD99A73B53A5A6E500D5.

Current repo FIXES BOTH programs, not just REF lookup:
- GITCWALK canonical_head and GITCIDX idx_head use explicit raw ASCII
  type name, 0x20 separator, 0x30+decimal-digit and NUL 0x00
  before appending raw object body. No native-text sprintf for Git
  object hashing. Both regular and optimized SHA-1 use fixed header.
- RTEST uses ASCII byte constants for ABC, D and E and directly
  validates the known Git ABC and ABCDE digests. GITCIDX SELF checks
  the known Git ABC digest without any staging file.
- New IDX2/SIDX2 reader/writer formats plus END2/SEND2 explicitly
  REJECT incompatible historical IDX1/SIDX1 indexes; host negative
  regressions prove rejection.
- New GITCIDX SVAUDIT independently reopens and SHA-1-checks every
  stored direct-seek cookie, with progress each 256 entries.
- Source-guard CI enforces no native sprintf Git header.
- All host code and tests pass, including independent Git-generated
  fixture and complete 1,808 synthetic stage/index and seek-audit
  tamper/legacy-version tests:
  https://github.com/mostangrymike/ibm-sandbox/actions/runs/36274871780 .
  Static ASCII/CMS source guard CI also passed:
  https://github.com/mostangrymike/ibm-sandbox/actions/runs/36274777916 .

CRITICAL: The earlier CMS 1,808-object OID parity and STAGE/VERIFY/
AUDIT/SGET results were internally consistent but all shared the
same EBCDIC canonical header bug. These runs prove raw PACK checksum,
decompression, OFS reconstruction, bounded CMS files and real fseek
behavior, NOT Git-compatible object identities. Mark all historical
GITSTAGE DATA A, GITINDEX DATA A (IDX1), GITSEEK INDEX A (SIDX1) as
LEGACY, never as production Git object store. Preserve legacy files;
do not overwrite or erase them until correct replacement validated.
The captured GITPBUF PACK A binary is still valid and needs NO
new GitHub download. Inspected older REXX GITBOID/GITOID already
construct ASCII headers as literal HEX and do not share this C flaw.
Do not fabricate corrected first/last OIDs for the real captured
PACK before the updated C source computes them on CMS.

Next actual CMS-dependent gate only: Mac git pull then upload updated
GITCWALK.C and GITCIDX.C via existing cms-upload.sh. Existing REFPACK
PACK A already transferred and checksum-validated; no retransmission.
Compile CMSCLNK GITCWALK and CMSCLNK GITCIDX PLAIN BEFORE FILEDEFs;
run GITCWALK RTEST, GITCIDX SELF; set PACKIN REFPACK PACK A,
run GITCWALK RPACK and RAPPLY. Expect known Git ABC/ABCD/ABCDE
OIDs, 3 objects, 2 REF DELTAs, no missing base, and correct PACK
checksum. When these pass, rebuild the existing captured PACK
OFFLINE into distinct GITFIX STAGE A, GITFIX INDEX A and
GITFIX SEEK A (IDX2/SIDX2); run STAGE, VERIFY, BUILD, CHECK,
AUDIT, SBUILD, SCHECK and SVAUDIT without touching legacy files.
New complete commands in docs/CANONICAL_OIDS.md. Corrected C code,
new indexes and SVAUDIT are HOST-proven only, NOT CMS-proven yet.
CMSCLNK NAPI compilation is target-proven; F disk is confirmed R/W,
but physical installed EXEC F state and CMSCLNK PLAIN test remain
unverified until labeled target output is seen.

Observe mandatory max-work-per-turn rule: no pause except for
actual CMS target validation. Keep issue #2 open for correct OID
migration, forward/external REF and durable generation/recovery.

### Latest canonical OID host gate

Final host CI run https://github.com/mostangrymike/ibm-sandbox/actions/runs/36275050558 succeeded after adding an explicit GITCIDX SELF invocation to host regression. Its logs include correct `CANONICAL ABC OID F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F`, `INDEX CANONICAL ASCII ABC PASSED`, successful backward REF PACK Git checks, and full `SEEK AUDIT VERIFIED UNIQUE 8` with corruption rejection. The complete safe CMS retest plus IDX2 migration procedure and expected markers are in docs/CANONICAL_OIDS.md. Main remains GitHub canonical; corrected code is HOST-proven and requires the real CMS retest before production use.

## 2026-09-26 18:42–18:43 CDT: corrected ASCII and REF target gate PASSED

User supplied the complete real CMS output: `GITCWALK RTEST`
printed `CANONICAL ABC OID F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F`
and `REFTEST OID 6a8165460570531a1247bd99a73b53a5a6e500d5`,
then `REF BACKWARD CHAIN AND NEGATIVE TESTS PASSED` (0.01 CPU /
0.02 elapsed). `GITCIDX SELF` printed
`INDEX CANONICAL ASCII ABC PASSED` (0.01/0.01).
With `FILEDEF PACKIN DISK REFPACK PACK A`, `GITCWALK RPACK`
verified PACK SHA-1 `9CD9B4CCFA5D5371C608230D3157F4766248355F`,
114 bytes and 3 objects; OBJ 1 blob abc OID
F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F,
OBJ 2 REF_DELTA reconstructed blob abcd OID
85DF50785D62D3B05AB03D9CBF7E4A0B49449730,
OBJ 3 chained REF_DELTA reconstructed blob abcde OID
6A8165460570531A1247BD99A73B53A5A6E500D5,
`PASS 3 OBJECTS NEXT OFFSET 94`, OFS=0, REF=2,
OIDs=3, CMS 0.01/0.03. `GITCWALK RAPPLY` independently passed
all 3 objects and 2 REF deltas without normal OID output,
0.01/0.02. These are target-proven **correct Git canonical ASCII
OID hashing** for tested vectors and **backward same-PACK chained
REF_DELTA** (with normal and on-demand base OID paths).

No actual negative REFBAD/REFFWD/REFSIZE/REFSHA CMS runs were
included in this latest user transcript: the negative fixtures
remain host-tested only; do not mark them target-proven. Nor was
the corrected full captured 1,808-object PACK restaged on CMS.
Existing GITPBUF PACK A stays verified; old GITSTAGE DATA A,
GITINDEX DATA A (IDX1) and GITSEEK INDEX A (SIDX1) remain
legacy with noncanonical Git OIDs; keep all untouched.

The next CMS-only step is the **offline canonical migration**:
use existing GITCWALK and GITCIDX binaries and existing
GITPBUF PACK A; create NEW GITFIX STAGE A (RECFM V LRECL 80)
and run GITCWALK STAGE/VERIFY, then new GITFIX INDEX A
(IDX2) BUILD/CHECK/AUDIT and GITFIX SEEK A (SIDX2)
SBUILD/SCHECK/SVAUDIT. Do not recompile/transfer/re-download
unless an independent code change is needed. Use docs/CANONICAL_OIDS.md
for exact commands. Preserve old files and never infer corrected
first/last captured PACK OIDs from historical values.

User rule: MAX WORK PER TURN; do all independent GitHub code,
regression, docs, issue hygiene possible; pause only for genuine
CMS validation. Keep issue #2 open for target-proven canonical
migration, external/forward REF and generation recovery.

### Independent follow-on after CMS canonical REF success

Committed GITCIDX optional PAIR: load both canonical IDX2/SIDX2
indexes via IDXIN/FIDXIN, compare each sorted binary OID, ordinal,
type and size and then invoke SVAUDIT to reopen/re-hash every
referenced staged body from STGIN. PAIR reports
`PAIR VERIFIED UNIQUE 1808` on a valid complete canonical real-PACK
migration. It fails on stale/mismatched index descriptor or body
tampering; host synthetic regression deliberately mutates valid
SIDX2 descriptor and body, checks rejection, restores them, and
checks acceptance. Latest host CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36280431393 .
New PAIR code is NOT in the older GITCIDX binary already run by the
user; it is OPTIONAL for the initial canonical migration and would
need the latest GITCIDX.C uploaded and recompiled in a later CMS
gate. Do not make its availability a prerequisite to running the
already prepared full 1,808-object offline canonical STAGE/VERIFY,
BUILD/CHECK/AUDIT, and SBUILD/SCHECK/SVAUDIT commands. Those
original CMS modules and GITPBUF PACK A are already present. Docs:
docs/CANONICAL_OIDS.md and docs/NATIVE_INDEX.md. Issue #2 remains
open until corrected full real-PACK migration and later external/
forward REF plus generation recovery are target-proven.

## 2026-09-26 18:50–18:54 CDT: full canonical GITFIX rebuild passed except slow SVAUDIT

User supplied actual corrected 1,808-object offline migration output.
`GITCWALK STAGE` read unchanged GITPBUF PACK A: SHA-1
8C92E274ECA84B797F8925A6082915DD6CCDE196, 340,027 bytes,
1,808 objects, 1,117 OFS_DELTA applied, zero REF_DELTA, final
offset 340007, 1,808 Git-canonical OIDs computed; wrote new
GITFIX STAGE A. 25.16/25.58 seconds CPU/elapsed.
Canonical first commit #1 OID
00D8D63229305230C8D37F884CE87F9E1A89468C, type 1/270 bytes.
Object #2 blob 1841 OID
01FC0AF6E08B17016283D86F94320EE91CDEF0E0.
Object #3 tree 139 OID
039DFF056096A2239B7D7839DE12200104BADE33.
Last tree #1808 OID
EB37E3F23FF4FC137D715D71A711D3B7632D75F2,
type 2/5224 bytes. `GITCWALK VERIFY` independently read back
and rehashed all 1,808 new GITFIX stage records, including the
correct first/last OIDs, in 22.37/22.57 CPU/elapsed.

`GITCIDX BUILD` wrote GITFIX INDEX A, 1,808 UNIQUE in
6.86/6.94 seconds. CHECK twice verified 1,808 UNIQUE,
0.13/0.14 and 0.15/0.16. AUDIT independently verified
all staged bodies and 1,808 unique index entries in
20.86/20.99 seconds. `SBUILD` wrote the new SIDX2
GITFIX SEEK A, 1,808 UNIQUE in 7.29/7.39 seconds.
`SCHECK` verified all 1,808 UNIQUE in 0.14/0.15.
`SVAUDIT` printed `SEEK AUDIT PROGRESS 256` and
user reported stalled/slow. The transcript contains NO completion
marker/return code for SVAUDIT; do NOT claim target SVAUDIT passed.
There is no evidence of stage or index corruption: everything
up to the SVAUDIT invocation passed.

Source inspection diagnosed slow audit: old SVAUDIT invoked
sidx_get 1,808 times, each reopening/closing STGIN; this is
unnecessary and especially expensive on CMS variable records.
Independent fixes made in GitHub source after user's installed build:
1. Reusable sidx_read_at(FILE*,OID) primitive: normal SGET still
opens/closes its own stream, and SVAUDIT opens STGIN only ONCE,
then fseeks and rehashes all unique objects.
2. New `GITCIDX SFAST` reads STGIN sequentially once, rehashes
all 1,808 objects, cross-checks descriptor metadata and compares
each unique entry's saved ftell cookie to the actual reopened
stream position, requiring full SIDX2 coverage. This removes
both 1,808 repeated opens and 1,808 repeated random fseeks
while checking the real seek-cookie values.
3. `GITCIDX PAIR` compares complete IDX2 vs SIDX2 descriptor
sets then invokes SFAST, avoiding the expensive old SVAUDIT path.
Original separate SGET remains intact. Host regression asserts
SFAST, SVAUDIT and PAIR use only ONE STGIN fopen each, tests
1,808 synthetic staged entries, stale/mismatched indexes,
corrupted contents and recovery. Full CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36281295118 .
All new audit code is HOST-tested, NOT CMS target-validated yet.

For current user execution: If old SVAUDIT is still active,
CMS PA1 can interrupt its READ-ONLY work. The already complete
GITFIX STAGE/INDEX/SEEK files are unaffected; do not rerun
PACK STAGE or index BUILD. Next actual CMS gate is Mac git pull,
upload current absolute-path src/GITCIDX.C using the existing
single c3270 cms-upload.sh. CMS `CMSCLNK GITCIDX PLAIN` before
reissuing FILEDEFs. Define STGIN GITFIX STAGE A, IDXIN
GITFIX INDEX A, FIDXIN GITFIX SEEK A; run
`GITCIDX SFAST` (expected FAST AUDIT VERIFIED 1808 UNIQUE 1808),
`GITCIDX PAIR` (expected PAIR VERIFIED UNIQUE 1808),
`GITCIDX SGET 00D8D63229305230C8D37F884CE87F9E1A89468C`
and `GITCIDX SGET EB37E3F23FF4FC137D715D71A711D3B7632D75F2`.
Observe actual CMS elapsed for SFAST/PAIR; do not predict.
Keep old GITSTAGE DATA A, GITINDEX DATA A (IDX1), GITSEEK
INDEX A (SIDX1) as legacy snapshots. Preserve correct new
GITFIX files. After SFAST/PAIR target proof, continue with
external/forward REF and safe generation/reboot recovery;
issue #2 remains open. Mandatory max-work-per-turn rule active.

## 2026-09-26 19:06–19:07 CDT FILEDEF readiness

User's latest CMS transcript: `FILEDEF STGIN CLEAR`, `IDXIN CLEAR` and `FIDXIN CLEAR` each returned `DMSFLD704I Invalid CLEAR request`, consistent with no existing definitions to clear after previous compilation. Immediately afterward, `FILEDEF STGIN DISK GITFIX STAGE A`, `FILEDEF IDXIN DISK GITFIX INDEX A` and `FILEDEF FIDXIN DISK GITFIX SEEK A` all returned normal `Ready` without error. Required current input FILEDEFs are therefore set; do not repeat CLEAR, redefine, retransfer, rebuild the PACK, stage or index. Proceed directly to read-only `GITCIDX SFAST`, `GITCIDX PAIR`, and canonical first/last SGET using 00D8D63229305230C8D37F884CE87F9E1A89468C and EB37E3F23FF4FC137D715D71A711D3B7632D75F2. The successful FILEDEF definitions do NOT yet prove SFAST or PAIR completed. docs/CANONICAL_OIDS.md corrected to omit unnecessary CLEAR lines in the current target gate.

## 2026-09-26 19:06–19:09 CDT: full canonical stage/index pair VALIDATED

User's real CMS log confirms `CMSCLNK GITCIDX PLAIN` assembled without flagged statements and built GITCIDX MODULE (4.07 CPU/4.23 elapsed). STGIN/IDXIN/FIDXIN DD names were successfully defined to GITFIX STAGE/INDEX/SEEK A after harmless `DMSFLD704I Invalid CLEAR request` messages for no previous definition. `GITCIDX SFAST` printed progress at 256, 512, 768, 1024, 1280, 1536, 1792 and `FAST AUDIT VERIFIED 1808 UNIQUE 1808` in 20.85 CPU/20.99 elapsed seconds. `GITCIDX PAIR` repeated the complete sequential canonical SHA and seek-cookie audit and printed `PAIR VERIFIED UNIQUE 1808` in 21.24/21.38 s. First canonical SGET `00D8D63229305230C8D37F884CE87F9E1A89468C` returned OBJ 1 TYPE 1 SIZE 270 in 0.15/0.15 s; last SGET `EB37E3F23FF4FC137D715D71A711D3B7632D75F2` returned OBJ 1808 TYPE 2 SIZE 5224 in 1.76/1.81 s. Terminal output truncates the PREFIX, but both commands returned RC0. These real target runs establish correct canonical Git OID independent readback, full IDX2 and SIDX2 agreement, saved ftell-cookie matching and complete object SHA verification across all 1,808 objects on the unchanged stage, not crash/reboot recovery proof. Previously verified raw PACK SHA, all 1117 OFS_DELTA applications, STAGE, VERIFY, IDX2 BUILD/CHECK/AUDIT and SIDX2 SBUILD/SCHECK apply to the same GITFIX generation. Historical GITSTAGE/GITINDEX/GITSEEK are legacy noncanonical and must remain separate.

The original SVAUDIT was slow due to reopening every target. Current SFAST and PAIR on CMS use one sequential stage stream each and completed in ~21 seconds. The independent optional latest SVAUDIT one-stream optimization is only host-verified and no longer necessary. The current issue #2 stays open for external and forward REF_DELTA, committed-generation/restart/recovery, and use by higher-level Git client. Mandatory max-work-per-turn rule: keep developing independent repository tasks until actual CMS gate.

## 2026-09-26 19:09 onward: canonical IDX2/SIDX2 target gate PASSED

User supplied full target result: CMSCLNK GITCIDX PLAIN built successfully (4.07/4.23 sec CPU/elapsed). The three GITFIX input FILEDEFs succeeded; invalid CLEAR requests simply indicated no earlier definitions to remove. `GITCIDX SFAST` completed every checkpoint and `FAST AUDIT VERIFIED 1808 UNIQUE 1808` (20.85/20.99 s). `GITCIDX PAIR` repeated SFAST, compared all 1,808 canonical IDX2/SIDX2 descriptors and printed `PAIR VERIFIED UNIQUE 1808` (21.24/21.38 s). Direct SGET returned corrected first commit 00D8D63229305230C8D37F884CE87F9E1A89468C, OBJ 1 TYPE 1 SIZE 270 (0.15/0.15 s), and last tree EB37E3F23FF4FC137D715D71A711D3B7632D75F2 OBJ 1808 TYPE 2 SIZE 5224 (1.76/1.81 s). Both target GITFIX canonical stage and IDX2/SIDX2 indexes therefore fully reconciled across separate invocation/seek and SHA-1 rehash of all objects. This proves contents in the existing CMS generation, not atomic commit/reboot recovery. Historical IDX1/SIDX1 files remain noncanonical and separate. No more target validation needed for the original 1,808-object stage/index full audit.

Independent next code after this milestone: isolated GITCWALK XPACK/XAPPLY modes resolve an external REF_DELTA base from a separately FILEDEF'd CMS staged-object stream dd:EXTIN. It scans up to 1,808 bounded stage records, validates hex record grammar and rehashes the selected external object using canonical Git SHA before application, failing closed on absent or corrupt bases. Normal RPACK/RAPPLY/STAGE and existing GITFIX artifacts remain untouched. New deterministic generator creates positive XPACK.PACK + EXTBASE.DATA and missing/corrupt negative fixtures. Native host zlib adapter tests external resolution both in XPACK and XAPPLY plus absent/corrupt/unmatched base cases against Git hash-object. Latest CI success: https://github.com/mostangrymike/ibm-sandbox/actions/runs/36281897291 . THIS NEW FEATURE IS HOST-PROVEN ONLY, NOT RUN ON CMS. User's previous RPACK backward REF and the canonical GITFIX stage/index remain target-proven; issue #2 still open for new external/forward REF gate and durable generations. Mandatory max-work-per-turn rule remains in force.

## 2026-09-26 final target-proven IDX2/SIDX2 gate; host follow-on

Actual latest user CMS result: `CMSCLNK GITCIDX PLAIN` built
without assembler errors (4.07/4.23 s CPU/elapsed). STGIN,
IDXIN and FIDXIN were bound to GITFIX STAGE/INDEX/SEEK A.
An invalid CLEAR request on previously undefined names was
harmless; the three DISK definitions all succeeded.
`GITCIDX SFAST` completed full canonical SHA and ftell-cookie
validation: 1,808 unique entries, 20.85/20.99 s.
`GITCIDX PAIR` cross-checked all IDX2/SIDX2 descriptors
and repeated the full body audit: 1,808 unique, 21.24/21.38 s.
`SGET` independently retrieved correct canonical first commit
`00D8D63229305230C8D37F884CE87F9E1A89468C`
(OBJ1, TYPE1, 270 bytes, 0.15/0.15 s) and last tree
`EB37E3F23FF4FC137D715D71A711D3B7632D75F2`
(OBJ1808, TYPE2, 5,224 bytes, 1.76/1.81 s).
GITFIX canonical stage + both indexes are therefore fully
target-proven for this unmodified generation, including complete
readback, reciprocal descriptor agreement, and seek-cookie validation.
Do NOT repeat existing full PACK download, STAGE, BUILD or SBUILD.
Keep historical noncanonical GITSTAGE/IDX1/SIDX1 separate.

Following mandatory maximum autonomous work, GitHub gained:
(1) isolated GITCWALK XPACK/XAPPLY modes which scan FILEDEF EXTIN
CMS stage records (up to 1,808 bounded objects), locate an
external REF base by 20-byte canonical OID, strictly validate
hex grammar and independently recompute its canonical Git
SHA-1 before applying the delta. Short, duplicate, missing,
altered and mismatched bases are rejected;
(2) isolated GITCWALK FPACK which buffers unresolved forward
same-PACK REF deltas and resolves chained dependencies in
bounded passes after all objects have been inflated;
(3) separate GITCIDX GENWRITE/GENCHECK which runs full IDX2/SIDX2
PAIR and writes a versioned GEN2 manifest LAST, binding sorted
OID + ordinal + type + length + ftell cookies in a deterministic
canonical SHA digest. On later GENCHECK, a fresh read of GENIN
rejects malformed/truncated/extra records, reruns full PAIR,
and confirms every descriptor plus digest matches.
GEN2 is a candidate completion proof, NOT atomic promotion or
active-generation pointer. Reboot/logoff recovery not yet tested.

Host CI independently proved forward PACK through actual Git
index-pack and Git cat-file, external REF with one and multiple
stage records, full canonical SHA checks, tamper/duplicate/missing
negative gates, and the GEN2 synthetic 1,808-entry seal/reopen,
manifest corruption/truncation and stage/index tamper rejection.
LATEST GREEN:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36282493293 .
No new features above are yet target-validated on CMS.
Docs: docs/REF_RESOLUTION.md and docs/GENERATION_RECOVERY.md.
They provide exact Mac single-existing-c3270 uploader commands and
isolated CMS FILEDEF tests. Fixtures include XREAL.PACK, a thin
no-op copy of the known canonical first commit in GITFIX STAGE A
to prove lookup from the actual 1,808-object persisted store.

Remaining issue #2: target validation of new modes, thin PACK
external actual stage, cross-logon/reboot GEN2 verification,
atomic active-generation pointer and multi-file recovery, broader
OFS-on-unresolved-forward dependency support and production Git
client object-store integration. New source/fixtures must be
uploaded before the new CMS test; do not confuse host CI success
with CMS proof or modify existing GITFIX files.
Mandatory rule: keep autonomous work maximal; stop only when
real CMS target validation is required, with exact commands.

## 2026-09-26 19:36–19:40 CDT: FORWARD/EXTERNAL REF AND GEN2 PASSED ON CMS

User supplied real target logs. CMSCLNK GITCWALK NAPI compiled cleanly
(6.06/6.33 s CPU/elapsed); CMSCLNK GITCIDX PLAIN compiled cleanly
(4.49/4.65 s). FCHAIN PACK A: verified SHA-1
0F5F312E5E584C32B83488C4AEDF9D2786806884, 114 bytes, 3
objects. GITCWALK FPACK reconstructed #3 abc OID
F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F, resolved chained
forward REF #2 abcd OID 85DF50785D62D3B05AB03D9CBF7E4A0B49449730
then #1 abcde OID 6A8165460570531A1247BD99A73B53A5A6E500D5.
PASS 3 OBJECTS NEXT OFFSET 94; REF DELTAS APPLIED 2; 0.01/0.04 s.
XPACK PACK A with EXTBASE DATA A: raw PACK SHA
0E8A9DC1EE44EF42AC26CE3B81B4CC5519BA9A98, 67 bytes, 1
object; verified external blob type3 3 bytes, applied 1 REF to abcd
canonical OID 85DF50785D62D3B05AB03D9CBF7E4A0B49449730,
0.01/0.02 s. XREAL PACK A with EXTIN GITFIX STAGE A: PACK SHA
0D53A7E7F292475203B4E6F0C5E3D66837686B19, 68 bytes, 1
object; independently verified external *actual persisted* first
commit type1 270 bytes and delta-copy reconstructed the same canonical
OID 00D8D63229305230C8D37F884CE87F9E1A89468C; 8.05/8.17 s
(full stage scan). In this user log, standalone XAPPLY and EXTMULT and
four negative fixture tests were NOT included: do not label those
individual cases CMS-proven; host suite covers them.

GITCIDX GENWRITE against existing, unchanged 1,808-object GITFIX
STAGE A, INDEX A (IDX2) and SEEK A (SIDX2): full SFAST verified all
1,808 unique OIDs and cookies; PAIR verified both indexes, then
GENERATION SEALED 1808 UNIQUE 1808, total 21.41/21.56 s.
GENCHECK reopened the manifest through GENIN GITFIX GEN A and
repeated complete SFAST/PAIR audit with 1,808 unique objects,
then GENERATION VERIFIED 1808 UNIQUE 1808, 21.42/21.57 s.
This proves a sealed, self-consistent candidate-generation manifest
reopened in a separate program invocation in one CMS session, NOT
across logoff/reboot and NOT atomic active-generation promotion.
**Preserve existing GITFIX STAGE/INDEX/SEEK/GEN A and historical
legacy noncanonical GITSTAGE DATA/GITINDEX DATA/GITSEEK INDEX A.**
No more PACK capture or index rebuild. Issue #2 remains open for
cross-logon/reboot proof, atomic active-pointer/recovery, combined
forward OFS-on-unresolved-REF and higher-level native Git integration.

Next useful autonomous performance work: XREAL required 8.17 s to
scan all external staged records to independently reject duplicate
OIDs. Existing target-proven SIDX2 cookies enable a separately scoped
optional direct-seek external REF mode with cryptographic body
verification, leaving XPACK's conservative full scan intact.
Mandatory user max-autonomy rule: implement and host-test as much
as possible; stop only at actual CMS validation with exact commands.

## Follow-on host-proven XSEEK direct external REF lookup

After the target-proven FPACK, external XPACK from actual GITFIX stage,
and GEN2 seal/recheck, the real external first-commit XPACK full scan
was observed at 8.05/8.17 sec on CMS. Independently committed
optional GITCWALK XSEEK/XSAPPLY to use already validated SIDX2
GITFIX SEEK A from FILEDEF EXIDX and direct fseek on EXTIN
GITFIX STAGE A. Selected record ordinal, type, length and OID are
checked against the index and its complete body is independently
rehashed to the requested canonical Git OID before REF application.
This leaves all known-good XPACK and target GITFIX artifacts
unchanged. The new isolated modes have host tests for positive
synthetic first and later entry, corrupt stage, stale saved cookie,
and truncated SIDX2 index. Latest fully green host CI:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36283446044 .
Actual CMS compilation/running and performance still required.
Exact one-source Mac upload plus CMS test commands in
`docs/INDEXED_EXTERNAL_REF.md`: CMSCLNK GITCWALK first, then
PACKIN XREAL PACK A, EXTIN GITFIX STAGE A, EXIDX GITFIX SEEK A,
GITCWALK XSEEK and XSAPPLY. Require verified type1 size270 and
reconstructed canonical commit OID
00D8D63229305230C8D37F884CE87F9E1A89468C. No new PACK,
staging, indexes or GEN2 manifest writes needed. In a separately
requested read-only durability test, GITCIDX GENCHECK after user
logoff/logon must re-open and independently validate existing
GITFIX GEN A without GENWRITE. No such cross-logon/reboot result
yet exists.
