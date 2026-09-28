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

## 2026-09-27 10:09–10:10 CDT: XSEEK / XSAPPLY target proof PASSED

User's CMS transcript: CMSCLNK GITCWALK compiled NAPI successfully with 3 clean Assembler XF passes (6.44 CPU/6.72 elapsed sec). With PACKIN XREAL PACK A, EXTIN GITFIX STAGE A and EXIDX GITFIX SEEK A, GITCWALK XSEEK verified PACK SHA-1 0D53A7E7F292475203B4E6F0C5E3D66837686B19 (68 bytes, 1 object); printed EXTERNAL SEEK VERIFIED TYPE 1 SIZE 270; applied one external REF_DELTA to reproduce canonical first commit 00D8D63229305230C8D37F884CE87F9E1A89468C, PASS 1 OBJECTS NEXT OFFSET 48, REF DELTAS APPLIED 1, OBJECT OIDS COMPUTED 1. Runtime 0.17/0.19 sec CPU/elapsed. Independent GITCWALK XSAPPLY repeated verified external type 1 size 270 and applied one REF without ordinary object-OID output; PASS 1 OBJECTS NEXT OFFSET 48, 0.17/0.18 sec. Prior sequential XPACK on same real-stage commit took 8.05/8.17 sec in a separate run; these are observed runs, not a controlled benchmark. Existing validated GITFIX STAGE/IDX2/SIDX2/GEN2 unchanged. No user output for cross-logon or reboot durability yet; do NOT claim. New independent host source hardening/CI and active-generation work may proceed without re-running original PACK or existing CMS milestones.

September 27 independent follow-on: XSEEK's optional SIDX2 index reader now additionally rejects unsorted or duplicate OID records; host multi-record fixture generator emits sorted canonical SIDX2 entries and an unsorted negative fixture. Full existing regression suite passed https://github.com/mostangrymike/ibm-sandbox/actions/runs/36328763996 . The added hardening has NOT yet been CMS-compiled; preceding XSEEK/XSAPPLY indexed external lookup already passed on target, and no immediate replay of the earlier successful test is necessary. Remaining non-destructive target gate: after user-controlled logoff/logon rebind GITFIX STAGE, INDEX, SEEK and GEN to STGIN, IDXIN, FIDXIN, GENIN and run GITCIDX GENCHECK without GENWRITE. Cross-logon and reboot survival are not proven.

## 2026-09-27 10:20–10:21 CDT: GEN2 cross-logon survival PROVEN ON CMS

After an actual logoff and fresh CMS logon, the user successfully defined STGIN GITFIX STAGE A, IDXIN GITFIX INDEX A, FIDXIN GITFIX SEEK A and GENIN GITFIX GEN A. They ran only `GITCIDX GENCHECK`, without rewriting the stage, indexes, or GEN2 manifest. The existing program printed all SFAST progress checkpoints (256 to 1792), `FAST AUDIT VERIFIED 1808 UNIQUE 1808`, `PAIR VERIFIED UNIQUE 1808`, and `GENERATION VERIFIED 1808 UNIQUE 1808`, with normal RC 0, CPU 21.47 sec and elapsed 21.68 sec. This now conclusively establishes **same minidisk cross-logon CMS persistence** for this validated, unmodified full canonical 1,808-object candidate generation, including stage body integrity, both index descriptors, saved seek-cookie correspondence and manifest digest. It does NOT establish survival across an actual system restart or atomic active-generation promotion/multi-writer safety. Protect GITFIX STAGE/INDEX/SEEK/GEN A; no need to rerun GENWRITE or recapture the PACK. The next user-controlled, read-only durability gate, only when a regular system reboot is appropriate, is to reaccess the same A minidisk and reissue the four input FILEDEFs followed by GITCIDX GENCHECK. Concurrent with target work, independently design active-generation selection and interrupted-promotion recovery in GitHub, without claiming an untested atomic CMS file rename guarantee.

## 2026-09-27 response to unnecessary pause: active-generation work resumed

Existing target milestone: after actual CMS logoff/logon, GITCIDX GENCHECK independently rehashed and verified the unchanged GITFIX STAGE/INDEX/SEEK/GEN A, 1,808 unique objects and saved seek cookies, RC0 in 21.68 s elapsed. Reboot durability has NOT yet been tested. It must not block independent GitHub development or trigger an unnecessary immediate reboot.

New design docs/ACTIVE_GENERATION_DESIGN.md specifies immutable next-generation files, two checksummed selector slots, independent complete GENCHECK of each selected candidate, fail-closed startup recovery, old-slot rollback and no assumption of atomic CMS rename or file replacement. Host-only tests/active_generation_selector.py implements strict SEL1 two-slot records (version, uint32 sequence, uppercase CMS 1-8-character generation basename, 40-hex digest, CRC32 over canonical ASCII). It chooses the highest-sequence *fully validated* candidate via an injected check_generation callback, falls back to the prior slot when newer is corrupted/incomplete, and refuses contradictory same-sequence slots. tests/test_active_generation_selector.py tests every truncated prefix, corrupt checksum, invalid name/digest/sequence, bad candidate, missing slots, equal-sequence conflict and correct fallback. Wired into native-stage CI: FULL HOST PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36329760231 . This is ONLY A HOST EXECUTABLE SPEC, not native CMS selector, not automatic atomic promotion, not yet safe for real GITFIX data. Next autonomous work: native C89 selector parser and disposable generation/active-selection integration with real GENCHECK; target-only test when code and host failures are ready. Keep GITFIX original unchanged. No need to ask for user approval to continue ordinary GitHub code work.

September 27 further autonomous implementation: `src/GITSEL.C` is a strict native C89, EBCDIC-safe canonical ASCII CRC32 reader for the proposed SEL1 dual-selector slots. `GITSEL CHECK` opens dd:SEL0/dd:SEL1, validates checksums, version, filename and sequence grammar, rejects same-sequence conflicts and lists surviving candidate records as explicitly UNTRUSTED pending *real* GENCHECK of each candidate. It does not choose or promote any generation and does not write or reference protected current GITFIX files. `tests/test_native_selector.py` builds the actual source under C89 -Wall -Wextra -Werror and generates records via the independent Python executable spec; tests all truncated prefixes, corrupted checksums, malformed slots and conflict cases. FULL CI success https://github.com/mostangrymike/ibm-sandbox/actions/runs/36329974642 . New source is host-compiled only, not CMS-proven. Next engineering: integrate full GENCHECK-driven candidate selection, disposable selector slot writes and failure-injected recovery on host before CMS validation. Reboot persistence is separate user-controlled test and does not block this work. Detailed design docs/ACTIVE_GENERATION_DESIGN.md.

## 2026-09-27 autonomous M14 recovery implementation (HOST-TESTED)

The user correctly challenged another unnecessary pause. Reboot validation is separate and cannot block independent GitHub development. New `src/GITSEL.C` now has strict, bounded SEL1 WRITE support with byte-for-byte parity against the independent Python ASCII/CRC32 protocol, and a fail-closed SELECT callback seam (available in verifier-linked builds only). `src/GITREC.C` is a new read-only combined native C89 GITSEL + GITCIDX module. It binds each selector slot to **four separately FILEDEF'd candidate files**, requires that its GEN2 descriptor DIGEST matches the selector, then calls the actual full `gen_check()`, which rehashes the complete stage via SFAST, reconciles both indexes and verifies saved seek cookies/GEN2. The recovery selector attempts the newer complete candidate then a separately verified older fallback; rejects missing/altered data and spoofed slot/name mismatch and refuses ambiguous identical CLI names. It does NOT create an active pointer or write existing generation data. `tests/native_index_host.c` now tests the actual compiled GITREC binary on two isolated 1,808-record synthetic generation copies and injects corrupted new GEN2, corrupted new stage body, truncated new SIDX2, missing new IDX2, spoofed slot names and missing older manifest, with expected full-verification-based fallback and fail-closed behavior. `tests/test_native_selector.py` exercises truncated selectors, conflicting slot sequences, full-verification callback simulation and native SEL1 WRITE byte-for-byte parity/invalid-input rejection. All C89 modules compile under GCC with -Wall/-Wextra/-Werror and full existing native staging/REF integration CI passed: https://github.com/mostangrymike/ibm-sandbox/actions/runs/36330993480 (integrated recovery) and https://github.com/mostangrymike/ibm-sandbox/actions/runs/36330834919 (SEL1 writer). Follow-on current source and tests remain covered by native-stage workflow; consult latest run when needed.

**CMS gate is now genuinely required for this new code**, not for already-proven GITFIX integrity: isolated read-only `GITREC SELECT` uses existing protected GITFIX generation as older slot and disposable new SEL1 selector files only. Exact Mac single-existing-c3270 uploads, CMS compile, real GEN2 digest acquisition and nondestructive valid-old/invalid-new test are in `docs/NATIVE_RECOVERY_GATE.md`. The user must copy actual `DIGEST` value from `TYPE GITFIX GEN A`; DO NOT invent it, substitute commit OID or request original PACK re-download. This integration and CMS `#include "GITCIDX.C"`/`#include "GITSEL.C"` resolution are HOST-only verified pending actual target compile/output. Existing GITFIX STAGE/INDEX/SEEK/GEN A have already passed real CMS full audit and same-minidisk cross-logon recheck; keep untouched. Real reboot durability and atomic writer/promoter are still open; never claim active transaction semantics.

## 2026-09-27 continuing independent M14 safety work

Native read-only GITREC recovery integration already landed and passed host CI: https://github.com/mostangrymike/ibm-sandbox/actions/runs/36330993480 . It invokes actual full GITCIDX GENCHECK for each candidate using per-slot input FILEDEFs rather than trusting a selector checksum; it falls back to a separate fully verified old generation if new fails. The latest complete source was checked before further edits. The follow-up `src/GITSEL.C` selector writer now rejects an existing `dd:SELOUT` file before opening it for writing and returns RC 8 `SELECTOR OUTPUT EXISTS`, preventing accidental sequential overwrites of any existing slot. Native strict C89 tests confirm attempted rewrite leaves original selector bytes unchanged; full host integration CI green: https://github.com/mostangrymike/ibm-sandbox/actions/runs/36331581650 . This is a best-effort existence guard, NOT atomic create-if-absent or a concurrency lock. `docs/NATIVE_RECOVERY_GATE.md` updated with safeguard and exact next isolated CMS test. Existing canonical GITFIX STAGE/INDEX/SEEK/GEN A are still protected, with 1,808-object full integrity, indexed external REF and cross-logon GEN2 proof already target-complete. Actual GITREC CMS compile and read-only SEL0 valid old/SEL1 invalid new fallback is the next genuine target gate; original PACK/rebuild and an unnecessary reboot are not prerequisites.

2026-09-27 resumed autonomous M14 development: native `GITSEL.C` now has `WRITEGEN SEQUENCE BASENAME`, a safe untrusted selector creation path reading GEN2 DIGEST from existing `dd:GENIN` instead of requiring manual copy of a 40-hex digest. It validates complete five-record GEN2/DIGEST/MINOID/MAXOID/GEND2 syntax, matching completion counts, uppercase 40-hex fields and no trailing records, then uses the existing best-effort immutable new `dd:SELOUT` check and ASCII CRC32 SEL1 writer. THIS DOES NOT ATTEST DATA; read-only `GITREC SELECT` still requires actual full candidate `gen_check()` with SFAST/PAIR. `tests/test_native_selector.py` now runs positive generated-manifest derivation against independent Python SEL1 bytes, existing slot nonoverwrite and malformed/truncated/extra GEN2 rejection. Entire CI passed https://github.com/mostangrymike/ibm-sandbox/actions/runs/36332001510 . `docs/NATIVE_RECOVERY_GATE.md` now gives the simpler target commands: upload current GITSEL.C, GITREC.C and GITCIDX.C; compile GITSEL/GITREC PLAIN before FILEDEF; FILEDEF GENIN DISK GITFIX GEN A; create only new disposable GITSEL0/1 PTR A using GITSEL WRITEGEN 41 GITFIX and WRITEGEN 42 GITBAD; run GITREC SELECT GITFIX GITBAD. Preserve all protected original GITFIX files. The target CMS integrated recovery compilation and fallback remains outstanding: host CI cannot replace that genuine CMS runtime gate. Do not ask for user to copy DIGEST manually now. Continue independent code/host work where available; reboot validation is independent and does not block M14.

# NEW CHAT HANDOFF — 2026-09-27 (verified current repository)

When a new chat begins, read THIS LAST SECTION of CHAT_STATE.md,
docs/STATUS.md, docs/NATIVE_RECOVERY_GATE.md and project rules on
GitHub before touching code. Repo: mostangrymike/ibm-sandbox,
default main. Continue maximizing independent development; do not
pause to await reboot or ask to redo already successful CMS tests.

TARGET-PROVEN, PRESERVE UNCHANGED: In actual IBM z/VM 6.3 CMS under
Hercules, original 340,027-byte PACK SHA
8C92E274ECA84B797F8925A6082915DD6CCDE196 reconstructed
all 1,808 objects (1,117 OFS deltas) with correct ASCII Git OIDs.
Persistent files on CMS A: GITFIX STAGE A, GITFIX INDEX A (IDX2),
GITFIX SEEK A (SIDX2), GITFIX GEN A (GEN2). STAGE/VERIFY,
BUILD/CHECK/AUDIT, SBUILD/SCHECK, SFAST, PAIR and full GENWRITE/
GENCHECK all passed on real CMS. On September 27, after a
genuine logoff/new logon, existing GITFIX files were rebound and
read-only GITCIDX GENCHECK again returned
FAST AUDIT VERIFIED 1808 UNIQUE 1808,
PAIR VERIFIED UNIQUE 1808,
GENERATION VERIFIED 1808 UNIQUE 1808, RC0
(21.47 CPU/21.68 elapsed). Cross-logon persistence PROVEN;
power-cycle/reboot persistence NOT TESTED. Protect all GITFIX
files; never run GENWRITE again on existing GITFIX GEN A or
overwrite the stage/indexes. Old GITSTAGE DATA A, GITINDEX DATA A
(IDX1), GITSEEK INDEX A (SIDX1) are historical noncanonical.
Canonical first commit OID
00D8D63229305230C8D37F884CE87F9E1A89468C (270 bytes);
last tree EB37E3F23FF4FC137D715D71A711D3B7632D75F2
(5,224 bytes). FPACK forward chained REF, XPACK synthetic and
real external REF, XSEEK and XSAPPLY indexed actual external REF
all target-proven. XSEEK real commit 0.19 s vs old XPACK scan
8.17 s in separate runs. More recent optional XSEEK sorted-OID
hardening host-tested, not target-retested.

CURRENT M14 INDEPENDENT IMPLEMENTATION (HOST-PROVEN,
CMS VALIDATION STILL PENDING):
src/GITSEL.C: strict C89 EBCDIC-safe ASCII CRC32 SEL1 selector
reader, fail-closed two slots, WRITE and WRITEGEN SEQ BASENAME.
WRITEGEN derives the exact GEN2 DIGEST from input dd:GENIN,
validates full GEN2 manifest grammar, and writes a NEW disposable
record to dd:SELOUT; existing output nonoverwrite is a
best-effort guard, NOT atomic create-if-absent or writer lock.
src/GITREC.C: links actual GITSEL.C and GITCIDX.C directly,
uses real gen_check() with full SFAST/PAIR for each candidate,
maps independent four-file sets C0STG/C0IDX/C0SEEK/C0GEN and
C1STG/C1IDX/C1SEEK/C1GEN, confirms candidate identity/manifest
DIGEST before accepting, falls back to older verified candidate
on damaged newer slot. It is READ-ONLY recovery, NOT active
pointer promotion, atomic transaction or a reboot proof.
Current last complete main host CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36332001510
HEAD e3046c83467e6b91b54df20d49c78da81ea31d5e
(full native C89 selector, generated-manifest digest,
nonoverwrite/malformed/truncated extra-record rejection,
real GITREC and 1,808 synthetic object pair fallback,
native Git PACK stages). The actual source state in GitHub
supersedes older in-chat fragments; fetch before editing.
Issue #2 remains OPEN.

