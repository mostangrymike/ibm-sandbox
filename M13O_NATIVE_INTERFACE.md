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
