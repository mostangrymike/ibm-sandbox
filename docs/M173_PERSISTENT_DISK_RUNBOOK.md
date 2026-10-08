# M173 persistent 3390 data-minidisk provisioning runbook

Status: **the new data minidisk has NOT been provisioned**.
This document separates read-only discovery, privileged allocation,
initialization of a NEW empty minidisk, and the actual Git importer.
Never infer usable cylinder gaps from an accessed CMS filemode's
BLKS LEFT value or from the Hercules backing-image size.

## Target-proven inputs and capacity

- GitHub project: `mostangrymike/ibm-sandbox`.
- Existing MAINT virtual `0191`, CMS `A`, label `MNT191`,
  physical CP `Rdev 0123`, volume `M01RES`, starts at
  cylinder 494 and occupies 175 cylinders. The active Hercules
  mapping was `0123 3390 dasd1`, effective host path
  `/home/admin/vm630/dasd1`. The live host configuration
  and process mapping must be reconfirmed before changes.
- At the last CMS checkpoint: `212` files on A,
  `8659` 4096-byte blocks used, `22841` free out of
  `31500`. This is 27% usage, not an integrity check.
- Retained `M171NET PACK A` and `M171NET META A` are essential;
  2,171,129 compressed bytes, 7,736 PACK objects, retained
  expected SHA-1 `A705122BC39A3383BC05ABC6C888A1F788B1D067`.
- The failed M173 stage grew to 19,213 blocks on A and failed
  independent verification at object 2625. Its incomplete A copy
  was erased by the operator. **Never rerun M173 on A.**
- The native M173 admission guard requires a writable 4K CMS
  data disk with at least **180,000 free blocks**. A 3390 cylinder
  of CMS 4K storage fits **180 blocks**, so admission requires
  more than 1000 cylinders after filesystem overhead.
- Planning size: **1,600 3390 cylinders**, approximately
  288,000 CMS data blocks before filesystem overhead,
  or about 1.10 GiB of block capacity. This is a *proposal*
  and must be validated against the ACTUAL model and unallocated
  extents; never assume any of the six existing DASD images
  has such a contiguous free allocation. A 3390-1 cannot fit
  1600 cylinders, whereas a sufficiently available 3390-2,
  3390-3 or larger model may be able to.
- Prefer persistent MDISK, not T-DISK or V-DISK; nothing
  ephemeral should become the sole verified staged generation.

## Phase 1: only read-only inventory; safe to run now

On CMS MAINT (the last two commands require CP privileges
which may not be assigned; errors are informational):

    CP QUERY VIRTUAL DASD
    CP QUERY MDISK 191 LOCATION
    CP QUERY DASD ALL
    CP QUERY ALLOC MAP ALL
    QUERY DISK

The `QUERY ALLOC` commands describe **CP-owned** system
volumes/regions and do not enumerate all user permanent
minidisks; the free-block counts from `QUERY DISK`
describe free filespace WITHIN a minidisk. Neither constitutes
authority to allocate a new MDISK extent.

If DirMaint is actually installed and your userid is
authorized, its inventory reports may supply the
permanent-minidisk picture:

    DIRM USEDEXT V=M01RES
    DIRM FREEXT V=M01RES

If other candidate CP volume IDs emerge from `CP QUERY DASD ALL`,
repeat authorized reports for those volumes. Some installations
lack DirMaint or manage the directory elsewhere; in that
case an authorized administrator must audit all `MDISK` and
`DEDICATE` definitions in the ACTIVE CP directory,
the directory manager's extent database if any, and CP
reserved `DRCT`, `PAGE`, `SPOOL`, `TDISK` extents.
Do NOT paste a complete `USER DIRECT` to a public report:
user entries may contain passwords or other secrets.
Share only the relevant redacted extent reports.

On the Linux Hercules host, after confirming the process
and active configuration, read-only:

    pgrep -af '[h]ercules'
    ls -lh /home/admin/vm630/dasd*
    df -h /home/admin/vm630
    bash scripts/inspect-hercules-config.sh /home/admin/vm630/hercules.cnf

Reconcile the CP real devices and volumes with the
Hercules CKD image geometry and process cwd, not filenames
alone. If a new DASD image is needed, capacity, device type,
host storage, CKD initialization/CP attachment and the
active guest directory must be planned separately. Do not
create/attach/reformat one from guessed commands.

## Phase 2: administrator-only allocation and backup

**Stop at this gate without a VERIFIED contiguous free 1600-cylinder
(or appropriately sized) region on a suitable volume.**
IBM explicitly warns that CP and directory-processing tools
do not completely prevent overlapping MDISK extents. The
administrator must reconcile user minidisks, CP extents,
historical/dummy users and current dedicated disks.