NEXT GENUINELY TARGET-DEPENDENT CMS TEST:
Docs docs/NATIVE_RECOVERY_GATE.md fully specify read-only
valid-old/invalid-new gate using only NEW disposable
GITSEL0 PTR A/GITSEL1 PTR A and protected GITFIX inputs.
On Mac in ibm-sandbox/src, git pull, upload latest
GITSEL.C, GITREC.C, GITCIDX.C using existing cms-upload.sh
and ONE existing c3270 (no second instance, no nc/socat).
On CMS compile BEFORE FILEDEF:
CMSCLNK GITSEL PLAIN
CMSCLNK GITREC PLAIN
TYPE GITFIX GEN A
Use FILEDEF GENIN DISK GITFIX GEN A and
FILEDEF SELOUT DISK GITSEL0 PTR A (RECFM V LRECL 80
GITSEL WRITEGEN 41 GITFIX
FILEDEF SEL0 DISK GITSEL0 PTR A
C0STG GITFIX STAGE A, C0IDX GITFIX INDEX A,
C0SEEK GITFIX SEEK A, C0GEN GITFIX GEN A.
GITREC SELECT GITFIX GITBAD should rehash every object
and print SELECTED 41 GITFIX with identical selector digest.
Then clear SELOUT ONLY IF ACTUALLY DEFINED, rebind to NEW
GITSEL1 PTR A and run GITSEL WRITEGEN 42 GITBAD using
the same GENIN GITFIX GEN A solely to create syntactically
valid but unverifiable newer selector. Define SEL1;
DO NOT define valid C1STG/C1IDX/C1SEEK/C1GEN.
GITREC SELECT GITFIX GITBAD must full-verify and print
RECOVERED 41 GITFIX (never SELECTED 42 GITBAD).
Detailed exact commands in docs/NATIVE_RECOVERY_GATE.md.
Before creating either selector ensure that file does not
already exist: if it exists use unused alternative names
and update FILEDEFs. If current main changes or a target
bug is discovered, fix source on GitHub, run CI, and
document accurately rather than declaring false target pass.

REMAINING INDEPENDENT WORK: native CMS target compile and
fallback gate above when user provides results; meanwhile
continue standalone GitHub engineering on disposable
interrupted-promotion tests and fail-closed selector hardening.
No need to reboot just for test; system reboot durability
later, with read-only GENCHECK only after an ordinary
authorized reboot. Do not claim atomic rename, locking
or concurrent write safety without actual proof.

LATEST CHAT REQUEST: user asked to save project state before
opening a new chat; this handoff is now committed. In new
chat pick up directly using these refs, re-fetch latest
GitHub status and proceed without asking to repeat past logs.

## M14 CMS checkpoint: September 27

GITSEL and GITREC both compiled PLAIN on CMS. Initial GITSEL WRITEGEN failed
with SELECTOR OUTPUT EXISTS despite absent PTR files: CMS lazy read-open
made the fopen guard unsuitable. GITREC could not select an unwritten slot.
The initial pasted commands also missed C0IDX definition. The existing
GITFIX stage/index/seek/GEN files remain the protected baseline.

GitHub adds WRITEGEN 41 GITFIX GITSEL0: explicit CMS STATE for a new PTR A
selector. Only missing RC 28 allows writing; existing RC 0 and every
other error fail closed. CMS runtime verification of this change is pending.
Recompile both GITSEL and GITREC after upload. Check STATE GITSEL0 PTR A;
if absent, write selector zero with the revised command, then bind SEL0
and every C0 input including C0IDX to the old canonical GITFIX data.
Require the full 1808-object GENCHECK and SELECTED 41 GITFIX. Do not
run GENWRITE or rebuild either canonical index.

## M14 dual-slot native CMS target evidence, September 27 12:19

GITSEL/GITREC PLAIN builds succeeded on CMS. GITRUN created
GITSEL0 PTR A (SEL1 seq 41 GITFIX) using REXX STATE RC28
and GITSEL WRITEGEN with ABSENT28 attestation. GITREC
verified all 1808 unique objects and selected seq 41 GITFIX
with digest 493F0896884B28AC4836B88328629B7E95404B46
and RC 0. Then GITRUN created GITSEL1 PTR A (seq 42
GITBAD), intentionally left all four C1 input DDs absent,
and full recovery rejected the new candidate and returned
RECOVERED 41 GITFIX with same 1808-object GEN2 audit and
RC 0 (elapsed 21.69s). Both M14 selection/fallback
native CMS gates PASSED. Four harmless invalid CLEAR
diagnostics resulted from trying to clear undefined DDs;
omit these on subsequent batches.

Preserve both existing selector files and all protected
GITFIX STAGE/INDEX/SEEK/GEN files. Do NOT rerun WRITEGEN,
GENWRITE, stage or index construction. Next GITRUN.EXEC
will be read-only: bind both selector inputs and the
four C0 data files, leave C1 absent, run GITREC SELECT.
Use after a normal fresh CMS logon, and optionally after
an authorized ordinary system reboot. Host-only interrupted
promotion design and atomicity/writer exclusion remain open.

## September 27 12:21 read-only dual-slot repeat audit

User ran the already-uploaded read-only GITRUN on CMS. Both STATE
checks passed for GITSEL0 and GITSEL1 PTR A. GITREC could not open
C1GEN for intentionally absent GITBAD, then fully audited the
original protected generation. Output: FAST AUDIT VERIFIED 1808
UNIQUE 1808; PAIR VERIFIED UNIQUE 1808; GENERATION VERIFIED
1808 UNIQUE 1808; RECOVERED 41 GITFIX
493F0896884B28AC4836B88328629B7E95404B46; GITRUN
RECOVERY RC 0. CPU 21.44s, elapsed 21.59s. User did not
explicitly confirm a logoff between the prior run and this
run; count this as read-only repeatability, not yet proof
of cross-logon selector survival. The original protected
GITFIX files and both selectors remain unchanged by GITRUN.
Next independent target durability gate is the same
read-only GITRUN after a confirmed ordinary logoff/logon,
or subsequently after an authorized normal VM reboot.
Do not force a reboot, rewrite selectors, or rerun GENWRITE.

## M14 next target gate: read-only identity rejection

Do not wait for reboot: continue independent work. The reusable
src/GITRUN.EXEC has been updated to bind both already-existing
GITSEL0/GITSEL1 PTR A slots and four protected C0 read inputs.
It first calls GITREC SELECT GITBAD GITFIX, intentionally
swapping expected generation names. The strict parser must
print SELECTOR SLOT 0 NAME MISMATCH and SELECTOR SLOT 1
NAME MISMATCH, then NO FULLY VERIFIED GENERATION and RC 8.
The EXEC treats this as the expected negative result; any
other RC aborts. It then calls the valid GITREC SELECT GITFIX
GITBAD, expecting complete 1808-object audit and RECOVERED
41 GITFIX DIGEST 493F0896884B28AC4836B88328629B7E95404B46
RC 0. This gate is pending actual CMS output, and no
source rebuild or selector write is necessary. Mac pull
and upload only GITRUN.EXEC, then run GITRUN once on CMS.

## September 27 12:26 M14 target identity gate PASSED

CMS GITRUN first invoked GITREC SELECT GITBAD GITFIX against
existing GITSEL0 seq41 GITFIX and GITSEL1 seq42 GITBAD.
It printed SELECTOR SLOT 0 NAME MISMATCH, SELECTOR SLOT 1
NAME MISMATCH, NO FULLY VERIFIED GENERATION, expected RC 8.
The same run then invoked proper GITREC SELECT GITFIX GITBAD,
reverified 1808 objects through full SFAST/PAIR/GENCHECK,
returned RECOVERED 41 GITFIX with digest
493F0896884B28AC4836B88328629B7E95404B46 and RC 0
(elapsed 21.84 seconds). Both selectors and protected GITFIX
stage/index/seek/GEN remain unmodified.

Reusable GITRUN.EXEC is now updated for the next independent
read-only negative gate: verify GITBAD GEN A is missing, bind
C0GEN to that missing input, require GITREC SELECT to fail
closed with RC 8, rebind C0GEN to protected GITFIX GEN A
and require full recovery with RC 0. Upload only the updated
GITRUN.EXEC after git pull; no C source change or rebuild.

## September 27 12:29 M14 missing-old-manifest gate PASSED

CMS GITRUN checked GITBAD GEN A absent (STATE RC28),
temporarily bound C0GEN to the nonexistent GITBAD GEN A
while maintaining SEL0 seq41 GITFIX and SEL1 seq42 GITBAD.
GITREC SELECT GITFIX GITBAD reported C1GEN and C0GEN open
errors, NO FULLY VERIFIED GENERATION, RC8. GITRUN then
restored C0GEN to protected GITFIX GEN A and reran the
complete 1808-object full audit. Result: RECOVERED 41
GITFIX digest 493F0896884B28AC4836B88328629B7E95404B46
RC0; elapsed 21.45 seconds. No source data was modified.

The same reusable GITRUN.EXEC is now a pending *read-only*
malformed-selector input test: temporarily map SEL0 to the
existing protected GITFIX GEN A (GEN2 text is not a valid
SEL1 slot), with SEL1 still the syntactically valid
unverifiable newer GITBAD. Expect NO FULLY VERIFIED
GENERATION RC8; then restore SEL0 mapping to GITSEL0 PTR A,
run full GITREC SELECT and expect RECOVERED 41 GITFIX RC0.
Do not write to any protected file or create more selectors.

## September 27 12:31 M14 malformed-slot gate PASSED

The user ran GITRUN with SEL0 deliberately rebound READ-ONLY
to existing GITFIX GEN A, whose GEN2 records cannot parse as
a SEL1 record. The newer SEL1 seq42 GITBAD remained readable
but C1GEN absent. GITREC returned NO FULLY VERIFIED
GENERATION RC8, as required. Rebinding SEL0 to GITSEL0
PTR A then caused the full native 1808-object audit to pass,
RECOVERED 41 GITFIX with digest
493F0896884B28AC4836B88328629B7E95404B46,
RC0; 21.50 seconds elapsed. No protected files or selector
records were changed.

GITRUN.EXEC is now advanced to a three-stage read-only
missing-slot test: require GITBAD PTR A nonexistent, map
SEL1 to that missing file and SEL0 to intact GITSEL0
and expect SELECTED 41 GITFIX RC0; then map SEL0 to
missing and SEL1 to invalid-new GITSEL1 and require
NO FULLY VERIFIED GENERATION RC8; finally restore
both original mappings, require RECOVERED 41 GITFIX
RC0. No compilation, writing, file erasure or reboot
is required. Pull and upload only src/GITRUN.EXEC.

## September 27 12:34 M14 missing-slot triple gate PASSED

Native CMS GITRUN required GITBAD PTR A absent, then mapped
SEL0 to the valid original GITSEL0 and SEL1 to missing:
full SFAST/PAIR/GENCHECK passed 1808 objects, SELECTED 41
GITFIX digest 493F0896884B28AC4836B88328629B7E95404B46
RC0. Then SEL0 was mapped missing and SEL1 to intact
syntactically valid but unverified seq42 GITBAD: the
new candidate failed because C1GEN absent; NO FULLY
VERIFIED GENERATION, RC8. Finally both true slots were
restored; complete 1808-object audit passed,
RECOVERED 41 GITFIX, same digest, RC0. Total elapsed
42.98s. All selector files and protected GITFIX data
were read-only. This closes the current M14 on-target
dual-slot read and fallback test matrix; cross-logon
of both selectors remains unconfirmed unless a new
CMS login occurred before one of the runs. A full
system reboot is not needed to continue independent
next-milestone development. Future GITRUN should
remain a reusable read-only dual-slot re-verification
gate until a genuinely new target test is engineered.

## M15 development resumed: September 27, host interruption CI green

M14 on-target matrix is completed through the missing-slot
triple gate (valid-old-only SELECTED 41 RC0, invalid-new-only
NO FULLY VERIFIED GENERATION RC8, both restored RECOVERED 41
RC0, full 1808-object audit in each accepted branch).
Original GITFIX STAGE/INDEX/SEEK/GEN A and selector GITSEL0,
GITSEL1 PTR A remain protected; no new CMS action needed.

M15 independent GitHub work has started rather than waiting
for reboot. Expanded tests/native_index_host.c runs the
**actual compiled native GITREC**, not just the Python
prototype, against disposable independent 1808-record
host candidate fixtures. It tests five interrupted writes
at different SEL1 prefix lengths; withholding stage, index,
seek and GEN2 candidate components separately; incomplete
new GEN2 write; fallback to the original full verified
candidate for each failure and selection of newer only
once restored. Complete integrated native-stage workflow
at f3445ada7dbcc4cc5a84b0c6b7be0786e30d488b PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36337600946 .
Additional design discussion in docs/ACTIVE_GENERATION_DESIGN.md.
This is host proof, not real CMS atomic writes, promotion
transaction safety or writer locking. Do not promote or
mutate any protected files. src/GITRUN.EXEC remains the
read-only dual-slot durability audit for the next ordinary
authorized logon or reboot. Next independent engineering
may build an isolated new-generation writer/recovery lab
using freshly allocated disposable data/slot filenames,
with capacity/lock assumptions explicit.

## M15 next real CMS gate committed: independent disposable generation

No waiting for reboot. src/GITRUN.EXEC is now reused for
a guarded one-command CMS candidate-build gate. Mac
from ibm-sandbox/src: git pull; ./cms-upload.sh GITRUN.EXEC.
CMS: GITRUN. It requires all four original protected
GITFIX files present and all four M15NEW STAGE/INDEX/
SEEK/GEN A filenames, plus M15SL0 and M15SL1 PTR A,
confirmed absent with CMS REXX STATE RC28 before any
copy. Reports QUERY DISK A. Copies original STAGE and
INDEX to fresh M15NEW (does not alter originals),
runs GITCIDX SBUILD against copied stage to write
fresh M15NEW SEEK ftell cookies, runs GITCIDX GENWRITE
to a newly created M15NEW GEN A, then reopens and runs
full GITCIDX GENCHECK. Expect 1808 unique objects
through every full audit and RC0. All step failures
abort and NO selector is written in this gate.
The CMS candidate-build gate is PENDING user output;
the host native GITREC interrupted-promotion test suite
previously PASSED at run 36337600946.

## September 27 12:43 M15 independent native candidate PASSED

User ran reusable GITRUN on CMS. Before writing, REXX STATE
reported all M15NEW STAGE/INDEX/SEEK/GEN A and new M15SL0/
M15SL1 PTR A unused (RC28). MNT191 A R/W 22393 free 4096
blocks reported. GITRUN copied only protected GITFIX STAGE
and IDX2 INDEX to new M15NEW files; rebuilt SIDX2 seek index
against the copied stage: SEEK INDEX WRITTEN 1808 UNIQUE
1808; GENWRITE reran complete 1808-object SFAST/PAIR and
sealed M15NEW GEN A. A fresh GENCHECK reran full SFAST/PAIR,
GENERATION VERIFIED 1808 UNIQUE 1808 and RC0, 51.20s total.
Existing GITFIX and GITSEL0/GITSEL1 are unchanged.
All four M15NEW candidate files now exist. DO NOT rerun
the copy/build batch or overwrite any M15NEW file.

GITRUN.EXEC now advances to a safe disposable two-slot
test using previously confirmed unused M15SL0/M15SL1 PTR A.
It first checks both candidates' four existing files and
both new pointer filenames. Binds complete C0 GITFIX and
C1 M15NEW read-only inputs. Creates new seq51 GITFIX
selector M15SL0 by WRITEGEN with REXX STATE RC28 and
ABSENT28 attestation, verifies old-only via real GITREC
(full GENCHECK). Then, only if M15SL1 remains absent,
creates seq52 M15NEW M15SL1 using GENIN M15NEW GEN A,
verifies newly selected M15NEW through full GITREC
GENCHECK. No original selectors or GITFIX files written.
Next user commands from ibm-sandbox/src: git pull;
./cms-upload.sh GITRUN.EXEC. On CMS: GITRUN.
If a selector creation fails halfway, preserve any partially
created file and stop; do NOT blindly rerun WRITEGEN.
This M15 selector test awaits native CMS results.

## September 27 12:46 M15 two genuine native generations selected

M15 isolated CMS selection test PASSED: the existing protected
GITFIX candidate was bound C0, and independently copied,
reindexed and sealed M15NEW candidate C1. Newly allocated
M15SL0 PTR A was written with seq 51 GITFIX and after full
1808-object GENCHECK selected RC0 with digest
493F0896884B28AC4836B88328629B7E95404B46.
Newly allocated M15SL1 PTR A was then written with seq52
M15NEW, whose independently produced GEN2 had the same
descriptor digest. Native GITREC SELECT GITFIX M15NEW
fully rehashed 1808 objects and SELECTED 52 M15NEW RC0.
Elapsed 43.01s. Existing GITSEL0/GITSEL1 and protected
GITFIX files remain unchanged. M15SL0/M15SL1 and all
M15NEW files now EXIST: never repeat that creation batch.

Next reused GITRUN.EXEC is a read-only M15 fallback gate:
bind the two existing M15SL selector files, complete old
GITFIX and new M15NEW candidate files except C1GEN, which
is deliberately mapped to nonexistent M15BAD GEN A only
after verifying absent RC28. Require RECOVERED 51 GITFIX
RC0 after full audit. Then restore C1GEN mapping to intact
M15NEW GEN A and require SELECTED 52 M15NEW RC0 after
fresh full audit. No selectors or data are modified.
Mac: git pull; ./cms-upload.sh GITRUN.EXEC.
CMS: GITRUN.

## September 27 12:48 M15 two-generation fallback PASSED; 10-case batch pending

Native CMS GITRUN temporarily bound newer seq52 M15NEW C1GEN
to verified-absent M15BAD GEN A, leaving real M15SL0 and
M15SL1 selectors and all data intact. GITREC ran full
1808-object SFAST/PAIR/GENCHECK on protected older GITFIX,
RECOVERED 51 GITFIX digest
493F0896884B28AC4836B88328629B7E95404B46, RC0.
Restoring C1GEN M15NEW GEN A led to complete independent
1808-object rehash/PAIR/GENCHECK, SELECTED 52 M15NEW
same digest RC0. Total elapsed 43.19 seconds.
Both generations' files and both disposable M15 selectors
remain intact.

User explicitly requests maximum work per CMS upload/run and
not pausing unnecessarily. The reusable GITRUN.EXEC is now
a **single 10-case read-only M15 test** using only FILEDEF
input remapping: first verify both original full candidate
file sets and both M15SL selector records exist and every
M15BAD STAGE/INDEX/SEEK/GEN A fixture is absent RC28.
Test four independent newer component omissions, each
requiring RECOVERED 51 GITFIX RC0; missing older GEN
requires SELECTED 52 M15NEW RC0; both GEN inputs missing
require NO FULLY VERIFIED GENERATION RC8; malformed
newer slot via a read-only GEN2 input requires SELECTED
51 GITFIX RC0; malformed older slot requires SELECTED
52 M15NEW RC0; both malformed slots require RC8;
then restore both true slot FILEDEFs and require
SELECTED 52 M15NEW RC0. Program requires expected RC
for each and aborts upon discrepancy. Visual output
must also be checked for the exact selected sequence/name.
No data bytes, pointer records, protected GITFIX
generation or M15NEW files are rewritten.
Mac: git pull, ./cms-upload.sh GITRUN.EXEC.
CMS: GITRUN. Ten cases may run several complete
~21-second full audits in a single invocation.

## September 27 12:53 comprehensive 10-case native matrix PASSED

User ran GITRUN on real CMS. All 10 cases returned expected
results, total CPU 170.88 s / elapsed 172.08 s.
Missing newer stage, index, seek and GEN separately each
triggered full verified recovery through older seq51
GITFIX with the exact digest
493F0896884B28AC4836B88328629B7E95404B46 and RC0.
An absent old GEN correctly selected new seq52 M15NEW
after full 1808-object audit, RC0. Both manifests missing
failed closed RC8. Individually malformed newer/older
selector inputs chose the remaining fully verified candidate
seq51/seq52 respectively; both invalid selector inputs
failed closed RC8. Restoring both selectors selected
seq52 M15NEW with full audit RC0. The error messages
for missing DDs were expected. No generation or slot
content was rewritten.

User explicitly requests maximal useful work per CMS
run plus cleanup on BOTH CMS and GitHub. Retired GitHub
host-only Python selector prototype and its test after
moving independent CRC32 encoder into
tests/test_native_selector.py, updating native-stage
workflow, and observing reworked native CI PASS
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36338727815 .
Retained production C89 selector/recovery source,
real native regression suites and historical docs.

New reusable GITRUN.EXEC performs three full real-CMS
audits and guarded cleanup in one run:
(1) independent GITCIDX GENCHECK original GITFIX,
(2) independent GENCHECK M15NEW,
(3) deliberately swap the two disposable M15SL selector
input bindings and require GITREC RC8, restore them and
require full GITREC selection of seq52 M15NEW RC0,
(4) only after all verifications erase exactly three
old NONCANONICAL, already superseded CMS files if they
exist: GITSTAGE DATA A, GITINDEX DATA A, GITSEEK INDEX A.
Each deletion requires STATE RC0, ERASE RC0, and
post-STATE RC28. If already absent RC28 it skips.
It finally confirms all four GITFIX and M15NEW
generation components and both pairs of selector
records GITSEL0/GITSEL1 and M15SL0/M15SL1 still exist.
Preserve captured original GITPBUF PACK A, all canonical
generations and rollback selectors. The CMS cleanup is
PENDING actual output: do not claim deletion before
GITRUN is run successfully. Mac from src: git pull,
./cms-upload.sh GITRUN.EXEC; CMS: GITRUN.

## September 27 13:01 guarded legacy CMS cleanup PASSED

Actual CMS GITRUN completed each prerequisite and final safety
check. Independent full GITCIDX GENCHECK on both GITFIX and
M15NEW returned FAST AUDIT VERIFIED 1808 UNIQUE 1808,
PAIR VERIFIED UNIQUE 1808, GENERATION VERIFIED 1808
UNIQUE 1808, RC0. GITREC rejected swapped disposable
M15SL1/M15SL0 slots with two identity mismatch messages,
NO FULLY VERIFIED GENERATION RC8, then correctly selected
seq52 M15NEW with digest
493F0896884B28AC4836B88328629B7E95404B46
after full 1808-object audit and RC0. The guarded cleanup
erased the old obsolete noncanonical CMS A-disk files
GITSTAGE DATA, GITINDEX DATA, GITSEEK INDEX, each
post-STATE confirmed absent RC28. The runner's final
STATE checks confirmed all four protected GITFIX files,
all four M15NEW files, both original GITSEL0/GITSEL1
PTR files, and both disposable M15SL0/M15SL1 PTR
files still exist. CPU 64.34s, elapsed 64.82s.
The original GITPBUF PACK A is also to be preserved;
it was not touched by the cleanup.

Next continue independent selector protocol hardening
in one high-density CMS batch against ONLY newly
allocated temporary pointer fixtures. Never recreate
old incompatible stage/index/seek or rerun M15 build.

## M16 latest committed work, September 27 after M15 cleanup

M15 full three-audit and guarded CMS legacy cleanup COMPLETED
and recorded above. Existing valid original seq41/invalid
seq42 GITSEL0/GITSEL1, independent true seq51 GITFIX /
seq52 M15NEW M15SL0/M15SL1 and all eight canonical
sealed GITFIX/M15NEW files must be preserved. The
original GITPBUF PACK A remains the forensic source.
All three old obsolete GITSTAGE DATA A, GITINDEX DATA A,
GITSEEK INDEX A were erased with absent STATE RC28.

The next single GITRUN.EXEC packs the M16 adversarial
selector tests and immediate disposable cleanup. Before
any writes it checks both complete generations and all
four preserved selector records exist and all three
M16BAD/M16LOW/M16CON PTR A filenames are unused (STATE
RC28). It binds real C0 GITFIX and C1 M15NEW inputs
and writes only the following disposable selector records:
M16BAD seq60 M15NEW with valid CRC32 but deliberately
wrong all-zero manifest digest (must RECOVER 51 GITFIX);
M16LOW seq50 M15NEW with authentic M15NEW digest (must
SELECT 51 GITFIX because it is a lower sequence);
M16CON seq51 M15NEW with authentic digest (must reject
same-sequence different generation conflict RC8).
It then restores M15SL1 seq52 M15NEW and requires a
complete full 1808-object audit and SELECTED 52 M15NEW
RC0. Only after this, it ERASEs and STATE-confirms
absent the three M16 temporary PTR files; it finally
checks all eight canonical data files and all four
preserved pointers still exist. NO original data or
pointer writes. This CMS test is pending.

The host native_index_host.c now independently tests
the actual production GITREC binary with forged-valid
CRC32, authentic low sequence, conflicting same
sequence and final restoration. Latest native CI
is https://github.com/mostangrymike/ibm-sandbox/actions/runs/36339171710 .
Mac: from ibm-sandbox/src run git pull and
./cms-upload.sh GITRUN.EXEC; CMS: GITRUN.

## M17 pending CMS cleanup batch

M16 target run PASSED on September 27 at 13:05: forged CRC-correct
seq60 M15NEW digest fell back to verified seq51 GITFIX,
genuine lower seq50 M15NEW lost to seq51 GITFIX, conflicting
same seq51 candidates failed closed RC8, and restoring
seq52 M15NEW reverified the entire 1808-object generation,
RC0. All three M16 disposable selector files M16BAD,
M16LOW and M16CON PTR A were erased and STATE-confirmed
absent. Both sealed generations and all four long-lived
selector records remained present.

User asked to embed exact previously enumerated abandoned
native TLS ERASE commands in the NEXT reused GITRUN.EXEC.
Current GitHub src/GITRUN.EXEC is that M17 batch. It first
STATE-checks all eight GITFIX/M15NEW sealed files, the
four GITSEL0/GITSEL1/M15SL0/M15SL1 PTR A selectors and
captured original GITPBUF PACK A. It independently runs
full GITCIDX GENCHECK on both sealed generations and
GITREC SELECT GITFIX M15NEW on existing M15 slots.
Only if all pass, it retires on CMS A the listed obsolete
native TLS research files M12ATLS/M12TLS2/M12TLS3/
M12TLS4 with ASSEMBLE/LISTING/MODULE/TEXT types where
present, and TLSQTEST/SSLTEST/SSLTEST2 C. Each file is
STATE-checked and, when present, ERASEd and STATE-
confirmed absent. Missing files are skipped, unexpected
RCs abort. It rechecks all protected files afterward.
This cleanup is PENDING target CMS output, not yet done.
Native TLS research sources were already removed from
GitHub main; stunnel transport and ordinary TCP/HTTP
are preserved. SSLPOOL service logs and historical
SSL trace DATA are NOT in this M17 deletion batch.
Mac from ibm-sandbox/src: git pull;
./cms-upload.sh GITRUN.EXEC. CMS: GITRUN.

## September 27 13:01-13:07 M17 CMS DATA INTEGRITY INCIDENT

M16 adversarial selector test fully passed and erased its
three disposable pointer fixtures, preserving all protected
data. The subsequent M17 GITRUN on CMS also passed both
complete independent GITCIDX GENCHECKs (GITFIX and
M15NEW, each 1808 unique) and complete GITREC selection of
seq52 M15NEW, digest
493F0896884B28AC4836B88328629B7E95404B46,
all before attempting any cleanup. However, on the FIRST
attempt to erase historical M12ATLS ASSEMBLE A1, CMS
displayed:
DMSDKD1307T File system error detected by DMSERS
at address 00F1CFE0 offset 00001428:
TRKDE request failed with code 4 while processing file
M12ATLS ASSEMBLE A1.
HCPGIR450W CP entered; disabled wait PSW
000A0000 00F08312.
User issued IPL CMS and received ordinary z/VM 6.3
CMS signon. This is NOT evidence of successful removal
or trustworthy persisted minidisk integrity.

IBM DMS1307T documentation explicitly identifies TRKDE
code 4 as attempted deallocation of a nonallocated
disk block, possibly due to prior CMS minidisk corruption,
storage allocation map corruption in virtual memory or
file structural corruption. Disabled wait can leave
uncommitted A-disk directories unwritten. Preserve any
CMS dump and operator/Hercules logs. NO FURTHER A-DISK
WRITES, CLEANUP, OR GITRUN TESTS before obtaining a
consistent backup/snapshot of actual host DASD image
with the VM properly quiesced. Do not assume the
Hercules host OS/path or run remote shell commands
without verification. After preserving disk image,
diagnose disk integrity on a copy, inspect directory,
allocation map, duplicate or cross-linked blocks,
and investigate any Hercules I/O errors. Only after
recovery and validated canonical data should development
resume. In GitHub, src/GITRUN.EXEC was immediately
replaced with a SAFETY HOLD exit RC12, no write actions,
to prevent accidentally rerunning the dangerous cleanup
batch from a new pull. Abandoned native TLS GitHub
experimental sources are deleted; historical Git
commits still preserve them. Current on-disk state
of M12ATLS ASSEMBLE after failed erase is UNKNOWN.

## After TRKDE incident: independent GitHub recovery work completed

Following user instruction "do not pause", completed the work
that does not touch the possibly damaged CMS A disk.
GitHub src/GITRUN.EXEC remains the RC12 safety hold; do
NOT run the prior cleanup EXEC still uploaded on CMS.
Added docs/CMS_DASD_RECOVERY.md with IBM sourced diagnosis,
minidisk image preservation, CP DDR/MDCHECK follow-up on
the actual z/VM version and recovery exit criteria.
Added scripts/backup-offline-dasd.sh: refuses to run without
OFFLINE_CONFIRMED=YES, accepts only explicit non-symlink
regular source and unused destination, checks optional
fuser and exact byte count/cmp plus SHA256, does not
modify the source, and retains incomplete backup output
on errors. It is NOT a live-snapshot substitute; no
actual host paths are assumed. Added synthetic
tests/test-offline-dasd-backup.sh and wired it into the
native-stage GitHub CI workflow; the complete suite
PASSED at
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36353242601 .
No CMS files or live DASD images have been copied,
inspected or repaired by assistant. User has not yet
provided host path, quiesced storage state, or a
verified backup of MNT191. The precise next step
requires preserving VM dump and taking the real DASD
backup once operator confirms actual Hercules image,
offline status and storage destination. Avoid claiming
any repair or safe A-disk writes until then.

## Continued offline-only recovery work after TRKDE incident

User said proceed after the safety hold. All independent
development remained on GitHub and on synthetic CI data;
NO CMS or real Hercules DASD images were touched.

Hardened scripts/backup-offline-dasd.sh to publish verified
offline copies using atomic hard-link create-if-absent rather
than mv -n, so two backup attempts cannot silently replace
each other's preservation result. Added
scripts/inspect-hercules-config.sh, a *read-only* inventory
helper that takes an operator-verified active Hercules
configuration file and reports simple CKD address/device/
backing-filename declarations without disclosing arbitrary
config lines or guessing the CMS virtual 191 host mapping.
It does not follow INCLUDE records or certify quiescence.
Added tests/test-hercules-config.sh with synthetic records,
missing-file and symlink refusal cases; integrated with
native-stage GitHub CI. Full integrated CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36353438291 .
Additional synthetic backup-helper symlink source/destination
negative cases were just committed, CI run
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36353470091
was queued when last inspected. Expanded
docs/CMS_DASD_RECOVERY.md with helper usage and
verification caveats.

Safest user next step: on the actual Hercules host,
locate verified active Hercules config and CP MDISK mapping,
preserve crash dump/Hercules logs, quiesce the actual guest
and emulator or take coordinated host-storage snapshot,
then back up the full appropriate DASD image/overlays
to independent storage. Do NOT run user CMS's old uploaded
cleanup GITRUN. GitHub src/GITRUN.EXEC remains fail-fast
safety hold (RC12). Actual host file names, verified image
backup and post-crash disk integrity are still UNKNOWN.

## September 27 onward — confirmed six Hercules devices; mapping tool ready

Operator actually ran configuration inventory:
`/home/admin/vm630/hercules.cnf` device declarations
`0123 3390 dasd1`, `0124 3390 dasd2`,
`0125 3390 dasd3`, `0126 3390 dasd4`,
`0127 3390 dasd5`, `0128 3390 dasd6`.
A subsequent CMS `QUERY DISK` showed affected
`MNT191` virtual 191 A R/W 175 cylinders,
239 files, 9110/31500 4K blocks used, 22390 free.
This read-only listing does NOT establish disk
health after TRKDE 4. The CP physical `Rdev`,
real volser, StartLoc, Size and actual Hercules
process cwd remain UNKNOWN; do not assume 0123
just because older projects happened to use 0123.

IBM CP documentation confirms `CP QUERY MDISK 191 LOCATION`
is a class-G read-only way to obtain OwnerID,
Odev, real volume ID, Rdev, StartLoc and Size.
After obtaining genuine output, match its Rdev
to the active Hercules channel, corroborate
the volser and 175-cylinder extent, inspect
dynamic attachments/includes/shadows, and
confirm emulator process cwd before any copy.

To avoid guesses, a new read-only
`scripts/map-cms-minidisk.sh` takes confirmed
CP-Rdev, actual active Hercules config and
verified process cwd; fails closed on missing/
ambiguous simple CKD declarations, missing
or symlink backing image; prints candidate
absolute base path but explicitly does NOT
certify quiescence or overlay completeness.
`tests/test-map-cms-minidisk.sh` exercises
unique success, missing image, invalid Rdev,
duplicate address; integrated full native
CI succeeded:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36355860458 .
The recovery runbook was updated with
the actual operator-supplied inventory.
No real CMS or Hercules DASD contents have
been modified by this work. GitHub GITRUN
remains deliberately safety-disabled,
and the old CMS-uploaded GITRUN must not run.

## M18 production-facing selected-generation GET — GitHub CI GREEN

User explicitly said "don't get sidetracked on this, continue
with project follow all rules." Developed actual native
Git functionality independently of live CMS storage and
without attempting any CMS A writes. Current main source
`src/GITREC.C` implements
`GITREC GET C0NAME C1NAME OID40`, extending existing
real-CMS-proven read-only SELECT. GET validates the OID
hex before any verification, applies identical identity,
sequence/conflict and fallback rules, full-audits the
selected candidate's GEN2 via existing native gen_check,
then opens only that verified candidate's bound SIDX2
seek index and stage through sidx_read/sidx_get. It
independently rehashes the requested object, returning
`SEEK OBJECT OID ... TYPE ... SIZE ... PREFIX ...`.
Missing OID returns RC4, invalid OID returns RC4 and
no complete verified generation returns RC8. It is
READ-ONLY and prints only 16-byte prefix, not yet a
complete object materialization/API.

Extended `tests/native_index_host.c` using real compiled
production GITREC against both fully independent 1808-
record host fixtures. Positive seq42 new GET; missing
OID and invalid hex rejection; new manifest missing
falls back old seq41 and GET; both manifests absent
must fail closed and not print object bytes; restored
new manifest selects seq42 and GET. Fixed test
expectations to the actual pre-existing SIDX2 output
`SEEK OBJECT OID` / `SEEK OID NOT FOUND`.
Full native-stage and all other GitHub CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36356300751 .
Improved native runner to print host output and exact RC
on regression failure. docs/ACTIVE_GENERATION_DESIGN.md
records this integration.

Do NOT ask user to CMS-upload or execute GET while the
M01RES/dasd1 post-TRKDE filesystem integrity is unresolved:
the old unsafe CMS GITRUN cleanup EXEC is still in user's
CMS A disk, and GitHub src/GITRUN.EXEC remains the RC12
safety hold. The user provided host evidence real 0123
M01RES file /home/admin/vm630/dasd1, open by Hercules
PID 879 FD12, file size 768999817, no observed shadows.
GitHub docs/CMS_DASD_RECOVERY.md has precise verified
path and offline backup prerequisites. No verified
offline backup or post-crash file integrity was reported.
Continue useful native Git source and host tests on GitHub
without reintroducing native SSL/TLS or risk of A-disk
writes until safe to resume.

## Latest operating rule and M19/M20 completed host work

USER'S EXPLICIT NEW RULE: "do not pause till cms work needed".
Continue advancing the active Git project autonomously on GitHub,
combining material source changes and associated tests per run,
fixing CI failures and committing stable results without requiring
repeated "proceed" prompts. Pause for user input only when the next
meaningful gate genuinely requires CMS or other unavailable target
data; do not disguise host proof as target CMS proof.

M18's native GITREC GET printed verified object type, size and
16-byte prefix. M19 extended production src/GITREC.C with
`CATHEX C0NAME C1NAME OID40`: after full GEN2 native audit,
use actual selected candidate's SIDX2 direct seek and rehash the
requested body, then print exact complete content as framed
`OBJECT DATA BEGIN` / 32-byte `HEX ` lines / `OBJECT DATA END`.
Empty body produces no HEX lines. Standalone GET unchanged.
Native host test ran the actual compiled C89 GITREC against
two independent complete 1808-record generations, positive
whole CATHEX, empty content, newer manifest fallback and
fail-closed both manifests unavailable.

M20 additionally created tests/test-native-cathex-large.py:
it independently assembles a 1808-object Git blob stage
including a 65536-byte binary body (MAX), empty body,
257-byte binary with NUL/high bytes and abc; native
GITCIDX BUILD/SBUILD/GENWRITE/GENCHECK generates sealed
artifacts; two separate candidate copies and CRC32
selector records are created; actual compiled GITREC
CATHEX output is byte-for-byte reconstructed and
compared with Python's independent Git canonical SHA1.
It also tests corruption of new stage, verified old
fallback, no data disclosure when both candidates
cannot verify, and restoration. Complete native
GitHub CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36356523315 .

A future CMS-only read-only batch is committed as
src/GITRCHK.EXEC (NOT GITRUN). It gates existence of
both full generations and four protected selectors,
captured GITPBUF PACK A and newly compiled GITREC
MODULE A. It uses canonical first commit OID
00D8D63229305230C8D37F884CE87F9E1A89468C,
then GET and CATHEX from real seq52 M15NEW; simulates
unavailable newer GEN2 to require seq51 GITFIX
fallback CATHEX; withholding both GEN2s must RC8,
and restoration must CATHEX from seq52 again. No
ERASE/COPYFILE/GENWRITE/SELOUT/GENMOD or persistent
output FILEDEF commands. tests/check-readonly-gitrchk.sh
enforces this and preserves src/GITRUN.EXEC's
post-TRKDE safety hold. Full integrated CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36356602355 .

**CMS NEXT GATE**: genuine target compile/upload of
the new src/GITREC.C and read-only src/GITRCHK.EXEC,
then single `GITRCHK` batch ONLY after the M01RES
actual dasd1 disk has an independently verified
forensic backup and verified healthy/reconstructed
CMS A filesystem. On actual Hercules host, the
confirmed original image is
/home/admin/vm630/dasd1, size 768999817, mounted
by Hercules PID879 FD12 at prior observation;
user has NOT supplied proof of its offline backup,
integrity recovery or safe CMS write capability.
Don't upload/compile new CMS sources or execute
the stale, unsafe CMS GITRUN cleanup while pending.
GitHub GITRUN remains RC12 safety hold. No more
independent changes are required for the M20
functional CATHEX gate; native CMS execution is
the next genuine proof, once storage is safe.

## September 27 M21 user workflow rule: ALWAYS USE GITRUN

User explicitly resumed CMS testing and reiterated
"use gitrun remember". For **every CMS test batch**
use the existing reusable `src/GITRUN.EXEC` name,
uploading a replacement after each approved GitHub
edit, then execute `GITRUN` in CMS. DO NOT create
additional alternate driver names such as GITRCHK
as the user-facing invocation and DO NOT require
manual repetition of separate CMS FILEDEF/audit
commands when they can be combined into GITRUN.
Continue autonomously with host source and regression
work until CMS is genuinely required.

To honor this rule, main `src/GITRUN.EXEC` now
contains M21's read-only, one-upload/one-run CMS
gate: STATE of both protected GITFIX/M15NEW
generations, four original selectors, PACK and
required compiled modules, require fixture
M15BAD GEN A absent; independently bind and
GENCHECK both sealed generations (1808 objects
each); bind existing M15 selector slots and both
generations, full `GITREC SELECT` seq52; first
commit canonical OID
00D8D63229305230C8D37F884CE87F9E1A89468C
native GET then full CATHEX; simulate missing
new GEN2 and require fallback older; both
GEN2s missing require RC8; restore both and
require full CATHEX again; STATE final protected
objects and print final success. All file
operations within M21 GITRUN are reads or
FILEDEF rebindings. No ERASE, COPYFILE,
GENWRITE, pointer creation or cleanup.
Old dangerous M17 cleanup is gone from GitHub.
The previously prepared alternate GITRCHK.EXEC
remains historical source but should NOT be
offered as user's execution name. The companion
CI guard tests both scripts read-only and all
required M21 stages. Full native GitHub CI
passed at
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36358843927 .

Exact next user Mac workflow from local
ibm-sandbox/src:
git pull
./cms-upload.sh GITCIDX.C
./cms-upload.sh GITREC.C
./cms-upload.sh GITRUN.EXEC
Then CMS, with real installed CMSCLNK:
CMSCLNK GITREC PLAIN
GITRUN
Only tell user CMS compile succeeded after
their actual returned output; host CI cannot
prove CMS target. The GitHub GET/CATHEX
features need current GITCIDX.C because
GITREC.C directly includes that source.
If CMSCLNK is not installed, diagnose against
known target GITCLNK EXEC A; do not assume a
compiler/linker path without actual result.
Uploading source/EXEC and compilation DO write
CMS A; the user explicitly requested resumed
target testing, but do not casually claim
the prior TRKDE incident has been repaired
or the /home/admin/vm630/dasd1 forensic
backup has been performed. Guarded M21
runtime does no persistent writes and never
touches M12ATLS ASSEMBLE or any obsolete
TLS cleanup source.

## September 27 18:32–18:35 — M21 TARGET CMS PASSED

User uploaded latest source and standard GITRUN.EXEC to
live z/VM CMS, actually ran CMSCLNK GITREC PLAIN:
ASSEMBLER (XF) DONE / NO STATEMENTS FLAGGED /
CMSCLNK: built GITREC MODULE mode PLAIN (5.68 CPU /
5.91 elapsed). Executed GITRUN M21 read-only native
Git suite to completion, real CMS output:
GITRUN M21 ALL READ ONLY NATIVE GIT TESTS PASSED,
Ready; T=150.70/151.97 18:35:46.

Live M21 independent full GITCIDX GENCHECK on both
existing sealed GITFIX and M15NEW stage/index/seek/GEN2
passed FAST AUDIT 1808 UNIQUE 1808, PAIR VERIFIED
1808 and GENERATION VERIFIED 1808 (RC0 each). Actual
GITREC SELECT chose seq52 M15NEW digest
493F0896884B28AC4836B88328629B7E95404B46.
GITREC GET of actual first commit OID
00D8D63229305230C8D37F884CE87F9E1A89468C
succeeded (type1, 270 bytes, RC0); CATHEX of its
entire canonical binary contents produced 9 HEX lines
and OBJECT DATA END (RC0). Deliberately FILEDEF
newer manifest to nonexistent M15BAD GEN A and full
CATHEX recovered seq51 GITFIX with full GENCHECK
and RC0. Both generation manifests rebound to
same nonexistent filename correctly printed NO FULLY
VERIFIED GENERATION RC8. Restored two valid mappings
fully reverified and selected seq52 M15NEW,
CATHEX complete RC0. Final all protected generation
and pointer slots STATE checks passed. CMS
DMSSTT002E M15BAD not found and DMSSOP036E
C1GEN/C0GEN open error 4 are intentional NEGATIVE
fixture messages. User pasted console output in
interleaved order; final PASS and all required
outcomes verified. M21 live CMS full read-only
feature is now TARGET PROVEN. User explicitly
requires *standard GITRUN* for every new CMS
test, one upload/run per batch; no new driver
name as user-facing command. User's earlier
rule: do not pause until genuinely CMS work needed.
Continue independent GitHub-native client
engineering and host regression until next
meaningful target batch, then modify/upload
src/GITRUN.EXEC only. Prior TRKDE4 cleanup
failure remains relevant to destructive
maintenance but do not derail native Git
functional development with repeated backup
discussion; no cleanup in current GITRUN.

## M22 NEXT TARGET GATE — GitHub host CI passed

M21 actually passed on real z/VM 6.3 CMS at 18:35:
the current native GITREC was compiled using
CMSCLNK GITREC PLAIN with no assembler warnings,
the standard GITRUN independently audited both
GITFIX and M15NEW 1808-object generations,
selected seq52 M15NEW, GET and CATHEX read the
real 270-byte first commit with canonical Git OID
00D8D63229305230C8D37F884CE87F9E1A89468C,
seq51 GITFIX fallback succeeded after deliberately
missing C1GEN, both missing manifests RC8, and
restoration selected seq52 with full CATHEX;
final protected file checks passed. User pasted
interleaved output but unambiguous final line:
GITRUN M21 ALL READ ONLY NATIVE GIT TESTS PASSED.
Target CPU/elapsed 150.70/151.97. The
deliberately missing M15BAD GEN emitted expected
DMSSTT002E and DMSSOP036E messages.

Acting on user's ongoing rule "do not pause till
cms work needed", autonomously implemented M22
native Git tree reader in src/GITREC.C:
GITREC TREE C0NAME C1NAME OID40; validates
complete GEN2/SFAST/PAIR before selecting a
candidate; uses verified candidate's SIDX2
to retrieve and rehash requested binary type-2
object; first validates entire tree entry grammar
and modes then emits `TREE DATA BEGIN`,
`TREE ENTRY MODE <mode> NAMELEN <n> OID <40hex>`
and `TREE NAMEHEX <up to 32 raw bytes>`
records, `TREE ENTRIES n`, `TREE DATA END`.
Supports empty trees, five standard Git modes,
arbitrary non-NUL/non-slash raw name bytes
(hex output to avoid EBCDIC issues). Rejects
corrupt/non-tree types with RC8 and no TREE
content emission. Host new
tests/test-native-tree.py compiles real
GITCIDX.C/GITREC.C C89 with strict -Werror,
builds/seals 1808-object stage including valid
6-entry tree, empty tree, malformed tree, blob,
and full selector fallback and restore tests.
CI PASS
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36359383185 .

Standard src/GITRUN.EXEC is now M22's one-upload
read-only CMS test batch, never GITRCHK. It
checks protected files, full independent audit
on both generations, verifies selected seq52,
GETs actual first commit, TREE-decodes its
actual tree OID
204E1D6968FB81C35BF830D63A611AC64C072945,
tests commit passed as TREE fails RC8, simulates
missing new GEN2 to recover old seq51 TREE,
simulates both missing RC8, restores both
and decodes tree again, checks all protected
files. CI read-only guard is updated and green.
This latest M22 source has NOT yet been compiled
or run on CMS. To target-validate, Mac from
ibm-sandbox/src:
git pull
./cms-upload.sh GITREC.C
./cms-upload.sh GITRUN.EXEC
On CMS:
CMSCLNK GITREC PLAIN
GITRUN
Do not upload GITCIDX.C again unless needed:
M22 did not change it; GITREC source directly
includes already uploaded current GITCIDX.C
and GITSEL.C. No native TLS/SSL experiments,
no filesystem cleanup, no pointer/file writes
from the M22 runtime batch. Next gate genuinely
requires user-provided live CMS M22 output;
do not report target proof until it arrives.

## September 28 09:24–09:28 — M22 ACTUAL CMS PASS

User compiled corrected GITREC.C with CMSCLNK GITREC
PLAIN: ASSEMBLER (XF) DONE, no statements flagged,
module built, T=5.98/6.22. They then ran the standard
GITRUN M22 batch on real z/VM CMS: all protected
generations and selector files present, independent
GITCIDX GENCHECK for GITFIX and M15NEW each returned
FAST AUDIT 1808 unique, PAIR 1808 and GENERATION
VERIFIED 1808, RC0. Real GITREC selected seq52
M15NEW digest 493F0896884B28AC4836B88328629B7E95404B46,
GET verified first commit OID
00D8D63229305230C8D37F884CE87F9E1A89468C
type1 270 bytes. Native GITREC TREE decoded its
actual tree 204E1D6968FB81C35BF830D63A611AC64C072945
with four entries: 100644 CHAT_STATE.md at
6DC1BFE370142E89C2DB239E12BA08A565C2CC62;
100644 README.md at 1BA7AE466BB0A16C294D52A8642E527B07D4D1F5;
40000 docs at 980E3417BEF3170BF6CCEDFECEB81EDF1C830477;
40000 src at A41B3EA7758F301B7E30BD3CFDF264300C02AE35.
TREE RC0. Deliberate TREE on commit correctly returned
OBJECT IS NOT A TREE RC8. Deliberately absent newer
manifest recovered seq51 GITFIX and full four-entry
TREE with RC0. Both manifests missing returned
NO FULLY VERIFIED GENERATION RC8, no tree data.
Restoration selected seq52 and decoded tree RC0;
final protected generation/selector checks passed.
Exact final CMS output:
GITRUN M22 ALL READ ONLY NATIVE GIT TESTS PASSED
Ready; T=172.16/173.64 09:28:13.
Intentional nonexistent M15BAD GEN reported
DMSSTT002E/DMSSOP036E as expected. Initial
failed M22 TREE due to ASCII/EBCDIC literal
mismatch is FIXED and native CMS PROVEN.
Next rule: autonomously continue independent
GitHub features and strict host CI, then prepare
ONE standard GITRUN batch when target CMS test
is genuinely needed; user wants no premature
pause or manual multi-command test sequences.

## SEPTEMBER 28 — M22 ACTUAL CMS PASS; M23 READY FOR CMS

M22 full actual CMS target test PASSED after user
recompiled the EBCDIC/ASCII-corrected production
GITREC with CMSCLNK GITREC PLAIN, assembler
flagged zero errors. Standard GITRUN M22 on
live CMS independently audited both complete
1808-object GITFIX and M15NEW generations;
selected seq52 M15NEW DIGEST
493F0896884B28AC4836B88328629B7E95404B46;
verified first commit GET; decoded the actual
tree OID 204E1D6968FB81C35BF830D63A611AC64C072945
as CHAT_STATE.md README.md docs src, with
correct 100644 / 40000 modes and binary OIDs;
non-tree negative RC8; recovered seq51 GITFIX
with the newer manifest absent; both manifests
absent RC8/no tree; restoration selected seq52;
all protected files STATE confirmed. Exact end:
GITRUN M22 ALL READ ONLY NATIVE GIT TESTS PASSED
Ready T=172.16/173.64 09:28:13.

After this live proof, independently developed M23
in GitHub: production src/GITREC.C now adds
COMMIT C0NAME C1NAME OID40, using full
GENCHECK-selected immutable candidate,
independent indexed selected-object rehash,
explicit ASCII Git header/hex parsing to avoid
CMS-native EBCDIC pitfalls, first tree OID,
zero-plus contiguous parent OIDs, required
author/committer and blank separator,
fail-closed malformed/not-commit rejection,
bounded formatted metadata output. Validated
actual C89 compiled source with full 1808-object
synthetic host fixtures for root commit, merge
with two parents, invalid parent and missing
committer, wrong type, old fallback, both
absent rejection and restoration. Full CI PASS:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36436943632 .

Standard src/GITRUN.EXEC is updated to M23
read-only combined suite; it checks protected
generation, original selectors and PACK;
independently GENCHECKs both full generations;
SELECT seq52; native COMMIT of real first
commit 00D8D63229305230C8D37F884CE87F9E1A89468C;
independently TREE of known tree
204E1D6968FB81C35BF830D63A611AC64C072945;
COMMIT on tree fails RC8; absent new GEN2
recovers old COMMIT; both GEN2s absent RC8;
restored both selects new COMMIT; final file
STATE checks. No persistent writes in GITRUN.
tests/check-readonly-gitrchk.sh CI guard was
updated and all host tests green.

LATEST GITRUN workflow: user explicitly requires
that new CMS tests all use standard GITRUN,
never auxiliary GITRCHK as user-facing runner,
and autonomous GitHub development continues
until real CMS test necessary. For M23 next
actual CMS test, user Mac prompt is in
ibm-sandbox/src, so:
  git pull
  ./cms-upload.sh GITREC.C
  ./cms-upload.sh GITRUN.EXEC
Then on CMS:
  CMSCLNK GITREC PLAIN
  GITRUN
GITREC directly includes unchanged GITCIDX.C
and GITSEL.C that are already on user's CMS.
Do not upload/rebuild originals or run historical
TLS cleanup; no changed GITCIDX.C needed.
M23 has not yet been target executed. Await
actual CMS output before claiming target proof.

## M23 stronger independent real-first-commit fixture — final green

Before requesting next CMS run, M23 host tests also
incorporated the EXACT nine HEX records of the
270-byte real first-commit CATHEX body previously
obtained on live CMS. The synthetic harness
independently asserts that its canonical Git
commit SHA1 is
00D8D63229305230C8D37F884CE87F9E1A89468C,
then uses production C89 GITREC COMMIT to parse
that real body and assert its tree
204E1D6968FB81C35BF830D63A611AC64C072945,
parent 2D5038C551318997B865497E04CF4C037DE4135E,
parent count 1 and exact message length.
The expanded full native GitHub CI PASS:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36437316442 .
This is host-proven fixture replay, NOT a substitute
for actual CMS M23 command execution.

NEXT REAL CMS M23 TEST: from Mac shell currently
ibm-sandbox/src, git pull, upload GITREC.C and
GITRUN.EXEC with existing cms-upload.sh using
single c3270 instance; on real CMS invoke
CMSCLNK GITREC PLAIN, then standard GITRUN.
Expect case 2 COMMIT of known first commit to
report tree, one parent, and message length,
along with ordinary full audits, non-commit
RC8, old generation fallback, both invalid
RC8, and restored full selection. Only mark
target PASS on actual returned GITRUN ending.

## September 28 — M23 live CMS PASS; M24 next target gate

User ran live CMSCLNK GITREC PLAIN: ASSEMBLER
(XF) DONE; no statements flagged, module built
T=6.50/6.80. They ran standard GITRUN M23
READ ONLY NATIVE GIT REGRESSION, independently
GENCHECKed both 1808-object original GITFIX
and M15NEW (both FAST/PAIR/GEN RC0), selected
seq52 M15NEW digest
493F0896884B28AC4836B88328629B7E95404B46,
COMMIT-decoded the actual first commit
00D8D63229305230C8D37F884CE87F9E1A89468C:
tree 204E1D6968FB81C35BF830D63A611AC64C072945,
parent 2D5038C551318997B865497E04CF4C037DE4135E,
parents1, message 44 bytes. Its linked tree
separately decoded four entries, TREE RC0;
non-commit input was correctly rejected RC8;
new manifest unavailable recovered old seq51
with same commit metadata RC0; both unavailable
failed closed RC8; restored seq52 COMMIT RC0;
final all protected files checks passed. Exact:
GITRUN M23 ALL READ ONLY NATIVE GIT TESTS PASSED,
CMS Ready T=172.06/173.45 at 09:41:52.
Expected absent M15BAD GEN / DMSSOP036E messages
are negative-test fixtures, not incident recurrence.

Following user's rules (direct GitHub edits and
keep progressing without asking until actual CMS
needed, all target tests via standard GITRUN),
implemented M24 production native Git functionality
in src/GITREC.C:
 LSROOT C0 C1 COMMIT_OID40 — verifies commit's
 binary Git ASCII tree header and follows that
 actual tree reference to independently verify
 and decode its binary tree within the selected
 immutable generation; no intermediate output
 unless linked object is fully verified.
 PATH C0 C1 COMMIT_OID40 PATHHEX — parses raw
 path bytes from hex CMS CLI; follows each
 required tree mode and authenticated 20-byte
 OID through nested subtrees, verifies and
 rehashes final blob/tree before emitting
 PATH OBJECT TYPE, SIZE and full OID; gitlink
 mode160000 prints external commit OID without
 assuming local availability. Rejects missing,
 corrupt or wrong-type links, malformed hex,
 absolute and empty path segments, non-tree
 intermediate, both-invalid generations.
 No permanent CMS file writes in these commands.

