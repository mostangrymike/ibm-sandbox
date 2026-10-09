## CURRENT GATE — 2026-10-09 09:05:28 CDT: M173VQ assembler PASS; execution safety review

**Real CMS MAINT (09:05:28):**

```text
ASSEMBLE M173VQ
ASSEMBLER (XF) DONE
NO STATEMENTS FLAGGED IN THIS ASSEMBLY
Ready; T=0.08/0.10 09:05:28
```

The IBM-documented raw `DIAGNOSE X'25C'` machine bytes
`83 24 02 5C` **now assemble on actual z/VM 6.3 CMS XF**
(no flagged statements, RC0). The previous IFO078 RC8
compiler error is resolved. This is not a successful
DIAG invocation or a complete active-directory inventory.

### Preexecution validation against IBM DIAG X'25C'

- MAINT has CP privilege **B** within ABCDEFG.
- `Rx=R2`: address of the 48-byte parameter list,
  subsequently the number of bytes returned.
- `Ry=R4`: address of the fixed record output buffer.
- `Ry+1=R5`: on entry buffer capacity, on exit
  the DIAG return code; zero indicates success
  when condition code is zero. The 65520-byte
  buffer fits exactly 1092 records of 60 bytes.
- Zero/nonzero condition code, zero/nonzero R5,
  zero-length result, over-capacity and incomplete
  60-byte records all fail closed.
- `LSTMDISK` selects all owners, all virtual devices,
  volume `VMCOM1`, and all SSI systems (`*`);
  output consists of MDISK owner/VDEV/volume/device/
  start/size/system fields, not passwords.
- The parameter list must be doubleword aligned
  AND **must not cross a 4K page boundary**. The
  earlier program used `DS 0D` but did not check
  whether runtime LOAD relocation placed its 48
  bytes across pages. The current host correction
  adds an **explicit nonmutating fail-closed guard**
  before DIAG: it calculates `R2 & X'FFF'` and
  exits RC8 if the offset exceeds 4048, so the
  complete 48 bytes cannot cross the page.
  This extra guard has **NOT yet been target-compiled**.
- IBM `DIAG X'25C'` reports buffer-too-small as R5
  status X'08' and bytes required via R2. M173VQ
  refuses such a partial inventory; no results may
  be considered complete.
- The result is read-only and does **not** authorize
  changes to the CP directory or protection of
  the overlapping PMAINT/0141 fullpack (live
  VMCOM1 real0127 start0 length11000).

**NEXT TARGET — RECOMPILE FINAL GUARDED SOURCE ONLY.**

Mac, in `ibm-sandbox/src`:

```bash
git pull
./cms-upload.sh M173VQ.ASSEMBLE
```

On CMS MAINT:

```text
ASSEMBLE M173VQ
```

Do **not** run `M173VQ`, `LOAD`, or `GENMOD` until
the actual output verifies the new guard assembles
cleanly. Once it does, code/return-path review is
complete and the next gate can generate and execute
this single read-only CP query, with explicit review
of all printed VMCOM1 owners and full-pack definitions.

**HARD STOP:** No `DIRECTXA` without `(EDIT`,
no activation/formatting or linking of proposed
new virtual 0600/G, no import or overwrite of
the 4282-record original/backup directories,
candidate, M171NET PACK/META, generations or selectors.
Full-pack mitigation and rollback approval remain
independent safety requirements.

References:
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=codes-diagnose-code-x25c-directory-query
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=query-responses
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-genmod

---

## CURRENT GATE — 2026-10-09 08:55 CDT: active full-pack confirmed; M173VQ compile RC8 fixed in source, CMS RETEST REQUIRED

**Real CMS MAINT read-only results (October 9, 08:54):**

```text
CP QUERY MDISK USERID PMAINT 0141 LOCATION DIRECTORY
PMAINT 0141 PMAINT 0141 3390 VMCOM1 0127 0 11000
Ready; T=0.01/0.01 08:54:45
CP QUERY SYSTEM 0127
DASD 0127 ATTACHED CPVOL 0015 VMCOM1
MAINT 0551 R/O, MAINT 02CC R/W, MAINT 049E R/O
VMSERVP 0311/0310/0309/0308/0307/0306/0305/0304
VMSERVP 0303/0301/0302/0191 R/W
Ready; T=0.01/0.01 08:54:45
ASSEMBLE M173VQ
ASSEMBLER (XF) DONE
11 DIAG 2,4,X'25C'
IFO078 UNDEFINED OP CODE
NUMBER OF STATEMENTS FLAGGED IN THIS ASSEMBLY = 1
Ready(00008); T=0.09/0.11 08:55:00
```

**Full-pack physical extent LIVE CONFIRMED:** The active CP
directory defines `PMAINT 0141` on VMCOM1 real 0127,
start 0, size **11000** cylinders. That spans the
entire real device 0–10999 and overlaps proposed 0600
6000–7599. The earlier candidate DIRMAP's full-pack
0–10016/10017 is its model-size inference, NOT
the active CP full-pack capacity. `QUERY SYSTEM 0127`
showed **15 linked devices**, and no PMAINT 0141
active link in that instant. This does NOT prevent a
future PMAINT 0141 link or its overlapping access.
A single-writer `W` on 0600 cannot alone isolate
against full-pack read/write access. Full inventory
and access-controls decision remain mandatory.

**Initial M173VQ assembler gate FAILED RC8.** This was
not a CP DIAG error. IBM explicitly states that
DIAGNOSE has *no assembler mnemonic*. `DIAG` is
a macro provided on supported macro paths and was
not expanded by the installed XF assembly. The
host GitHub source replaces only the offending line:

```asm
* IBM opcode X'83'; Rx=2 Ry=4 base=0, code X'25C'.
         DC    X'83',X'24',XL2'025C'
```

The four emitted bytes are `83 24 02 5C`,
and the surrounding CP condition-code, return-code
and 60-byte bounded record checks are unchanged.
This is the IBM-documented machine instruction
encoding, not an invented assembler alias. A new
host regression parses the bytes and tests opcode,
both register fields, base=0, and X'25C' code.

**NEXT ACTUAL CMS GATE — COMPILE ONLY.** From Mac's
`ibm-sandbox/src` working directory, after new
GitHub CI passed:

```bash
git pull
./cms-upload.sh M173VQ.ASSEMBLE
```

On CMS MAINT:

```text
ASSEMBLE M173VQ
```

Do not LOAD, GENMOD or execute M173VQ/DIAG until
the actual assembler status and new listing are
evaluated, including correct return/error handling.
No target proof for fixed source exists yet.
The earlier RC8 source must not be used again.

**HARD STOP:** No non-EDIT DIRECTXA, active CP directory
activation, LINK, ACCESS, FORMAT, importer, or
overwriting USER DIRECT C, M173BAK DIRECT C, M173NEW
DIRECT C, PACK, or verified generations. PMAINT full-pack
access and complete live directory definitions still
need a separately approved mitigation/rollback plan.

IBM:
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=machine-instruction-format
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=machine-macro-format
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=codes-diagnose-code-x25c-directory-query

---

## CURRENT GATE — 2026-10-09 08:37 CDT: Gate 5e full-pack discovery PASS

Real MAINT `CP QUERY PRIVCLASS` at 08:36:37 returned Currently
ABCDEFG and Directory ABCDEFG, establishing CP class B.
`PIPE < M173NEW MDISKMAP C | DROP 100 | TAKE 100 | CONSOLE`
at 08:37:07 revealed `VMCOM1 3390 PMAINT 0141 MR
000-10016 length10017`: a full-pack definition overlapping
the proposed MAINT-1 0600 cylinders 6000-7599.
A nearby `$DIRECT$ 0B01 R 131-230` is outside that extent.
This is candidate source-map data, not yet an active-directory
inventory. IBM warns that full-pack minidisks may overlap
other minidisks and bypass normal link-mode conflict checking.
Thus W on 0600 is not independent protection from full-pack
access. The discovery is an explicit safety hold, not a
failure of the prior Gates 5c and 5d geometry checks.

