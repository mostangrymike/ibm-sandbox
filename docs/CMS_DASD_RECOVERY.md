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