tests/test-native-tree.py now has 1808-record
sealed synthetic generation with nested tree,
zero tree, multiple Git modes, bad linked
tree/type, missing trees (real commit's
external historic root not in fixture),
missing/invalid path, 160000 gitlink and
fallback/fail-closed/restored cases. Real
M23 fixture remains asserted for canonical
270-byte SHA1, tree, parent, count & message.
Production C89 compiled with -Wall/-Wextra/
-Werror and full host GitHub CI PASS:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36438588523 .

Standard reusable src/GITRUN.EXEC is now M24
read-only CMS batch with both full existing
generation GENCHECKs, sequence52 verification,
actual first commit LSROOT, real README.md
PATH (524541444D452E6D64) and nested
docs/STATUS.md PATH
(646F63732F5354415455532E6D64), wrong-type
LSROOT RC8, missing path RC4, non-tree
intermediate RC8, newer-manifest unavailable
older verified fallback, both manifests absent
RC8 and seq52 restored nested path, final
all protected generation/selector/PACK checks.
All current host suite including GITRUN
source read-only guard PASSED. This source
requires NEW actual CMS M24 compilation/test.
DO NOT claim target M24 proof yet.

User Mac prompt normally inside
ibm-sandbox/src. For next actual CMS gate:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
Actual CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
Do not upload unchanged GITCIDX.C, GITSEL.C,
or rebuild the eight sealed stage/index/
seek/gen or selectors. GitHub M24 does not
run obsolete TLS cleanup or disk repairs.
Always test through GITRUN, no GITRCHK
or separate manual FILEDEF command wall.

