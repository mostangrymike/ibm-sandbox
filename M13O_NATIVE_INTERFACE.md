# M13O bounded native PACK inflater integration

The current PACK walker GITP9PWK calls GITPZBUF TOOBUF for
ordinary, OFS_DELTA and REF_DELTA entries. GITPZBUF delegates
to GITPSTRM, validates Adler-32 from bounded GITOBUF reads,
and queues consumed zlib bytes and output bytes. Preserve
this public contract and the existing REXX fallback.

GITINFA currently has internal raw INFLATE and ZINFLATE routines,
not a callable CMS service. R2=input, R3=bytes, R4=output,
R5=capacity; R6=output bytes and R15=status. M13O adds
R7=consumed raw DEFLATE bytes on successful INFLATE and
BITUSED for debugging. Count is (BITPOS+7)/8 after BFINAL.
The standalone regression checks fixed, stored and mixed
block consumption. This change needs CMS assembly/runtime proof.

GITPBUF stores hex-encoded 64-byte records. A native adapter
must decode binary bytes without assembling the full PACK in
REXX, retain 32 KiB history across bounded reads, and write
GITOBUF's bounded records. A PACK stream contains concatenated
zlib objects; locate Adler-32 from consumed DEFLATE bytes,
not the length of the remaining PACK.

Next: implement a separate callable CMS adapter and isolated
small-PACK fixture, preserving the standalone GITINFA test.
Then opt in at GITPZBUF with fallback. Do not claim live
PACK acceleration until tested on CMS.

## 2026-09-25 larger regression batch

Target confirmed the consumed-byte and trailing-data gate at 08:48:48.
Next source batch adds adjacent 11-byte zlib streams, truncated body and
trailer, insufficient output capacity, bad checksum with trailing data,
and a 5400-byte dynamic-Huffman zlib fixture with exact full-output,
82-byte consumed-length, and capacity checks. These additions are
committed but not yet target-proven. They exercise the stream boundary
and bounded decoding contract before exposing a callable adapter.

## Bounded binary adapter checkpoint

An internal APICALL entry now accepts R2 pointing to six fullwords:
input address, available input bytes, output address, output capacity,
output byte count and consumed zlib byte count. R15=0 on success,
4 on invalid arguments and nonzero on decode failure. Both output
counts are reset before decoding, so a failed call does not publish
stale lengths. This is an internal callable subroutine, not yet an
externally callable CMS MODULE or REXX command.

Standalone regressions now exercise the adapter with two adjacent
zlib streams, insufficient output capacity, a null parameter-list
pointer, truncated zlib input and a full 5400-byte dynamic stream.
These source changes require the next CMS assembler/runtime gate.

External CMS command/stack I/O and bounded PACK input/output record
transport remain unimplemented; the existing REXX path is unchanged.

## 08:54:54 CMS gate and next batch

CMS confirmed the APICALL parameter-list implementation and 5400-byte
adapter regression. The next code batch expands negative tests for
null input/output pointers, zero input/output lengths, corrupt Adler-32,
zeroed result fields on every failure, and recovery by reusing the same
parameter block for valid trailing-data and adjacent-stream calls.

APICALL is currently an **internal** assembler subroutine with static
DATAORG state; it is not reentrant and has no external CMS entry point.
Do not route production PACK traffic through it until a callable CMS
module and bounded transport exist. The next implementation should
introduce an external entry with standard CMS register preservation,
plus a separate caller regression, then connect GITPBUF/GITOBUF
64-byte records without whole-PACK REXX strings. Retain the current
GITPZBUF/GITPSTRM fallback throughout.

## External assembler entry checkpoint

CMS confirmed the expanded internal APICALL failure/recovery batch at
08:57:50. Source commit f7e6d044 introduces exported GITNAPI in the
GITINFA CSECT. It accepts the six-fullword parameter list in R1,
uses standard R13 save-area linkage, establishes the decoder's two
code bases and DATAORG base, and dispatches to APICALL. This external
entry has **not yet passed target assembly or a separate caller test**.
It is nonreentrant. It is not yet a CMS REXX command, nor connected
to GITPBUF/GITOBUF; retain the REXX PACK path.

## External entry XF assembler correction

First target assembly flagged BASR as undefined at the new GITNAPI
entry. Commit 40fc0479 replaces it with BALR 12,0 and fixes the
external entry's restore path: restore R0-R12 and R14 from the caller
save area without overwriting R15, which carries the API status.
This correction requires CMS target assembly and runtime validation.

## Separate external-caller regression

Commit fa7f3af adds src/GITNCALL.ASSEMBLE. It declares EXTRN GITNAPI,
loads its V-type address, and calls it with the public six-fullword
parameter list in R1. It verifies an 11-byte abc zlib stream, the
same stream with trailing PACK bytes, and an insufficient-capacity
failure with zeroed result counts. This separate assembler CSECT is
intended to link with GITINFA TEXT, not to replace GITINFA's built-in
selftest. Both the external caller and its linkage remain untested on
CMS; assemble both and validate the load/link sequence on target.

## 09:18:58 CMS external linkage gate PASSED

CMS Assembler XF assembled GITNCALL without flagged statements;
LOAD GITNCALL GITINFA and GENMOD GITNCALL succeeded. Executing
GITNCALL printed GITNCALL: EXTERNAL NATIVE API PASSED. All five
independent caller cases passed: valid abc, trailing PACK bytes,
insufficient output capacity, corrupted Adler checksum, and recovery
with the second of two adjacent zlib members. The first external
caller data comparison initially used EBCDIC C'abc'; commit e19cc16
corrected the expected binary bytes to X'616263'. External API
is now target-proven; PACK transport remains unimplemented.