A host source-guarded prototype `M173VQ.ASSEMBLE` makes a
read-only CP DIAG X'25C' LSTMDISK request for VMCOM1
(all owners and virtual devices, all systems), with a 48-byte
doubleword-aligned parameter list, flags zero, and a bounded
65520-byte output (1092 fixed 60-byte records). The 6.4
SUBCONFIG output flag is not available on z/VM 6.3. The
prototype rejects nonzero CP return, missing, overflow and
partial data. **It has not yet run or compiled on CMS.**
Its console marker is QUERY COMPLETE NOT ACTIVATION APPROVAL.

NEXT read-only CP commands on CMS MAINT:

```text
CP QUERY MDISK USERID PMAINT 0141 LOCATION DIRECTORY
CP QUERY SYSTEM 0127
```

After host CI succeeds, separate CMS **compile-only**
verification: on Mac in ibm-sandbox/src run `git pull` and
`./cms-upload.sh M173VQ.ASSEMBLE`; on CMS run
`ASSEMBLE M173VQ`. No LOAD, GENMOD or execution of the
new DIAG program until actual assembler results are
reviewed. Those steps are distinct from CP directory
activation, LINK, ACCESS, FORMAT and M173 import,
which remain on hold pending complete live directory
inventory and controlled rollback authorization.

---
## CURRENT GATE — 2026-10-09 08:28:36 CDT: M173 Gate 5d LIVE PASS

Real MAINT z/VM 6.3 CP and CMS read-only results:

```text
CP QUERY DASD DETAILS 0127
0127  CUTYPE = 3990-C2, DEVTYPE = 3390-0C, VOLSER = VMCOM1, CYLS = 11000
Ready; T=0.01/0.01 08:28:13
CP QUERY MDISK USERID 6VMHCD20 0300 LOCATION DIRECTORY
6VMHCD20 0300 6VMHCD20 0300 3390  VMCOM1 0127       5756        180
Ready; T=0.01/0.01 08:28:15
CP QUERY MDISK 0600 DIRECTORY
HCPQMD040E Device 0600 does not exist
Ready(00040); T=0.01/0.01 08:28:26
CP QUERY ALLOC MAP VMCOM1
VMCOM1 0127          -          -      0      0      0   0% NOT FOUND
Ready; T=0.01/0.01 08:28:26
M173DCHK
M173 DIR ORIGINAL/BACKUP VERIFIED 4282
M173 DIR MAINT-1 SUBCONFIG VERIFIED
M173 DIR SINGLE MDISK INSERT RECORD 213
M173 DIR DELTA CHECK PASS
Ready; T=0.83/0.85 08:28:36
```

**Gate 5d LIVE PASS:** Real DASD VMCOM1 = RDEV 0127, 11,000
cylinders; the existing permanent 6VMHCD20/0300 occupies
5756-5935 (180); MAINT virtual 0600 is still absent RC40
(expected negative gate); no CP-use PAGE/SPOOL/TDISK/DRCT
extents are reported by QUERY ALLOC MAP on VMCOM1;
M173DCHK target PASS RC0 proves original USER DIRECT C
and protected M173BAK DIRECT C (4,282 records) are equal
and M173NEW DIRECT C has only one MAINT-1 MDISK at 213.
Gate 5c already independently confirmed the candidate-map
`VMCOM1 3390` context, 0600 W 6000-7599 length1600,
and surrounding gaps 5936-5999, 7600-10016.

**This PASS is NOT approval to activate.** IBM says
QUERY ALLOC MAP excludes PERM/PARM extents, and CP can
permit full-pack minidisks to overlap ordinary ones;
DIRMAP ignores fullpack MDISKs in overlap detection.
Candidate-source mapping plus two targeted CP queries
do not enumerate every active VMCOM1 directory definition.

### Gate 5e: safely qualify a complete active-directory inventory

Two **read-only** commands on CMS MAINT; no new code, build,
FILEDEF, directory edit, or disk access is required:

```text
CP QUERY PRIVCLASS
PIPE < M173NEW MDISKMAP C | DROP 100 | TAKE 100 | CONSOLE
```

The first identifies MAINT's current privilege classes.
**Only** if the `Currently:` response contains B can
a later separately engineered *read-only* CP
`VMUDQ LSTMDISK` directory query be considered;
IBM's supported VMUDQ interface can select all owners,
all virtual addresses and the **VMCOM1** volser.
Its availability and exact macro interface on the
installed z/VM 6.3 level remain UNTESTED. Do not
grant privileges, change CP state or guess a CMS
assembler command. If class B is absent, stop this
approach and find an authorized, nonmutating inventory
alternative.

The second command displays the earlier (previously
unseen in the recent output) candidate-map rows
before the confirmed page-5 VMCOM1 section, including
any full-pack definitions within the source map. Inspect
privately and share only nonsensitive map data.
An apparent VMCOM1 full-pack definition needs special
review; it does not automatically mean 0600 is unusable
but could defeat overlap/access protections. This
source inspection by itself is NOT independent CP proof.

Following those two read-only outputs, design and
host-test an authorized independent, **complete**
active-directory inventory of VMCOM1 before deciding
whether controlled activation is acceptable. Require
evidence accounting for VMCOM1 full-pack/END overlays,
SSI local vs global entries, all PERM/PARM and CP-owned
areas, and an explicit rollback operator plan. Any
unresolved case fails closed. IBM `MDISK` cautions that
overlaps can compromise integrity; do not rely only
on a clean candidate map.

**HARD STOP**: No non-EDIT DIRECTXA, CP directory activation,
LINK, ACCESS, FORMAT, M173CHK/import, disk erase,
source overwrite or gratuitous privilege change. The
new virtual 0600/G does not exist in the online CP directory;
the original PACK, generations and saved directory
sources are protected. The completed EBS snapshot's
source/Region were operator-matched; isolated restore
is **not** proven. A final separately authorized change
and rollback procedure remains required.

Official IBM:
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-privclass
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=macros-vmudq-vm-user-directory-query
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=directory-mdisk-statement
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-alloc

---

## CURRENT GATE — 2026-10-09: M173 Gate 5c LIVE PASS; CP independent hold

**Gate 5c now PASSED on real CMS.** On October 9,
`PIPE < M173NEW MDISKMAP C | DROP 200 | TAKE 100 | CONSOLE`
displayed the complete candidate-map context across pages 5–6.
The repeated section header explicitly establishes `VMCOM1 3390`,
followed in the same section by these exact nonsecret rows:

```text
VMCOM1 3390     6VMDIR30  02B1 MR        4850       4859        010
                 6VMHCD20  0300 MR        5756       5935        180
                                          5936       5999        064     Gap
                 MAINT     0600 W         6000       7599       1600              MAINT-1   *
                                          7600      10016       2417     Gap
-------------------------------------------------------------------
630RL1 3390     MAINT630  0131 MR         000      10016      10017
```

The displayed `630RL1` full-pack mapping is on **another
volser**; it is not evidence of a VMCOM1 overlap. Within
the candidate VMCOM1 map there is no reported conflicting
extent: preceding permanent `6VMHCD20 0300` ends 5935;
gap 5936–5999 is 64 cylinders; new MAINT-1 virtual 0600
is exclusive `W` from 6000 through 7599 (1600);
gap 7600–10016 is 2417. All counts and adjacencies match.
This is **source-derived candidate map proof**, not proof
that all active CP PERM/PARM/full-pack extents have been
independently inventoried.