## September 28 10:01–10:07: M24 CMS PASS; M25 host complete

User successfully compiled M24 GITREC with CMSCLNK
GITREC PLAIN (no assembler warnings, T=7.08/7.36)
and executed one standard GITRUN M24 on actual
CMS. Both GITFIX and M15NEW each fully GEN2
audited 1808 unique objects. Selected seq52
M15NEW digest
493F0896884B28AC4836B88328629B7E95404B46.
LSROOT of canonical first commit
00D8D63229305230C8D37F884CE87F9E1A89468C
returned the actual 4-entry Git tree (RC0).
PATH README.md gave Git blob type3 size567 SHA1
1BA7AE466BB0A16C294D52A8642E527B07D4D1F5.
Nested PATH docs/STATUS.md gave blob type3
size5737 SHA1
46135A22C7394D8090619C6C70453C58A24F5239.
Wrong-type LSROOT RC8, missing path RC4,
non-tree intermediate RC8; missing newer
manifest recovered seq51 GITFIX (RC0),
both absent failed closed RC8, restoration
selected seq52 and authenticated nested blob
(RC0); protected generation/selector/PACK
STATE rechecks passed. Exact final line:
GITRUN M24 ALL READ ONLY NATIVE GIT TESTS PASSED
Ready; T=239.20/240.98 10:07:02.
The missing M15BAD GEN / C0GEN/C1GEN messages
were intentional negative-test fixtures.
M24 is now NATIVE CMS TARGET-PROVEN.

