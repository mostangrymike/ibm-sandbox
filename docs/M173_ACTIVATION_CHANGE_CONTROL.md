# M173 0600/G CP directory activation — controlled change plan

## 2026-10-09 09:50:09 CDT — ACTUAL CP ACTIVATION AND LIVE DIRECTORY VERIFICATION PASS

**The operator has executed the privileged directory update.** The
previous draft-only activation warning is now historical; the
**DIRECTORY ACTIVATION SUCCEEDED on real CMS MAINT**, but disk
access and CMS FORMAT have **NOT** happened. Keep rollback protection.

```text
DIRECTXA M173NEW DIRECT C
z/VM USER DIRECTORY CREATION PROGRAM - VERSION 6 RELEASE 3.0
EOJ DIRECTORY UPDATED AND ON LINE
HCPDIR494I User directory occupies 58 disk pages
Ready; T=0.18/0.21 09:49:23
CP QUERY MDISK USERID MAINT 0600 LOCATION DIRECTORY
MAINT 0600 MAINT 0600 3390 VMCOM1 0127 6000 1600
Ready; T=0.01/0.01 09:49:38
CP QUERY ALLOC DRCT ALL
M01RES 0123 1 20 20 1 1 5% ACTIVE
Ready; T=0.01/0.01 09:50:01
CP QUERY SYSTEM 0127
DASD 0127 ATTACHED CPVOL 0015 VMCOM1
MAINT 0551 R/O, MAINT 02CC R/W, MAINT 049E R/O
VMSERVP 0311/0310/0309/0308/0307/0306/0305/0304
VMSERVP 0303/0301/0302/0191 R/W
Ready; T=0.01/0.01 09:50:09
```

**Directory update PASSED:** explicit UPDATED AND ON LINE,
RC0; active directory is still on M01RES/0123 cylinders
1–20; active MAINT/0600 directory entry is
VMCOM1 RDEV0127 cylinder6000 size1600 (end7599);
15 current VMCOM1 links unchanged, with no linked
PMAINT0141 fullpack in this snapshot. Nothing in
this evidence says the already logged-on MAINT has
new vdev0600 **in its virtual machine** or that
the disk has a CMS filesystem. No format is proven.
Do not change USER DIRECT C or the original/backup
directory source until recovery is fully settled.
`M173NEW DIRECT C` remains the activated source.

### Phase 7A — live virtual-device admission (low risk)

CMS MAINT may have been logged on before the
online directory update and therefore may not yet
have virtual 0600. Rather than logging off blindly,
first issue read-only:

```text
CP QUERY VIRTUAL DASD
CP QUERY MDISK 0600 LOCATION
QUERY DISK
```

Confirm no virtual device at 0600 (or, if
already present, demand exact 3390/1600-cylinder
real VMCOM1/0127 6000 mapping and exclusive R/W).
Also verify that CMS G is **not currently
accessed** for an unrelated filesystem and
that A/C and source directory files are
available. The MDISK LOCATION command can
return expected missing-device diagnostics if
the new MDISK has not been instantiated
in the logged-on VM; distinguish it from
the successful ACTIVE DIRECTORY query above.

Only when virtual0600 is confirmed **absent**
and the active-directory physical extent
remains exactly as validated is it appropriate
to consider the IBM supported own-minidisk
self LINK, without MAINT relogon:

```text
CP LINK * 0600 0600 W
```

This is a **non-formatting, VM configuration action**,
not a directory edit, and must not be attempted if
any other virtual 0600 is defined, if the command
cannot be authorized as a link to MAINT's exact
new disk, or if another fullpack writer appears.
After any successful self-link, use the same
read-only CP QUERY VIRTUAL/MDISK LOCATION and
QUERY DISK checks. Stop on read-only,
unexpected geometry, access conflict or
nonzero LINK RC. Do not guess that `ACCESS`
can mount an unformatted device; do not
release or overwrite an unrelated current G.

### Phase 7B — separately guarded **destructive** FORMAT

Only after a live, virtual `0600` is demonstrated
to map the new real VMCOM1 / 0127 / 6000–7599
disk in exclusive R/W mode, the existing fullpack
PMAINT0141 is confirmed not currently linked
for write, G is unused, and the backup/rollback
cautions are accepted, may a separately
authorized CMS FORMAT initialize **that new
virtual 0600 alone** with 4K blocks and a
distinct, ≤6-character label. It erases disk
contents within that virtual minidisk.
Do **not** invoke FORMAT during Phase 7A.

The native M173 importer has an independent
admission guard: G R/W, CMS 4K blocks and
at least 180,000 *free* 4K blocks. After
FORMAT and CMS access, verify via `QUERY DISK G`
before starting M173; gross 1600×180=288000
blocks is not by itself a measured free count.

IBM:
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=dasds-linking-sharing-minidisks
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-virtual-all
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-format

---


**STATE: DRAFT FOR OPERATOR REVIEW. NOT APPROVED TO EXECUTE.**
Updated October 9, 2026 after completed 09:33:55 CDT CMS Gate 6.
This document is not a license to issue a non-EDIT DIRECTXA or FORMAT.

