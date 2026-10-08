# CMS A-disk obsolete-file cleanup (2026-10-08)

## Real target baseline

The operator successfully removed the failed partial M173NET STAGE A,
then individually removed GITREC, GITCWALK, and GITCIDX LISTING A.
The latest CMS QUERY DISK output was MNT191 A R/W, 175 cylinders,
4096 bytes per block, 295 files, 10361 blocks used and 21139 free.
No proof of A minidisk integrity or independent DASD backup has been
reported since the September 27 TRKDE 4 deallocation-map incident.
An actual unmodified backup/snapshot is the prudent prerequisite
for further intentional deletes. Do not ERASE an unverified file
system in bulk.

## Why there are three separate batches

The cleanup tool `src/ACLEAN.EXEC` is deliberately restricted to
**exact A-disk filenames** observed in the operator's LISTFILE
inventory. Its default is not to erase anything. `PLAN` is read
only; `APPLY` is explicitly destructive. It uses CMS STATE for
each item, skips absent files only on RC28, stops on unexpected
errors, and issues one exact-file ERASE at a time, stopping at the
first failed erase. It reports disk space after each APPLY batch.

1. `LISTINGS` — 20 remaining older compiler/assembler LISTING
   files. The three largest legacy listings have already been erased.
   The four current diagnostic listings GITPIMP, GITINFA,
   GITPCHK, GITPCENS are retained. Expected additional LISTING
   file reduction is 20 files, 489 blocks (~1.91 MiB) based
   on the operator's snapshot. All are generated outputs.

2. `EXPERIMENTS` — 26 generated artifacts: paired MODULE and
   TEXT files for CCTEST1, HELLO, GITCABI, GITCINF, GITCPARS,
   GITCPROB, GITC2, GIT12Q, M12ABEG, M12BOPN,
   M12TLS2, M12TLS3, M12TLS4. Their C or ASSEMBLE
   source remains on A, and most are additionally in GitHub.
   They are retired historical experiments, not active native
   generalized import modules. Approximate historical
   allocation: 229 blocks (~0.89 MiB). Their standalone
   MODULE invocations will cease to work until they are rebuilt.

3. `OLDTESTS` — 29 early M9–M13 disposable testing EXECs
   whose original sources are present in GitHub. They are not
   called by current GIT, GITVREF, GITWT, GITFETCH or GITPOST.
   GITTEST's older M13AAREF/M13ABREF requirements are
   explicitly *excluded*. Standalone past milestone test
   EXECs can be restored later from `src/` in GitHub.
   This is a separate opt-in because it retires callable
   historical test entry points rather than generated outputs.

If every manifest entry still exists and all three batches pass,
75 old files are removed, bringing the observed 295-file
inventory to approximately 220 files plus the new ACLEAN EXEC.
The exact disk-block changes must be measured on CMS; more
than the LISTFILE sum may be reclaimed through disk-directory
metadata, as seen in the previous listing cleanup.

## Protected and deliberately retained files

- GITFIX and M15NEW verified STAGE/INDEX/SEEK/GEN files;
  GITSEL0/GITSEL1/M15SL0/M15SL1 PTR selectors.
- GITPBUF PACK and M171NET PACK/META; other PACK input/fixtures.
- GITREF2 REPO and GITOBJ files; old DATA, diagnostic traces,
  and network payload fixtures unless explicitly archived.
- All C, ASSEMBLE, EXEC, and CMS compiler/toolchain source
  except the opt-in named early tests in OLDTESTS.
- All active MODULE/TEXT for GITCORE, GITSTRM, GITREC,
  GITSEL, GITCIDX, GITCWALK, GITCAPI, GITINFA,
  GITPCHK, GITPCENS, GITPIMP. The native bridge
  GITNDRV/GITNCALL/GITNHEX is also retained.
