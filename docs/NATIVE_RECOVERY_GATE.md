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

From the existing GEN2 manifest, copy the 40 uppercase
hexadecimal characters following the `DIGEST` record.
This is the GEN2 descriptor digest, **not** the first commit
OID, final tree OID or PACK trailer checksum.

Only if `GITSEL0 PTR A` and `GITSEL1 PTR A` do not already
exist, create two new disposable selector records. Replace
`YOUR40CHARACTERGEN2DIGEST` in the following commands with
the actual 40-digit DIGEST value you just read:

```text
FILEDEF SELOUT DISK GITSEL0 PTR A (RECFM V LRECL 80
GITSEL WRITE 41 GITFIX YOUR40CHARACTERGEN2DIGEST
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
GITSEL WRITE 42 GITBAD YOUR40CHARACTERGEN2DIGEST
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