## Native PACK integration boundary

The existing GITP9PWK WALK invokes GITPZBUF TOOBUF at each zlib
offset for ordinary, OFS_DELTA and REF_DELTA entries. Its contract
is two queued decimal lines: consumed zlib bytes and output bytes.
GITPBUF READSTACK exposes finalized PACK bytes as hex, up to 64
bytes per record; GITOBUF INIT/APPEND/FINAL accepts the same bounded
hex record size. Preserve these interfaces, avoid assembling an
entire PACK in REXX, and do not enable native routing by default.

The next native transport must provide bounded binary conversion,
respect available PACK input length and the output capacity, and
commit GITOBUF only after a successful decode. GITNAPI currently
requires its complete zlib member in addressable memory and a
preallocated output buffer; it is not yet a streaming decoder.
A 340027-byte, 1808-object PACK must not be loaded into one REXX
string. Do not claim streaming/native PACK acceleration until a
bounded native transport and its real-PACK gate pass.

## M13P bounded staging implementation (CMS gate passed)

GITNSTG STAGE offset max-bytes copies up to 65536 bytes from the
finalized GITPBUF PACK A into GITNSTG DATA A as at most 64-byte
hex records, then publishes GITNSMT DATA A metadata. It never
materializes the full PACK in REXX. M13PSTG exercises boundary,
short-tail and invalid-offset handling. GITNOUT COMMIT bytes
preflights GITNOUT DATA A records (binary hex, at most 64 bytes
per record), checks exact output length and extra records, then
replaces GITOBUF via INIT/APPEND/FINAL. M13POUT checks malformed
and truncated output preserve the previous object and that valid
binary output is committed. These components are NOT wired into
the PACK walker and have passed the CMS gate.

The remaining bridge must read GITNSTG records, convert hex to
binary into a bounded native input buffer, invoke GITNAPI with
its six-fullword parameter block, convert the output buffer back
to bounded GITNOUT records, and report both consumed and decoded
byte counts. Never silently truncate an input member at the
65536-byte staging limit; a successful native decode must consume
a complete zlib member, otherwise fall back to the existing REXX
GITPZBUF implementation. Keep native routing opt-in until the
bridge and real PACK regression pass.

## M13P expanded CMS gate, 2026-09-25 09:33:33

The original M13PSTG and M13POUT target regressions passed at
09:26:51 and 09:26:52. The expanded M13PSTG regression, including
64-byte/two-record staging, passed at 09:33:33 after correcting
metadata-tail handling and a mistaken test expectation. These
results establish the bounded REXX staging adapters, not the
assembler transport or native PACK routing.

## M13P expanded gate and M13Q guarded dispatcher

M13PSTG expanded 80-byte two-record staging regression passed on CMS
at 09:33:33 2026-09-25, following fixes to the finalized metadata
tail sentinel and test's expected 64-byte first record. M13POUT
previously passed on CMS at 09:26:52. Both adapters are target-proven.

M13Q adds GITPZNAT TOOBUF offset [REXX|NATIVE] as an isolated
explicit dispatcher; default REXX forwards to proven GITPZBUF.
NATIVE requires a GITNBRG MODULE and its wrapper, neither of which
is implemented. M13QDISP verifies a synthetic 11-byte zlib member
expands to binary abc and consumes exactly 11 bytes via default
and explicit REXX dispatch. M13QDISP is not yet CMS-tested.
No production PACK walker route is changed. Do not enable native
routing until the assembler bridge and real PACK regression pass.

## M13Q CMS gate, 2026-09-25 09:37:56

M13QDISP returned `M13Q GUARDED REXX DISPATCH PASSED` on CMS.
Default and explicit REXX dispatcher paths are target-proven for the
synthetic 11-byte zlib member and three-byte ASCII abc output.
This does not prove a native bridge, and production routing remains
unchanged pending native assembler/file I/O integration and PACK tests.

## M13Q extended negative gate, 2026-09-25 09:38:55

The expanded M13QDISP regression passed on CMS. It verifies
that an invalid dispatch mode is rejected without replacing the
previously decoded three-byte output. M13P staging/output and
M13Q guarded REXX dispatch are target-proven; native file-to-binary
assembler bridging and production integration remain pending.

## M13R native hex/ABI CMS gate, 2026-09-25 09:43:44

GITNHEX assembled under Assembler XF without flagged statements,
linked with GITINFA, generated a CMS module and printed
`GITNHEX: HEX/BINARY NATIVE ABI PASSED`. The test covers
EBCDIC hex-to-binary conversion, external GITNAPI invocation,
three-byte decoded output, exact 11-byte compressed consumption,
binary-to-EBCDIC-hex conversion, and invalid-digit rejection.
The remaining task is CMS file I/O for staged input/output records;
production PACK walking still uses GITPZBUF.

## M13S missing-driver CMS gate, 2026-09-25 09:53:13

M13SFAIL passed on CMS. Explicit NATIVE dispatch reported
`GITPZNAT: native bridge unavailable; use REXX`; the regression
confirmed that failure did not replace the existing decoded object.
This establishes fail-closed behavior with GITNDRV MODULE absent.
It does not establish driver CMS file I/O or native PACK integration.