Before any allocation or format operation, preserve the
backing volume and all overlays/dependencies with a
verified, quiesced offline copy, or coordinated provider
snapshot. This matters particularly because of the earlier
CMS A `DMSDKD1307T` / TRKDE 4 incident. The existing
repo `scripts/backup-offline-dasd.sh` works ONLY after
the actual Hercules instance is offline and the specific
base image has been validated; a live ordinary `cp`
of `dasd1` is not an acceptable substitute.

With verified free physical extents, define a new
**permanent** 3390 MDISK on the MAINT user with an
unused virtual address, a verified real volume ID, a
checked start location and agreed length. The directory
`MDISK` statement format is:

    MDISK <VDEV> 3390 <START> <CYLINDERS> <VOLSER> <MODE>

This is **syntax only, not a command to execute**.
The actual numbers and VOLSER are intentionally
absent. Use the installed DirMaint's authorized
allocation functions or carefully approved USER
DIRECT/DIRECTXA procedure; do not overlay A/191,
existing system extents or users. The directory must
be applied and the device made visible in MAINT
before continuing. Never choose VDEV 0192 because
CMS can automatically manage it as its D disk.

## Phase 3: format ONLY the newly created empty target

After the administrator provides the verified VDEV,
VOLSER, backing volume extent and confirmation that
this is an unused NEW disk, inspect again:

    CP QUERY VIRTUAL DASD
    CP QUERY MDISK <VDEV> LOCATION

**Do not run FORMAT against an old or uncertain device.**
CMS `FORMAT` is destructive; it erases previous data.
Initialize the newly allocated empty disk under the
verified virtual device address, use a 4096-byte CMS
blocksize and the intended volume label, and ACCESS
that *new* device as G. Consult the installed z/VM
6.3 `FORMAT` syntax and prompts before entering
a destructive command.

After new formatting/access:

    QUERY DISK G

Require exactly one G disk, R/W, TYPE 3390,
BLKSZ 4096, with `BLKS LEFT` at least 180000.
Record VDEV, label, size, used/free blocks and
`CP QUERY MDISK <VDEV> LOCATION`.
Avoid formatting or re-accessing A, and do not
rename G to A.

## Phase 4: Git source transfer, build and target gates

GitHub contains updated `M173CHK.EXEC` to
`M176CHK.EXEC`, all accepting a single non-A
filemode letter, e.g. G. M173 output is
`M173NET STAGE G`, M174 output `M174NET INDEX G`;
live input PACK and META remain on A. M173/174 gates
are fail-closed and retain failed output for diagnosis;
they do not automatically ERASE a large output on failure.

On the Mac from `ibm-sandbox/src`:

    git pull
    ./cms-upload.sh M173CHK.EXEC M174CHK.EXEC
    ./cms-upload.sh M175CHK.EXEC M176CHK.EXEC

On CMS, only after G has passed the capacity gate:

    GIT LEVEL
    QUERY DISK G
    M173CHK G

`GITPIMP MODULE` already exists from the M176
target checkpoint; do not rebuild unless the module
or source has changed. On M173 failure, retain the
stage for diagnosis and do not rerun while it exists.
If and only if M173 independent readback is PASS,
continue (build later native modules as needed):

    CMSCLNK GITPIDX PLAIN
    M174CHK G
    CMSCLNK GITPCAT PLAIN
    M175CHK G
    CMSCLNK GITPTRE PLAIN
    M176CHK G

Target-specific module compilation and `CMSCLNK`
link modes must be cross-checked against each milestone
before execution. The above commands assume the
`.C` source for each later module is present on A;
upload current GitHub sources first if missing.

Do not claim M173–M176 target validation until real
CMS produces their full expected PASS outputs.

## Source documentation

