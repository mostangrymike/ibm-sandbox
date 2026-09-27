# Indexed external REF_DELTA: isolated CMS performance gate

## Target-proven baseline

The 1,808-object canonical GITFIX STAGE A, IDX2 and SIDX2
indexes and GEN2 sealed manifest passed all CMS audit and separate
GENCHECK invocations. FPACK has reconstructed both chained forward
REF_DELTA objects on CMS. XPACK has verified and reconstructed the
270-byte first commit from the actual GITFIX stage through XREAL
PACK A, using canonical commit OID
00D8D63229305230C8D37F884CE87F9E1A89468C.
The sequential XREAL scan took 8.17 seconds elapsed because XPACK
checks all 1,808 staged records for absent, duplicate and malformed
matching bases. Existing XPACK remains available and unchanged.

## New optional XSEEK and XSAPPLY modes

GITCWALK XSEEK/XSAPPLY use FILEDEF EXIDX to read the complete
SIDX2 seek index, select the matching 20-byte canonical Git OID
and obtain its saved ftell cookie. The index must have the correct
SIDX2/SEND2 envelope and sorted, unique records. The selected
external object is read via fseek on FILEDEF EXTIN, with exact
ordinal, type, size and OID comparisons and independently
recomputed canonical Git SHA-1 of the reconstructed body. Its
verified bytes then form the base of the native REF_DELTA.

XSEEK computes the final object's OID; XSAPPLY tests the
apply-only path with no final OID printing. Neither changes
the PACK, stage, index or GEN2 manifest. They do not replace
full GEN2 integrity checking or make a new active-generation
pointer. The production stage/index pair must already have
passed SFAST/PAIR/GENCHECK; indexing a maliciously substituted
stage is not a substitute for full generation attestation.

Host integration includes synthetic first- and later-record
indexed lookups, stale saved-cookie rejection, truncated index
rejection and selected-body tamper rejection. Complete suite
passed:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36283446044 .
CMS runtime and actual performance are **not yet tested**.

## Minimal actual CMS gate

The current GITFIX STAGE A, GITFIX SEEK A, GITFIX INDEX A and
GITFIX GEN A are already complete. There is no need to rebuild
them or recapture the live GitHub PACK.

On the Mac, from /Users/mikewommack/ibm-sandbox/src, use the
existing single c3270-based uploader:

```sh
git pull
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITCWALK.C
```

On CMS, compile before defining the DD names; make sure that
XREAL PACK A was preserved from the earlier successful target run.
If the named DD definitions already exist, first clear only
those actual old definitions that point elsewhere. In a fresh
CMS process, these commands can be entered directly:

```text
CMSCLNK GITCWALK
FILEDEF PACKIN DISK XREAL PACK A
FILEDEF EXTIN DISK GITFIX STAGE A
FILEDEF EXIDX DISK GITFIX SEEK A
GITCWALK XSEEK
GITCWALK XSAPPLY
```

Required XSEEK markers:

```text
EXTERNAL SEEK VERIFIED TYPE 1 SIZE 270
OID OBJ 1 TYPE 1 SIZE 270 00D8D63229305230C8D37F884CE87F9E1A89468C
PASS 1 OBJECTS NEXT OFFSET 48
REF DELTAS APPLIED 1
```

XSAPPLY must independently report the verified external type
and size, one applied REF delta, and successful PACK completion
without printing a final OID. Measure actual CMS CPU/elapsed
time for both commands; compare the observed XSEEK result with
the previous *single-run* XPACK XREAL elapsed time of 8.17 s.

For subsequent cross-logon durability validation, avoid
overwriting GITFIX GEN A and only rebind the four required input
FILEDEFs and run GITCIDX GENCHECK after logging back on. Reboot
persistence and atomic generation promotion are separate gates.