### Next Gate 5d: live CP preactivation revalidation, READ-ONLY

On CMS MAINT run this small independent query/check batch,
without editing or activating anything:

```text
CP QUERY DASD DETAILS 0127
CP QUERY MDISK USERID 6VMHCD20 0300 LOCATION DIRECTORY
CP QUERY MDISK 0600 DIRECTORY
CP QUERY ALLOC MAP VMCOM1
M173DCHK
```

Expected: physical 0127 VOLID VMCOM1, CYLS 11000;
6VMHCD20/0300 VMCOM1 real0127 start5756 size180,
ending5935; MAINT/0600 remains ABSENT `HCPQMD040E`
(RC40, expected *negative* test); no VMCOM1 CP-owned
PAGE/SPOOL/TDISK/DRCT extent (`NOT FOUND` for
`QUERY ALLOC MAP`); M173DCHK full original/backup and
one-line MAINT-1 candidate verification RC0. Any unexpected
response, denied privilege, changed device, or ambiguity
stops the gate; `NOT FOUND` in ALLOC does **not** prove
absence of PERM/PARM or fullpack overlays. These are
rechecks of previously target-proven syntax and prior
results, not a newly authorized allocation or activation.

**After Gate 5d** still require independent confirmation
that the active CP directory has no full-volume/hidden
VMCOM1 overlay, explicit controlled activation/rollback
authorization, working console and tested or accepted EBS
restore risk. A completed snapshot (operator-attested
source/region) is not a test restore. IBM DIRMAP ignores
fullpack MDISKs for overlap detection; an MDISKMAP with
no overlap flag does not override that limitation. IBM
QUERY ALLOC omits PERM/PARM allocations from its map.
Keep `USER DIRECT C`, `M173BAK DIRECT C`,
`M173NEW DIRECT C`, candidate MDISKMAP, original PACK,
and sealed generations unchanged.

**HARD STOP**: no non-EDIT DIRECTXA/CP directory activation,
LINK, ACCESS, FORMAT, `M173CHK` or import. New virtual 0600
and CMS G do **not** exist in the active configuration.

References:
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-dirmap
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-mdisk
- https://www.ibm.com/docs/en/zvm/7.2?topic=commands-query-alloc

---

## CURRENT GATE — 2026-10-09 08:16:20 CDT: Gate 5c boundaries LIVE PASS, VOLSER context pending

**Real CMS MAINT results, read-only candidate DIRMAP report**:
```text
PIPE < M173NEW MDISKMAP C | LOCATE /6000/ | CONSOLE
                 MAINT     0600 W         6000       7599       1600              MAINT-1   *
Ready; T=0.01/0.01 08:15:58
PIPE < M173NEW MDISKMAP C | LOCATE /7599/ | CONSOLE
                 MAINT     0600 W         6000       7599       1600              MAINT-1   *
Ready; T=0.01/0.01 08:15:59
PIPE < M173NEW MDISKMAP C | LOCATE /5936/ | CONSOLE
                                          5936       5999        064     Gap
Ready; T=0.01/0.01 08:16:19
PIPE < M173NEW MDISKMAP C | LOCATE /7600/ | CONSOLE
                                          7600      10016       2417     Gap
Ready; T=0.01/0.01 08:16:20
```

**Four boundary filters LIVE PASS (RC0).** MAINT-1 MDISK
0600 W spans cylinders 6000-7599 (1600 cylinders). Adjacent
candidate-map gaps are 5936-5999 (64) and 7600-10016
(2417); endpoint arithmetic independently agrees.

**FULL GATE 5c PENDING:** DIRMAP continuation rows omit their
VOLSER; the four matches do not establish the enclosing
VMCOM1 report section or rule out additional allocations.
Next **read-only** command on CMS MAINT:

```text
PIPE < M173NEW MDISKMAP C | DROP 200 | TAKE 100 | CONSOLE
```

Review the contiguous VMCOM1 section privately. Report only
nonsecret VOLSER/extent summaries, not password-bearing
USER DIRECT source. If context is absent or ambiguous, STOP,
do not infer VMCOM1 solely from the numeric filters.

Even a clean contextual DIRMAP is source-derived, **not an
independent CP allocation census**. IBM specifies that DIRMAP
ignores fullpack MDISKs for overlap detection; hidden PERM/PARM
reservations and current live fullpack allocation must be
considered separately before any activation authorization.
Neither the CP directory nor new G device has changed.
HARD STOP: no non-EDIT DIRECTXA, LINK, ACCESS, FORMAT,
M173CHK/import or replacement of protected directory sources.
IBM: https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-dirmap

---

## CURRENT GATE — 2026-10-08 16:32:22: Gate 5b CMS PASS

Operator completed every Gate 5b command in sequence:

```text
DIRECTXA M173BAK DIRECT C (EDIT
z/VM USER DIRECTORY CREATION PROGRAM - VERSION 6 RELEASE 3.0
EOJ DIRECTORY NOT UPDATED
Ready; T=0.17/0.19 16:31:49
STATE M173NEW MDISKMAP C
DMSSTT002E File M173NEW MDISKMAP C not found
Ready(00028); T=0.01/0.01 16:31:57
DIRMAP M173NEW DIRECT C C
DMSCYD2231I M173NEW DIRECT C1 read.
DMSCYD2232I M173NEW MDISKMAP C1 written - no errors.
Ready; T=0.02/0.03 16:32:10
LISTFILE M173NEW MDISKMAP C (ALLOC
M173NEW MDISKMAP C1 F 100 394 10
Ready; T=0.01/0.01 16:32:11
QUERY DISK C
MNT2CC 2CC C R/W 10 3390 4096 8 298-17 1502 1800
Ready; T=0.01/0.01 16:32:22
```

**Gate 5b backup EDIT + new C-only map generation PASS.**
The original backup syntax-compiles with RC0, not updated.
Report output was absent before generation and the DIRMAP
utility wrote it without errors. New report is 394 F100
records, ten 4K blocks; the prior original USER MDISKMAP C
was 392 F100 records, ten blocks. This difference is
consistent with new allocation and free-gap splitting but
is NOT by itself proof of their physical locations.
CMS C (MAINT 02CC) is R/W with 1502 free 4K blocks;
the two original directory source files are untouched.

### Gate 5c: read-only prospective VMCOM1 extent review

CMS MAINT: use the proven CMS PIPE syntax to filter the
new candidate report by extent-boundary numbers. Unlike
a filter on VMCOM1 alone, numeric matching finds rows
whose leading VOLSER is omitted by DIRMAP continuation
format. These reads do not modify any CMS file:

```text
PIPE < M173NEW MDISKMAP C | LOCATE /6000/ | CONSOLE
PIPE < M173NEW MDISKMAP C | LOCATE /7599/ | CONSOLE
PIPE < M173NEW MDISKMAP C | LOCATE /5936/ | CONSOLE
PIPE < M173NEW MDISKMAP C | LOCATE /7600/ | CONSOLE
```

Expect the new MAINT-1 allocation on VMCOM1 with
VDEV `600` (or `0600`), type 3390, exclusive W,
start 6000, end 7599, size1600; gaps 5936-5999
and 7600-10016, unless the report reveals additional
allocations. The 6000 filter can also match other
volumes or values. Check report section headings and
surrounding entries privately before accepting a row;
do not infer completeness from four text filters.

If outputs are ambiguous, privately use the earlier
proven contiguous report chunk to see the whole
VMCOM1 section, without showing USER DIRECT lines:

