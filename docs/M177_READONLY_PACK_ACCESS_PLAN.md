# M177 — explicit, read-only PACK access to verified CMS G repository

## Implemented source checkpoint — October 9, 2026

Added `src/GITPVIEW.EXEC`, a new 8-character CMS name,
without changing existing `GIT.EXEC`, `GITVREF.EXEC`
or native C modules. A corresponding
`tests/test-m177-pack-view.py` source guard runs in
the native-stage GitHub workflow. **Host proof is
not actual CMS validation.**

The EXEC checks an explicit non-A filemode
accessed with 4096-byte blocks, both retained
M173 stage/M174 index files, and the needed
existing native GITPCAT/GITPTRE module on A.
It checks the complete CMS `QUERY FILEDEF`
listing before binding inputs: any preexisting
STGIN or IDXIN causes refusal, with **no
replacement** of the caller's DD assignment.
The wrapper binds only its own two read-only
inputs and clears only its own definitions
after the native call. It requires both
native terminal PASS and exact request-OID
match. It performs no import, build,
directory update, CMS FORMAT or ERASE.
The z/VM 6.3 details of `QUERY FILEDEF`
remain to be proven at the actual target.

**Next target smoke-check**, only after
confirming the existing 7,736-object stage
and index remain intact and there is no
session FILEDEF conflict. On the Mac from
`ibm-sandbox/src`:

```sh
git pull
./cms-upload.sh GITPVIEW.EXEC
```

On CMS MAINT:

```text
QUERY DISK G
STATE M173NET STAGE G
STATE M174NET INDEX G
STATE GITPVIEW EXEC A
QUERY FILEDEF
GITPVIEW INFO G ADA83FF3B3813961CEF2A9FFC50A453540039E0B
GITPVIEW TREE G CCB18BEC067E7886D70B82EF138EE56A8B899A61
QUERY FILEDEF
```

The before/after FILEDEF queries must have
identical state. If either DD was defined
beforehand, **do not clear it**; wrapper is
designed to fail closed. INFO should print
`M175 PACK INFO PASS` and
`M177 PACK VIEW INFO PASS`; TREE should
print `M176 TREE CLOSURE PASS` and
`M177 PACK VIEW TREE PASS`, verifying
the same 8-tree/272-blob/280-verified
closure as the live M176 run. Stop on
unexpected RC or mismatched output, and
preserve the stage/index. A standalone
`M175CHK G` full PASS is still a distinct
milestone check if not already performed.

Official IBM CMS:
https://www.ibm.com/docs/en/zvm/7.3.0?topic=gc-query-filedef
https://www.ibm.com/docs/en/zvm/7.2?topic=commands-filedef

---


**Status: isolated source prototype implemented on GitHub; not target-proven.**
Prepared October 9, 2026 after actual M173, M174 and
M176 G-stage/index target PASS. The standalone M175CHK G
terminal result was not supplied with the M176 output.

## Verified baseline

- z/VM 6.3 CMS MAINT on Hercules; GCCCMS C compiler and
  CMS XF assembler operational. Use the existing C-first
  toolchain; do not recreate the verified M173 stage/index.
- New GIT600 CMS disk: MAINT vdev0600 3390 R/W 1600 CYL
  with 4096B blocksize, VMCOM1 real0127 start6000.
- Retained original M171NET PACK/META A:
  7736 objects, version2, 2171129 bytes,
  SHA1 A705122BC39A3383BC05ABC6C888A1F788B1D067.
- M173NET STAGE G: actual M173 independent READBACK PASS.
- M174NET INDEX G: 7736 unique OIDs, index audit and
  commit GET PASS.
- Live tip commit:
  ADA83FF3B3813961CEF2A9FFC50A453540039E0B,
  OBJ7000, type1, size265, parent
  B81D3CE7BAC08420BF7DB862E93F82FB3968DDC0.
- M176 root:
  CCB18BEC067E7886D70B82EF138EE56A8B899A61;
  full root closure 8 tree, 272 blob, 0 gitlinks,
  279 entries, 280 verified objects.
  Largest decoded object 393767B, resident peak 394058B.
- `GITPCAT MODULE` and `GITPTRE MODULE` were used
  successfully by M176. Its internal M175 PACK INFO PASS
  is **not** sufficient evidence of standalone M175CHK G.

## Problem to solve

The higher-level GIT EXEC already dispatches
`GIT PACK-CAT <40-hex-oid>` to GITPCAT and
`GIT PACK-TREE <40-hex-tree-oid>` to GITPTRE.
Native modules use the DDnames STGIN and IDXIN,
currently provided by the M175/M176 test checkers
through explicit `FILEDEF` setup/cleanup.
For everyday Git use, a caller should be able to
choose an existing non-A CMS filemode explicitly,
bind the verified stage/index without manually
recreating those FILEDEFs, and view one object/tree.
Do not silently choose A, overwrite any output
files, or alter a user's session FILEDEF state.

## Suggested M177 user-visible interface

One new short CMS REXX name, e.g. `GITPVIEW EXEC`
(8-character name). Proposed commands only:

```text
GITPVIEW INFO G ADA83FF3B3813961CEF2A9FFC50A453540039E0B
GITPVIEW TREE G CCB18BEC067E7886D70B82EF138EE56A8B899A61
```

Validate exact argument count, explicit single-letter
data filemode other than A, 40 uppercase hex OID,
and an accessed 4096-byte CMS disk.
Require existing `M173NET STAGE <mode>` and
`M174NET INDEX <mode>` with STATE RC0.
Do not create or update either protected file.
INFO must require expected type1 for a requested
commit in its target regression; TREE checks
native root/descendant walk and its own proof
marker.

The REXX wrapper should invoke only the native
read paths (`GITPCAT INFO`, `GITPTRE WALK`),
with bounded/checked pipeline results and
RC propagation. Do not copy object text to A,
modify Git refs, or run M173/M174.
The wrapper must **not** clobber preexisting
STGIN or IDXIN FILEDEFs: establish and test
the exact IBM CMS QUERY FILEDEF behavior on
the actual installed release first. If either
DD is already defined, fail closed without
rebinding or clearing it; otherwise bind
both, invoke, and clear only the bindings it
created, including all error paths.
Do not change global FILEDEF state in the
absence of a reliable preexisting-binding check.
If this check cannot be proven, prefer a
documented manual command sequence over an
unsafe wrapper. Avoid modifying GIT/GITVREF
until the isolated wrapper passes host tests
and real CMS validation.

Host tests: argument validation; unsafe filenames,
wrong mode, wrong OID, missing stage/index,
already-bound DDs, native nonzero RC and
cleanup; ensure zero ERASE/FORMAT/WRITE commands.
Test source formatting within fixed 80-column
CMS upload limits. Host fixture tests are not
proof of CMS QUERY FILEDEF behavior.

Target proof order: preserve M173/M174 data,
confirm standalone M175CHK G if not already
passed; transfer only new EXEC, run INFO on
tip and TREE on root, compare OID and closure
counts to M176. Leave existing G stage and
index intact; no repeat of lengthy imports,
index audits or disk formatting.

**Safety:** Physical PMAINT0141 VMCOM1 fullpack
overlaps G; never link it for writing while G
contains data. Preserve the CP directory
original/backup and original PACK on A.
