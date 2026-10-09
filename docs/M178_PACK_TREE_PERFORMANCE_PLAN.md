# M178 — forward-only authenticated tree closure (live CMS proven)

## October 9, 2026, 16:24 CDT — ACTUAL z/VM 6.3 M178 CMS PASS

**TARGET-PROVEN.** The operator uploaded the previously host-tested
`GITPFST.C` and `GITPFAST.EXEC`, checked that the existing G disk and
stage/index were accessible, and compiled the new module without any
flagged assembly statements. This proof supersedes the earlier
"not CMS target-proven" provisional status below; that text is retained
as historical design/validation context.

- `QUERY DISK G`: `GIT600 600 G R/W 1600 3390 4096`, 2 files,
  62526 blocks used (22%), 225474 free of 288000 total.
- `STATE M173NET STAGE G` and `STATE M174NET INDEX G`: RC 0.
- `QUERY FILEDEF` before: `No user defined FILEDEF in effect`.
- `STATE GITPFST C A`: RC 0; `CMSCLNK GITPFST PLAIN`:
  `ASSEMBLER (XF) DONE`, `NO STATEMENTS FLAGGED IN THIS ASSEMBLY`,
  `CMSCLNK: built GITPFST MODULE mode PLAIN` (2.01s elapsed).
  `STATE GITPFST MODULE A`: RC 0.
- Real run: `GITPFAST G CCB18BEC067E7886D70B82EF138EE56A8B899A61`
  returned RC 0, CPU 455.95s, elapsed **460.66s** at 16:24:00 CDT.
- Exact closure: **8 trees, 272 blobs, 0 gitlinks, 279 entries,
  280 verified objects**, largest 393767 bytes; peak resident
  **6546851 bytes** (approximately 6.24 MiB).
- Existing index: **7736 total and 7736 unique**. Forward scans **2**,
  object-header visits **15472** (7736 per pass; not physical CMS
  stage records), seeks **0**, authenticated blobs **272**.
- Native markers: `M178 TREE CLOSURE PASS` and
  `M178 VERIFIED FAST TREE TARGET GATE PASS
  CCB18BEC067E7886D70B82EF138EE56A8B899A61 G`.
- `QUERY FILEDEF` after at 16:25:37:
  `No user defined FILEDEF in effect`, matching before.

This is **positive-path native functional verification**, not proof
of comparative speed. Prior M177 TREE output had overflowed elapsed
counters, so the raw earlier wall-clock gap is not a valid timing
baseline. No original M173 stage, M174 index, M171 input PACK,
GITPTRE, GITPVIEW, directory or selector was altered by M178.
Keep these protected; especially never write-link overlapping
`PMAINT 0141`. Any next optimization must be isolated, host-tested,
and measured against comparable CMS runs without reimport or format.

---

## October 9, 2026 — independent two-pass native C prototype

**IMPLEMENTED SOURCE ONLY; NO REAL CMS TARGET RESULT AND NO
PERFORMANCE IMPROVEMENT CLAIMED.** A new `src/GITPFST.C`
reuses the original GITPTRE SHA-1/index parsing and
tree-format validation, but changes the access strategy:

1. Read `M174NET INDEX G` read-only, validate PIDX1,
   monotonic OID order, every offset, and build an
   in-memory object-number-to-index map.
2. **Forward scan 1** over `M173NET STAGE G`:
   sequentially validate object headers and records,
   cache and SHA1-verify tree objects using a strict
   64MiB resident budget. It matches each selected
   tree's identity and file position against the index.
   No random stage seeks.
3. Traverse cached trees with bounded depth 256,
   mode/name/type, missing-child, external-gitlink and
   cycle rules. Mark distinct reachable blobs without
   accepting their contents yet.
4. **Forward scan 2** over the stage: SHA1-verify only
   marked reachable blob bodies and compare their OID,
   type, length, record number and byte offset against
   the original index. Count authenticated reachable
   blobs. The module does not use `fseek`.
5. Require all reached blobs authenticated, no memory
   leak, and output validated TREE CLOSURE counters,
   `M178 FORWARD SCANS 2 RECORDS ... SEEKS 0`,
   `M178 AUTHENTICATED BLOBS ...`, and
   `M178 TREE CLOSURE PASS`. Fail closed otherwise.