```text
PIPE < M173NEW MDISKMAP C | DROP 200 | TAKE 100 | CONSOLE
```

**Never paste password-bearing USER DIRECT excerpts.**
The map is generated and ordered by DIRMAP from a
candidate source, not an independent live CP database;
source-invisible permanent extents, full-volume mappings
and parameter reservations require separate review.
STOP on any wrong volser/start/end/size, overlap, missing
boundary, or unknown report meaning. Do NOT activate CP
directory, LINK, ACCESS, FORMAT, or run M173 importer.

---
## CURRENT GATE — 2026-10-08 16:23:33: CP preactivation reads PASS

Observed real z/VM 6.3 MAINT console results:

```text
CP QUERY CPOWNED VOLID VMCOM1
Slot 5 VMCOM1 0127 Own Online and attached
Ready; T=0.01/0.01 16:23:10
CP QUERY ALLOC MAP VMCOM1
VMCOM1 0127 - - 0 0 0 0% NOT FOUND
Ready; T=0.01/0.01 16:23:10
CP QUERY ALLOC DRCT ALL
M01RES 0123 1 20 20 1 2 5% ACTIVE
Ready; T=0.01/0.01 16:23:25
CP QUERY MDISK 0600 DIRECTORY
HCPQMD040E Device 0600 does not exist
Ready(00040); T=0.01/0.01 16:23:25
M173DCHK
M173 DIR ORIGINAL/BACKUP VERIFIED 4282
M173 DIR MAINT-1 SUBCONFIG VERIFIED
M173 DIR SINGLE MDISK INSERT RECORD 213
M173 DIR DELTA CHECK PASS
Ready; T=0.82/0.84 16:23:33
```

**Gate 5 read-only allocation checks PASS as observed.** VMCOM1
real 0127 is CP-owned and online. IBM QUERY ALLOC MAP
`NOT FOUND` means no PAGE, SPOOL, TDISK, or DRCT extents
are allocated on VMCOM1, not that the volume is blank.
IBM explicitly warns that areas absent from this map
are **PERM/PARM** allocations; it does not detect user
minidisk overlap or full-pack/parameter overlays.
The previously generated USER MDISKMAP C on
the original 4282-line source maps VMCOM1 gap
5936-10016, and an earlier live query verified
6VMHCD20 0300 ends at cylinder 5935. Proposed
start6000 size1600 covers 6000-7599, wholly within
the reported gap but not proven against every possible
outside-source/hidden allocation.

**Directory system extent:** the active object directory
is on M01RES real 0123, CKD cylinders 1-20;
`TOTAL=20`, `IN USE=1`, `HIGH=2`, `USED=5%`, `ACTIVE`.
These are reported allocation figures, not a guaranteed
test of writing an alternate directory or rollback.
Virtual 0600 is still absent in the active permanent
directory; verified candidate M173NEW remains unchanged.

### Gate 5b: prepare rollback source and prospective map

These are **non-activating** operations on MAINT. Run in
the order shown and STOP on an unexpected RC or collision.
First syntax-check the saved untouched rollback source:

```text
DIRECTXA M173BAK DIRECT C (EDIT
```

Require installed z/VM 6.3 version, `EOJ DIRECTORY NOT
UPDATED`, RC0, and no errors. In particular, do not omit
the literal `(EDIT` or substitute `USER DIRECT C`.

Next check the prospective report name is unoccupied:

```text
STATE M173NEW MDISKMAP C
```

Expected not-found RC28. **If the file exists or the
RC is not 28, STOP without executing DIRMAP.**
Only if absent and backup EDIT passed, generate a
new CMS C report from the candidate using the
previously target-proven standalone CMS DIRMAP syntax:

```text
DIRMAP M173NEW DIRECT C C
LISTFILE M173NEW MDISKMAP C (ALLOC
QUERY DISK C
```

This DIRMAP operation creates a report on C; it is
not DirMaint, not a CP directory activation, and does
not reassign any MDISK. Require normal RC0 and a
newly created M173NEW MDISKMAP C file. The original
USER MDISKMAP C is preserved.

Privately inspect the report's VMCOM1 entries and
record only nonsensitive extent summaries: exactly
one new MAINT/MAINT-1 virtual 600/0600 with
VMCOM1 start 6000 size1600 end7599; no reported
overlaps; and the original free gap split around
the new allocation. Expected open sub-gaps if
there are no other mapped entries: 5936-5999
and 7600-10016. Do not paste USER DIRECT
records, passwords, or the entire report.

**STOP after Gate 5b.** A new DIRMAP report is
source-derived, not an exhaustive inventory of
live full-volume minidisks, future allocations or
CP-owned parameter space. Explicit activation
permission, a credible source-based rollback
operation, current console access, and guest-logon
refresh planning remain separate gates. No
`DIRECTXA` without `(EDIT`, no LINK/ACCESS/FORMAT
of 0600, no G admission or Git M173 import yet.

IBM references:
https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-alloc
https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-directxa
https://www.ibm.com/docs/en/zvm/7.2.0?topic=configuration-changes-maint-user-id

---
## CURRENT GATE — 2026-10-08 16:20:21: TARGET GATE 4 PASS

Operator's real MAINT CMS syntax-only compilation completed:

```text
STATE DIRECTXA MODULE *
Ready; T=0.01/0.01 16:20:11
DIRECTXA M173NEW DIRECT C (EDIT
z/VM USER DIRECTORY CREATION PROGRAM - VERSION 6 RELEASE 3.0
EOJ DIRECTORY NOT UPDATED
Ready; T=0.52/0.57 16:20:21
```

**GATE 4 RC0 PASS**. The installed-release DIRECTXA
compiled the 4283-record candidate without errors and
explicitly did NOT change the online CP directory.
Prior Gate 3 target M173DCHK RC0 also passed.

### Gate 5: CP allocation and rollback preflight (read-only)

STOP: no activation is authorized yet. IBM DIRECTXA without
EDIT writes an alternate CP object directory and updates
the CP-owned DASD directory pointer, potentially taking
the new directory online immediately. Source backups
on CMS C do not by themselves guarantee an independently
recoverable CP-owned directory. The EBS recovery snapshot
was completed and operator-matched but not test-restored.

Run the following **read-only** commands on MAINT:

```text
CP QUERY CPOWNED VOLID VMCOM1
CP QUERY ALLOC MAP VMCOM1
CP QUERY ALLOC DRCT ALL
CP QUERY MDISK 0600 DIRECTORY
M173DCHK
```

Expect VMCOM1 real 0127 and the proposed new physical
extent 6000–7599 absent from every CP-owned page/spool/
tdisk/directory allocation as well as existing MDISK map.
`QUERY ALLOC MAP` checks **CP-owned areas**, not ordinary
permanent or parameter areas, which must be checked
separately against the prior USER MDISKMAP and direct
permanent-directory boundary evidence. An unrecognized
command or privilege denial is NOT evidence of safety.
`QUERY ALLOC DRCT ALL` must identify the current ACTIVE
directory allocation and show it has space for the alternate
directory. Record the active directory VOLID and extent
privately; do not post any password-bearing directory text.
Repeat the permanent 0600 absence check to rule out a
last-minute conflicting allocation. Any new or unknown
extent overlap, change, or discrepancy: STOP.

IBM QUERY ALLOC requires CP privilege class D for
allocation reports; QUERY CPOWNED is class G. The
active CP directory may be on M01RES, but this is
not established by the 16:20 DIRECTXA EDIT output.