Without waiting for another "proceed" prompt,
implemented M25 GitHub source and native strict
host regressions. New production GITREC PATHCAT
C0NAME C1NAME COMMIT_OID40 PATHHEX traverses the
same fully authenticated linked commit and
nested tree path as target-proven PATH,
independently verifies full final blob SHA1
and only then emits PATH OBJECT TYPE/SIZE/OID
and framed PATH DATA BEGIN/END with 32 body
bytes per PATH HEX line (empty blobs have none).
Missing, wrong-type, malformed path, tree
instead of blob, gitlink instead of blob and
unavailable candidate fail closed without
disclosing PATH DATA. All operations are
read-only and preserve target 65536 object cap.

tests/test-native-tree.py now additionally
roundtrips ASCII, nested, empty, 257-byte
binary with NUL/high bytes and max 65536-byte
binary through the actual compiled C89 native
GITREC, verifies older fallback/both absent/
restoration. Pinned exact immutable original
README blob at
tests/fixtures/first-commit-README.md
(567 bytes SHA1
1BA7AE466BB0A16C294D52A8642E527B07D4D1F5).
Synthetic host stage includes independent
reconstruction of the original four-entry root
tree (SHA1 204E1D6968FB81C35BF830D63A611AC64C072945)
and the exact previously captured 270-byte
original commit, then byte-for-byte verifies
historical README via LSROOT and PATHCAT.
All expanded CI passed, including read-only
GITRUN source guard:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36441754586

Single standard src/GITRUN.EXEC is now M25
read-only CMS batch, with independent full
GENCHECK for both originals, seq52 selection,
PATHCAT real README.md 567 bytes and nested
docs/STATUS.md 5737 bytes, reject tree/missing/
non-tree intermediate cases, recover seq51
when newer GEN2 unavailable, reject both
unavailable RC8, restore seq52 with README
full output, final all protected file checks.
No persistent writes. GITCIDX.C and GITSEL.C
unchanged. M25 CMS runtime still PENDING and
must not be claimed passed before target output.

USER'S PERMANENT WORKFLOW: Continue GitHub
development autonomously until a genuine CMS
test is required. Run every CMS test via standard
GITRUN, not ad hoc commands or GITRCHK.
From Mac prompt ibm-sandbox/src:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
Then on CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
No need to upload unchanged GITCIDX/GITSEL or
rebuild protected stage/index/seek/manifests
or run historical TLS cleanup.

## September 28 10:19–10:28 — M25 live CMS PASS, M26 ready

The user ran CMSCLNK GITREC PLAIN on native z/VM
CMS; ASSEMBLER (XF) DONE, no flagged statements,
module built (T=7.18/7.47). They ran the standard
GITRUN M25 and pasted interleaved console output
ending unambiguously:
  GITRUN M25 ALL READ ONLY NATIVE GIT TESTS PASSED
  Ready; T=218.04/220.32 10:28:26
Both existing sealed GITFIX and M15NEW generations
again passed all full 1808-object native audits.
M15NEW seq52 selected. Actual production PATHCAT
emitted full Git binary hex for historical
README.md (567 bytes, OID
1BA7AE466BB0A16C294D52A8642E527B07D4D1F5)
and nested docs/STATUS.md (5737 bytes, OID
46135A22C7394D8090619C6C70453C58A24F5239).
Negative target cases returned their expected
type/path RCs, old generation fallback worked,
both missing manifests failed closed, restored
seq52 PATHCAT returned full README, protected
files STATE rechecks passed. Deliberate M15BAD
absence and C0/C1 missing GEN messages are
expected. M25 is ACTUAL CMS TARGET-PROVEN.

Following user's explicit autonomous development
and single standard GITRUN rules, independently
implemented M26 production C89 in GitHub:
  GITREC LSDIR C0NAME C1NAME COMMIT_OID40 DIRHEX
It extends the proven authenticated nested
PATH resolver, with full selected-generation
GEN2 verification, per-object Git SHA1, raw
binary names/modes and an additional requirement
that final object is a structurally sound type2
tree; emits validated TREE DATA BEGIN, TREE
ENTRY MODE/NAMELEN/OID, TREE NAMEHEX, TREE
ENTRIES, TREE DATA END. Wrong types, gitlinks,
missing or invalid paths, corrupt tree and
both-invalid generations fail closed without
TREE data. The strict production C89 host
integration tests exact nested entry, malformed
and missing targets, wrong types, fallback,
both-invalid, restoration alongside earlier
CATHEX/PATHCAT max-size and binary tests.
Single standard src/GITRUN.EXEC was advanced
to M26 with read-only checks of both protected
1808-object generations; seq52 selection;
LSDIR actual first commit's docs directory
(known historical BUILD.md/STATUS.md);
blob-as-directory RC8, missing RC4,
non-tree intermediate RC8, newer-GEN unavailable
seq51 fallback, both missing RC8, restored
seq52, final original protected-file checks.
Updated tests/check-readonly-gitrchk.sh to
guard M26 one-batch read-only behavior.
Full host CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36444249032 .
M26 CMS live test is still PENDING.

User Mac shell is usually in ibm-sandbox/src.
NEXT ACTUAL CMS M26 test, no repeated GITCIDX or
GITSEL upload; they are unchanged:
 Mac:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
 CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
Wait only for genuine user-provided CMS results,
not for repeated 'proceed'. Do not touch original
stage/index/seek/GEN/pointers, do not run obsolete
GITRUN cleanup or legacy TLS experiments.

## September 28 10:36-10:40 — M26 actual CMS PASS; compact output requested

The user compiled GITREC with CMSCLNK GITREC PLAIN,
ASSEMBLER (XF) DONE with no statements flagged
(T=7.20/7.48). Standard GITRUN M26 on real CMS
passed both independent full 1808-unique audits,
selected M15NEW seq52, and LSDIR of actual first
commit's historical docs directory returned
73-byte tree OID 980E3417BEF3170BF6CCEDFECEB81EDF1C830477
containing BUILD.md OID D4BE895844FECE160E31411ABB2ECDD6ACAECC17
and STATUS.md OID 46135A22C7394D8090619C6C70453C58A24F5239.
Blob-as-directory RC8, missing path RC4 and
non-tree intermediate RC8; missing newer
manifest recovered seq51 GITFIX (RC0); both
missing GEN2 manifests rejected RC8; restored
seq52 and verified the same directory RC0;
all protected files checked at end.
Final real CMS output: GITRUN M26 ALL READ ONLY
NATIVE GIT TESTS PASSED, T=194.96/196.38 at
10:40:21. M26 is NATIVE CMS TARGET-PROVEN.

User explicitly reports GITRUN produces 6-7
pages requiring manual copy/paste and requests
ONE PAGE OR LESS containing all diagnostics
needed to continue development. In response,
GitHub src/GITRUN.EXEC was replaced by M26Q,
a compact read-only regression that preserves
M26's complete core audits and cases but uses
CMS Pipelines `PIPE CMS <command> | STEM out.`
to capture verbose synchronous native output
in an in-memory REXX stem, inspect the actual
PIPE return code and required distinct output
markers, and emit only compact PASS/FAIL lines.
Expected test absent M15BAD STATE is also
captured in-memory. On any failure print
stage name, actual/expected RC, marker hits and
at most last four captured diagnostic lines;
fail closed RC12. Positive docs LSDIR checks
exact selected seq52, exactly two entries and
both historical BUILD.md/STATUS.md OIDs;
fallback checks seq51, both invalid checks
the actual NO FULLY VERIFIED GENERATION message.
Original protected files rechecked before
and after with STATE and never mutated.
No CMS files are used for capturing output.
The successful report is about 15 short lines,
not hundreds of progress/HEX lines.
Source read-only/summary checks updated and
full GitHub CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36446263848
M26Q source is host/CI-guarded; its CMS PIPE
integration still requires one real target
test. Do not claim CMS one-page output proven
until actual GITRUN output from user.

USER WORKFLOW: user Mac shell normally inside
ibm-sandbox/src. GITREC.C/GITCIDX.C and modules
were already target-proven with M26 and are
UNCHANGED by M26Q. To deploy concise GITRUN
only:
 Mac: git pull
 Mac: ./cms-upload.sh GITRUN.EXEC
 CMS: GITRUN
No target recompile or GITREC.C upload necessary.
Always use standard GITRUN for subsequent
CMS tests; keep compact output pattern by
default and no need for giant logs.

## September 28 10:51 — compact M26Q false failure fixed in M26Q2