- IBM [MDISK directory statement](https://www.ibm.com/docs/en/zvm/7.2.0?topic=directory-mdisk-statement):
  overlap warnings and persistent extent syntax.
- IBM [QUERY ALLOC](https://www.ibm.com/docs/en/zvm/7.2?topic=commands-query-alloc):
  CP-owned extents only.
- IBM [DirMaint USEDEXT](https://www.ibm.com/docs/en/zvm/7.3.0?topic=ivp-test-0710-dm0710):
  authorized extent inventory.
- IBM [FORMAT](https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-format):
  destructive initialization and 180 4K blocks/cylinder.
- Existing project `docs/CMS_DASD_RECOVERY.md`:
  exact Hercules 0123 volume mapping and prior A-disk
  integrity warning.


## 2026-10-08 11:49 — real CP extent inventory

The operator supplied the following live evidence:

- `CP QUERY VIRTUAL DASD` listed full-pack MAINT virtual
  `0122 M01S01` (real `0124`), `0123 M01RES` (real `0123`),
  and `0124 M01W01` (real `0126`), each 11,000 cylinders.
  These are **existing mappings**, not unused/new storage.
  Virtual `0191 M01RES` remains 175 cylinders on real `0123`.
  Several other minidisks share M01RES.
- `CP QUERY DASD ALL` reports `0123 M01RES` with 158
  *links* to minidisks; `0124 M01S01` with 1,
  `0125 M01P01` with 0, `0126 M01W01` with 1,
  `0127 VMCOM1` with 15, and `0128 630RL1`
  with 32. These trailing counts are links, **NOT**
  number of free cylinders. No free or offline real
  DASD device was reported.
- `CP QUERY ALLOC MAP ALL` shows existing CP allocations:
  `M01RES` real `0123`, cylinders **1–20**,
  `DRCT ACTIVE`; `M01S01` real `0124`,
  cylinders **1–10999**, `SPOOL`; and `M01P01`
  real `0125`, cylinders **1–10999**, `PAGE`.
  The extremely low **IN USE** numbers on PAGE/SPOOL
  do not imply that the extents are allocatable for
  permanent user MDISK definitions. Do not allocate
  an M173 minidisk in these regions.
- `DIRM USEDEXT V=M01RES` failed with
  `DVHDIR1002T FILE NOT FOUND: WHERETO DATADVH *; RC=28`
  and `DVHDIR1001T ... 1 REQUIRED FILES NOT FOUND`
  (overall RC1001). It produced **no valid
  minidisk allocation report**. IBM's DVH1001T
  reference says WHERETO absence means DirMaint may
  be stopped or its interface disk/configuration is
  unavailable. The IBM-recommended first recovery
  step if it is not running is starting the DIRMAINT
  service machine, often with `XAUTOLOG DIRMAINT`
  performed by an authorized system administrator.

### Next DirMaint investigation

First use the non-mutating CP status check:

    CP QUERY DIRMAINT

If DIRMAINT is **not logged on**, an authorized
administrator can initialize it with:

    CP XAUTOLOG DIRMAINT

This step starts a privileged service, so do not run
blindly if already logged on or if the installation's
DirMaint interface was intentionally disabled. If
the service is already logged on, check the accessed
interface disk, current CONFIG DATADVH, WHERETO
availability and DirMaint log; IBM also documents
`DVHBEGIN` at the DIRMAINT virtual console when
appropriate. Do not reset its configuration arbitrarily.

Once the service and its interface are functioning,
request read-only allocation reports:

    DIRM USEDEXT V=M01RES
    DIRM FREEXT V=M01RES

If needed and the other available volumes are
registered for DirMaint extent management, request
the same for `M01W01` and `VMCOM1`, avoiding CP
SPOOL and PAGE extents. DirMaint usually returns
these as CMS reader files, so check reader queue
rather than expecting the full report at the
command prompt. Do not share unredacted full USER
DIRECT contents with authentication fields.

If DirMaint is not configured or cannot be safely
started, have the authorized administrator locate
the true active source CP directory and use IBM's
read-only `DISKMAP` utility to display gaps and
overlaps from the MDISK definitions. DISKMAP writes
an output report file; do not process a guessed,
outdated, or untrusted directory as the source of
truth. Full-pack mappings must be handled specially
and do not constitute safe free extents.

**NO PERMANENT MINIDISK EXTENT CONFIRMED YET.**
Avoid CREATE/FORMAT/DEFINE until a verified
nonoverlapping, persistent extent and independent
backup are both available.


## 2026-10-08 13:08 — DirMaint autolog does not stay running

MAINT attempted the prescribed commands; actual results:

    CP QUERY DIRMAINT
    HCPCQU045E DIRMAINT not logged on
    CP XAUTOLOG DIRMAINT
    Command accepted
    AUTO LOGON *** DIRMAINT USERS = 19
    HCPCLS6056I XAUTOLOG information for DIRMAINT:
      The IPL command is verified by the IPL command processor.
    USER DSC LOGOFF AS DIRMAINT USERS = 18
    CP QUERY DIRMAINT
    HCPCQU045E DIRMAINT not logged on

Both `DIRM USEDEXT V=M01RES` and `DIRM FREEXT V=M01RES`
still produced `DVHDIR1002T FILE NOT FOUND: WHERETO
DATADVH *; RC=28`, then `DVHDIR1001T`. These are NOT
working directory allocation reports. `CP QUERY RDR ALL`
displayed many old RDR files and CPDUMPs, not a
DirMaint extent report. Do NOT clear/purge the reader
queue or CP dump material while investigating.

A successful XAUTOLOG acceptance and an IPL-command
verification do not prove that the DIRMAINT service
completed CMS initialization; it promptly logged off.
Do not endlessly restart it. Find the underlying
startup/PROFILE/DVHPROF/linked-disk condition or
use an independently verified offline/read-only
mapping alternative.

### Next **read-only** CMS checks

    LISTFILE ACCESS DATADVH *
    LISTFILE CONFIG* DATADVH *
    LISTFILE WHERETO DATADVH *
    STATE USER DIRECT C
    LISTFILE * DIRECT C (ALLOC
    LISTFILE * BACKUP C (ALLOC
    LISTFILE * DIRECT A (ALLOC

In this z/VM 6.3 setup `MAINT 02CC` is accessed
R/W as C (the last inventory showed just four
files). IBM's z/VM basics manual identifies
`MAINT 2CC USER DIRECT` as a common source-directory
location. It is a **candidate**, NOT yet proven
present/current on this system. Ask for the file
STATE/LISTFILE and exact build provenance without
displaying password-bearing directory text.

If `USER DIRECT C` exists and the operator can
establish it corresponds to the **currently active**
CP directory, `DISKMAP USER DIRECT C` or the
systems-programmer `DIRMAP USER DIRECT C <outfm>`
can report MDISK gaps and overlaps without DirMaint.
IMPORTANT: these utilities **write new map output files**
(`USER DISKMAP` or `USER MDISKMAP` and related)
to a CMS minidisk; they are not fully read-only.
Before invoking, choose a verified writable output
filemode, check that each named output is absent
and leave headroom. Avoid A due to its earlier
TRKDE 4 issue, and avoid accidentally replacing
an existing saved map. IBM documents that DIRMAP
may ignore or mischaracterize full-pack overlaps
and can assume a smaller disk model if no high
cylinder exists in the input. Reconcile volume
geometry and CP reserved DRCT/SPOOL/PAGE extents
independently. A stale `USER DIRECT` is NOT
authority for allocating a new physical cylinder
range.

IBM docs:
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-diskmap
- https://www.ibm.com/docs/SSB27U_7.2.0/com.ibm.zvm.v720.dmsb4/dirmap.htm
- https://www.redbooks.ibm.com/redbooks/pdfs/sg247316.pdf

DIRMAINT server recovery requiring logon to DIRMAINT,
DVHBEGIN, or changes to its disks/profile is an
independent, privileged maintenance task. Do not
modify its configuration or source directory
without a verified recovery plan and backup.
No disk extents are yet approved for M173.


## 2026-10-08 13:12 — confirmed USER DIRECT on MAINT C (2CC)

Operator ran `STATE USER DIRECT C` on CMS, RC0, then
`LISTFILE * DIRECT C (ALLOC`. This confirmed:

    USER DIRECT C1 F 80, 4282 records, 84 CMS blocks.

This is the conventional directory source on MAINT's
virtual 02CC, already accessed as C R/W with roughly
1694 free 4-KiB blocks in the last `QUERY DISK`.
The file is **a candidate source, not independently
proven equal to the active CP binary directory**.
Do not display/paste raw USER DIRECT (may contain
user passwords or MDISK access passwords). Do not
run `DIRECTXA` without the `EDIT` option: the
non-EDIT form can activate a replacement CP directory.

IBM `DISKMAP USER DIRECT C` would write `USER DISKMAP A`,
so avoid it after the earlier A-disk integrity incident.
IBM `DIRMAP` accepts an independent `outfm` and
writes `fn MDISKMAP` there. Only after an output
collision check and capacity check, it can run against
the candidate source, **without activating it**.

Next target commands, in order:

    QUERY DISK C
    STATE USER MDISKMAP C

If C is still writable with ample space, and STATE
returns RC28 (file absent), generate the map there:

    DIRMAP USER DIRECT C C

The last C is the output filemode, so the output
will be `USER MDISKMAP C`, not on A.
`DIRMAP` writes this file and must not be described
as entirely read-only; verify there is no preexisting
`USER MDISKMAP C` before running it. It does not
alter the source USER DIRECT or CP active directory.

After a successful map, compare at least the
MAINT 0191 and additional 0190, 0193, 0401 MDISK
locations with live `CP QUERY MDISK ... LOCATION`.
Flag discrepancy as a potentially stale directory
source and do not allocate anything. Inspect only
the map output (which reports owner, virtual address,
VOLSER and physical start/end but not passwords).
For a focused read-only display:

    PIPE < USER MDISKMAP C | LOCATE /M01RES/ | CONSOLE

If that produces excessive output, show
the map's gap and overlap lines separately, along
with appropriate surrounding minidisk records,
or extract the relevant sections to another
report after reviewing what they expose.
Do not choose a new starting cylinder on the
strength of any single map or gap marker: reconcile
its total volume geometry, all full-pack definitions,
CP DRCT/PAGE/SPOOL, and directory-source currency
first.

Source: IBM z/VM CMS `DIRMAP` utility specifies
`fn ft fm outfm` and states that default A1 may
be overridden; IBM z/VM `DISKMAP` writes its output
to A and flags unbounded END MDISK statements
unless DOENDS is used.