IBM DIRECTXA update semantics: it writes a new alternate
directory instead of overwriting the current one; changes
the volume-label pointer, and brings an eligible current
directory online. A rollback would require a separately
authorized non-EDIT compile of the **retained, original**
`M173BAK DIRECT C` from a usable recovery console.
Do NOT issue such a command during preflight; first
validate the backup candidate in its own `(EDIT` run and
document access/relogon and restore procedure in a
separate approved change window. Re-compilation may
also overwrite the alternate slot, so do not describe the
existing inactive slot as a permanent standalone backup.

After eventual activation, the existing logged-on MAINT
virtual configuration may still reflect the OLD directory.
Expect an expressly planned logoff/logon or other IBM-
supported refresh before verifying virtual 0600, and
never FORMAT until owner, real-device 0127, VMCOM1,
start6000, length1600, exclusive R/W mode, and new
blank-disk identity are independently proven. Preserve
`USER DIRECT C`, `M173BAK DIRECT C`, `M173NEW DIRECT C`
and protected Git source/stage artifacts; a later
separate task must reconcile authoritative USER DIRECT
source with the activated directory after confirming
success, without losing the rollback source.

Official IBM references:
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-directxa
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-cpowned
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-alloc
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=dasds-displaying-list-cp-owned-volumes

---
## CURRENT GATE — 2026-10-08 16:13:55: TARGET GATE 3 PASS

Real MAINT CMS output:

```text
M173DCHK
M173 DIR ORIGINAL/BACKUP VERIFIED 4282
M173 DIR MAINT-1 SUBCONFIG VERIFIED
M173 DIR SINGLE MDISK INSERT RECORD 213
M173 DIR DELTA CHECK PASS
Ready; T=0.82/0.84 16:13:55
```

**Gate 3 is target-verified RC 0**. The 4282-record
`USER DIRECT C` and `M173BAK DIRECT C` are identical;
the 4283-record `M173NEW DIRECT C` is exactly the original
plus one MDISK at record 213, within SSI-ready
`SUBCONFIG MAINT-1` belonging to `IDENTITY MAINT` via
its active BUILD reference. VDEV spelling `600` and `0600`
denotes the same hexadecimal device address. No additional
source edits or file copies are needed.

### Gate 4 next: **DIRECTXA (EDIT) syntax-only**, no activation

The IBM DIRECTXA documentation explicitly says the EDIT
option checks syntax **without updating the directory on disk**.
Supply the fully-qualified candidate file ID and keep the
literal `(EDIT` option; omission can write the CP directory.
Do not use the DELTA option: it is incompatible with
IDENTITY/SUBCONFIG sources. `EOJ DIRECTORY NOT UPDATED` is
necessary but not sufficient for success, because errors can
produce that response too. Require no errors and RC0.

From CMS MAINT, first check availability (read-only):

```text
STATE DIRECTXA MODULE *
```

If RC0 and the unchanged Gate 3 result is trusted, the
only authorized Gate 4 operation is:

```text
DIRECTXA M173NEW DIRECT C (EDIT
```

Stop on any error or RC other than 0; preserve the full
private console diagnostic for yourself and share only
redacted, nonsecret error codes, final EOJ line and CMS
return code. The CP user directory contains passwords.
Do not perform an unqualified/non-EDIT DIRECTXA, DIRECTORY
replacement, DIRMAP, LINK, ACCESS, FORMAT, or M173 importer
as part of Gate 4. Do not change `USER DIRECT C` or
`M173BAK DIRECT C`.

If `STATE DIRECTXA MODULE *` reports missing, stop.
IBM says DIRECTXA is normally on the PMAINT 551 cross-release
utilities disk, whose MAINT-1 source contains a LINK;
check its virtual presence and whether it is accessed
before attempting any read-only disk ACCESS. Do not
guess a filemode or replace any existing access entry.

IBM reference:
https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-directxa

---
## IMPORTANT 2026-10-08 16:04 — SSI-ready MAINT-1 correction

**Earlier Gate 3 directions that require a USER MAINT heading
immediately before the new MDISK are SUPERSEDED. DO NOT rerun
XEDIT, COPYFILE, DIRECTXA, DIRMAP, LINK, ACCESS or FORMAT.**

Operator inspection established this nonsecret structure:
`IDENTITY MAINT` at record 162, its active
`BUILD ON * USING SUBCONFIG MAINT-1` mapping,
`SUBCONFIG MAINT-1` at record 181, and the one added
`MDISK` at record 213 inside that section immediately before
its end comment. This is a valid location for a minidisk
statement of a multiconfiguration MAINT identity.

The displayed virtual address `600` is the same hexadecimal
device number as `0600`. In REXX, numeric-looking operands
compared with `=` may compare equal, explaining why the
earlier seven-field diagnostic reported MATCH while
whole-line text comparison rejected the inserted record.
Do not rewrite the candidate merely to add a leading zero.

IBM confirms that an IDENTITY's BUILD statement associates
the appropriate SUBCONFIG and that minidisks belong inside
the SUBCONFIG:
https://www.ibm.com/docs/en/zvm/7.2.0?topic=directory-build-statement
https://www.ibm.com/docs/en/zvm/7.2.0?topic=directory-subconfig-statement

The new read-only `M173DCHK.EXEC` requires exactly one added
MDISK with address `600` or `0600`, seven approved fields,
full equality of original/backup, full shifted-record equality
of candidate, enclosing `SUBCONFIG MAINT-1`, and exactly one
active `BUILD ON * USING SUBCONFIG MAINT-1` under
`IDENTITY MAINT`. It must PASS on CMS before a separate
syntax-only DIRECTXA EDIT review. Do not publish unredacted
directory records: the original source contains credentials.

---
# M173 dedicated CMS G: controlled MAINT directory change plan

Status: **Gate 2b PASS; candidate M173NEW now has 4283 F80 records.
Gate 3 first read-only verifier attempt failed at original EXECIO
(EXECCOMM rc8). Corrected checker is host-gated; CMS rerun PENDING.
NO CP directory activation, LINK/ACCESS, FORMAT or M173 import.**
This plan is for the z/VM 6.3 MAINT operator, not a shell script.
Do not execute a privileged action automatically or as a single batch.

## Evidence and boundaries — 2026-10-08

- The AWS EC2 snapshot shows **Completed**, **100%**, 16 GiB
  original EBS volume, and a 2026-10-08 start time.
- The operator independently confirms that the snapshot source EBS
  volume and AWS Region match the Hercules EC2 root EBS volume,
  and that the recovery procedure is understood. No isolated restore
  test has been performed. Keep IDs/private credentials off GitHub.
- Hercules PID 724, cwd `/home/admin/vm630`, configuration
  real `0123 -> dasd1` (FD12), real `0127 -> dasd5` (FD16).
- CMS A/M01RES and C/VMCOM1 are preserved, with essential
  `M171NET PACK A` and `M171NET META A`.
- Candidate virtual address `0600`: `CP QUERY VIRTUAL 0600`
  and `CP QUERY MDISK 0600 DIRECTORY` both returned
  device-does-not-exist. Reconfirm immediately before activation.
- VMCOM1 real `0127` is 11,000 cylinders. The source DIRMAP
  showed physical gap `5936–10016`. The permanent-directory query
  for `6VMHCD20 0300` confirmed start `5756`, size `180`,
  last cylinder `5935`. Four MAINT M01RES permanent minidisks
  agreed exactly with `USER DIRECT C` source. This is convincing
  *sample corroboration*, NOT an exhaustive active-directory or
  reserved-extent equivalence proof.
- Target candidate: MAINT virtual `0600`, device `3390`,
  real volume `VMCOM1`, start **6000**, length **1600**,
  end **7599**. Planned CMS filemode `G` later.
