# CMS A-disk TRKDE 4 recovery — September 27, 2026

## Safety status

**HOLD ALL CMS A-DISK WRITES.** The M17 cleanup failed on the first
`ERASE M12ATLS ASSEMBLE A` with `DMSDKD1307T`, TRKDE code 4, and
`HCPGIR450W` disabled wait. The user performed `IPL CMS`. All
successful 1,808-object GEN2 audits and selection of M15NEW seq52
occurred **before** the failed ERASE. Do not extrapolate their results
to the A disk after the filesystem crash.

IBM documents TRKDE code 4 as attempted deallocation of a block the
allocation map considers unallocated. Possibilities include an older
cross-linked file block, allocation map corruption in virtual memory,
or damaged file structure. IBM advises preserving the VM dump and
making a copy of the affected minidisk promptly using CP DDR, then
diagnosing corruption and copying unaffected files to a fresh
formatted disk. See:
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=dms1906s-dms1307t
- https://www.ibm.com/docs/en/zvm/7.2?topic=errors-diagnosing-cms-file-system
- https://www.ibm.com/support/pages/zvm/library/640pdfs/64618707.pdf

## Immediate preservation, outside CMS

1. Save the console text, any generated VM dump, Hercules log and
   z/VM EREP records. Avoid anything that would overwrite a dump.
2. Establish the **actual** host machine, running emulator process,
   Hercules configuration and file backing the VM's virtual 191
   CMS A minidisk. The CMS label was `MNT191`, device `0191`,
   CMS A, 175 cylinders, 3390; this is an identity cross-check,
   not a guessed host pathname. The user currently runs z/VM 6.3
   in Hercules; do not use older Raspberry Pi/z/VM 4.4 paths.
3. If a consistent storage snapshot is available for the *full*
   backing storage, take it using its provider's crash-consistent
   snapshot mechanism, or shut down/quiesce the VM and Hercules
   cleanly **only if the current situation permits**, then copy
   the backing file and any dependent image/overlay metadata.
   Prefer preserving every DASD file participating in the CMS
   minidisk and CP directory, not a guessed single file. If the
   backing disk is a dedicated CP minidisk extent within a shared
   DASD image, preserve the entire image.
4. Verify source and backup independently with SHA-256 and record
   source and destination sizes. Retain the first unmodified
   forensic copy. Do not attempt `ERASE`, `COPYFILE`,
   `GENWRITE`, `GENMOD`, `ACCESS ... (ERASE`, `FORMAT`,
   or another `GITRUN` on the potentially damaged original
   before preservation.

## Diagnostics **after** preserving original

Use a separately attached **copy** of the suspect minidisk,
preferably read-only, and examine IBM's optional `MDCHECK`
diagnostic (often supplied on MAINT 193) or `DFSMS CHECK`
if installed on this z/VM level. Confirm availability and
syntax for the actual z/VM 6.3 installation before invocation.
Do not install utilities to the damaged A disk. Compare CP
directory minidisk extents for overlaps and inspect host I/O
errors, EREP and VM dump. Run nondestructive checks first,
then export unaffected files to a *different* clean disk and
reconstruct original A only after a separate verified copy
exists and the corruption's scope is understood.

### Protected inventory

- `GITFIX STAGE/INDEX/SEEK/GEN A`: original independently
  full-verified 1,808-object generation; cross-logon tested
  before the crash.
- `M15NEW STAGE/INDEX/SEEK/GEN A`: second independently
  indexed and sealed full-verified generation.
- `GITSEL0 PTR A`, `GITSEL1 PTR A`,
  `M15SL0 PTR A`, `M15SL1 PTR A`: existing selector
  records; last observed M15SL1 seq52 M15NEW.
- `GITPBUF PACK A`: original 340,027-byte captured Git
  PACK, SHA-1
  `8C92E274ECA84B797F8925A6082915DD6CCDE196`.
- CMS development toolchain on A and F; back up any data
  necessary to reproduce `GITCIDX`, `GITSEL`, `GITREC`
  and the original Git client.

Historical `M12ATLS ASSEMBLE A` may be partially erased
or still present. Treat its file structure as suspect;
do not retry its ERASE. `GITRUN.EXEC` on GitHub is
deliberately replaced with a safety hold (RC 12).
A Git pull does **not** replace CMS's previously uploaded
cleanup EXEC unless it is transferred; do not run that
existing CMS copy.

