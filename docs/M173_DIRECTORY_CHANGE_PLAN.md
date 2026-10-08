# M173 dedicated CMS G: controlled MAINT directory change plan

Status: **PREPARE ONLY. No source copy, edit, DIRECTORY activation,
LINK/ACCESS, FORMAT or M173 importer run has been reported.**
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

## Gate 2: controlled duplicate copies on C — not yet executed

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
