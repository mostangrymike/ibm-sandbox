# M14: native dual-slot recovery against a complete GEN2 audit

## Current result and safety boundary

The 1,808-object GITFIX stage, IDX2, SIDX2 and GEN2 seal have
passed full native-CMS checks, including a complete GENCHECK
after a new CMS login. The new recovery components below were
subsequently implemented in GitHub and have **passed host tests
only**. They do not perform active-generation promotion or write
to any existing GITFIX data file.

- `src/GITSEL.C`: strict SEL1 parser, CRC32 over explicit ASCII
  bytes (independent of the host/CMS character set), and a
  `WRITE` command that creates one caller-directed selector
  record on FILEDEF SELOUT. The write does not mark a
  generation as verified or selected.
- `src/GITREC.C`: read-only recovery selector linking native
  GITSEL and GITCIDX. For each candidate it binds the correct
  separate set of four input FILEDEFs, compares the claimed
  selector digest with its GEN2 manifest, then calls the
  **actual complete GENCHECK**, which reruns SFAST and PAIR
  over all staged objects, index entries and seek cookies.
  It selects only a fully verified candidate, checks that
  selector names match their assigned slots, refuses
  ambiguous identical slot names, and falls back to an older
  fully verified slot if the newer candidate fails.
  It never writes any stage, index, seek or GEN2 file.

The host fixture uses 1,808 synthetic staged records and two
independent GEN2 candidates. Tests inject changed staged bytes,
a damaged GEN2 manifest, truncated SIDX2, missing IDX2, spoofed
slot identities, invalid selector checksums and interrupted
selector writes. The real complete GEN2 verifier rejects each
damaged newer candidate and recovery chooses the older verified
one; it rejects both when neither can be verified.

The full host CI suite passed:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36330993480 .

## Isolated first CMS compilation and recovery check

These are a **read-only test on GITFIX**, plus two *new* small
selector files. They are not an active-generation promotion.
Do not run GENWRITE, STAGE or either index BUILD. The same
GITFIX files remain the protected baseline.

On the Mac, from `/Users/mikewommack/ibm-sandbox/src`:

```sh
git pull
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITSEL.C
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITREC.C
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITCIDX.C
```

On CMS compile both new programs **before** defining FILEDEFs:

```text
CMSCLNK GITSEL PLAIN
CMSCLNK GITREC PLAIN
TYPE GITFIX GEN A
```

The new `GITSEL WRITEGEN` can read the completed `GEN2` manifest
from the input FILEDEF `GENIN` and derive its DIGEST without
copying a 40-character value by hand. The record it writes
remains **untrusted** until GITREC performs complete GENCHECK.
Use the existing GITFIX GEN A; do not regenerate the manifest.

Only if `GITSEL0 PTR A` and `GITSEL1 PTR A` do not already
exist, create two disposable selectors using that input manifest:

```text
FILEDEF GENIN DISK GITFIX GEN A
FILEDEF SELOUT DISK GITSEL0 PTR A (RECFM V LRECL 80
GITSEL WRITEGEN 41 GITFIX GITSEL0
FILEDEF SEL0 DISK GITSEL0 PTR A
FILEDEF C0STG DISK GITFIX STAGE A
FILEDEF C0IDX DISK GITFIX INDEX A
FILEDEF C0SEEK DISK GITFIX SEEK A
FILEDEF C0GEN DISK GITFIX GEN A
GITREC SELECT GITFIX GITBAD
```

The first result should rehash every existing object, print
`GENERATION VERIFIED 1808 UNIQUE 1808`, and then
`SELECTED 41 GITFIX` with the same DIGEST. No SEL1 file or
new candidate generation is required for this first test.

Then test an invalid newer **disposable selector**, still
without creating or modifying any new generation's data:

```text
FILEDEF SELOUT CLEAR
FILEDEF SELOUT DISK GITSEL1 PTR A (RECFM V LRECL 80
GITSEL WRITEGEN 42 GITBAD GITSEL1
FILEDEF SEL1 DISK GITSEL1 PTR A
GITREC SELECT GITFIX GITBAD
```

Do not bind C1STG/C1IDX/C1SEEK/C1GEN to valid data.
The newer selector is syntactically valid, but its
referenced GEN2 data cannot be opened and verified.
Recovery must instead run full GENCHECK on the existing
GITFIX candidate and print `RECOVERED 41 GITFIX`.
Any false `SELECTED 42 GITBAD` result is a serious gate
failure. Preserve both disposable selector files for
diagnosis and keep all original GITFIX files unchanged.

If CMS cannot resolve the included `GITCIDX.C` or
`GITSEL.C` while compiling GITREC, capture the complete
compiler diagnostic. Do not substitute an untested
binary or claim target validation from host success.

## What remains