- IBM MDISK mode `W` gives exclusive write access and is preferred
  for this privately owned data disk; historical `MR` examples
  are **not approved**. A final privileged review must confirm
  mode, sharing/passwords, and no SSI/subconfig/extent conflict.
- A 1600-cylinder 3390 holds about 288,000 4KiB CMS blocks gross;
  actual `QUERY DISK G` must confirm at least 180,000 **free**
  blocks after the *new* disk has been intentionally initialized.

## Gate 1: read-only CMS preflight — safe to run before copying

On the logged-on MAINT CMS session:

```text
QUERY DISK C
STATE USER DIRECT C
STATE M173BAK DIRECT C
STATE M173NEW DIRECT C
STATE M173NEW MDISKMAP C
CP QUERY MDISK 0600 DIRECTORY
```

Expected: C is R/W 4K with comfortably more than 500 free blocks;
the original USER DIRECT C is present; the three **new output IDs
are absent** with `STATE` return code **28**, and 0600 is still
absent in MAINT's permanent directory. Any unexpected result:
**STOP and report the error without showing password-bearing data**.
No existing output must be replaced or erased.

All new CMS filenames/filetypes are at most 8 characters;
`M173BAK` and `M173NEW` are distinct from `USER DIRECT C`.

## Gate 2: controlled duplicate copies on C — completed, see below

Only after Gate 1 passes, use IBM CMS COPYFILE **NEWFILE** so a
collision fails closed instead of replacing an existing file:

```text
COPYFILE USER DIRECT C M173BAK DIRECT C (NEWFILE
COPYFILE USER DIRECT C M173NEW DIRECT C (NEWFILE
LISTFILE USER DIRECT C (ALLOC
LISTFILE M173BAK DIRECT C (ALLOC
LISTFILE M173NEW DIRECT C (ALLOC
```

Both copies must match the original F80 record count and type/size.
This is a sanity comparison only, not a cryptographic comparison.
`M173BAK DIRECT C` is the **untouched fallback source**, and
`M173NEW DIRECT C` the **only candidate to edit**; never edit
`USER DIRECT C` in this phase. A same-volume copy protects against
editing mistakes but NOT loss of VMCOM1 or the root EBS volume.
The separately confirmed EBS snapshot and recovery path remain
the disaster recovery source. CMS file content is sensitive:
do not upload or paste either copy into a public report.

## Gate 3: candidate-only single-MDISK edit — separate review

After checking that `M173NEW DIRECT C` matches the original
and locating the correct `USER MAINT` stanza **privately**,
edit ONLY `M173NEW DIRECT C` with XEDIT. Do not paste
USER/MDISK passwords into GitHub or chat.

**Illustration to review and insert in the correct stanza only:**

```text
MDISK 0600 3390 6000 1600 VMCOM1 W
```

No other lines should change. The operator must check duplicate
0600 entries, existing full-pack entries, device overlap, CP owned
extents, and correct staging-disk access/security. A successful
sample comparison of USER DIRECT vs active directory does not by
itself authorize this edit.

## Gate 4: syntax and prospective extent checks — not activation

IBM documents `DIRECTXA ... (EDIT` as a test compilation
that **does not update the active CP directory**. Confirm the
correct-release utility is available (often cross-release PMAINT
551) before using it, and investigate any warnings.

On an already reviewed candidate, the syntax-only form is:

```text
DIRECTXA M173NEW DIRECT C (EDIT
```

Expected terminal response is `EOJ DIRECTORY NOT UPDATED`
with a successful test return code; inspect all intervening
diagnostics before deciding the compilation passed.
**Never omit `(EDIT` in this gate.**

Optionally regenerate an isolated prospective extent report
only after checking `M173NEW MDISKMAP C` is absent:

```text
DIRMAP M173NEW DIRECT C C
```

This **writes** `M173NEW MDISKMAP C`; it must not overwrite
`USER MDISKMAP C`, and the DIRMAP output is not independently
authoritative for full-pack or CP-reserved extents.
Review the new VMCOM1 6000–7599 row and any GAP/OVERLAP diagnostic.

**STOP AFTER TEST COMPILE / MAP REVIEW.** Return only the
sanitized compiler status, return code, and nonsecret extent summary.
No `DIRECTXA` without EDIT, `CP DEFINE`, `LINK`, `ACCESS`,
or `FORMAT` is authorized by this document.

## Separate later activation — NOT authorized yet

If all gates pass, prepare a separate explicit go/no-go with an
authorized operator. Include **exact** online-directory activation
and re-logon/device-visibility procedure, recovery path to the
previous active CP directory, and the retained `M173BAK DIRECT C`.
Any rollback compilation or activation is itself a privileged
operation to be separately approved and may affect all users.
Never assume adding a USER DIRECT entry automatically changes
an already logged-on MAINT virtual device configuration.

Only after a new permanent 0600 minidisk has been definitively
created and its *physical* location verified as VMCOM1 real0127
start6000 length1600 may CMS initialization/FORMAT of that
**new empty disk** be reviewed. Existing A/0191, C/02CC,
full-pack 0127 and retained stages must NEVER be formatted.
After G is safely initialized and verified R/W, BLKSZ 4096
with >=180000 free blocks, start `M173CHK G`, then M174–M176.

## Official references

- IBM CMS COPYFILE (including NEWFILE and collision behavior):
  https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-copyfile
- IBM DIRECTXA EDIT is a non-activating syntax check:
  https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-directxa
- IBM MDISK modes and overlapping extent warnings:
  https://www.ibm.com/docs/en/zvm/7.2.0?topic=directory-mdisk-statement


## 2026-10-08 15:25 — Gate 1 completed on real CMS, Gate 2 authorized

The MAINT operator supplied six read-only results:

```text
QUERY DISK C
MNT2CC 2CC C R/W 10 3390 4096 5 117-07 1683 1800
Ready; 15:24:53

STATE USER DIRECT C
Ready; T=0.01/0.01 15:24:54

STATE M173BAK DIRECT C
DMSSTT002E File M173BAK DIRECT C not found
Ready(00028); T=0.01/0.01 15:25:03

STATE M173NEW DIRECT C
DMSSTT002E File M173NEW DIRECT C not found
Ready(00028); T=0.01/0.01 15:25:04

STATE M173NEW MDISKMAP C
DMSSTT002E File M173NEW MDISKMAP C not found
Ready(00028); T=0.01/0.01 15:25:14

CP QUERY MDISK 0600 DIRECTORY
HCPQMD040E Device 0600 does not exist
Ready(00040); T=0.01/0.01 15:25:15
```

**GATE 1 PASS**: original USER DIRECT C present RC0, C is R/W
3390/4096 with **1683 free 4K blocks**, both intended directory
copy destinations and prospective map absent RC28, and MAINT 0600
still unassigned in its permanent directory. The prior original
`USER DIRECT C` was 4282 fixed 80-byte records, ~84 blocks;
two copies should leave ample room, subject to actual allocation.

IBM CMS COPYFILE `NEWFILE` was independently checked against
IBM's COPYFILE reference: it rejects pre-existing destinations
with DMS024E/RC28 instead of REPLACE. Its temporary `COPYFILE
CMSUT1` workfile may be created by the utility. The operator
may now perform **Gate 2 only**:

```text
COPYFILE USER DIRECT C M173BAK DIRECT C (NEWFILE
COPYFILE USER DIRECT C M173NEW DIRECT C (NEWFILE
LISTFILE USER DIRECT C (ALLOC
LISTFILE M173BAK DIRECT C (ALLOC
LISTFILE M173NEW DIRECT C (ALLOC
QUERY DISK C
```