## Desired outcome and immutable constraints

Provide a **new** dedicated writable 4096-byte-block CMS G disk for the
M173 native Git import. Its one additional `MDISK` statement appears
ONLY in candidate `M173NEW DIRECT C`, SUBCONFIG `MAINT-1`,
virtual **0600**, on **VMCOM1**, physical RDEV **0127**,
start **6000**, **1600 cylinders** (physical end **7599**), mode `W`.
The existing object directory remains on **M01RES** RDEV0123,
cylinders 1–20. The original retained `M171NET PACK A`
holds 7,736 objects; never rerun M173 on A.

Never edit or replace the protected 4282-record
`USER DIRECT C` or byte-identical `M173BAK DIRECT C`.
`M173NEW DIRECT C` is the **one-insertion candidate**,
4283 records (new record 213). Both the original-backup and
candidate passed `DIRECTXA ... (EDIT` with RC0 and explicitly
`EOJ DIRECTORY NOT UPDATED`; a clean `DIRMAP` was generated
on CMS C as `M173NEW MDISKMAP C`. Do not print or commit
password-bearing source directory records.

### Target-proven preactivation Gate 6 on 2026-10-09

```text
CP QUERY SYSTEM 0127
DASD 0127 ATTACHED CPVOL 0015 VMCOM1
MAINT 0551 R/O, MAINT 02CC R/W, MAINT 049E R/O
VMSERVP 0311/0310/0309/0308/0307/0306/0305/0304
VMSERVP 0303/0301/0302/0191 R/W
Ready; T=0.01/0.01 09:33:40
CP QUERY ALLOC DRCT ALL
M01RES 0123 1 20 20 1 2 5% ACTIVE
Ready; T=0.01/0.01 09:33:41
CP QUERY MDISK 0600 DIRECTORY
HCPQMD040E Device 0600 does not exist
Ready(00040); T=0.01/0.01 09:33:53
M173DCHK
M173 DIR ORIGINAL/BACKUP VERIFIED 4282
M173 DIR MAINT-1 SUBCONFIG VERIFIED
M173 DIR SINGLE MDISK INSERT RECORD 213
M173 DIR DELTA CHECK PASS
Ready; T=0.81/0.83 09:33:55
```

**ALL FOUR PASS**, including the *expected* negative RC40.
No other 0600 minidisk or new directory is active.
The target-proven CP DIAG X'25C' VMUDQ inventory completed
at 09:26:50 with `M173VQ VMCOM1 QUERY COMPLETE NOT
ACTIVATION APPROVAL`. All finite **ordinary** VMCOM1
MDISKs in that active source finish by **5935**;
`6VMHCD20 0300` is at 5756–5935 (180).
The proposed interval 6000–7599 is disjoint by 64
intervening cylinders 5936–5999.

**CRITICAL EXCEPTION:** active directory contains
`PMAINT 0141 VMCOM1 3390 0000000000 END`.
CP QUERY MDISK LOCATION independently confirmed this
full-pack covers real0127, cylinders **0–10999** (11,000).
It overlaps the proposed G disk even though PMAINT0141
was not linked among the 15 active links when queried.
IBM documents full-pack exceptions to ordinary LINK
access-mode conflict controls. This cannot be ignored,
and `W` on new 0600 is **not a guarantee** against
future full-pack writes. The IBM DIRMAP report assumed
a different model-derived full-pack end of 10016;
CP's live 11000-cylinder geometry is authoritative.

## Remaining authorization gates (operator-owned)

1. **Full-pack access policy.** Before any modification,
   explicitly agree that nobody may attach/use
   PMAINT0141 full-pack for **writing** while 0600
   contains Git data. Identify anyone else who can
   issue privileged full-pack links and arrange a
   concrete operator access restriction. A transient
   QUERY SYSTEM snapshot does not enforce this
   policy over time. If it cannot be enforced,
   **do not activate or format** the candidate; use
   a different physical storage plan.
2. **Recovery provenance and feasibility.** Operator previously
   matched completed root EBS snapshot source and Region
   privately; the actual snapshot was **not test-restored**.
   Confirm at change time that the snapshot still exists
   and both `/home/admin/vm630/dasd1` and
   `/home/admin/vm630/dasd5` are covered by it.
   Confirm a working independent Hercules/3270 console
   and that the saved `M173BAK DIRECT C` remains
   accessible. A rollback that cannot be executed while
   the main console is unavailable is not sufficient.
   Explicitly accept or mitigate the untested-restore risk.
3. **Operator approval and maintenance window.** Obtain
   explicit authorization to update the active CP
   directory, verify the desired MAINT SSI subconfiguration
   and possible logoff/logon impact, preserve running
   VMSERVP/system use, and choose a period with no other
   directory management changes. DirMaint is not
   operational here; do not invent an alternative update
   facility.