The current code does **not** write an active pointer, make
CMS file writes power-loss atomic or claim restart/reboot
recovery. A future isolated promotion milestone must use
different never-before-used generation filenames, two slot
records and failure injection, with a verified writer
exclusion protocol. Actual CMS recovery across system
reboot is still untested. The verified existing GITFIX
generation must never be used as a mutation target.

## Existing selector overwrite safeguard (host-proven)

The latest native `GITSEL WRITE` additionally opens SELOUT for
reading first and refuses to create an output when the mapped
selector slot already exists. It returns RC 8 and prints
`SELECTOR OUTPUT EXISTS` without overwriting the existing record.
The strict C89 regression tests verify the old selector bytes remain
unchanged after a second WRITE attempt. Full host CI passed:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36331581650 .

This guard prevents accidental sequential reuse of a selector file;
it is **not** an atomic create-if-absent operation or concurrent
writer lock. The test above must still use only previously unused
disposable selector filenames. Never bind SELOUT to a protected
existing selector or any GITFIX stage/index/seek/GEN data file.

## Host-proven digest-safe selector creation

The latest `src/GITSEL.C` also supports `WRITEGEN SEQUENCE BASENAME`.
It reads the existing completed GEN2 manifest through `GENIN`,
requires the complete five-record GEN2/DIGEST/MINOID/MAXOID/GEND2
grammar and matching counts, and uses its exact 40-hex DIGEST to
create a new untrusted selector through `SELOUT`. No user-supplied
digest is required. The existing best-effort output-exists guard
still refuses to overwrite an existing selector file. This avoids
confusing a commit, PACK checksum or min/max OID with the descriptor
digest and reduces error-prone manual copying. The host suite tests
correct byte-for-byte output, malformed/truncated/extra GEN2 records
and attempted overwrite. Complete CI passed:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36332001510 .
`WRITEGEN` has not yet been compiled or tested on CMS. It does not
validate staged content itself; the separate GITREC SELECT full
GENCHECK remains mandatory. Never bind SELOUT to an existing GITFIX
file. If either disposable selector filename already exists, choose
new unused 8-character names rather than overwrite it.

## Actual target compiler and first-runtime recovery finding

Both `CMSCLNK GITSEL PLAIN` and `CMSCLNK GITREC PLAIN`
compiled successfully on native CMS September 27, 2026 after
replacing literal C XOR operators incompatible with this DFT
source translation. The first `WRITEGEN` operation did not
create a selector: its read-only fopen existence probe returned
a non-null stream on an absent CMS DD, triggering
`SELECTOR OUTPUT EXISTS`. Recovery therefore could not
read SEL0/SEL1. This is a target-discovered runtime defect;
it is not evidence that the original GEN2 seal is damaged.

The updated `WRITEGEN SEQUENCE BASENAME OUTPUTNAME`
uses CMS `STATE OUTPUTNAME PTR A` instead of the lazy
read-only DD probe. It proceeds only if STATE reports missing
with RC 28; RC 0 refuses an existing file, and every other
return code fails closed. The operator must bind SELOUT to
the same OUTPUTNAME PTR A on a write-accessible minidisk.
The extra argument is mandatory for this CMS gate. It is
not an atomic concurrent-writer lock; STATE and write
remain separate operations.

After the revised code compiles, require STATE to report
missing for each new selector before binding SELOUT.
For slot zero, define all four inputs including C0IDX;
none of STAGE/INDEX/SEEK/GEN may be output FILEDEFs.
Do not rerun GENWRITE or any index build.

## September 27 CMS runtime correction: REXX owns the STATE gate

The target showed that GCCCMS C `system("STATE GITSEL0 PTR A")`
returns 0 even when interactive CMS and REXX `STATE` report
RC 28. Calling `fopen("dd:SELOUT","r")` before creating a file
also falsely reports an existing file. Thus neither C-level
probe can safely guard selector creation on this runtime.

The new CMS test path requires `GITRUN.EXEC`, which executes
`STATE GITSEL0 PTR A` with `ADDRESS CMS` and accepts only
RC 28. It then binds SELOUT to that same new filename and calls
`GITSEL WRITEGEN 41 GITFIX GITSEL0 ABSENT28`. The final
argument is an explicit attestation of the REXX-side check;
GITSEL rejects the named-slot form without it. This is only
a guarded single-writer test, NOT an independent atomic
create-if-absent guarantee. Never run it concurrently and
never run it against the existing verified GITFIX data files.

After fresh compilation, GITRUN first creates the new slot,
confirms STATE RC 0, binds SEL0 and all four C0 input DDs,
and invokes read-only `GITREC SELECT GITFIX GITBAD`.
If any gate fails, it stops. Reuse this exact GITRUN filename
for later milestone batches by editing it on GitHub first.
