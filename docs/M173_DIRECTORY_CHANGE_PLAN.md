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