User ran initial compact standard GITRUN M26Q on
actual CMS. In-memory PIPE capture worked:
GITFIX GENCHECK returned PIPE RC0 and all
required FAST AUDIT 1808, PAIR 1808,
GENERATION VERIFIED 1808 output markers were
seen (MARKERS 1 1 1 1), final diagnostic tail
was captured correctly (10 lines total).
However, REXX multi-line CALL syntax joined
the expected numeric RC and subsequent marker
text into a single expected argument, making
the GITFIX full audit wrongly report FAIL and
abort RC12. This is solely a compact EXEC
harness formatting defect, not a Git store
or GENCHECK failure.

GitHub src/GITRUN.EXEC updated to M26Q2:
defines short expected output marker variables
at top and invokes EVERY CALL gate with all
arguments on exactly ONE physical line,
avoiding REXX trailing-comma continuation.
It retains in-memory PIPE CMS ... | STEM out.,
the full independent audits, real docs directory
2-entry exact OID checks, negative RC cases,
seq51 recovery, both absent fail-closed, seq52
restore and pre/post protected STATE checks.
tests/check-readonly-gitrchk.sh fully corrected,
now rejects split CALL gate lines and persistent
CMS write commands. Entire full native host CI
PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36447522308 .
The M26Q2 compact runner is NOT yet target
proven; actual CMS run may reveal PIPE CMS
stage return-code propagation nuances on
negative cases. Keep feedback within one page
on success and last 4 diagnostics on failure.

Next MAC commands from ibm-sandbox/src:
 git pull
 ./cms-upload.sh GITRUN.EXEC
Next CMS command:
 GITRUN
No GITREC or GITCIDX recompile/upload is needed;
M26's compiled module itself is already real
target-proven. NEVER run old cleanup GITRUN.

## September 28 11:05 — M26Q2 one-page target CMS PASS

User ran the updated standard GITRUN M26Q2 on
actual CMS, producing a compact 15-line report:
GITRUN M26Q2 COMPACT REPORT
PASS PROTECTED FILES AND ABSENT TEST MANIFEST
PASS GITFIX FULL AUDIT RC 0
PASS M15NEW FULL AUDIT RC 0
PASS SELECT SEQ52 RC 0
PASS DOCS HAS TWO VERIFIED ENTRIES RC 0
PASS BLOB IS NOT DIRECTORY RC 8
PASS MISSING DIRECTORY RC 4
PASS NON TREE INTERMEDIATE RC 8
PASS RECOVERED SEQ51 RC 0
PASS BOTH INVALID FAIL CLOSED RC 8
PASS RESTORED SEQ52 RC 0
PASS FINAL PROTECTED FILES
GITRUN M26Q2 ALL READ ONLY NATIVE GIT TESTS PASSED
Ready; T=195.18/196.47 11:05:02.
No raw FAST AUDIT progress or tree data was printed.
This PROVES the CMS `PIPE CMS ... | STEM out.`
in-memory capture, REXX single-line CALL gate
argument semantics and positive and intentional
negative PIPE return code propagation all work.
Going forward, EVERY STANDARD GITRUN CMS gate
MUST produce ONE PAGE OR LESS: short PASS/FAIL
stage summary; on failure observed/expected RC,
marker hits and last four captured diagnostic
lines. Never ask the user to paste multi-page
audit or 5737-byte PATHCAT data again. Keep
no CMS persistent writes and preserve the
independent 1808-object dual-generation
audits and existing recovery/fail-closed tests.
M26Q2 compact console contract is TARGET PROVEN.
Continue next independent native source/host
development and use standard GITRUN for next
one-page CMS target gate.

## September 28 11:05 M26Q2 passed; M27 host-complete next gate

User's actual standard GITRUN M26Q2 produced
exactly the desired ONE-PAGE compact report.
PASS protected files, separate GITFIX and
M15NEW complete 1808-unique GENCHECK, seq52
M15NEW selection, verified historic docs
directory two entries, wrong-type RC8, missing
path RC4, non-tree intermediate RC8, seq51
GITFIX recovery, both invalid fail-closed RC8,
restored seq52 and final protected checks.
Exact final:
GITRUN M26Q2 ALL READ ONLY NATIVE GIT TESTS PASSED
Ready T=195.18/196.47 11:05:02.
CMS PIPE ... | STEM in-memory output capture,
REXX GATE return codes for both success and
intentional failure, one-line CALL syntax
and compact diagnostic behavior are now
TARGET PROVEN. User will not babysit or
paste multi-page logs again: ALL FUTURE
standard GITRUN test suites MUST fit one page
on success, last four diagnostic lines on
failure, without dumping raw progress or hex.

Immediately progressed independently to
M27 production C89 GITREC FIRSTPAR C0NAME
C1NAME COMMIT_OID40: fully audits selected
GEN2 generation; validates and rehashes child
commit; reads first-parent raw Git ASCII OID;
locates, rehashes and validates first-parent
commit in SAME sealed generation; outputs
FIRST PARENT VERIFIED, full parent OID and
parent tree OID only after BOTH objects are
verified. Wrong-type/malformed/missing child
or parent fail closed RC4 or RC8 without
parent metadata; root commit returns RC4,
both unavailable RC8. Strict compiled
production C89 test extended with staged
two-parent merge, root, missing parent,
blob as parent, structurally invalid
parent, wrong-type child, seq51 recovery,
both invalid and seq52 restoration.
Previous CATHEX/TREE/COMMIT/PATH/PATHCAT/LSDIR
and max 65536 binary tests remain passing.
FULL NATIVE HOST CI:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36450050947

The ONE standard src/GITRUN.EXEC is now M27
COMPACT REPORT: checks original protected
objects, two independent full 1808-object
audits, seq52 selector, FIRSTPAR of actual
first commit OID
00D8D63229305230C8D37F884CE87F9E1A89468C
with exact historical parent
2D5038C551318997B865497E04CF4C037DE4135E
and GitHub-verified parent tree
F3EF36AAD778D5DA84857D8DED46495C75F4CAB0,
wrong-type and missing-commit negative tests,
seq51 recovery, both absent RC8, restored
seq52 and post-protected STATE checks.
All CMS native outputs captured in REXX STEM
and GATE verified against exact markers and RC;
no persistent CMS file writes. The standard
read-only GITRUN source guard now enforces
compact M27 stages and no multiline REXX
CALL GATE lists, and full host CI passed.
M27 has NOT YET run on live CMS.

User's Mac prompt typically ibm-sandbox/src.
Next target work requires ONLY Mac:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
Then real CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
Keep response/request compact; no changed
GITCIDX.C or GITSEL.C. Never run old cleanup,
rebuild protected original generations, or
claim target M27 PASS before real console.

## September 28 11:23–11:26 — M27 live CMS PASS; M28 host complete

Actual z/VM CMS: user uploaded latest M27
GITREC.C and GITRUN.EXEC; CMSCLNK GITREC PLAIN
reported ASSEMBLER (XF) DONE with no flags
(T=7.48/7.77); standard GITRUN M27 COMPACT
REPORT ran entirely and returned:
 PASS protected files/absent fixture
 PASS GITFIX FULL AUDIT RC0
 PASS M15NEW FULL AUDIT RC0
 PASS SELECT SEQ52 RC0
 PASS FIRST PARENT VERIFIED RC0
 PASS NON COMMIT INPUT RC8
 PASS MISSING COMMIT RC4
 PASS RECOVERED FIRST PARENT RC0
 PASS BOTH INVALID FAIL CLOSED RC8
 PASS RESTORED FIRST PARENT RC0
 PASS FINAL PROTECTED FILES
 GITRUN M27 ALL READ ONLY NATIVE GIT TESTS PASSED
 Ready; T=171.82/172.92 at 11:26:34.
First-parent traversal and the single-page
GITRUN are now proven on actual CMS. Continue
to preserve <1 page target console reporting,
PIPE CMS ... | STEM out. in-memory capture,
single-physical-line REXX CALL gate invocations,
read-only stage/index/GEN/selector/PACK access.
Do not request full raw audit or hex dump logs.

Autonomously implemented M28 in current GitHub
main: production native C89 GITREC ANCESTOR
C0 C1 COMMIT_OID40 DEPTH (strict numeric depth
1-16) follows a bounded series of first-parent
links within the SAME fully GEN2-verified sealed
generation. Every traversed commit is located,
fully independently SHA1 verified and structurally
validated before attempting the next link.
Only the final, fully verified ancestor's
40-hex object ID, tree ID and depth are printed,
no partial output on missing/corrupt links.
Depth0/bad/out-of-range values RC4; root reached
too early RC4; absent link RC4, invalid type/
structure RC8, both-invalid full generations
RC8 without ancestor output. Preserves all
historical native functionality.

Strict host integration tests compile actual
native GITREC/GITCIDX C89 -Werror against
1808-object sealed fixture including a new
three-commit first-parent chain (grandchild,
two-parent merge and root), success at depth1/2,
root exhaustion at depth3, invalid depths,
missing/corrupt/wrong-type links, seq51 recovery,
both missing RC8 and seq52 restore. Full CI
PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36451606606

Standard src/GITRUN.EXEC is M28 COMPACT, preserving
both independent 1808-object original audits,
read-only protected files pre/post, seq52
selection, real known commit OID
00D8D63229305230C8D37F884CE87F9E1A89468C.
New M28 one-page checks first parent depth1
2D5038C551318997B865497E04CF4C037DE4135E,
depth2 historical grandparent GitHub SHA
C67A53164ADFC6FDEB708F13F1822E2CF24C060C
tree B8A987847912D6B67C1064D5361F5A9E5868DC18;
invalid depth RC4, noncommit RC8, older-seal
fallback at depth2, both unavailable RC8, full
restored depth2. Host CI source guard enforces
one-line GATE calls and read-only commands.
M28 target CMS run is PENDING, not yet proven.

User Mac normally at ibm-sandbox/src.
M28 next actual target step:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
Real CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
No protected files rebuilt, no extra source
uploads, no manual FILEDEF command sequences.

## September 28 11:47 — M28 CMS compile failed; fixed on GitHub

User uploaded M28 GITREC.C and GITRUN.EXEC
and ran CMSCLNK GITREC PLAIN on real CMS:
<stdin>: In function main:
<stdin>:578: 'ance' undeclared;
<stdin>:578: syntax error before 'stor';
CMSCLNK: C compile failed, Ready(00012),
T=6.03/6.15 11:47:44.
The exact source line 577 contained an
87-character OR expression ending in
"||ancestor)&&". CMS GCCCMS toolchain
truncated source records near 72 columns,
splitting token ancestor into "ance"/"stor".
Two other new lines (length79) in GITREC
also exceeded 72. The already-compiled M27
GITREC module is unaffected by unsuccessful
compilation; M28 GITRUN was not run.

Fixed all 3 long lines directly in GitHub
src/GITREC.C, wrapping declarations and
logical predicates so NO source line exceeds
72 columns, commit
952cc7b9145f9f74e089aa1e46d9dbddadc70935.
Added persistent native CI guard in existing
tests/check-cmsclnk-source.sh to reject ANY
GITREC.C line >72 before host test success
can be reported, commit
235d8e4bd523d3431badb3238b3ff45259d6a630.
Full host workflow PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36453892515 .
User M28 compact GITRUN.EXEC already uploaded
and unchanged; no repeat upload necessary.
Only ask Mac from ibm-sandbox/src:
 git pull
 ./cms-upload.sh GITREC.C
Real CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
GITCIDX and GITSEL unchanged. Retain compact
one-page GITRUN PIPE-to-REXX-STEM summary and
read-only sealed generation checks. M28 CMS
target PASS still pending the corrected compile
and actual GITRUN output; do not claim success.

## September 28 11:54–11:57 M28 actual CMS PASS

User re-uploaded 72-column-safe M28 GITREC.C
following the earlier GCCCMS compile failure.
Real CMSCLNK GITREC PLAIN: ASSEMBLER (XF)
DONE, zero statements flagged, GITREC MODULE
PLAIN built T=7.78/8.07 at 11:54:29.
Standard one-page GITRUN M28 then completed
fully on real CMS:
 PASS PROTECTED FILES AND ABSENT TEST MANIFEST
 PASS GITFIX FULL AUDIT RC0
 PASS M15NEW FULL AUDIT RC0
 PASS SELECT SEQ52 RC0
 PASS ANCESTOR DEPTH1 RC0
 PASS ANCESTOR DEPTH2 RC0
 PASS INVALID DEPTH RC4
 PASS NON COMMIT INPUT RC8
 PASS RECOVERED DEPTH2 RC0
 PASS BOTH INVALID FAIL CLOSED RC8
 PASS RESTORED DEPTH2 RC0
 PASS FINAL PROTECTED FILES
 GITRUN M28 ALL READ ONLY NATIVE GIT TESTS PASSED
 Ready T=172.80/173.94 at 11:57
(actual seconds in pasted log truncated).
This PROVES bounded 2-hop native Git ancestry,
strict invalid-depth handling, fallbacks,
both-missing fail-closed, compact console
reporting and protected originals on target.
The prior CMS line-truncation fix is target-
proven, and the permanent GITREC.C 72-column
CI guard stays mandatory. M28 now COMPLETE.

User requires autonomous GitHub development
until next genuine CMS test, every CMS test
via one standard GITRUN and output one page
or less. Keep original 1808-object generation
files and selectors read-only; no repeated
manual FILEDEF sequences, no changes to
unchanged GITCIDX/GITSEL.

## September 28 11:54–11:57 — M28 LIVE CMS PASS, M29 READY

User uploaded the 72-column-corrected M28
GITREC.C and built using CMSCLNK GITREC PLAIN:
ASSEMBLER (XF) DONE, no statements flagged;
GITREC MODULE mode PLAIN built, T=7.78/8.07.
Standard GITRUN M28 COMPACT REPORT then passed
on real CMS:
 PASS protected originals/absent M15BAD GEN
 PASS GITFIX/M15NEW independent 1808 full audits
 PASS seq52 M15NEW
 PASS ANCESTOR DEPTH1 RC0
 PASS ANCESTOR DEPTH2 RC0
 PASS invalid depth RC4
 PASS noncommit RC8
 PASS recovered depth2 seq51 RC0
 PASS both missing GEN2 fail closed RC8
 PASS restored depth2 seq52 RC0
 PASS final protected originals
 GITRUN M28 ALL READ ONLY NATIVE GIT TESTS PASSED
 Ready T=172.80/173.94 11:57 (seconds truncated).
M28 is NATIVE TARGET-PROVEN. Permanent strict
72-column CMS GITREC.C source guard and
one-page GITRUN with PIPE CMS to STEM are
both target-proven and still required.

Autonomously developed M29 on GitHub main:
Production native C89 GITREC HISTORY C0 C1
COMMIT_OID40 DEPTH, where DEPTH=1..16 first-
parent links. It selects one fully GEN2
audited generation, SHA1-rehashes and
structurally validates EVERY traversed commit
there, stores up to 17 commit/tree IDs in
fixed arrays, and emits framed HISTORY HOP
index, OID, TREE, HISTORY HOPS and DATA END
ONLY after the entire requested chain passes.
No partial success metadata when reaching
root early (RC4), missing (RC4), wrong-type
or malformed parent (RC8), or both invalid
generations RC8. No persistent writes.
Earlier M28 ANCESTOR command and error string
remain backward compatible.

tests/test-native-tree.py native strict C89
host integration now tests 2-hop history on
grandchild/merge/root synthetic fixture,
exact OIDs and trees, no partial output for
missing/malformed links, root exhaustion,
invalid depths, old-generation seq51 fallback,
both-invalid failure and restored seq52.
Existing M0-M28 tests still pass, including
binary PATHCAT and full 1808-unique audits.
Standard src/GITRUN.EXEC is now M29 compact
one-page gate: full independent GENCHECK for
GITFIX/M15NEW, exact seq52 selection, real
original first commit
00D8D63229305230C8D37F884CE87F9E1A89468C
HISTORY depth2, matching historical parent
2D5038C551318997B865497E04CF4C037DE4135E
and grandparent
C67A53164ADFC6FDEB708F13F1822E2CF24C060C
with tree B8A987847912D6B67C1064D5361F5A9E5868DC18,
invalid depth RC4, noncommit RC8,
seq51 fallback, both unavailable RC8,
seq52 restore and final original file checks.
All output captured in-memory by PIPE-to-STEM;
only approx 13 short PASS lines printed.
Both C89 host tests, all native CI and
read-only source guard PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36463930319 .
M29 is HOST-PROVEN ONLY, needs actual CMS test.

NEXT actual CMS gate from user's usual Mac
ibm-sandbox/src:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
Actual CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
No GITCIDX/GITSEL changes, no original
stage/index/seek/GEN or selector modifications.
Never regress to multi-page logs or manual
FILEDEF commands. Only mark M29 target-proven
once user supplies actual compact PASS output.

## September 28 13:26–13:27 — M29 CMS output truncation; fix green

