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