4. **Final freshness check.** Immediately before any
   approved activation, re-run the already-proven
   four read-only commands above and require identical
   expected outcomes. If any unrecognized owner,
   full-pack link, unexpected CP DRCT extent, duplicate
   0600, directory-source mismatch, or return code,
   abort **before** updating anything.

## Only in a separately authorized change window

**No command in this section is approved for execution today.**

- Use the previously syntax-validated candidate
  `M173NEW DIRECT C` as the source of the single
  proposed MDISK. A non-EDIT `DIRECTXA` is a
  privileged **state-changing** directory update,
  unlike `DIRECTXA ... (EDIT`, which does not
  update the directory on disk. Never remove `(EDIT`
  during a preparatory test.
- IBM DIRECTXA writes an alternate object directory
  and modifies the volume-label directory pointer.
  Its console conclusion matters:
  `EOJ DIRECTORY UPDATED AND ON LINE` means an
  online directory update; `EOJ DIRECTORY UPDATED`
  without `AND ON LINE` is **not** proof CP
  brought the result online. `EOJ DIRECTORY NOT
  UPDATED`, diagnostics, nonzero RC or mismatched
  source/target is a failed change. If the result
  is not unambiguously online, **stop** without
  trying to format or to force an ambiguous rerun.
- After **confirmed** online update, independently
  inspect the active CP directory, without using
  the logged-on MAINT virtual-device list alone:
  `CP QUERY MDISK USERID MAINT 0600 LOCATION DIRECTORY`.
  Require owner MAINT, vdev0600, 3390, VMCOM1,
  RDEV0127, start6000, size1600 and end7599.
  Compare `CP QUERY ALLOC DRCT ALL` to M01RES
  0123 and `CP QUERY SYSTEM 0127` to expected
  active system links; no new full-pack writer.
  Re-run the read-only `M173VQ` inventory only
  if appropriate and the program is still usable.
- Logged-on MAINT may retain its earlier virtual
  configuration after directory update. Plan and
  control any required **MAINT logoff/logon**;
  do not infer new 0600 from a changed source
  file alone. Use a verified operator console
  and check that MAINT's current virtual 0600
  maps to the exact new real VMCOM1 extent.
  Do not attempt to format a virtual disk until
  its real CP backing and blank/dedicated status
  have been independently established.
- **Formatting is a separate destructive gate**,
  not an implied continuation of activation.
  CMS FORMAT erases data in the target minidisk.
  Only initialize the new physical 0600 after
  exact ownership, RDEV/VOLSER/start/end/size,
  4096-byte block size plan, no existing CMS
  files and operator authorization. Never
  format VMCOM1 full-pack, MAINT 02CC/C,
  MAINT 0191/A, other users' minidisks,
  or any overlapping whole-volume virtual disk.
  Afterward validate G is R/W, block size
  4096, with **at least 180000 free blocks**
  before invoking any M173-stage importer.

## Failure and recovery branches

- **No online update or uncertain outcome:** keep
  the existing running CP configuration untouched,
  gather console diagnostics, and explicitly
  validate current active directory/virtual disks.
  Do not guess what SOURCE FILE filename is
  the current object directory; IBM can decline
  to bring an alternate output online.
- **Online update but failed subsequent checks:**
  enter prearranged recovery mode using the
  retained, previously EDIT-validated
  `M173BAK DIRECT C` as the original source
  for a separately authorized recovery
  DIRECTXA compile (not as an accidental
  activation during review). Revalidate the
  corresponding old MAINT directory content
  and active CP directory after recovery.
  The inactive directory slot is not a
  guaranteed standalone rollback backup.
  Do not run untested corrective commands,
  relogon blindly, or erase existing data.
- **Unrecoverable directory/host issue:**
  consult the prepared EBS snapshot recovery
  path and a working out-of-band host console.
  Restoring backing EBS while Hercules runs
  is unsafe; host stop/quiescence and attachment
  coordination belong in the operator's
  authorized disaster recovery procedure.
  A completed but untested snapshot is
  not a proof that recovery will succeed.
- **Format failure or later bad G content:**
  STOP, preserve original M171NET PACK A
  and pre-existing verified Git generations,
  do not overwrite existing A/C disks and
  do not run importer again until independent
  physical G identity and capacity recheck.

## IBM references

- [DIRECTXA utility](https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-directxa):
  EDIT semantics, alternate directory, explicit
  UPDATED / ONLINE / NOT UPDATED response distinctions
- [DIRMAP utility](https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-dirmap):
  ignores full-pack minidisks in overlap detection
- [LINK command](https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-link):
  full-pack/ordinary MDISK overlap exceptions
- [Formatting minidisks](https://www.ibm.com/docs/en/zvm/7.2.0?topic=defined-formatting-minidisks):
  destructive CMS FORMAT operation, new-disk setup

**Bottom line:** Ordinary allocation inventory and
preactivation integrity checks have passed on
the real target. Do **not** activate until the
full-pack access and recovery gates are explicitly
accepted, and do **not** format automatically even
if activation later succeeds.