- M12ATLS ASSEMBLE A (historically involved in TRKDE 4),
  M12ATLS MODULE A, PROFILE EXEC/XEDIT and
  all disks other than MAINT A.

## Operator workflow

On the Mac, from `ibm-sandbox/src`:

    git pull
    ./cms-upload.sh ACLEAN.EXEC

On CMS, preview and then run only the approved batch:

    ACLEAN PLAN LISTINGS
    ACLEAN APPLY LISTINGS
    QUERY DISK

Check the output and free-block count before the next category.

    ACLEAN PLAN EXPERIMENTS
    ACLEAN APPLY EXPERIMENTS
    QUERY DISK

The final opt-in test cleanup:

    ACLEAN PLAN OLDTESTS
    ACLEAN APPLY OLDTESTS
    QUERY DISK

`PLAN` is the safest entry to run immediately; only `APPLY`
performs deletion. If any STATUS or ERASE fails, stop and investigate.
Do not run `GITRUN` or a generic wildcard cleanup as a shortcut.

To reconstruct a removed historical experiment, restore its
source or EXEC from the canonical GitHub repository, compile or
assemble as appropriate and link it normally. The retained
historical PACK and staged object generations are unchanged.

This cleanup reduces A-disk clutter but does **not** solve
M173's capacity problem: the new generalized live-PACK STAGE and
INDEX belong on a larger, separate persistent writable
minidisk, with the verified 2,171,129-byte input PACK retained on A.


## Follow-up A inventory after the 75-item cleanup

The operator reported CMS QUERY DISK: 221 A files, 9,620 blocks used,
21,880 blocks free, 31% utilized. This represents net 74 fewer files
and 741 additional blocks free since the 295-file baseline; a
newly installed ACLEAN EXEC accounts for the file-count difference.

The next operator inventory listed 26 ASSEMBLE files and many
remaining EXECs. These are **not** all expendable: handwritten
GITCAPI/GITINFA/GITNCALL/GITNDRV/GITNHEX/GITCORE/GITSTRM
and M12* diagnostic assembler inputs are sources rather than
compiler outputs; retain them. M12ATLS ASSEMBLE is specifically
excluded because its attempted removal previously triggered a
TRKDE 4 deallocation-map error.

The new optional `BUILDDECK` batch contains exactly nine
GCCCMS-generated intermediary ASSEMBLE files, each corresponding
to a retained original `.C` source in GitHub. Current production
MODULEs are untouched; the old experiment MODULEs were already
retired in the previous cleanup: GITCABI, GITCINF, GITCPARS, GITCPROB,
GITC2, GITREC, GITCIDX, GITCWALK, GITSEL.
Individual CMS LISTFILE allocations total **952 blocks**,
about 3.72 MiB. These files are not required to *run*
the existing native modules. When rebuilding any one of
them later, use `CMSCLNK NAME NAPI` or `CMSCLNK NAME PLAIN`
as appropriate; the compiler regenerates the ASSEMBLE.
Deleting a generated deck removes convenient direct
reassembly until recompilation. The target is a reduction
of nine more files (221 to roughly 212 after updating
ACLEAN itself), but count and blocks must be verified
through QUERY DISK rather than claimed in advance.

The existing source-backed M155-M173 checkers, GIT EXEC/GITVREF,
GITFETCH/GITPOST, GITWT, GITIMP, PROFILE, GITTEST,
native bridge EXECs, and old potentially unique diagnostics
are retained. Some orphan-looking M13* EXECs do not have
matching files in the current GitHub source tree and must not
be erased as though they were already backed up.

After preserving an independently verified DASD image/snapshot,
upload the updated `ACLEAN.EXEC` on CMS A and run:

    ACLEAN PLAN BUILDDECK
    ACLEAN APPLY BUILDDECK
    QUERY DISK

Do not include wildcard targets or run the new batch
without first inspecting PLAN. This only tidies A;
a distinct large persistent minidisk is still required
for the generalized live 7736-object stage.