## Recovery exit criteria

On a verified clean *copy* or newly reconstructed CMS disk:
full `GITCIDX GENCHECK` independently succeeds for both
generations; both selector files parse as expected;
`GITREC SELECT GITFIX M15NEW` fully selects seq52 with
digest `493F0896884B28AC4836B88328629B7E95404B46`
(or recovers a verified older generation if seq52 is
damaged). Reboot survival, concurrency and atomic
promotion are still separately unproved. Do not erase
old generations or selectors during restoration.

## Optional offline Linux backup helper

The repository now includes `scripts/backup-offline-dasd.sh`,
which operates on an explicitly identified ordinary *regular
file* backing a Hercules DASD image. It does not discover
or guess any real device path and does not create a live
snapshot. After the affected VM and Hercules are offline,
identify all dependent backing images and overlays, choose
backup storage with adequate capacity, and back up each
required image individually, or use a coordinated volume
snapshot for a multi-image setup. Example **using illustrative
paths only**, not this installation's real layout:

```sh
OFFLINE_CONFIRMED=YES bash scripts/backup-offline-dasd.sh \
  /verified/path/to/cms-191-backing-file \
  /safe/offline/volume/cms-191-preserved-image
```

It refuses overwrite, missing/symlink source, unconfirmed
offline operation, and a source reported open by `fuser`
if installed; it uses a new destination file, compares
every byte with `cmp`, records SHA-256 of both copies
and leaves incomplete output marked for inspection on
error. `fuser` is only a secondary safeguard and cannot
prove the guest is offline or discover all overlays.
The test `tests/test-offline-dasd-backup.sh` exercises
these gates on small, synthetic files in CI. Use
operator judgment and provider-specific storage snapshots
rather than this utility for live systems or non-regular
block/CKD volume devices.

## Read-only host inventory and stronger forensic copy finalization

A host-side helper `scripts/inspect-hercules-config.sh` can list
simple CKD device records from the **operator-confirmed active**
Hercules configuration file without starting or changing Hercules,
reading disk images, or dumping unrelated configuration settings.
Supply the actual configuration path as its only argument:

```sh
bash scripts/inspect-hercules-config.sh /actual/path/hercules.cnf
```

The reported channel address, device type and filename are only
an inventory. Hercules `INCLUDE` files, dynamically attached
devices, DASD shadows/overlays and the VM directory's MDISK
mapping must still be checked. In particular, a VM's virtual
`0191` is not necessarily the same as a Hercules hardware
address `0191`, nor does a CKD volume automatically map to
the user's `MNT191` CMS minidisk without corroboration.

The optional offline file-backup helper now finalizes with
an atomic hard-link create rather than `mv -n`; the destination
cannot be silently replaced by another process racing to use
the same name. It retains an incomplete copy if another
destination appears and does not delete either the source
or the pre-existing destination. This is *not* a substitute
for confirming the guest and emulator are offline and that
the entire backing storage set is preserved.

## September 27 17:34 — actual device inventory, mapping pending

The operator ran the read-only Hercules configuration
inventory against `/home/admin/vm630/hercules.cnf` and reported:
- Hercules `0123 3390 dasd1`
- Hercules `0124 3390 dasd2`
- Hercules `0125 3390 dasd3`
- Hercules `0126 3390 dasd4`
- Hercules `0127 3390 dasd5`
- Hercules `0128 3390 dasd6`

Immediately afterward, CMS `QUERY DISK` showed its
affected A disk as `MNT191`, virtual `191`, R/W,
175 cylinders, 239 files, 9110/31500 4-KiB blocks used,
22390 free. This is a post-failure inventory only;
it does **not** establish filesystem integrity. The
Hercules filenames are relative to Hercules' effective
working directory, which has not been independently
verified. The CP real-device mapping and starting
cylinder for the 175-cylinder virtual 191 disk remain
UNKNOWN; do not assume that Hercules address 0123 is
the relevant image merely from a historical resemblance.

Read-only next steps:
- On CMS: `CP QUERY MDISK 191 LOCATION`, obtaining
  physical real device, disk volume label, minidisk
  offset and size. Compare actual returned real device
  with the six active Hercules addresses above.
