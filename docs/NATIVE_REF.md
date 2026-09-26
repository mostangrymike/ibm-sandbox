# M13 native backward REF_DELTA gate

The captured 340,027-byte real GitHub PACK contains 1,808 objects
and 1,117 OFS_DELTA entries, but **no REF_DELTA entries**.
Its existing CMS-proven staging/index/seek modes are retained.
The separate native REF_DELTA implementation below is
host-regression-proven; the first CMS compilation succeeded but
its REF lookup exposed a shared EBCDIC Git-header defect, corrected
in current source but not yet retested on CMS.

## Implemented scope

GITCWALK now resolves a REF_DELTA base by its 20-byte Git object ID
when a fully reconstructed matching object **precedes** the REF in
the same PACK. It inherits the base's final object type, applies
the bounded delta to the base's reconstructed bytes, and computes
the canonical OID of the resulting object. Chained backward REF
bases are supported. OFSAPPLY can compute prior base OIDs on demand
without enabling object-ID output for its whole run.

An absent, forward-only, or external base fails closed with
`UNRESOLVED REF BASE OBJ n`. Do not claim complete REF_DELTA
interoperability until forward/external base lookup exists and has
its own regression and target proof. The new code changes no
previous target-proven ordinary/OFS behavior for a PACK that
contains zero REF_DELTA objects.

## Host-generated fixtures and independent Git verification

`tests/make-native-ref-pack.py` writes CMS ASCII hex-record fixtures
(each record 64 characters or less), plus a host-only binary copy:

- `REFPACK PACK`: a three-object Git PACK v2. Object #1 is
  blob `abc`, #2 is a REF_DELTA referencing #1 and making
  blob `abcd`, and #3 is a chained REF_DELTA referencing #2
  and making blob `abcde`.
- `REFBAD PACK`: same structure but an unknown base OID for
  the second object; valid recomputed PACK SHA-1.
- `REFFWD PACK`: the base exists later in the PACK but is not
  yet reconstructed; must reject rather than use uninitialized data.
- `REFSIZE PACK`: valid PACK SHA-1 but a REF delta declares the
  wrong base length; must fail bounded delta application.
- `REFSHA PACK`: valid objects but a corrupted trailer SHA-1;
  must fail before reconstructing any object.

The host harness substitutes zlib only for the existing CMS
GITCAPI/GITINFA inflater, so all native C PACK header parsing,
REF lookup, delta reconstruction, and native SHA-1 logic is
exercised. It compares each resulting blob OID against
`git hash-object`. The same generated binary `REFPACK`
is independently ingested by Git's `git index-pack --stdin`,
and `git cat-file` must reconstruct all three blobs correctly.
Thus the positive fixture is Git-readable rather than merely
self-consistent with our parser.

`GITCWALK RTEST` also exercises a small two-step REF chain,
missing/forward base lookup rejection, malformed delta length,
and the final independently checked OID entirely in memory.
`RPACK` accepts a bounded synthetic PACK of fewer than
340,027 bytes and enables REF reconstruction plus OID output.
`RAPPLY` tests the same PACK with OIDs generated on demand for
base resolution instead of the normal object-OID output path.
Neither writes to GITSTAGE or changes the saved real PACK.

Host tests including negative fixtures and independent Git
PACK acceptance passed in GitHub Actions run
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36274025088 .

## Single isolated CMS target gate

This is the first actual target compilation of the updated
REF-capable GITCWALK source. No live GitHub request, modification
to `GITPBUF PACK A`, or restaging is required.

On the Mac, in `/Users/mikewommack/ibm-sandbox/src`:

```sh
git pull
python3 ../tests/make-native-ref-pack.py .
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITCWALK.C
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/REFPACK.PACK
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/REFBAD.PACK
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/REFFWD.PACK
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/REFSIZE.PACK
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/REFSHA.PACK
```

On CMS, compile with the intended F-disk compiler wrapper, if
installed; the prior `GITCLNK GITCWALK` remains a fallback.
Define each PACKIN only after compilation:

```text
CMSCLNK GITCWALK
GITCWALK RTEST
FILEDEF PACKIN CLEAR
FILEDEF PACKIN DISK REFPACK PACK A
GITCWALK RPACK
GITCWALK RAPPLY
FILEDEF PACKIN CLEAR
FILEDEF PACKIN DISK REFBAD PACK A
GITCWALK RPACK
FILEDEF PACKIN CLEAR
FILEDEF PACKIN DISK REFFWD PACK A
GITCWALK RPACK
FILEDEF PACKIN CLEAR
FILEDEF PACKIN DISK REFSIZE PACK A
GITCWALK RPACK
FILEDEF PACKIN CLEAR
FILEDEF PACKIN DISK REFSHA PACK A
GITCWALK RPACK
```

The expected positive case reports:

```text
PASS 3 OBJECTS NEXT OFFSET 94
OFS DELTAS APPLIED 0
REF DELTAS APPLIED 2
OID OBJ 1 TYPE 3 SIZE 3 F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F
OID OBJ 2 TYPE 3 SIZE 4 85DF50785D62D3B05AB03D9CBF7E4A0B49449730
OID OBJ 3 TYPE 3 SIZE 5 6A8165460570531A1247BD99A73B53A5A6E500D5
```

The OID lines occur earlier in the actual program output,
before the PASS/counter lines. `RTEST` must print
`REF BACKWARD CHAIN AND NEGATIVE TESTS PASSED`.
`RAPPLY` must print `REF DELTAS APPLIED 2` without needing
the normal object OID output. All four negative test invocations
should return CMS RC 8 with, respectively,
`UNRESOLVED REF BASE OBJ 2`,
`UNRESOLVED REF BASE OBJ 1`,
`FAIL NATIVE DELTA APPLY`, and
`FAIL NATIVE PACK SHA1`.
Keep each preceding negative file definition isolated;
do not accept any unexpected RC 0.

The currently stored 1,808-object PACK remains untouched.
After this test, the next distinct functional milestone is
persisted/external and forward REF_DELTA base resolution with
restart/recovery tests; the real captured PACK cannot exercise
those cases. Keep GitHub issue #2 open.

## September 26 CMS failure and confirmed correction

The user compiled the original REF implementation successfully
with `CMSCLNK GITCWALK` (NAPI, no assembler flags), but the first
real target REF fixture failed at OBJ 2. The raw PACK was valid:
SHA-1 `9CD9B4CCFA5D5371C608230D3157F4766248355F`, 114 bytes,
3 objects. The ordinary first blob `abc` was incorrectly reported
as `5492DC378EC7097F3437B18BE17F4C58D0923A03` instead of
Git's `F2BA8F84AB5C1BCE84A7B441CB1959CFC7093B7F`.
RPACK and RAPPLY each printed `UNRESOLVED REF BASE OBJ 2` (RC 8).
The original RTEST passed its internal chain, but its resulting
`0414AADE456A43A390C3A0E689DD2CDE0439DAA7` was also not the
correct Git ABCDE OID.

This is the confirmed EBCDIC canonical object-header bug, not an
inflater or PACK SHA defect. Corrected GitHub source now builds the
hash preimage using explicit ASCII bytes and checks known Git test
vectors directly on CMS. GITCIDX was corrected too; earlier staged
and indexed OIDs need rebuilding separately, not promotion. Host
regressions passed; the corrected implementation is **awaiting CMS
validation**. For current minimal Mac transfer, exact CMS retest,
and safe separately named staging/index rebuild, use
[Canonical Git OIDs on CMS](CANONICAL_OIDS.md). The older RPACK
steps above are historical and do not by themselves establish a
successful target result. No new live GitHub capture is needed.