**Stop if either copy fails** and do not execute the second if
the first fails. Verify all copies are F80 and have exactly
4282 records, with no source or destination replacement.
Return metadata/RC only: the real USER DIRECT source may contain
passwords. Gate 3 candidate edits, Gate 4 `DIRECTXA ... (EDIT`,
directory activation, LINK/ACCESS, G FORMAT and M173 importer
remain **UNAUTHORIZED/PENDING**.


## 2026-10-08 15:29 — Gate 2 actual CMS copies: metadata PASS

The operator completed both individually guarded copies successfully:

```text
COPYFILE USER DIRECT C M173BAK DIRECT C (NEWFILE
Ready; T=0.01/0.01 15:28:37
COPYFILE USER DIRECT C M173NEW DIRECT C (NEWFILE
Ready; T=0.01/0.01 15:28:46
```

The resulting three independent `LISTFILE ... (ALLOC` reports
agreed exactly in the published **nonsecret metadata**:

| CMS file | FM | RECFM | LRECL | RECS | BLOCKS |
| --- | --- | --- | ---: | ---: | ---: |
| USER DIRECT | C1 | F | 80 | 4282 | 84 |
| M173BAK DIRECT | C1 | F | 80 | 4282 | 84 |
| M173NEW DIRECT | C1 | F | 80 | 4282 | 84 |

The operator's last `QUERY DISK C` at **15:29:07**
reported `MNT2CC 2CC C R/W 10 3390 4096`, **7 files**,
**287 used blocks**, **1513 free blocks**, **1800 total**.
The operation raised used blocks from 117 to 287, preserving
plenty of CMS C free space. No `USER DIRECT C` edit,
new 0600 MDISK, online directory activation, G FORMAT or M173
execution has been reported.

**GATE 2 METADATA PASS; FULL CONTENT EQUALITY PENDING.**
Identical file attributes, records, and allocated blocks are
necessary but not a full record-by-record content check.

### Gate 2b: read-only record-for-record content comparisons

IBM CMS `COMPARE` checks every column of each record by default
when no COL option is specified. It is read-only. It returns an
ordinary Ready/RC0 response for identical files; nonidentical
contents produce `DMSCMP209W`/RC4, and mismatched file lengths
can produce `DMSCMP010E`/RC40. **CAUTION**: when files differ,
COMPARE can display their differing records, which can include
passwords embedded in `USER DIRECT`. Keep this on the operator's
private console and **do not paste mismatch records** into chat
or the public GitHub repository. Report only return code and
whether they were identical.

```text
COMPARE USER DIRECT C M173BAK DIRECT C
COMPARE USER DIRECT C M173NEW DIRECT C
```

Run the second **only if the first returns RC0**. If either
does not return RC0, STOP; do not edit or replace any of the
three directory files. If both pass, `M173BAK DIRECT C` is a
record-identical, untouched CMS backup and `M173NEW DIRECT C`
is a record-identical candidate ready for separate
`USER MAINT` stanza review. Gate 3 XEDIT and Gate 4
syntax-only `DIRECTXA ... (EDIT` have NOT been authorized
or executed at the metadata stage.

IBM reference:
https://www.ibm.com/docs/en/zvm/7.2?topic=commands-compare


## 2026-10-08 15:32 — Gate 2b record identity: target PASS

The operator executed both IBM CMS COMPARE commands in MAINT:

```text
COMPARE USER DIRECT C M173BAK DIRECT C
DMSCMP179I Comparing USER DIRECT C with M173BAK DIRECT C
Ready; T=0.03/0.04 15:32:13

COMPARE USER DIRECT C M173NEW DIRECT C
DMSCMP179I Comparing USER DIRECT C with M173NEW DIRECT C
Ready; T=0.04/0.04 15:32:15
```

IBM COMPARE reports differing records and `DMSCMP209W` on a
mismatch; here each completed with just `DMSCMP179I` and Ready.
**GATE 2b CONTENT EQUALITY PASS**. Both copies are 4282 F80
records, and each is record-identical to `USER DIRECT C`
at this checkpoint. The last C-disk usage was 287/1800 blocks,
leaving **1513 free 4K blocks**.

The `USER DIRECT C` and `M173BAK DIRECT C` files are now
protected inputs; never XEDIT, replace or erase them.
The only candidate is `M173NEW DIRECT C`.

### Gate 3 controlled single-line edit in XEDIT (candidate only)

The planned `M173DCHK EXEC` verifies after the edit that all
4282 original records match the backup and that `M173NEW`
has **exactly one inserted** entry, immediately after the
specific `USER MAINT` heading that precedes the actual delta:

    MDISK 0600 3390 6000 1600 VMCOM1 W

On CMS MAINT, start the editor for the **candidate only**:

```text
XEDIT M173NEW DIRECT C
```

At the XEDIT command line, run one command at a time:

```text
TOP
LOCATE /USER MAINT /
```

Privately inspect the located CURRENT line. It must be the
actual directory `USER MAINT` heading, not a comment,
not another user, and not an `INCLUDE` or `MDISK` line.
**Do not paste its text**; the heading can carry a password.
If it is wrong or ambiguous, exit XEDIT with `QQUIT`
without modifying anything and report just the problem.

Only if the correct `USER MAINT` heading is current, enter
the XEDIT *subcommand* (not plain CMS and not data input mode):

```text
INPUT MDISK 0600 3390 6000 1600 VMCOM1 W
```

IBM XEDIT `INPUT line` inserts exactly one line **after the
current line**. Visually verify that the new entry is exactly
one line, inside the `USER MAINT` stanza, with the right
VDEV/real extent and **W** mode. If anything is wrong use
`QQUIT` to discard unsaved changes. If correct, from the
XEDIT command line enter:

```text
FILE
```

This writes **only `M173NEW DIRECT C`** and exits XEDIT.
On return to CMS, run metadata-only:

```text
LISTFILE M173NEW DIRECT C (ALLOC
STATE USER DIRECT C
STATE M173BAK DIRECT C
```

Expected `M173NEW` is **4283 F80 records**, while both
original and backup remain 4282 records. Do not paste any
directory text or password material.

Before *any* `DIRECTXA` call, install the read-only checker
from GitHub, using the proven Mac transfer workflow:

```sh
cd /path/to/ibm-sandbox/src
git pull
./cms-upload.sh M173DCHK.EXEC
```

Then on CMS:

```text
M173DCHK
```

Expected exact final marker:
`M173 DIR DELTA CHECK PASS`. The check uses only read-only
`STATE` and `EXECIO DISKR`, emits no directory contents,
requires 4282 original records and 4283 candidate records,
verifies both original and backup have identical bytes, and
only accepts the single expected MDISK line directly after the
source record immediately preceding the actual insertion, which
must begin with `USER MAINT`. It fails closed on **any**
other change with RC8. Until actual CMS PASS, treat its
behavior as host-reviewed, **not target-proven**.

**STOP after XEDIT and M173DCHK.** Do not run `DIRECTXA`
even with `(EDIT`, `DIRMAP`, any online activation or
any CMS FORMAT before reviewing the result and planning
the correct installed-utility options. All directory
identifiers and passwords remain private.


## 2026-10-08 15:44 — M173DCHK first target run RC8, not a delta failure

The CMS operator showed that the candidate file was saved successfully:

```text
LISTFILE M173NEW DIRECT C (ALLOC
M173NEW DIRECT C1 F 80 4283 84
Ready; T=0.01/0.01 15:44:40
M173DCHK
DMSEIO632E I/O error in EXECIO; rc=8 from EXECCOMM command
M173 DIR ORIGINAL READ FAIL
Ready(00008); T=0.01/0.01 15:44:42
```

