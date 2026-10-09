# M178 — speed up read-only tree closure without regenerating the PACK

**Status: analysis and implementation plan, not coded or target-proven.**
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