This approach holds more tree bodies temporarily than
the original walk and rereads the stage twice. That
is an explicit bounded-memory tradeoff, not an
established faster implementation on CMS. An unusual
repository with more than 64MiB cumulative tree
data may fail this prototype while the original
walker succeeds; keep the original as baseline.
All previous M176/M177 modules and G stage/index
are unchanged.

Added the independent `GITPFAST EXEC` wrapper:
it requires an explicit non-A 4096-byte CMS
disk and 40-hex tree OID; checks the existing
stage/index and new GITPFST module, refuses
caller-bound STGIN or IDXIN DDs, establishes
temporary input FILEDEFs, runs the native
walker and cleans only its own DDnames.
It independently crosschecks counts, native
PASS, authenticated blob count, zero-seek
diagnostic, requested root, and cleanup RC.
No ERASE, FORMAT, stage/index OUTPUT or
directory command is present.

Host model: `tests/test-m178-forward-tree.py`
compiles both old/new modules with GCC
C89 `-Wall -Wextra -Werror`, compares
output for a tree/blob/gitlink fixture
including a 70,000B blob and verifies
failure on malformed OID, corrupted
blob body and missing child. Actions
native-stage runs the test for relevant
source changes. **Host testing cannot
establish z/VM 6.3 FILEDEF or large-stage
runtime behavior.**

### Exact eventual CMS target validation (after host CI)

Mac, from existing `ibm-sandbox/src`:

```sh
git pull
./cms-upload.sh GITPFST.C GITPFAST.EXEC
```

CMS MAINT, ensure previous stage/index remain
protected and no DD definitions exist:

```text
QUERY DISK G
STATE M173NET STAGE G
STATE M174NET INDEX G
QUERY FILEDEF
STATE GITPFST C A
CMSCLNK GITPFST PLAIN
STATE GITPFST MODULE A
GITPFAST G CCB18BEC067E7886D70B82EF138EE56A8B899A61
QUERY FILEDEF
```

Only run GITPFAST if the new C compiler/module
build succeeds. Check expected root closure:
8 trees, 272 blobs, zero gitlinks, 279 entries,
280 verified objects, global index 7736/7736.
Require `M178 TREE CLOSURE PASS`, the
two-pass/zero-seek counter, and final
`M178 VERIFIED FAST TREE TARGET GATE PASS`.
The FILEDEF state must be identical before/
after. Measure wall time externally and
compare with the old result only if the
measurement methods are genuinely comparable.
Never run `M173CHK G`, `M174CHK G` or
FORMAT as part of this experiment.
Retain the existing GITPTRE and GITPVIEW
as fallback under all circumstances.

---


## October 9, 2026, 15:51 CDT — prerequisite native gate closure

Subsequent to writing this plan, the operator confirmed
**full M175CHK G PASS**, **M177 GITPVIEW INFO G PASS**
and **identical empty before/after QUERY FILEDEF**
at 15:46:33 / 15:48:54. INFO runtime was
41.52s elapsed; standalone M175 runtime 124.65s.
Together with previously verified M177 TREE,
M173–M177 positive-path CMS validation is
complete. The below section titled *Immediate remaining
M177/M175 checks* is now historical and should
not be rerun before engineering M178.

No production C code has been changed, and the
unmeasured random-seek performance hypothesis
remains an engineering investigation, not fact.

---


**Status: isolated prototype source and host tests; not CMS target-proven.**
Prepared October 9, 2026 after full real-CMS M176 and M177 TREE
closure success using the 7,736-object stage/index on GIT600.

## Proven, immutable reference

- `M173NET STAGE G`: actual native PACK import and readback PASS
  (7,736 objects); expensive to recreate.
- `M174NET INDEX G`: 7,736 unique OIDs with complete stage/index
  audit PASS; do not modify.
- Root `CCB18BEC067E7886D70B82EF138EE56A8B899A61`;
  tip `ADA83FF3B3813961CEF2A9FFC50A453540039E0B`.