**GATE 3 DELTA VERIFICATION STILL PENDING, NOT PASS.** Failure was
at the first `EXECIO ... DISKR`, before any candidate delta check.
IBM's EXECCOMM return code **8** denotes an **invalid variable name**;
IBM's EXECIO documentation requires uppercase REXX stem names in the
literal `STEM` operand. Previous `M173DCHK EXEC` had lowercase
`(STEM u. FINIS`, `(STEM b. FINIS`, and `(STEM n. FINIS`.
These were changed in GitHub to `U.`, `B.`, and `N.` without
changing the read-only comparison logic; the host guard now checks
the exact uppercase commands. This is the strongly supported
cause of the EXECCOMM rc8; actual corrected CMS validation remains
necessary. IBM references:
- https://www.ibm.com/docs/en/zvm/7.2?topic=commands-execio
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=macros-execcomm

**No new copy, file edits, directory activation, LINK/ACCESS,
FORMAT or M173 import is required or authorized for this fix.**
Preserve original `USER DIRECT C`, backup `M173BAK DIRECT C`,
and saved candidate `M173NEW DIRECT C` (4283 F80 records).
Only upload corrected `M173DCHK.EXEC` from GitHub to CMS and
rerun `M173DCHK`. The upload replaces the verifier EXEC only,
not any directory source. Require terminal
`M173 DIR DELTA CHECK PASS` and RC0 before Gate 4.


## 2026-10-08 15:49 — Gate 3 failure at global MAINT count

Actual CMS output after the previous uppercase-STEM fix:

```text
LISTFILE M173NEW DIRECT C (ALLOC
M173NEW DIRECT C1 F 80 4283 84
Ready; T=0.01/0.01 15:49:40
M173DCHK
M173 DIR MAINT STANZA NOT UNIQUE
Ready(00008); T=0.54/0.56 15:49:42
```

**Not a pass.** The three DISKR calls succeeded and the 4282,
4282, 4283 record-count gate passed. The former source checker
required that `USER DIRECT C` contain *exactly one* record
whose first two fields were `USER MAINT`. The printed failure
means the count was **zero or greater than one**; it did not
report which, so do NOT claim duplicates as a confirmed fact.
This earlier uniqueness assumption was not proven by source
inspection and is not needed to verify the exact inserted line.

### Revised target verifier — preserves fail-closed behavior

`src/M173DCHK.EXEC` now checks, in order:

1. All three files exist, READ without error, and counts match
   original 4282, backup 4282, candidate 4283.
2. Every original record is identical to its backup counterpart.
3. Find the **first difference** between original and candidate.
   This must be the one new record, with exact fields
   `MDISK 0600 3390 6000 1600 VMCOM1 W`.
4. Check that the record immediately before that insertion in the
   original begins `USER MAINT`; no global uniqueness assumption.
5. Check that **every original record from that insertion onward**
   matches the candidate one record later. Any extra modification,
   deletion or second insertion returns RC8.
6. Never print a directory line, password or other file content.

This proves precisely one new approved MDISK record after a
`USER MAINT`-prefixed source line, even when the unmodified
directory has multiple similarly prefixed lines. It does **not**
establish the *semantic validity* of a duplicate/alternate
MAINT stanza or CP directory syntax; those require a separately
reviewed **syntax-only DIRECTXA (EDIT)** gate later.

Do not re-edit or re-copy the original or candidate. Update
`M173DCHK.EXEC` only from the repository, then run it on CMS.
If this revised checker reports anything other than
`M173 DIR DELTA CHECK PASS` and RC0, **STOP**.
`DIRECTXA`, `DIRMAP`, online directory replacement, LINK,
ACCESS, FORMAT and M173 import are still off limits.


## 2026-10-08 15:56 — Gate 3 first-difference check failed

Actual MAINT operator output:

```text
M173DCHK
M173 DIR INSERTED RECORD INVALID
Ready(00008); T=0.52/0.54 15:56:14
```

**Not a pass.** Three `EXECIO DISKR` reads and record-count
checks succeeded, and the full original/backup record
comparison did not report an error. The verifier rejected the
first difference between original and candidate because the
candidate record at that position was not the approved MDISK
line. This does **not** establish that the approved MDISK
line is absent: another altered record may precede it.
The count and metadata alone do not prove exact insertion.

The revised **read-only** `src/M173DCHK.EXEC` no longer
assumes the first difference is the added record. It scans
all candidate records for exact approved MDISK text, and
then checks **all 4282** original records against the
candidate aligned around the one approved insertion.
No relaxation of the acceptance gate: precisely one
`MDISK 0600 3390 6000 1600 VMCOM1 W` immediately
after an original `USER MAINT`-prefixed record,
unmodified `USER DIRECT C` and `M173BAK DIRECT C`,
and no other file changes. Its diagnostics disclose
**only counts and an optional mismatch record number**:
`M173 DIR APPROVED LINE COUNT`,
`M173 DIR MDISK 0600 PREFIX COUNT`,
`M173 DIR OTHER CHANGE AT RECORD`.
No directory data or passwords are displayed.

**Action:** Leave all three directory files unchanged.
After checking host CI, update only the verifier EXEC
with `git pull` and `./cms-upload.sh M173DCHK.EXEC`
from the Mac `ibm-sandbox/src` directory, rerun
`M173DCHK` on MAINT and return its output. If the
checker again fails RC8, use the safe counters to
determine whether any source-candidate repair is needed;
do **not** try XEDIT edits by guesswork.
Never invoke `DIRECTXA`, `DIRMAP`, CP directory
activation, LINK/ACCESS, FORMAT or M173 import
until complete target verification passes.


## 2026-10-08 16:00 — Exact candidate line absent, MDISK 0600 exists

The operator ran the latest read-only target checker:

```text
M173DCHK
M173 DIR APPROVED LINE COUNT 0
M173 DIR MDISK 0600 PREFIX COUNT 1
M173 DIR INSERTED RECORD INVALID
Ready(00008); T=0.85/0.87 16:00:11
```

**Gate 3 FAIL; do NOT run DIRECTXA**. All three source
files were read, original/backup comparison and record
count checks succeeded, but the existing candidate contains
**zero exact approved MDISK lines and one line beginning
`MDISK 0600`**. We must not infer whether this is a
spacing-only issue, wrong field, extra text or another edit.

A read-only diagnostic-only revision of `M173DCHK.EXEC`
reports, for that unique candidate MDISK prefix:
- candidate **record number** and **field count**;
- seven `FIELD <number> MATCH/DIFF` indicators compared against
  the fixed approved words, **never actual words**;
- `SPACING ONLY YES/NO` after uppercase and whitespace
  normalization (does not bypass exact-match validation);
- whether the immediately preceding original record begins
  with `USER MAINT`;
- number of records differing outside the hypothesized
  one-line insertion and index of the first difference, if any.

All fields derived from the directory are kept confidential.
The diagnostic only emits nonsecret status/position numbers and
MATCH/DIFF indicators, never directory text or passwords.
**The accept condition remains unchanged**: exactly the approved
record, correct preceding MAINT record, complete shifted-file
equality, RC0 and final PASS marker. The diagnostic does not edit
anything, and even `SPACING ONLY YES` is NOT sufficient for PASS.

After new GitHub CI completes, upload only the revised
`M173DCHK.EXEC` from the Mac and run `M173DCHK` on MAINT.
Stop and preserve `USER DIRECT C`, `M173BAK DIRECT C`,
`M173NEW DIRECT C`. Do not apply a guessed XEDIT correction
or run `DIRECTXA`, `DIRMAP`, directory activation,
LINK/ACCESS, FORMAT or M173 import before reviewing the
new safe diagnosis.