User compiled M29 GITREC successfully on actual
CMS with CMSCLNK GITREC PLAIN (ASSEMBLER XF,
zero flagged statements, T=7.98/8.30 at 13:26:08).
Standard single-page GITRUN M29 then passed both
independent 1808-object GITFIX/M15NEW audits,
seq52 selection, and GITREC HISTORY depth2
returned RC0. The compact GATE observed
HISTORY HOPS 2, known parent OID
2D5038C551318997B865497E04CF4C037DE4135E
and grandparent OID
C67A53164ADFC6FDEB708F13F1822E2CF24C060C,
but fourth marker (complete second ancestor TREE
B8A987847912D6B67C1064D5361F5A9E5868DC18)
was absent. CMS PIPE-to-STEM captured truncated
native lines, for example HISTORY HOP 2 OID
C67A53164... TREE B8A987847912D6B6,
because M29 printed OID and tree (2x40 hex)
on one line exceeding CMS text record width.
Observed GATE: FAIL VERIFIED HISTORY TWO HOPS
RC0 EXPECTED0, MARKERS 1 1 1 0; intentional
abort RC12. This is an output formatting issue,
NOT a staged Git-data or ancestry verification
failure. Target M29 full GITRUN PASS is pending.

Fixed production src/GITREC.C to print each
HISTORY HOP index's OID and TREE on SEPARATE
short 80-column-safe records, only after
entire chain is validated. The standard M29
GITRUN.EXEC is UNCHANGED; its existing exact
grandparent TREE marker will now match the
complete short TREE record. The native C89
host regression tests were updated to
independently check each OID and TREE line
and enforce all history output lines <=80
characters, preventing recurrence. All
expanded native host CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36465703179 .
This change is read-only and does not touch
original STAGE/INDEX/SEEK/GEN/selector/PACK.

Next user Mac (usual ibm-sandbox/src):
 git pull
 ./cms-upload.sh GITREC.C
Then real CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
No GITRUN upload, other source upload or
protected data rebuild needed. Continue
single-page compact GITRUN CMS reporting,
and mark M29 actual CMS PASS only if real
corrected output finishes successfully.

## September 28 13:34–13:36 — M29 actual CMS PASS

User compiled corrected (short CMS output-record) M29
GITREC.C with CMSCLNK GITREC PLAIN: ASSEMBLER XF
DONE, no flagged statements, GITREC PLAIN built,
T=8.07/8.40 at 13:34:02. Single-page GITRUN
M29 passed live z/VM CMS:
 PASS original protected files/absent test GEN
 PASS GITFIX/M15NEW independent 1808 full audits
 PASS seq52 M15NEW selected
 PASS VERIFIED HISTORY TWO HOPS RC0
 PASS INVALID DEPTH RC4
 PASS NON COMMIT INPUT RC8
 PASS RECOVERED HISTORY RC0
 PASS BOTH INVALID FAIL CLOSED RC8
 PASS RESTORED HISTORY RC0
 PASS final protected originals
 GITRUN M29 ALL READ ONLY NATIVE GIT TESTS PASSED
 Ready T=150.68/151.64 at 13:36:37.
Native HISTORY complete commit+tree OID records,
two-hop traversal, generation fallback and fail
closed behavior now TARGET-PROVEN. The 72-column
GITREC.C guard and single-page GITRUN PIPE-STEM
capture remain mandatory. The immutable original
STAGE/INDEX/SEEK/GEN, selector and GITPBUF PACK
files must not be rewritten. Continue autonomously
with next native read-only feature, update same
standard GITRUN only; never request long raw logs.

## September 28 13:34–13:36 — M29 target PASS; M30 host verified

User compiled the shortened-output-record M29 GITREC
with CMSCLNK GITREC PLAIN on live z/VM CMS;
ASSEMBLER (XF) DONE, no flagged statements;
GITREC module built T=8.07/8.40 at 13:34:02.
Standard one-page GITRUN M29 completed all tests:
GITFIX/M15NEW independent 1808-object audits RC0,
seq52 selected, HISTORY depth2 RC0 with full
parent/grandparent OIDs and tree IDs on separate
CMS-safe records, invalid depth RC4, noncommit
RC8, recovered seq51 RC0, both unavailable
fail closed RC8, restored seq52 RC0 and final
protected originals checks. Exact:
GITRUN M29 ALL READ ONLY NATIVE GIT TESTS PASSED
Ready T=150.68/151.64 at 13:36:37.
M29 is ACTUAL CMS TARGET PROVEN.

Immediately developed M30 production C89
GITREC PARENT C0NAME C1NAME COMMIT_OID40 N
where N is a strict decimal one-based ordinal
1..16, supporting both first and later Git
merge parents. It selects a fully independently
GEN2-audited original sealed generation,
rehashes and fully validates the child commit's
Git binary parent headers, selects precisely
Nth parent, checks that the parent is actually
staged as a COMMIT in the SAME generation,
rehashes and validates the parent's entire
commit header, then emits short PARENT VERIFIED
ORDINAL, PARENT OID and PARENT TREE records.
Absent ordinal or missing staged parent returns
RC4; invalid child/parent type/structure or
both invalid generations fail closed RC8.
No persistent writes and all GITREC source
records remain <=72 columns.

Native strict C89 host test added a new fully
staged second parent and a real two-parent
synthetic merge, verified both 1st/2nd ordinals,
missing 3rd ordinal, root absent first parent,
missing/wrong type/malformed parent,
invalid ordinal, seq51 fallback, both unavailable
and seq52 restored. Existing historical original
commit fixture and M0–M29 tests still run.
Full native CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36467257408
This successful CI SHA 3b54aef77ee40f61be82d58bc3b00dcf937dd4da
includes latest production M30 C, standard
M30 GITRUN and source guards. Prior failed CI
runs were a host fixture unique-count assertion
stale at 21 when two new distinct objects
made 23; assertion was corrected and rerun PASS.

Standard one-page src/GITRUN.EXEC now M30:
protect originals, both 1808 independent
GENCHECK audits, seq52 select, first original
commit OID 00D8D63229305230C8D37F884CE87F9E1A89468C
PARENT ordinal 1 authenticates historical
parent 2D5038C551318997B865497E04CF4C037DE4135E
with parent tree F3EF36AAD778D5DA84857D8DED46495C75F4CAB0;
the original commit has no second parent (RC4).
Additional invalid zero ordinal RC4 and
noncommit child RC8, seq51 fallback,
both unavailable RC8, restored seq52 and
protected originals final STATE. All detailed
output held in-memory PIPE CMS to STEM; only
approx 14 compact PASS lines, on failure
last four diagnostics. Read-only GITRUN
source guard updated and host CI PASS.
M30 live CMS compile/GITRUN NOT yet run.

User Mac typically at ibm-sandbox/src.
Next real M30 target:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
Real CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
Do not upload unchanged GITCIDX/GITSEL,
touch original protected data or use auxiliary
CMS test runners. Continue autonomously
after real M30 target result.

## September 28 13:46–13:49 — M30 actual CMS target PASS

User compiled M30 GITREC.C on real z/VM CMS:
CMSCLNK GITREC PLAIN, ASSEMBLER (XF) DONE,
no statements flagged, module PLAIN built
T=8.28/8.61 at 13:46:45. Standard one-page
GITRUN M30 completed fully:
PASS both independent 1808-object full audits,
seq52 selection, PARENT ordinal1 RC0 verified
historic parent and tree, missing ordinal2 RC4,
invalid ordinal0 RC4, noncommit child RC8,
older seq51 recovery RC0, both unavailable
fail closed RC8, newer seq52 restoration RC0,
and final original protected-file checks.
Exact target final:
GITRUN M30 ALL READ ONLY NATIVE GIT TESTS PASSED
Ready T=172.35/173.54 at 13:49:42.
M30 numbered-parent retrieval is now ACTUAL
CMS TARGET-PROVEN, including compact output
and recovery; all original generations,
selectors and GITPBUF PACK unchanged.
Continue next native feature independently
on GitHub. Keep <=72 C source columns,
CMS output lines <80 characters,
single standard one-page read-only GITRUN,
in-memory PIPE CMS to STEM, full two-generation
audits and negative/recovery/restoration tests.

## September 28 13:46–13:49 M30 CMS PASS; M31 host-green

Actual user CMS console: CMSCLNK GITREC PLAIN
ASSEMBLER (XF) DONE, no statements flagged,
GITREC MODULE PLAIN built, T=8.28/8.61 at
13:46:45. Standard one-page GITRUN M30
completed all PASS: protected original STATE
and absent M15BAD, independent full 1808-object
GENCHECK GITFIX/M15NEW RC0, seq52 M15NEW
select RC0, numbered parent ordinal1 RC0
(actual historic parent OID
2D5038C551318997B865497E04CF4C037DE4135E
and parent tree F3EF36AAD778D5DA84857D8DED46495C75F4CAB0),
absent second parent RC4, invalid ordinal
RC4, noncommit child RC8, recovered seq51
RC0, both manifests unavailable RC8,
restored seq52 RC0, final protected files
present. Final line:
 GITRUN M30 ALL READ ONLY NATIVE GIT TESTS PASSED
 Ready T=172.35/173.54 13:49:42.
M30 numbered Git parent authentication and
one-page compact GITRUN are TARGET PROVEN.

Without pausing, autonomously developed
M31 production native strict C89
 GITREC PARENTS C0NAME C1NAME COMMIT_OID40
which authenticates ALL parents of a merge
commit atomically. After full verified
GEN2 selection, checks child's type, raw
Git SHA1 and complete header structure;
collects up to 16 raw first/second/... parent
OIDs in order BEFORE fetching parent objects,
then each parent in SAME sealed generation
must be staged type1, SHA1-rehashed and
complete commit structure validated.
Emits framed PARENTS DATA with one CMS-safe
short ordinal/OID and ordinal/TREE line
per parent, PARENTS COUNT and DATA END ONLY
after full success; zero-parent root returns
count0. Missing parent RC4, wrong-type/
malformed parent RC8, no partial output.
No original protected file writes, no C
source lines >72.

Native C89 host integration extends authentic
synthetic two-parent merge/second root fixture,
tests both exact merge parent OIDs and trees,
zero-parent root, missing/wrong-type/malformed
parents, bad child, seq51 fallback, both
unavailable RC8 and restored seq52, preserving
all prior full native tests. Standard one-page
src/GITRUN.EXEC M31 tests historical first
commit's count1 and known exact parent/tree,
noncommit input RC8, missing child RC4,
seq51 fallback, both invalid RC8, restored
seq52, independent real 1808-object GENCHECK
for both immutable originals and final
all-protected STATE. PIPE CMS ... | STEM
in-memory capture, no lengthy logs.
tests/check-readonly-gitrchk.sh updated.
Complete host CI SUCCESS:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36468308462

M31 HOST PASS ONLY, needs actual live CMS
compile and standard one-page GITRUN to
prove target. User Mac prompt ibm-sandbox/src:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
Do not touch original GITFIX/M15NEW
STAGE/INDEX/SEEK/GEN, selectors or GITPBUF
PACK. GITCIDX.C/GITSEL.C unchanged and
need no new upload. After target M31
results, continue independently.

## September 28 13:55–13:58 — M31 LIVE CMS PASS

User compiled M31 GITREC C89 on real z/VM CMS:
CMSCLNK GITREC PLAIN, ASSEMBLER (XF) DONE,
NO STATEMENTS FLAGGED, GITREC MODULE mode PLAIN
built at 13:55:12 (T=8.67/9.02).
The single standard compact GITRUN M31 then
passed every target regression:
 protected originals and absent M15BAD GEN
 both original independent 1808-object
  GITFIX/M15NEW full audits RC0
 selected seq52 M15NEW RC0
 atomic PARENTS list RC0
 noncommit child RC8
 missing child RC4
 recovered seq51 parents RC0
 both missing GEN2 fail-closed RC8
 restored seq52 parents RC0
 protected originals final STATE present
 GITRUN M31 ALL READ ONLY NATIVE GIT TESTS PASSED
 Ready T=172.13/173.25 at 13:58:09.
M31 atomic full Git merge-parent listing is
ACTUAL CMS TARGET-PROVEN. Keep one-page
GITRUN, native C records <=72 columns,
output lines <=80, and original sealed
generations, selector pointers and PACK
untouched. Continue GitHub host development
autonomously before next actual target test.

## September 28 13:55–13:58 — M31 native CMS PASS; M32 host-green

Actual CMSCLNK GITREC PLAIN: assembler XF done,
no flagged statements, module built T=8.67/9.02
at 13:55:12. Standard one-page GITRUN M31
completed ALL tests on live CMS: protected originals,
both GITFIX/M15NEW original 1808-object independent
audits RC0, seq52 selected, verified complete
parent list RC0, noncommit RC8, missing child RC4,
seq51 fallback RC0, both manifests absent RC8,
restored seq52 RC0 and all original STATE present.
Exact final marker:
 GITRUN M31 ALL READ ONLY NATIVE GIT TESTS PASSED
 Ready T=172.13/173.25 at 13:58:09.
M31 is ACTUAL CMS TARGET-PROVEN.

Autonomously implemented M32 in GitHub main.
Production src/GITREC.C extends existing
rec_parents with optional full parent-root
tree validation, new read-only CLI:
 GITREC PARENTROOTS C0NAME C1NAME COMMIT_OID40
After full GEN2 audit and verified selection,
rehashes and structurally parses child commit,
each referenced parent commit (max 16), and
EACH parent's root tree referenced by its
raw Git ASCII tree header, all within SAME
selected immutable generation. Roots must
be staged Git type2 trees, independently
SHA1-rehashed and fully binary-tree parsed
before any PARENTS DATA is emitted. On
success emits PARENT ROOT TREES VERIFIED
and existing short CMS-safe complete parent
list with ordinal OIDs/trees and count.
Missing parent root RC4, bad type or invalid
tree RC8; no partial list, no persistent writes.
Previously target-proven PARENTS behavior
unchanged.

Strict host native C89 regression added
synthetic merge parent references for
missing tree, blob-as-tree and malformed
tree; tests both valid parent roots,
zero-parent root, missing parent object,
no partial output, older seq51 recovery,
both invalid fail-closed and restored seq52,
alongside ALL original M0–M31 tests.
Synthetic sealed fixture expands from 23
to 27 unique objects, still 1808 staged.
C89 source lines stay <=72 columns.
Standard src/GITRUN.EXEC now M32 one-page
read-only full target suite: independent
GITFIX/M15NEW full 1808-object audits,
seq52 select, PARENTROOTS real historic
commit with known parent/tree and marker,
bad child RC8, missing child RC4,
older seq51 recovery, both unavailable RC8,
seq52 restoration, final protected STATE.
Host source guard updated to M32.
Complete GitHub native CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36470706971
M32 is HOST PROVEN; actual CMS compile and
GITRUN has NOT run.

Next user Mac from ibm-sandbox/src:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
Actual CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
DO NOT rewrite protected original GITFIX/
M15NEW STAGE INDEX SEEK GEN, pointers or
GITPBUF PACK. GITCIDX and GITSEL unchanged.
No auxiliary test runner or manual FILEDEF.
All subsequent target logs one-page compact.

## September 28 14:17–14:20 — M32 REAL CMS PASS

User uploaded M32 GITREC.C and GITRUN.EXEC
and compiled on actual z/VM CMS:
CMSCLNK GITREC PLAIN, ASSEMBLER (XF) DONE,
NO STATEMENTS FLAGGED, built GITREC MODULE
mode PLAIN, T=8.71/9.01 at 14:17:38.
Standard one-page GITRUN M32 completed:
 PASS protected originals and absent M15BAD
 PASS GITFIX FULL AUDIT 1808 objects RC0
 PASS M15NEW FULL AUDIT 1808 objects RC0
 PASS SELECT SEQ52 RC0
 PASS VERIFIED PARENT ROOTS RC0
 PASS NON COMMIT CHILD RC8
 PASS MISSING CHILD RC4
 PASS RECOVERED ROOTS RC0
 PASS BOTH INVALID FAIL CLOSED RC8
 PASS RESTORED ROOTS RC0
 PASS FINAL PROTECTED FILES
Exact final:
GITRUN M32 ALL READ ONLY NATIVE GIT TESTS PASSED
Ready T=172.79/173.90 at 14:20:37.
M32 PARENTROOTS full parent-commit and
parent-root-tree authentication is now
ACTUAL CMS TARGET-PROVEN. Keep one-page
GITRUN using PIPE CMS ... | STEM, all
original generations/selector pointers/
GITPBUF PACK read-only; GITREC.C <=72
columns and output records <=80.
Proceed autonomously to next native feature
and update only standard GITRUN for target.

## September 28 14:17–14:20 — M32 target PASS; M33 host green