- On host: `cd /home/admin/vm630 && pwd && ls -lah
  dasd*` and inspect `hercules.cnf` for `sf=`,
  `shadow`, `INCLUDE`, and working-directory changes.
  Corroborate the active Hercules process's cwd and
  configuration; relative image paths do not guarantee
  residence beside the config.
- No CMS ERASE/COPYFILE/GITRUN and no host backup of a
  guessed disk. Once the actual volume/image/dependencies
  and quiescence are verified, preserve crash dump and
  create an independently verified forensic backup.

## Correlating the confirmed Hercules inventory to CMS MNT191

The active operator-supplied Hercules configuration is
`/home/admin/vm630/hercules.cnf`. Its simple 3390
declarations are `0123 dasd1`, `0124 dasd2`,
`0125 dasd3`, `0126 dasd4`, `0127 dasd5`,
`0128 dasd6`. CMS `QUERY DISK` reports
`MNT191` mounted R/W as virtual 191 with 175
cylinders, 239 files, 9110 used and 22390 free
4-KiB blocks, AFTER the interrupted ERASE. Virtual
191 still is not the Hercules real channel address.

On CMS, **read-only**:

```text
CP QUERY MDISK 191 LOCATION
```

Record `OwnerID`, `Odev`, `Dtype`,
`Vol-ID`, `Rdev`, `StartLoc` and `Size`.
Match `Rdev` to the Hercules real channel address,
`StartLoc` and `Size` to the 175-cylinder minidisk
extent, and corroborate real volume `Vol-ID`.
IBM CP QUERY MDISK documentation:
https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-mdisk

On the Hercules Linux host, establish the effective cwd
of the **actual** emulator process. The config lists only
relative `dasd1`–`dasd6`, not verified absolute
image paths. Inspect any INCLUDE and shadow/overlay
configuration before backup. After CP reports the actual
real device, the repo's new read-only helper can resolve
only an unambiguous straightforward CKD declaration:

```sh
bash scripts/map-cms-minidisk.sh CP_REAL_RDEV \
  /home/admin/vm630/hercules.cnf /verified/hercules/process/cwd
```

The helper explicitly requires the real `Rdev` from
CP, refuses duplicate device declarations and missing
backing files, and prints an absolute base-image path.
It cannot prove that the base image is sufficient for
a consistent backup or that the system is offline.
It does not inspect or modify disk contents and it
does not accept a guessed Rdev for production use.

## Confirmed CP-to-Hercules volume mapping at 17:36

The actual CP read-only command `CP QUERY MDISK 191 LOCATION`
reported:

```text
TargetID Tdev OwnerID Odev Dtype Vol-ID Rdev StartLoc Size
MAINT    0191 MAINT   0191 3390  M01RES 0123 494      175
```

Combined with the operator-confirmed active Hercules
configuration line `0123 3390 dasd1`, this conclusively
identifies MAINT's virtual `0191` CMS A minidisk
(label `MNT191`) as a 175-cylinder region starting
at cylinder 494 on real `0123`, volume `M01RES`,
backed by the active Hercules `dasd1` image and
any applicable overlays/shadows. `MNT191` is the
CMS minidisk label; `M01RES` is the real CKD volume
serial. These are not contradictory.

**The candidate backup base image is dasd1, NOT all
six Hercules drives, and NOT an assumed /home/admin/
vm630/dasd1 until the emulator's actual working
directory is verified.** The minimal preservation
scope is all backing files necessary to reconstruct
the current real 0123 volume, including any shadow
chain, plus available dump/log evidence; a coordinated
wider snapshot is prudent if disk dependencies cross
volumes or the host setup is not simple.

On the Hercules host, first identify its actual
process ID and cwd without changing anything:

```sh
pgrep -af '[h]ercules'
readlink -f /proc/ACTUAL_HERCULES_PID/cwd
grep -nEi 'sf=|shadow|include' /home/admin/vm630/hercules.cnf
```

Resolve `dasd1` relative to the verified emulator
cwd, then cross-check volume M01RES from emulator
startup logs/operator device query if available;
a filename alone does not prove its internal VOLSER.
Do not use the backup helper on the live, still
open DASD file. Quiesce the actual emulator first
or use a coordinated, provider-supported snapshot
that captures all backing files atomically. The
original user-facing CMS cleanup EXEC remains unsafe
until disk integrity and a verified backup are
established; the GitHub runner is an RC12 safety hold.
