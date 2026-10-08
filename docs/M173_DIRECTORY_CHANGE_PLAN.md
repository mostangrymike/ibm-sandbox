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