User ran live CMSCLNK GITREC PLAIN for M32,
ASSEMBLER (XF) DONE with no flagged statements,
built PLAIN MODULE at 14:17:38 T=8.71/9.01.
Standard one-page GITRUN M32 passed:
PASS protected originals/absent M15BAD GEN,
independent original GITFIX and M15NEW
1808-object full GENCHECK audits RC0,
select seq52 RC0, verified parent root
trees RC0, noncommit child RC8, missing
child RC4, recovered seq51 roots RC0,
both missing generation manifests failed
closed RC8, restored seq52 roots RC0,
final protected file integrity PASS.
Exact:
GITRUN M32 ALL READ ONLY NATIVE GIT TESTS PASSED
Ready T=172.79/173.90 at 14:20:37.
M32 actual z/VM CMS TARGET PROVEN.

Immediately implemented M33 on GitHub main:
production strict C89 native GITREC COMMITROOTS
C0NAME C1NAME COMMIT_OID40. Extends proven
PARENTROOTS: after one fully audited GEN2
generation selection, validates SHA1 and
structure of supplied child commit, every
parent commit (max16) and EVERY parent
root tree, and ALSO validates child commit's
own root tree as real staged SHA1-authenticated
structurally valid Git type2 tree. All
within SAME selected generation. Emits short
COMMIT ROOTS VERIFIED marker and framed
complete PARENTS list ONLY after all pass;
missing trees RC4, non-tree/malformed trees
RC8 and no partial parent metadata. Zero
parent root commit still requires its own
root tree. No protected file writes.
Existing PARENTS and PARENTROOTS unchanged.

Native strict C89 host integration now tests
both root trees of a synthetic two-parent
merge, root commit, missing/wrong-type/
malformed CHILD root trees, missing/wrong-
type/malformed PARENT root trees, missing
parent commit, noncommit child, older seq51
fallback, both unavailable RC8, restored
seq52 and previous native regressions.
No changes to 1808 staged fixture objects
or protected CMS originals. Source remains
<=72 columns; output records <=80.
Standard M33 compact one-page src/GITRUN.EXEC
uses real historic first commit, validates
its own root plus known parent root, checks
noncommit/missing child, seq51 fallback,
both-missing RC8, seq52 restore and pre/post
protected STATE. In-memory PIPE CMS to STEM.
Readonly GITRUN guard updated; complete
GitHub CI PASS:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36472033887
M33 HOST-PROVEN, still needs real CMS test.

NEXT Mac from ibm-sandbox/src:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
No GITCIDX/GITSEL changes, original GITFIX/
M15NEW STAGE/INDEX/SEEK/GEN, selectors and
GITPBUF PACK stay read-only. Single one-page
GITRUN is only required CMS regression;
do not introduce auxiliary manual gates.

## September 28 14:47–14:51 — M33 live CMS PASS

Actual z/VM CMS:
 CMSCLNK GITREC PLAIN
 ASSEMBLER (XF) DONE
 NO STATEMENTS FLAGGED IN THIS ASSEMBLY
 CMSCLNK: built GITREC MODULE mode PLAIN
 Ready T=8.85/9.18 14:48:08.
Standard one-page GITRUN M33 COMPACT REPORT
passed every case: protected original files
and absent M15BAD manifest, both independent
GITFIX/M15NEW original 1808-object GENCHECK
audits RC0, seq52 M15NEW select RC0,
verified supplied commit's OWN root tree
and every parent COMMIT and PARENT root tree
COMMITROOTS RC0, noncommit child RC8, missing
child RC4, older seq51 recovery RC0, both
generation manifests unavailable RC8 fail
closed, newer seq52 restored RC0 and final
protected originals STATE PASS. Exact marker:
 GITRUN M33 ALL READ ONLY NATIVE GIT TESTS PASSED
 Ready T=172.95/174.07 14:51:04.
M33 is now ACTUAL CMS TARGET-PROVEN.
Retain source <=72 columns, console output
lines <=80, independent original dual 1808-
object audits and standard one-page in-memory
PIPE CMS ... | STEM GITRUN for future gates.
Original staged generations, selectors,
pack and unchanged GITCIDX/GITSEL stay
immutable/read-only. Continue independently
on next native Git feature.

## September 28 14:47–14:51 — M33 LIVE CMS PASS; M34 HOST GREEN

User ran actual CMSCLNK GITREC PLAIN for M33:
ASSEMBLER XF DONE, no flagged statements,
built GITREC PLAIN module T=8.85/9.18
at 14:48:08. Standard single-page M33 GITRUN
then passed BOTH independent original 1808-
object GITFIX/M15NEW audits RC0, seq52 select,
COMMITROOTS verified supplied commit own root,
every parent commit/root RC0; negative noncommit
RC8, missing child RC4, seq51 recovered graph
RC0, both unavailable failed closed RC8,
seq52 restored RC0, final protected originals
PASS. Exact:
GITRUN M33 ALL READ ONLY NATIVE GIT TESTS PASSED
Ready T=172.95/174.07 at 14:51:04.
M33 is ACTUAL CMS TARGET-PROVEN.

Independently implemented native M34 ROOTLINKS
in GitHub main, adding to M33 auth of child
commit/own root and each parent commit/root
verification of ALL directly referenced root
tree entries, mode-appropriate Git blob/tree
type, SHA1 rehash, and structure for directly
linked subtrees. Gitlinks mode 160000 refer
to external repos and skip local verification.
Static C89 bound maximum 256 direct entries
per root prevents excessive CMS memory usage.
Not recursively walking nested tree contents.
Atomic output: no ROOT DIRECT LINKS VERIFIED
or parent listing until every required
object passes within same selected GEN2.
Missing referenced entry RC4; wrong-type
or malformed subtree RC8; no original
data writes. C source <=72 columns,
console output <=80; GITCIDX/GITSEL untouched.

Synthetic native host fixture remains
1808 objects, now 34 unique and includes
missing direct blob, wrong-type direct
blob (tree object), invalid direct subtree
and invalid parent direct entry. Tests
valid two-parent merge and zero-parent
root, missing/type/subtree negative cases,
seq51 fallback, both invalid fail closed,
restored seq52 and previous M0-M33
regressions. Standard one-page read-only
src/GITRUN.EXEC now M34: independent original
1808-object GENCHECKs, seq52 selected,
ROOTLINKS on authentic historic commit,
negative wrong-type and missing child,
seq51 fallback, both invalid RC8,
restored seq52 and final original STATE.
PIPE CMS to STEM captures all diagnostics,
console prints only brief PASS lines.
Source guard updated. Full GitHub CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36475668731 .
M34 host-proven ONLY; actual CMS target
compile and GITRUN still required.

Next real target user Mac from ibm-sandbox/src:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
Actual CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
NEVER touch original GITFIX/M15NEW
STAGE/INDEX/SEEK/GEN, protected selectors
or GITPBUF PACK. Single standard compact
one-page GITRUN only, no manual FILEDEF.

## September 28 14:59–15:03 — M34 LIVE CMS PASS; M35 host green

User's actual CMSCLNK GITREC PLAIN for M34:
ASSEMBLER (XF) DONE, NO STATEMENTS FLAGGED,
GITREC MODULE mode PLAIN built T=9.10/9.42
14:59:57. Standard one-page GITRUN M34
completed every stage:
 PASS original protected files/absent M15BAD
 PASS GITFIX full audit 1808 objects RC0
 PASS M15NEW full audit 1808 objects RC0
 PASS seq52 selected RC0
 PASS verified actual root direct links RC0
 PASS noncommit child RC8
 PASS missing child RC4
 PASS seq51 recovery RC0
 PASS both GEN2 unavailable fail closed RC8
 PASS restored seq52 RC0
 PASS original protected file final STATE
 GITRUN M34 ALL READ ONLY NATIVE GIT TESTS PASSED
 Ready T=183.05/184.48 at 15:03:06.
M34 is LIVE CMS TARGET PROVEN; no protected
original files rewritten.

Autonomously developed M35 native read-only
GITREC NESTLINKS C0NAME C1NAME COMMIT_OID40.
Extends M34 ROOTLINKS: after full GEN2 audit
and selected generation, authenticates child
and all parent commits, all corresponding
root trees and all immediate root entries.
Also descends exactly ONE subtree level
from EVERY direct root subtree for child
and all parent roots, authenticating every
nested entry's referenced Git blob or tree
of correct mode/type and SHA1, and parsing
linked nested tree structure. External Gitlinks
160000 skipped (external repositories).
Bounded to 256 entries per tree, shared
1024-tree visit budget on CMS. No unbounded
recursive traversal and no partial parent
list/success marker on missing/wrong-type
or invalid nested links. No writes. All
C source lines <=72; output <=80.
Prior M34 ROOTLINKS semantics unchanged.

Synthetic strict C89 native host fixture
1808 objects now 41 unique; adds
structurally valid direct subtrees
containing missing or wrong-type nested
blob and malformed parent-nested reference.
Proves old M34 ROOTLINKS passes these
shallow-valid structures while new
NESTLINKS correctly fails RC4 or RC8
without partial output. Tests two-parent
merge valid nested links and zero-parent
root, seq51 recovery, both invalid RC8
and seq52 restoration; all M0–M34 tests
continue passing. Corrected fixture
binary literal escapes after initially
discovering duplicated source backslashes.
Standard src/GITRUN.EXEC now M35 compact
one-page read-only test of both independent
real original 1808-object GENCHECKs,
seq52 selected, historic commit NESTLINKS
and expected known parent/tree, wrong-type
and missing child, seq51 fallback, both
missing fail closed and seq52 restore,
final original protected STATE. In-memory
PIPE CMS to STEM, last-four-line diagnostics
on failure. GITRUN source guard updated.
FULL native host CI SUCCESS:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36476834575
M35 HOST-PROVEN ONLY, target CMS not run yet.

Next real target gate from user Mac
ibm-sandbox/src:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
Real CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
Do NOT rewrite original GITFIX/M15NEW
STAGE/INDEX/SEEK/GEN, selector PTRs
or GITPBUF PACK. Unchanged GITCIDX and
GITSEL need no uploads. Only standard
one-page GITRUN, no auxiliary CMS runner.
If M35 fails due to missing original
historical nested references, diagnose
without weakening fail-closed rules.

## September 28 — MAX-WORK TURN: M36+M37 host complete; batch M35-M37

User explicitly requested "please do max work per turn".
Continue proactively through multiple fully host-tested milestones,
run full CI and source guards, batch compatible live CMS gates into
ONE transfer/compile/standard one-page GITRUN, preserve protected
originals and avoid stopping merely to request permission.

M34 remains actual-CMS target-proven. M35 NESTLINKS was
full host green but NOT yet tested on CMS (run
36476834575), so it must NOT be called target-proven.

Following the user preference, independently completed M36
and M37 in GitHub main and expanded the same standard compact
target gate to cover M35, M36 and M37 in one user run:

M36: `GITREC DEEPLINKS C0 C1 COMMIT_OID40`
extends M35 immediate child/parent subtree entry validation
to two consecutive nested subtree levels, within the same
fully audited selected GEN2 generation, rehashing all
referenced mode-appropriate staged objects and structurally
parsing each linked tree; external Gitlinks skipped.
Per-tree max 256 direct entries; shared 1024-tree visit budget.
Only after the entire request passes emits
`DEEP ROOT LINKS VERIFIED` plus safe short parent records.

M37: `GITREC DEPTHLINKS C0 C1 COMMIT_OID40 DEPTH`
parameterizes depth as exactly one digit 0..4, where
0=direct root links/M34, 1=M35, 2=M36, 3/4 descend
further. Strict invalid depth RC4, missing reference
RC4, wrong type/structure/exceeded budgets RC8.
Only on complete success emits `LINK DEPTH N VERIFIED`
and complete parent records. Child, parents, every root
all SHA1-authenticated independently in same selected seal.
Original M34/M35 command outputs preserved, no data writes.

Strict native C89 integration host fixture remains 1808 staged
objects but 63 unique synthetic Git contents, with three
successive nested levels and wrong/missing deepest blobs,
corruption in a second merge parent, a 257-entry over-limit
root, five valid depth values, invalid strings, missing/
noncommit child, seq51 recovery, both generation manifests
invalid RC8, restored seq52 and every previous regression.
No source record in GITREC.C exceeds CMS 72-column safety.
Full GitHub CI, native C89 -Werror, and read-only GITRUN
source guards ALL PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36478127516

Standard src/GITRUN.EXEC now `M37 COMPACT REPORT`,
ONE-PAGE target batch: protected originals/absent M15BAD,
independent original 1808-object GITFIX and M15NEW full
GENCHECK audits, seq52 select, three positive stages
M35 NESTLINKS / M36 DEEPLINKS / M37 DEPTHLINKS 2 on
historical first commit 00D8D63229305230C8D37F884CE87F9E1A89468C
with known parent
2D5038C551318997B865497E04CF4C037DE4135E and
parent tree F3EF36AAD778D5DA84857D8DED46495C75F4CAB0,
invalid M37 depth RC4, noncommit child RC8,
missing child RC4, seq51 recovered M37 depth2 RC0,
both unavailable RC8 fail closed, seq52 restored
M37 depth2 RC0 and final full protected originals.
All detailed command logs captured only in-memory with
PIPE CMS ... | STEM out.; at most four diagnostics on failure.
No auxiliary CMS test EXECs; no protected changes.

NEXT user Mac from ibm-sandbox/src:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
Then real z/VM CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
ONLY these two CMS uploads; GITCIDX and GITSEL unchanged.
M35, M36 and M37 are host-proven ONLY. Do not declare any
actual CMS pass until user shares successful compact M37 output.
If failed, diagnose using compact failure markers and fix
proactively in GitHub; retain fail-closed integrity and
the protected immutable original stage/index/seek/GEN,
selector PTR and GITPBUF PACK files.

## September 28 15:30–15:42 CDT — M35/M36/M37 REAL CMS PASS

Actual target transcript supplied by user:
 CMSCLNK GITREC PLAIN
 ASSEMBLER (XF) DONE
 NO STATEMENTS FLAGGED IN THIS ASSEMBLY
 CMSCLNK: built GITREC MODULE mode PLAIN
 Ready T=9.28/9.63 15:30:01.
The standard GITRUN M37 one-page compact regression passed:
 protected originals and absent M15BAD manifest;
 independent GITFIX/M15NEW full original 1808-object GEN2
 audits RC0; seq52 selected RC0; M35 NESTLINKS RC0;
 M36 DEEPLINKS RC0; M37 DEPTHLINKS 2 RC0;
 invalid depth RC4, noncommit child RC8,
 missing child RC4, older seq51 recovered depth2 RC0,
 both generation manifests invalid fail-closed RC8,
 restored seq52 depth2 RC0, final protected originals.
Exact final marker:
 GITRUN M37 ALL READ ONLY NATIVE GIT TESTS PASSED
 Ready T=693.54/708.96 at 15:42:10.
M35, M36, M37 are now actual CMS TARGET-PROVEN.
No original staged generations, pointers or PACK were altered.
Keep earlier host and CMS evidence intact.

## September 28 after M37 — M38 audit batching development

The full M37 target regression took 693.54 CPU and
708.96 elapsed seconds. Each GITREC command independently
runs a full audited GEN2 selection, causing repeated cost.
Added M38 GITREC LINKBATCH C0 C1 COMMIT_OID40:
once a complete selected-generation GENCHECK passes, perform
a single depth-two link walk for child and ALL parent roots;
only on complete success emit ALL three authenticated markers:
 NESTED ROOT LINKS VERIFIED
 DEEP ROOT LINKS VERIFIED
 LINK DEPTH 2 VERIFIED
plus the complete existing framed parent list. Fail closed
on missing/wrong/corrupt linked objects before any markers.
Depth-two success logically subsumes depth zero/one checks.
All existing M34–M37 commands remain available unchanged.
Updated host integration to cover batch positive, missing,
wrong type, noncommit/missing child, seq51 recovery, both
invalid and restored seq52. Standard read-only GITRUN M38
uses one LINKBATCH in place of three separate positive
GITREC audits and uses batch for fallback/restoration.
The independent original GITFIX/M15NEW full audits, explicit
selector audit, bad-depth/child negatives, dual invalid
fail-closed and final protected STATE remain unchanged.

GitHub main source commits:
 20c920312a7ae830235f0720212e9a77b1cd5cc4
 b5c46993cea026ad26a800796fc3bfa7eb21ba8a
 39417f4a3a2ff9216e76b4e8120372f9f1052205
M38 has NOT been compiled or run on CMS. Do not claim
host CI passed until a concrete completed run is checked.
Next target gate only after host checks:
 Mac in ibm-sandbox/src:
 git pull
 ./cms-upload.sh GITREC.C
 ./cms-upload.sh GITRUN.EXEC
 Actual CMS:
 CMSCLNK GITREC PLAIN
 GITRUN
The expected last marker is
 GITRUN M38 ALL READ ONLY NATIVE GIT TESTS PASSED.
GITCIDX/GITSEL unchanged; never rewrite GITFIX/M15NEW
STAGE/INDEX/SEEK/GEN, original selector PTR or GITPBUF PACK.
Standard compact GITRUN only; no auxiliary scripts.