- Full `GITPTRE WALK` reached
  8 trees + 272 blobs = 280 verified objects, 279 entries,
  0 gitlinks, largest object 393767B, peak resident 394058B.
  The standalone `GITPVIEW TREE G` returned
  `M177 PACK VIEW TREE PASS` at 15:32 CDT on Oct 9.
- Its CMS `Ready; T=*.**/*.**` timing overflowed.
  A previous Ready line at 13:28:51 and TREE Ready at
  15:32:00 are about 2h03m09s apart, **not proof of exact
  elapsed duration for the TREE command**.

## Mechanism worth investigating

`src/GITPTRE.C` builds an in-memory OID-sorted index and
calls `fetch()` for each required tree/blob. In `fetch()`
it does `fseek(stage, ix[pos].offset, SEEK_SET)`,
then decodes and SHA1-verifies the object from
`dd:STGIN`. The 280-object root closure is verified
correctly; however, many random byte-offset seeks into
a large CMS variable-record stage could be costly.
This is a **hypothesis**, not a measured causal finding.

Do not weaken any of the existing guards:
- object header number/type/size/OID must match the
  verified index, and computed Git OID must match body
  SHA1 and object header;
- mode, name, child existence, child type, cycle/depth,
  external gitlink rules and resident memory caps;
- index ordered/unique boundaries and PEND1;
- full root/object counts and final authenticated
  closure PASS; wrong OID or corrupted body must
  fail closed;
- existing M176/GITPTRE/ GITPVIEW paths and original
  stage/index remain available for comparison.

## Safest work sequence

1. Add an **isolated** M178 native module (e.g.
   `GITPFST C`/MODULE) and M178 checker, built PLAIN,
   with its own input FILEDEFs. Avoid changing or
   overwriting the target-proven `GITPTRE MODULE`.
2. Begin with a portable Linux host fixture matching the
   native CMS text STAGE and PIDX1 formats. Compare
   new module vs `GITPTRE` in the same process environment:
   same tree/blob/gitlink/entry/verified counts;
   same accepted modes; identical SHA-authenticated
   subobject closure and same failure classes for
   missing/corrupt child, truncated stage/index,
   bad OID, cycle, depth, and memory exhaustion.
3. Consider **forward-only reading** of stage objects
   rather than up to 280 independent seeks:
   scan stage sequentially in its original object
   sequence, authenticate tree bodies while caching
   only bounded parsed tree edges; construct the
   reachable tree/blob closure using the existing
   OID index; scan stage sequentially to authenticate
   only the reachable blobs. Fail closed if tree-edge
   memory exceeds the bounded budget. A second full
   forward scan may outperform hundreds of random
   backward seeks on CMS, but must be measured.
4. Add bounded counters (stage records consumed,
   seeks attempted, objects authenticated) and host
   performance comparison. Counters are diagnostic
   only, not validation evidence.
5. After host CI passes, upload the **new** module only,
   run it on the existing 7736-object G stage/index
   without writes, and compare the live closure exactly
   against the already-proven M176/M177 counts.
   Record actual wall-time externally or via bounded
   instrumentation since CMS Ready T overflowed.
6. Only if new behavior is demonstrably correct and
   faster may an opt-in new GIT frontend command be
   considered. Do not change existing `GIT PACK-TREE`
   dispatch or the proven M177 TREE handler by default.

## Immediate remaining M177/M175 checks

The observed M177 TREE PASS does **not** independently
establish M177 INFO success, unchanged before/after
`QUERY FILEDEF` output or the complete M175 checker.
Their minimal read-only target checks are:

```text
QUERY FILEDEF
GITPVIEW INFO G ADA83FF3B3813961CEF2A9FFC50A453540039E0B
QUERY FILEDEF
M175CHK G
```

Skip standalone M175 if full terminal PASS was already
obtained. Do not re-run the slow root TREE just to
check filedef hygiene.

**Physical protection:** PMAINT0141 fullpack still
overlaps VMCOM1/0127 cylinders 6000–7599; do not
link/write it while G contains retained Git data.
Preserve `M171NET PACK/META A`, G stage/index and
directory backups.
