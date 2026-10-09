# M173 persistent 3390 data-minidisk provisioning runbook

## 2026-10-09 08:28:36 CDT — M173 Gate 5d live CP PASS

Actual MAINT commands succeeded except the **expected**
RC40 negative permanent-directory query:
`CP QUERY DASD DETAILS 0127` = VMCOM1, 3390-0C,
CYLS11000; `CP QUERY MDISK USERID 6VMHCD20 0300
LOCATION DIRECTORY` = VMCOM1 RDEV0127 start5756
size180 (ending5935); `CP QUERY MDISK 0600
DIRECTORY` = HCPQMD040E, RC40, new device absent;
`CP QUERY ALLOC MAP VMCOM1` = NOT FOUND for
CP-use extents; `M173DCHK` = original/backup
4282 identical, candidate MAINT-1 single insertion
record213, DELTA CHECK PASS RC0.

**Gates 5c and 5d pass.** No activation has occurred.
IBM's QUERY ALLOC MAP does not enumerate PERM/PARM,
and DIRMAP ignores fullpack minidisk overlaps.
No complete independent enumeration of active
VMCOM1 directory MDISK definitions exists yet.

### Gate 5e — class-B and earlier candidate-map read-only probe

On CMS MAINT:
```text
CP QUERY PRIVCLASS
PIPE < M173NEW MDISKMAP C | DROP 100 | TAKE 100 | CONSOLE
```
CP QUERY PRIVCLASS identifies the **current** classes.
IBM VMUDQ LSTMDISK (privilege class B) supports selecting
all current CP-directory MDISK definitions on a given
volser; installed 6.3 interface/module availability
is still unverified, and no executable has been added.
If B is unavailable, do not modify privilege classes.
The PIPE displays earlier report rows that could
contain candidate-source full-pack/END definitions;
it is not independent CP enumeration.
Keep volume-wide full-pack risk and rollback gating
separate from observed 5d success.

Do not run DIRECTXA without EDIT, LINK, ACCESS, FORMAT,
M173CHK or importer. Retain USER DIRECT C,
M173BAK DIRECT C, M173NEW DIRECT C, all PACK
and sealed original Git objects unchanged.


## 2026-10-09 — Gate 5c contextual VMCOM1 map LIVE PASS

Actual CMS `DROP 200 | TAKE 100` read from
`M173NEW MDISKMAP C` includes the `VMCOM1 3390`
header and consecutive entries: 6VMHCD20/0300
5756-5935 size180, gap5936-5999 size64, MAINT-1
0600 exclusive W 6000-7599 size1600, and gap
7600-10016 size2417. No overlap is shown within the
**source-derived candidate map**. The displayed
`630RL1 3390 MAINT630 0131 MR 000-10016`
is a separate volume, not a VMCOM1 overlay.

**Full Gate 5c source-map context PASS.** A new 0600/G
device has NOT been activated, linked, accessed or
formatted. A clean DIRMAP does not establish complete
active-CP PERM/PARM/full-pack safety.

**Next Gate 5d is independent read-only CP revalidation**:
`CP QUERY DASD DETAILS 0127`,
`CP QUERY MDISK USERID 6VMHCD20 0300 LOCATION DIRECTORY`,
`CP QUERY MDISK 0600 DIRECTORY`,
`CP QUERY ALLOC MAP VMCOM1`,
and `M173DCHK`. See the current-gate banner in
`docs/M173_DIRECTORY_CHANGE_PLAN.md` for expected
results and fail-closed policy. No directory activation,
LINK, ACCESS, FORMAT or import before a separately
authorized rollback and fullpack/PERM/PARM review.


## 2026-10-09 08:16:20 CDT — Gate 5c boundary filters LIVE PASS

Four read-only CMS `PIPE < M173NEW MDISKMAP C | LOCATE`
commands returned normal RC0 on MAINT. The source-derived
report shows MAINT-1 0600 W, 6000-7599 length 1600,
gap 5936-5999 size64 and gap 7600-10016 size2417.
All endpoint calculations match. But the VOLSER field is
blank on the returned continuation rows, so **full Gate 5c
and volume context remain pending**, not proven.

Next read-only check: `PIPE < M173NEW MDISKMAP C |
DROP 200 | TAKE 100 | CONSOLE`. Inspect the contiguous
VMCOM1 section; publish only nonsecret extent summaries.
No CP directory activation, LINK, ACCESS, FORMAT,
or M173 import. DIRMAP is not proof against fullpack
and hidden PERM/PARM overlaps. Original USER DIRECT C
and backup M173BAK DIRECT C remain protected.


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


## 2026-10-08 13:18 — DIRMAP generated on C; full volume still unseen

The operator confirmed `QUERY DISK C`: MNT2CC on virtual
2CC, C R/W, ten 3390 cylinders, BLKSZ 4096, four files,
106 used blocks, **1694 free** of 1800. `STATE USER
MDISKMAP C` returned RC28: absent. The actual command

    DIRMAP USER DIRECT C C

succeeded with

    DMSCYD2231I USER DIRECT C1 read.
    DMSCYD2232I USER MDISKMAP C1 written - no errors.

`STATE USER MDISKMAP C` then returned RC0, and
`LISTFILE USER MDISKMAP C (ALLOC` showed F100,
**392 records and ten allocated 4K blocks**, on C1.
Thus C-only mapping was target-verified; USER DIRECT
was not activated with DIRECTXA. No new G minidisk
has been allocated or formatted.

The operator ran:

    PIPE < USER MDISKMAP C | LOCATE /M01RES/ | CONSOLE

This returned ONLY three physical report rows:

    M01RES 3390 MAINT   0123 MR   000   10016  10017 MAINT-1 *
    M01RES 3390 VMSERVR 0301 WR  3438    3439    002 VMSRVR-1 *
    M01RES 3390 OSASF   0200 MR  7973    7987    015 OSASF-1  *

**These three lines are NOT the entire M01RES
allocation list**. IBM DIRMAP output suppresses
repeating volser/devtype on continuation rows;
the volser reappears at section/page boundaries.
As a result, LOCATE /M01RES/ omits other
M01RES minidisks and all unlabelled GAP rows.
The first MAINT 0123 is a special full-pack mapping,
not necessarily exclusive use of every cylinder.
The DIRMAP full-pack ending cylinder 10016 implies
a 10017-cylinder inferred model, whereas live
`CP QUERY VIRTUAL DASD` reports 11000 cylinders
for virtual 0123. IBM documents model-size estimation
and FULLPACK DEFINES overrides. Do not infer
that cylinders beyond 10016 are free, or that
the three filtered lines imply few actual
minidisks. Correctness also requires matching
current CP directory, SSI/subconfig context and
CP-allocated DRCT 1-20.

Real CP location cross-checks (read only):

    MAINT 0190 M01RES real0123 start280 size214 (280-493)
    MAINT 0191 M01RES real0123 start494 size175 (494-668)
    MAINT 0193 M01RES real0123 start669 size500 (669-1168)
    MAINT 0401 M01RES real0123 start1961 size292 (1961-2252)

Next read-only target commands to display **all**
392 records in ordered chunks, including unlabelled
continuation rows and GAP markers:

    PIPE < USER MDISKMAP C | TAKE 100 | CONSOLE
    PIPE < USER MDISKMAP C | DROP 100 | TAKE 100 | CONSOLE
    PIPE < USER MDISKMAP C | DROP 200 | TAKE 100 | CONSOLE
    PIPE < USER MDISKMAP C | DROP 300 | CONSOLE

These commands DO NOT create or replace map files
and never expose the password-bearing USER DIRECT.
Return the relevant M01RES pages including headings,
blank-volser rows, GAP and OVERLAP entries, then
reconcile all minidisk extent rows with CP real
locations and live model before proposing a new
permanent 1600-cylinder allocation. Do NOT treat
DIRMAP gap estimates as automatically validated
unallocated physical cylinders, particularly
because DIRMAP excludes special full-pack overlaps
and can assume a different device geometry.


## 2026-10-08: M01RES tail discovered; physical end not yet verified

Second set of operator-supplied MDISKMAP records (through end of M01RES)
shows minidisks allocated consecutively through cylinder 9412:
ZHCP 0100 4478-7807, assorted service disks 7808-9412,
including CBDIODSP 0400 9053-9412.
DIRMAP explicitly reports GAP 9413-9419 (7 cylinders),
MAINT 029D 9420-9439 (20 cylinders), then
GAP 9440-10016 (577 cylinders).
The next page switches to M01S01, confirming no further
ordinary M01RES rows under DIRMAP's assumed geometry.

However real CP QUERY VIRTUAL DASD reported that the
MAINT fullpack 0123 mapping of M01RES is 11000
cylinders. A physically available tail 9440-10999
would be 1560 consecutive cylinders if this geometry
and absence of allocations beyond 10016 are independently
established. Gross CMS 4K capacity at 180 blocks per
cylinder is 280800 blocks (~1.07 GiB), above M173's
180000-free-block preflight. One possible future
conservative allocation would use fewer than all
1560 cylinders, such as 1500, preserving end headroom.
None is authorized or proven free yet.

The DIRMAP output's fullpack end 10016 may reflect
default legacy 3390-9 model geometry. IBM DIRMAP
documents the FULLPACK DEFINES file, with
"3390 10999" identifying an 11000-cylinder fullpack,
and explicitly ignores fullpack overlaps during detection.
Do not infer availability solely from the partial report,
and DO NOT alter FULLPACK DEFINES or rerun DIRMAP over
the existing USER MDISKMAP C without a separately
verified output-collision plan.

Use read-only live CP geometry checks:

    CP QUERY DASD DETAILS 0123
    CP QUERY MDISK 0123 LOCATION

Review the rest of the 392-record map, especially
the remaining VMCOM1/630RL1 sections:

    PIPE < USER MDISKMAP C | DROP 200 | TAKE 100 | CONSOLE
    PIPE < USER MDISKMAP C | DROP 300 | CONSOLE

Host free space must also be checked BEFORE expanding
CKD allocations or writing a large imported stage:

    df -h /home/admin/vm630
    ls -lh /home/admin/vm630/dasd1

Do NOT run FORMAT or change the active CP directory.
Even after geometry confirmation, physical space,
backup provenance, source directory currency and
nonoverlap must be reconciled. Existing MAINT 0191
M01RES and the project PACK/generations stay untouched.


## 2026-10-08 13:29 — VMCOM1 is the preferred candidate

The operator continued the actual `USER MDISKMAP C` output
using `PIPE < USER MDISKMAP C | DROP 200 | TAKE 100 | CONSOLE`.
The terminal output arrived with some page-boundary lines out of
order, but its VMCOM1 physical extent list is unambiguous:

- The last normal VMCOM1 allocation was `6VMHCD20 0300 MR`
  on cylinders **5756–5935**, 180 cylinders.
- DIRMAP then displayed an explicit **Gap 5936–10016,
  4081 cylinders**.
- The following report section is a *different* volume,
  `630RL1`; those entries are not allocations on VMCOM1.
- Real DASD `0127` is CP-owned volume `VMCOM1`.
  Hercules config previously mapped `0127 3390 dasd5`
  in the verified `/home/admin/vm630` working directory.
- A proposed **1600-cylinder** permanent MAINT data minidisk
  beginning at **6000** and ending at **7599** fits entirely
  *within* DIRMAP's 5936–10016 reported gap, without
  extrapolating past the map's conservative 10017-cylinder
  3390 volume geometry. Gross CMS capacity is 288000
  4096-byte blocks; the actual free count after FORMAT
  must still exceed M173's 180000-block admission threshold.

**This is a candidate, not a confirmed/authorized MDISK allocation.**
IBM documents that CP does not completely prevent overlapping
minidisk allocations. Before defining, initializing, or writing
the proposed range, the operator/administrator must verify
(1) live VMCOM1 real geometry, (2) live minidisk locations for
at least two VMCOM1 entries vs the DIRMAP source, (3) MAINT
virtual device address availability and any unrecorded
subconfiguration/extent reservations, (4) Linux host space
and active Hercules backing path, and (5) an independently
verified backup or provider-consistent snapshot covering
both VMCOM1 (the proposed target and MAINT 2CC source)
and M01RES (which contains the active CP directory),
including every relevant CKD overlay or shadow. Record
recoverable source-directory and active-directory state
before any directory recompilation. A new MDISK
definition must also be saved/applied via a verified,
site-approved directory management procedure; DirMaint
currently does not initialize on this host.

### Read-only next gate — CMS

    CP QUERY DASD DETAILS 0127
    CP QUERY MDISK 02CC LOCATION
    CP QUERY MDISK 049E LOCATION
    CP QUERY MDISK 0551 LOCATION
    CP QUERY VIRTUAL DASD

Expected from directory map, subject to *independent*
confirmation: real 0127 VMCOM1 >=7600 cylinders;
current virtual 02CC is linked to PMAINT 02CC
at start 121 length 10; 049E maps to 6VMLEN20
049E start 4104 length 250; PMAINT 0551 is
start 572 length 40. If any mismatch, stop.
Query only extant minidisks; do not create virtual
device mappings to "test" cylinder boundaries.

### Read-only next gate — verified Hercules host

    pgrep -af '[h]ercules'
    readlink -f /proc/ACTUAL_HERCULES_PID/cwd
    ls -lh /home/admin/vm630/dasd5
    df -h /home/admin/vm630
    bash scripts/inspect-hercules-config.sh /home/admin/vm630/hercules.cnf

Replace `ACTUAL_HERCULES_PID` with the process ID
observed now, not a historical PID. The current 0127
device must actually resolve to the active VMCOM1
`dasd5` backing image; do not infer it solely from
past process state. Do not copy a live CKD image with
ordinary `cp`; take a verified offline backup after
quiescing the guest/emulator, or a provider-consistent
snapshot that covers the real image and overlays.
Check that VMCOM1 has adequate growth space when
M173 writes its potentially very large stage.

### Gate to authorized provisioning

No `USER DIRECT` source edits, `DIRECTXA`,
`FORMAT`, `LINK`, or `ACCESS` of a proposed
new virtual device until the above evidence and
backup safeguards are satisfied. Choose a truly
unused MAINT virtual address after verifying
its currently active directory and device map;
do not confuse the proposed real-volume cylinder
start `6000` with the hexadecimal virtual device
number. Only the site administrator should commit
an appropriate permanent `MDISK` statement
under MAINT and validate it before CMS initializes
that *new empty* minidisk. Retain existing A, C,
M171NET PACK/META and all sealed generations.


## 2026-10-08 13:31 — REAL CP DASD GEOMETRY VERIFIED

The operator has now independently checked live z/VM CP, not
just the MAINT source-directory map. Actual results:

    CP QUERY DASD DETAILS 0123
    0123 CUTYPE 3990-C2 DEVTYPE 3390-0C VOLSER M01RES CYLS 11000

    CP QUERY DASD DETAILS 0126
    0126 CUTYPE 3990-C2 DEVTYPE 3390-0C VOLSER M01W01 CYLS 11000

    CP QUERY DASD DETAILS 0127
    0127 CUTYPE 3990-C2 DEVTYPE 3390-0C VOLSER VMCOM1 CYLS 11000

    CP QUERY MDISK 123 LOCATION
    MAINT 0123 MAINT 0123 3390 M01RES 0123 start0 size11000

    CP QUERY MDISK 124 LOCATION
    MAINT 0124 MAINT 0124 3390 M01W01 0126 start0 size11000

These facts resolve **real physical geometry**: the three
existing volumes each present 11,000 cylinders. DIRMAP's
smaller `0–10016` inferred full-pack interval is an
inaccurate boundary for these emulated 3390s. It may
reflect DIRMAP's default model/definitions; do not
assume that absence of DIRMAP records above 10016
is evidence of completely unused real cylinders.

The preferred proposed M173 data allocation remains
**VMCOM1 / real 0127 / cylinders 6000–7599 /
length 1600**, which lies completely within DIRMAP's
own explicit VMCOM1 gap 5936–10016. No reliance on
the extra 983 physical cylinders is necessary.

### What remains before **any** CP directory change

1. Verify at least two live VMCOM1 minidisk locations
   against source directory and verify that the
   selected new MAINT virtual device number is unused.
   On MAINT:

       CP QUERY MDISK 02CC LOCATION
       CP QUERY MDISK 049E LOCATION
       CP QUERY MDISK 0551 LOCATION

   For comparison, DIRMAP says MAINT 02CC is an
   existing link to PMAINT 02CC at VMCOM1 start121,
   length10; 049E is 6VMLEN20 start4104 length250;
   0551 is PMAINT start572 length40. These are
   expectations from source, not yet live confirmations.

2. Reverify the ACTIVE Hercules instance's real
   `0127` -> `dasd5` image mapping and its current
   storage and available Linux filesystem space.
   On the Hercules host (only after confirming actual
   process and working directory):

       pgrep -af '[h]ercules'
       ls -lh /home/admin/vm630/dasd5
       df -h /home/admin/vm630
       bash scripts/inspect-hercules-config.sh /home/admin/vm630/hercules.cnf

   The repo's `scripts/map-cms-minidisk.sh` also
   verifies an unambiguous configuration record by
   REAL RDEV and verified process cwd; run it against
   real **0127**, not the MAINT virtual address.

3. Establish an independently verified restorable
   offline backup or coordinated provider-consistent
   snapshot of both VMCOM1 (the future stage and
   directory source volume) and M01RES (the active
   CP directory volume), plus overlays/metadata.
   Do not ordinary-`cp` a currently open Hercules
   DASD backing file, and do not destroy retained
   dump evidence.

4. Confirm the site-specific CP directory update and
   rollback procedure while DirMaint is not running.
   `USER DIRECT C` alone is a candidate source and
   must be proved current before it is used for any
   `DIRECTXA` activation. Never format an existing
   full-pack or minidisk to "test" the gap.

**Status: physical geometry confirmed, but new MDISK
allocation, FORMAT, ACCESS and M173 target execution
are all still pending.** No target has been changed.


## 2026-10-08 13:43 — live VMCOM1 link corroboration and host capacity

Operator-supplied read-only evidence on CMS:

    CP QUERY MDISK 02CC LOCATION
    MAINT 02CC PMAINT 02CC 3390 VMCOM1 real0127 start121 size10

    CP QUERY MDISK 049E LOCATION
    MAINT 049E 6VMLEN20 049E 3390 VMCOM1 real0127
    start4104 size250

Both locations independently **match** the actual
`USER MDISKMAP C` DIRMAP definitions. The third expected
link `CP QUERY MDISK 0551 LOCATION` has **not yet**
been provided. Two matches support, but do not prove
the complete currency of the source directory
against the active CP directory.

On the Hercules Linux host `ip-172-31-14-90`,
the operator reported:

    pgrep -af '[h]ercules'
    7174 hercules -f hercules.cnf -r hercules.rc

    ls -lh /home/admin/vm630/dasd5
    -rw-r----- 1 admin admin 1.9G Oct 6 17:51
    /home/admin/vm630/dasd5

    df -h /home/admin/vm630
    /dev/nvme0n1p1 16G total, 8.8G used, 6.1G
    available, 60% utilized, mounted on /

The candidate DASD backing file has a **1.9 GiB
approximate apparent** size, and the shared root
filesystem has **6.1 GiB available at this checkpoint**.
An apparent compressed CKD image size is *not* a
measure of guest disk free cylinders, import growth
headroom, or independently backed-up storage.
This is encouraging capacity evidence, not final
permission to allocate or write the candidate.

The current PID is **7174**, not the older historical
PID 879. Its actual working directory, configuration
record, live file descriptor and possible shadow
files are still to be independently confirmed.
Execute on the Hercules Linux host, read-only:

    readlink -f /proc/7174/cwd
    grep -nE '^[[:space:]]*0127[[:space:]]+3390' \
      /home/admin/vm630/hercules.cnf
    ls -l /proc/7174/fd | grep -F 'dasd5'
    du -h /home/admin/vm630/dasd5

If the runtime cwd proves `/home/admin/vm630`,
the repository's read-only mapper can corroborate:

    bash scripts/map-cms-minidisk.sh 0127 \
      /home/admin/vm630/hercules.cnf /home/admin/vm630

(The repository scripts must actually exist on this
host to invoke them; otherwise the plain read-only
commands above are sufficient.) A configured base
image may have overlays or dynamically attached
CKD definitions, so reconcile the emulator's
open file handles and site setup before any backup.

### Snapshot and mutation boundary

A recoverable **independent** snapshot/backup
covering active `VMCOM1` and `M01RES`, with all
CKD overlays and active/source directory state,
is still NOT established. A copy stored on
the same 16 GiB root filesystem is not independent.
Never ordinary-`cp` open `dasd5` or `dasd1` while
Hercules is running; arrange a coordinated provider
snapshot or a verified offline copy to separate
storage. Account for snapshot and post-provisioning
write growth and maintain restart/rollback steps.

The proposed physical interval `VMCOM1 6000–7599`
remains only a candidate despite the live CP matches.
Do not initialize a disk or activate `USER DIRECT C`
until both image identity and backup state are
confirmed and a site-approved change plan exists.


## 2026-10-08 13:48 — live 0127 image and third minidisk VERIFIED

The operator supplied the full host/CP identity chain:

    readlink -f /proc/7174/cwd
    /home/admin/vm630

    grep -nE '^[[:space:]]*0127[[:space:]]+3390' \
        /home/admin/vm630/hercules.cnf
    37:0127 3390 dasd5

    ls -l /proc/7174/fd | grep -F 'dasd5'
    16 -> /home/admin/vm630/dasd5

    du -h /home/admin/vm630/dasd5
    1.9G /home/admin/vm630/dasd5

    CP QUERY MDISK 0551 LOCATION
    MAINT 0551 PMAINT 0551 3390 VMCOM1 real0127 start572 size40

The last of the three live VMCOM1 minidisk links matches the
DIRMAP source. The other two were MAINT 02CC PMAINT 02CC
VMCOM1 start121 size10 and MAINT 049E 6VMLEN20
VMCOM1 start4104 size250. Therefore all **three**
targeted real extent corroboration checks passed.
PID 7174's verified working directory, Hercules
configuration line 37, and live FD16 establish that
`/home/admin/vm630/dasd5` is the **currently open
base backing image** for Hercules real device 0127.
This still does not independently rule out shadow/
overlay files, hot device changes, or invisible host
filesystem damage. Recheck before any system change.

No new MDISK was defined, no CMS FORMAT or ACCESS was
run, and no M173 import was attempted. The preferred
candidate is still VMCOM1 real 0127 cylinders 6000–7599,
1600 contiguous cylinders inside the independently
generated DIRMAP gap 5936–10016 and live 11000-cylinder
volume geometry. At 180 CMS 4K blocks per cylinder,
gross capacity is 288000 blocks. Actual free space
must pass M173's guard after initialization.

### Next gate: identify the EC2 backing volume, then preserve it

Existing Linux `df -h /home/admin/vm630` showed
`/dev/nvme0n1p1` mounted at `/`, total 16G,
used 8.8G and 6.1G available. AWS EBS volumes
can have independent point-in-time snapshots;
however the filesystem device path is NOT by
itself proof that the backing block device is EBS
or identifies its AWS volume ID.

Safe read-only identification on the Linux host:

    findmnt -no SOURCE,TARGET,FSTYPE /
    lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS,SERIAL
    cat /sys/block/nvme0n1/device/serial
    ls -l /dev/disk/by-id/ | grep -E 'Elastic_Block_Store|nvme'

If a corresponding EBS volume ID is established,
choose a reliable restoration approach and snapshot
that volume (and any other EBS volume containing
a required DASD overlay) through the EC2 console or
authorized AWS tooling. A snapshot of a **running**
Hercules process is *not* necessarily guest-
or application-consistent because the emulator
and guest may have unwritten caches. AWS recommends
pausing writes/unmounting when possible and recommends
stopping an EC2 instance before snapshotting its
root EBS volume. The operator must plan the
downtime and avoid unplanned guest I/O during
quiescence. Preserve full original snapshots and
record snapshot ID, region, account, originating
volume, creation time, and completion state.
Before considering the backup verified/restorable,
validate its recovery procedure, ideally by
restoring a test volume and examining the backing
files on an isolated host. An EBS snapshot normally
covers the entire selected EBS block volume, not
just `dasd1` and `dasd5`; if both are under the
same root filesystem and there are no separate
overlays elsewhere, this one EBS volume can
preserve both backing images together.

References:
- AWS EBS create snapshots:
  https://docs.aws.amazon.com/ebs/latest/userguide/ebs-creating-snapshot.html
- AWS EBS snapshots and restoration:
  https://docs.aws.amazon.com/ebs/latest/userguide/ebs-snapshots.html
- IBM DIRECTXA EDIT syntax verification and non-EDIT
  directory activation:
  https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-directxa

### Do not cross the provisioning boundary yet

Even with all three corroborations passing, the
recovery point remains **NOT established**.
Do not add an MDISK statement to the live USER
DIRECT, run non-EDIT DIRECTXA, change CP
directory pointers, define permanent new space,
or FORMAT any disk without a recorded independent
backup and a reviewed fallback/restore procedure.
Existing A, C, all sealed GITFIX/M15NEW generations,
and retained M171NET PACK/META must be preserved.


## 2026-10-08 — AWS EBS root volume positively identified

The operator's live `lsblk`, `/sys/block/nvme0n1/device/serial`,
and `/dev/disk/by-id` outputs agree that the 16 GiB
`/dev/nvme0n1` root block device is an **Amazon Elastic Block
Store volume**. Its exact volume identifier was verified in
the live conversation but is **intentionally omitted from
this public repository**; retrieve it from the host NVMe
serial or EC2 console when performing a snapshot.

The host's mounted `/dev/nvme0n1p1` root filesystem
contains both active Hercules images `dasd1`
(M01RES) and `dasd5` (VMCOM1); operator should
check `findmnt` and all CKD overlay locations
once more before backup. This means one **root
EBS volume snapshot** may cover both base images,
provided all dependencies reside on that volume.

**Required human-controlled steps before provisioning:**

1. Verify correct AWS account, region, EC2 instance
   and root volume attachment in the AWS EC2 console.
2. Quiesce guest I/O and cleanly shut down Hercules,
   then stop EC2 normally through the console and
   confirm the stopped state. AWS advises stopping
   an instance before snapshotting its root volume.
3. Create a snapshot of the privately verified EBS
   volume. Record `snap-...`, account/region,
   originating EBS volume, state, and completion.
   A snapshot is `pending` until its data transfer
   is finished; wait for `completed` before
   risky directory/storage changes.
4. Check the snapshot recovery route; ideally create
   a new test volume and examine data in isolation.
   Verify SSH access after instance restart, because
   AWS may assign a new public IPv4 address if no
   Elastic IP is attached. Confirm Hercules startup
   and guest state; do not assume guest restarted.
5. Review the complete admin-only checklist
   `docs/M173_EBS_RECOVERY_CHECKLIST.md`. Its
   exact host cloud identifiers are intentionally
   omitted from the public Git repository.

A snapshot completion state does **not** prove
a bootable guest or tested restoration, and an
inconsistent live-root snapshot is not equivalent
to an orderly offline backup. No snapshot has been
reported as created or tested so far; no new
permanent VMCOM1 MDISK, CMS FORMAT, or M173 run
has occurred.

References:
- https://docs.aws.amazon.com/ebs/latest/userguide/ebs-creating-snapshot.html
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Stop_Start.html
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/how-ec2-instance-stop-start-works.html


## 2026-10-08 — snapshot completion reported by operator

The operator reports **"snapshot is complete"** for
the previously identified AWS EBS root volume. This
advances the backup state from "not taken" to
**"operator-reported completed"**, but the actual
`snap-...` ID, source volume ID, AWS region, state
`completed`, whether the EC2/Hercules I/O was
quiesced, and isolated restoration have not yet
been independently inspected or reported. Do not
treat this as a validated restoration or claim to
have created or checked an AWS resource from GitHub.

Detailed next-phase checklist (public file deliberately
omits exact AWS identifiers):
`docs/M173_EBS_RECOVERY_CHECKLIST.md`.

After the EC2 instance is started again, first
verify its reachable endpoint, booted Hercules
configuration, and all protected Git artifacts.
**Do not yet modify `USER DIRECT C`, run non-EDIT
`DIRECTXA`, or FORMAT any minidisk.** Validate
the most important host and CMS read-only checks.

Linux host:

    pgrep -af '[h]ercules'
    df -h /home/admin/vm630
    ls -l /home/admin/vm630/dasd1 /home/admin/vm630/dasd5

CMS MAINT:

    CP QUERY DASD DETAILS 0127
    CP QUERY MDISK 02CC LOCATION
    CP QUERY MDISK 049E LOCATION
    CP QUERY MDISK 0551 LOCATION
    CP QUERY VIRTUAL DASD
    QUERY DISK A
    QUERY DISK C
    STATE M171NET PACK A
    STATE M171NET META A
    STATE USER DIRECT C

The favored new allocation on physical volume
VMCOM1 real Rdev 0127 is still **start cylinder
6000, length 1600, end cylinder 7599**, wholly
within verified DIRMAP free gap 5936–10016.
An example unused virtual device to investigate is
`0600`, **not approved** until both the current
session's virtual device table and the active CP
directory are checked. These are read-only:

    CP QUERY VIRTUAL 0600
    CP QUERY MDISK 0600 DIRECTORY

IBM documents `QUERY MDISK ... DIRECTORY` as
querying the directory-defined MDISK rather
than only the current virtual assignment.
An absent VDEV does not itself prove there is
an available real DASD cylinder interval.

A later one-line **illustrative** CP directory
addition under the actual `USER MAINT` stanza,
after vdev/source/backup/privilege/recovery gates:

    MDISK <VERIFIED_UNUSED_VDEV> 3390 6000 1600 VMCOM1 MR

This is not a CMS command to run, and `6000`
here is **decimal cylinder start** whereas the
virtual device number is hexadecimal. Read
IBM's MDISK statement notes: CP does NOT prevent
every overlapping minidisk allocation, and
any overlap can damage existing data.

A candidate modified USER DIRECT must be
preserved separately from the active source;
DIRECTXA `(EDIT` offers syntax checking
without activating the directory. IBM's
non-EDIT DIRECTXA can bring a new directory
online and change CP directory pointers.
Do not issue activation without a reviewed
recovery plan, confirmed source equivalence,
and an independently restorable snapshot.

References:
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-mdisk
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-directxa
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=directory-mdisk-statement
- https://docs.aws.amazon.com/ebs/latest/userguide/ebs-describing-snapshots.html


## 2026-10-08 14:44 — post-snapshot guest/host read-only checks passed

After the operator reported the EBS snapshot completed, the
EC2 instance and z/VM were restarted and the following
live results were supplied (guest commands were read-only):

    pgrep -af '[h]ercules'
    724 hercules -f hercules.cnf -r hercules.rc

    df -h /home/admin/vm630
    /dev/nvme0n1p1 16G size, 8.8G used, 6.1G free (60%)

    ls -l /home/admin/vm630/dasd1 /home/admin/vm630/dasd5
    dasd1 769571364 bytes (Oct 8 19:29)
    dasd5 1954890581 bytes (Oct 8 19:29)

    CP QUERY DASD DETAILS 0127
    VMCOM1 3390-0C real0127, 11000 cylinders

    CP QUERY VIRTUAL DASD
    MAINT 0122/0123/0124 fullpacks 11000 cylinders,
    MAINT 02CC VMCOM1 10 cylinders R/W,
    MAINT 049E VMCOM1 250 cylinders R/O,
    MAINT 0551 VMCOM1 40 cylinders R/O,
    and original A 0191 M01RES 175 cylinders R/W;
    NO new 0600 disk in this session's virtual DASD list.

    QUERY DISK A
    MNT191 0191 A R/W 175 CYL BLKSZ4096,
    212 files, 8659 used, 22841 free of 31500 (27%)

    QUERY DISK C
    MNT2CC 02CC C R/W 10 CYL BLKSZ4096,
    5 files, 117 used, 1683 free of 1800 (7%)

    STATE M171NET PACK A  --> RC0
    STATE M171NET META A  --> RC0
    STATE USER DIRECT C   --> RC0

Thus the previously verified CP device topology survived
restart, A's free-block count is unchanged, C contains
the additional report, and required PACK/META/directory
source files are still present. Their mere presence is
NOT an end-to-end pack/directory checksum or proven
snapshot restoration. Note Hercules is now PID **724**,
so previous `/proc/7174` file descriptor observations
do not describe the current process. The current
`dasd1` and `dasd5` filenames exist, but if a new
allocation operation is prepared, re-check current
open FDs and CKD overlay state for PID 724.

### Next safe VDEV gate — no directory changes

The session's `CP QUERY VIRTUAL DASD` contained no
`0600`, but the **active CP directory** must be
queried as well. IBM documents that `QUERY MDISK ...
DIRECTORY` reads directory-defined MDISK information,
which can differ from currently instantiated disks.
Both commands are read-only:

    CP QUERY VIRTUAL 0600
    CP QUERY MDISK 0600 DIRECTORY

Only if both reports show no device can 0600 become
a possible virtual address for a subsequent reviewed
directory edit. The proposed physical offset is
**decimal cylinder 6000**, length 1600, VMCOM1
real Rdev0127; the unrelated VDEV `0600` is
hexadecimal. No new MAINT MDISK has yet been defined.

### Verify the recovery point, don't retake it blindly

Operator-reported completed EBS snapshot must be
correlated with the root EBS volume in AWS EC2 console
(`Completed`, source ID, region, timestamp). If the
instance was quiesced and snapshot is correct, save
metadata and a credible restoration procedure; an
isolated restore test is recommended. No additional
snapshot is required simply because no ID was
shared here. Do not publish account, instance, snapshot,
or root volume identifiers in the public GitHub repo.

References:
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-mdisk
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-directxa
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=directory-mdisk-statement


## 2026-10-08 14:53 — corrected MAINT 0600 directory query

After the post-snapshot boot, the operator confirmed Hercules PID 724,
cwd `/home/admin/vm630`, and open image FDs 12 => `dasd1`
(real 0123) and 16 => `dasd5` (real 0127); active config has
`0123 3390 dasd1` and `0127 3390 dasd5`.
`CP QUERY VIRTUAL 0600` returned `HCPQVD040E Device 0600 does
not exist`, establishing that 0600 is not currently attached.

The previous example `CP QUERY MDISK MAINT 0600 DIRECTORY` was
syntactically wrong and returned `HCPQMD022E` (invalid/missing
virtual device number). The **correct** read-only query on the
MAINT session is:

    CP QUERY MDISK 0600 DIRECTORY

IBM documents `QUERY MDISK vdev DIRECTORY`: `DIRECTORY` checks
the permanent CP directory, and the issuing userid (MAINT) is used
when `USERID` is omitted. The response is **still pending**;
do not infer that the permanent 0600 entry is absent from the
syntax error. Once the directory check is satisfactory, independent
snapshot provenance and credible restoration procedure, source-directory
currency, and a syntax-only directory change plus rollback review
remain required before **any** activation, LINK/ACCESS or FORMAT.
IBM reference: https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-mdisk


## 2026-10-08 15:01 — BOTH MAINT 0600 VDEV GATES PASSED

Actual CMS MAINT command and response:

    CP QUERY VIRTUAL 0600
    HCPQVD040E Device 0600 does not exist
    Ready(00040); T=0.01/0.01 14:53:40

    CP QUERY MDISK 0600 DIRECTORY
    HCPQMD040E Device 0600 does not exist
    Ready(00040); T=0.01/0.01 15:01:35

The first confirms no MAINT 0600 *instantiated* virtual device.
IBM's QUERY MDISK DIRECTORY operand checks the *permanent CP user
directory* for the issuing userid MAINT; its HCPQMD040E establishes
no current permanent MAINT MDISK at 0600. Unlike the earlier
HCPQMD022E syntax failure, **both are valid absence results**.
Virtual address 0600 is therefore confirmed available at this
point in the **MAINT** virtual/directory views only, not globally.
Recheck immediately before activation because configuration may change.

The previously independently mapped physical range on VMCOM1 real
0127, cylinders 6000 through 7599 inclusive, length 1600, is
still a candidate for the new permanent G minidisk; confirming
a VDEV does not, by itself, prove physical extent safety.

Host at the previous gate: Hercules PID 724, cwd
`/home/admin/vm630`, real 0123 -> `dasd1` FD12 and real
0127 -> `dasd5` FD16, config lines 33 and 37, respectively.

**NO DIRECTORY EDIT, DIRECTXA, LINK, ACCESS, FORMAT, OR M173 IMPORT
HAS OCCURRED.** Next safeguards before any change: independently
match the operator-reported completed EBS snapshot to its correct
source volume and region; retain a credible offline restoration
procedure, including CKD overlay dependencies; establish the
currency of `USER DIRECT C` against active directory entries and
review the entire nonoverlap/CP-reserved extent inventory; and
prepare a separately reviewed reversible one-MDISK directory
change with syntax-only `DIRECTXA ... (EDIT`. Do not execute a
non-EDIT DIRECTXA command or initialize any device at this gate.
IBM QUERY MDISK documentation:
https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-mdisk


### Next source-directory currency sample — read-only, not full proof

The `USER MDISKMAP C` report came from `USER DIRECT C` and
previous live `QUERY MDISK ... LOCATION` checks matched selected
source records. To compare the *permanent active CP directory*
rather than only currently linked devices, run from MAINT:

    CP QUERY MDISK 0190 LOCATION DIRECTORY
    CP QUERY MDISK 0191 LOCATION DIRECTORY
    CP QUERY MDISK 0193 LOCATION DIRECTORY
    CP QUERY MDISK 0401 LOCATION DIRECTORY

IBM QUERY MDISK permits LOCATION and DIRECTORY together in either
operand order. The sample source-map expectations, which must be
matched against the actual command results, are:

| MAINT VDEV | VOLSER | Real Rdev | Source start | Source length |
| --- | --- | --- | ---: | ---: |
| 0190 | M01RES | 0123 | 280 | 214 |
| 0191 | M01RES | 0123 | 494 | 175 |
| 0193 | M01RES | 0123 | 669 | 500 |
| 0401 | M01RES | 0123 | 1961 | 292 |

These queries expose device locations, not USER DIRECT passwords.
If any differ, **STOP** and investigate source currency/SSI context.
Even perfect agreement for this sample does **not** prove every
directory line matches the active binary directory or that the
proposed VMCOM1 physical range is free of all unrepresented uses.

The independent backup check is still required: in AWS
EC2 **Snapshots**, privately verify snapshot source EBS volume,
region, timestamp and `Completed` state, and retain a workable
offline restoration path for the original images/overlays.
No AWS identifiers or password-bearing directory text belong in
this public repo or a pasted diagnostic transcript.
IBM: https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-mdisk


## 2026-10-08 15:07 — active MAINT CP directory source sample: 4/4 PASS

Operator issued four **read-only** `CP QUERY MDISK vdev LOCATION DIRECTORY`
commands from MAINT. All four returned RC0 and matched the independently
generated `USER MDISKMAP C` report, including userid, owner, device type,
volume, real address, start and size:

| Tdev | TargetID | OwnerID/Odev | Dtype | Vol-ID/Rdev | Active start/size | Source-map start/size |
| --- | --- | --- | --- | --- | --- | --- |
| 0190 | MAINT | MAINT/0190 | 3390 | M01RES/0123 | 280 / 214 | 280 / 214 |
| 0191 | MAINT | MAINT/0191 | 3390 | M01RES/0123 | 494 / 175 | 494 / 175 |
| 0193 | MAINT | MAINT/0193 | 3390 | M01RES/0123 | 669 / 500 | 669 / 500 |
| 0401 | MAINT | MAINT/0401 | 3390 | M01RES/0123 | 1961 / 292 | 1961 / 292 |

Actual query completion times: 15:07:39, 15:07:40, 15:07:51,
and 15:07:52, respectively, all `Ready` without an error.
**PASS: 4/4 source-to-active sample matches.**

These are *permanent directory* reports rather than merely running
guest links. Together with the earlier three VMCOM1 live MDISK
location matches, they substantially improve confidence that the
MAINT `USER DIRECT C` source matches the current active directory.
They are **not** a comprehensive equivalence check of every
directory entry or SSI/subconfiguration variant, and do not
establish that no unrepresented MDISK/CP-reserved extent overlaps
the candidate VMCOM1 6000–7599 allocation.

**Preserve the current checkpoint:** No directory source edit, no
DIRECTXA activation, no new G disk, no LINK/ACCESS, no FORMAT,
and no M173CHK G execution. Proposed new MAINT `0600` virtual
address passed both virtual and directory absence checks.
Host PID724 FD12 / `dasd1` and FD16 / `dasd5` are corroborated.

### Remaining operator-controlled safety gate

Before modifying or compiling an altered `USER DIRECT` source:
1. Privately verify the already reported completed AWS root EBS
   snapshot's **account/region, source volume, state, date**,
   and image/overlay coverage; preserve a credible restore procedure.
   Do not repeat a snapshot merely because its ID was not shared here.
2. Establish how a saved, unchanged known-good `USER DIRECT C`
   can be recovered without overwriting protected CMS A/C data;
   confirm the active CP directory corresponds to the source
   sufficiently for a controlled one-MDISK change. If needed,
   use further nonmutating permanent-directory location reports.
3. Separately review a minimal one-line `MAINT MDISK 0600`
   source change for VMCOM1 cylinders 6000–7599 (1,600).
   Confirm the required directory permissions/access mode for
   the intended CMS disk. A source edit is NOT authorized by
   these four successful location queries.
4. IBM's `DIRECTXA filename filetype filemode (EDIT` is a
   **syntax-only test compile** (not directory activation);
   review the exact invocation and output locations for this
   installed system before considering it. **Never run the
   non-EDIT variant** during preflight. Do not FORMAT unless
   the independently verified new minidisk is later created,
   attached and exclusively identified by start/length/volume.

Official references:
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-mdisk
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-directxa
- https://www.ibm.com/docs/en/zvm/7.2.0?topic=directory-mdisk-statement


### Next targeted read-only VMCOM1 boundary comparison

To corroborate the source directory's **last allocated physical
minidisk immediately before** the candidate gap, from the
privileged MAINT CMS session query:

    CP QUERY MDISK USERID 6VMHCD20 0300 LOCATION DIRECTORY

Expected from the prior `USER MDISKMAP C`: owner
`6VMHCD20`, virtual `0300`, `3390 VMCOM1`, real
`0127`, `StartLoc 5756`, `Size 180`
(ending cylinder 5935). The map's next reported gap begins
at cylinder 5936 and runs through cylinder 10016.
A live active-directory mismatch, invalid syntax, or privilege
denial is **not** proof of nonoverlap; stop and reassess.
This is read-only and does **not** allocate, activate, link
or format the future 0600 MDISK. IBM confirms QUERY MDISK
supports the `USERID userid`, `LOCATION`, and
`DIRECTORY` operands:
https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-mdisk

This does **not** replace independently validating the correct
EBS snapshot/restore plan or final complete extent safety.


## 2026-10-08 15:11 — VMCOM1 final preceding MDISK: live directory PASS

The MAINT operator executed the documented *read-only* active
permanent-directory query:

    CP QUERY MDISK USERID 6VMHCD20 0300 LOCATION DIRECTORY
    TargetID Tdev OwnerID  Odev Dtype Vol-ID Rdev   StartLoc       Size
    6VMHCD20 0300 6VMHCD20 0300 3390  VMCOM1 0127       5756        180
    Ready; T=0.01/0.01 15:11:52

This **exactly matches** the `USER MDISKMAP C` source-directory
record for user `6VMHCD20` virtual `0300`: VMCOM1 real `0127`,
start `5756`, length `180`; inclusive end `5935`.
The mapped gap begins at `5936` and extends to `10016`;
candidate MAINT virtual `0600` on physical VMCOM1 `6000–7599`
lies entirely inside that report. The existing four M01RES
MAINT permanent-directory comparison rows also matched, and
`0600` was absent from both the instantiated virtual view and
the active MAINT CP permanent directory.

**Result: LIVE LEADING-BOUNDARY MATCH PASS.** This directly
corroborates the last mapped disk before the candidate gap,
but is not itself a full active-directory equivalence proof
or universal absence-of-overlap guarantee; the source map's
remaining unrepresented/full-pack/CP reservations and future
changes must still be considered before allocation.

**Hard stop unchanged:** operator-reported EBS snapshot completion
has not yet been independently correlated to correct source
volume, region, timestamp and `completed` state or a credible
restore procedure. Do not run `DIRECTXA` activation, write a
USER DIRECT replacement, LINK/ACCESS or FORMAT. No new G
minidisk exists and M173 has not been rerun.

Next operator step requires **no CMS modifications**:
privately inspect the existing EBS snapshot in the same AWS
account and Region as the Hercules root volume, confirm
`State=completed`, matching source volume and a usable
restore path. Keep identifiers out of the public repository.
Once the backup gate is attested, review a reversible, minimal
one-MDISK source change and syntax-only `DIRECTXA ... (EDIT`
before separately considering activation.


### Pre-activation access-mode review: do not blindly copy MR

The earlier non-executable illustration ended in `MR`, but IBM's
MDISK directory statement distinguishes **W (single-writer
exclusive write access)** from **MR (multiple-write with fallback
to read-only)**. This dedicated G staging disk has no documented
need for multiwriter access. Consider `W` as the safer planned
access mode, subject to exact installed-version semantics and
the site's existing MAINT directory policy. **Access mode is not
yet approved; the old illustrative MR line is NOT an instruction
to paste into USER DIRECT.** Confirm access restrictions, passwords,
links, SSI/subconfig implications and any full-pack interactions
in the privileged change review. Regardless of mode, the real
CMS admission gate is R/W, block size 4096, >=180000 free blocks.
IBM: https://www.ibm.com/docs/en/zvm/7.2.0?topic=directory-mdisk-statement


## 2026-10-08 — snapshot Completed/100% screenshot proof

AWS EC2 Snapshots console screenshot from operator visibly showed
one owned snapshot marked **Completed**, **100%**, original volume
**16 GiB**, displayed full snapshot size **10.66 GiB**, started
**2026/10/08 14:10 GMT-5**. Description begins with
`ibm-sandbox-pre-M173` but was truncated. This **upgrades the
snapshot completion-status evidence from operator report to
VISUALLY CONFIRMED**. Do not disclose its snapshot ID in this
public repository.

The screenshot does **NOT** show snapshot source Volume ID, Region,
account or root-device attachment, and no isolated restoration
or recovery test has been performed. These remain unverified,
so the privileged directory activation / G FORMAT hard stop
**remains**. The operator's next action is read-only AWS console
verification of the snapshot's source Volume ID and Region versus
the Hercules EC2 instance's attached root EBS volume, followed by
review of the recovery path. No additional CMS CP commands are
required for this AWS identity step. No new 0600 minidisk exists.


## 2026-10-08 — EBS source/Region match and recovery procedure attested

The user explicitly confirmed that the completed snapshot's
**source volume and Region match** the Hercules EC2 instance root
EBS volume and that the **recovery procedure is understood**.
The earlier AWS screenshot independently showed snapshot
`Completed`, `100%` progress, 16 GiB source volume.
**PROVENANCE: OPERATOR VERIFIED**. A separate isolated
restoration test has NOT been performed; do not elevate this
operator attestation to a demonstrated guest-level restore.

The prior snapshot-provenance stop condition is now satisfied
as operator attestation, so advance to **source-directory
preparation**, not activation/formatting. The new staged and
collision-safe runbook is
`docs/M173_DIRECTORY_CHANGE_PLAN.md`. Its immediate gate
is purely read-only: `QUERY DISK C`, `STATE USER DIRECT C`,
`STATE M173BAK DIRECT C`, `STATE M173NEW DIRECT C`,
`STATE M173NEW MDISKMAP C`, and
`CP QUERY MDISK 0600 DIRECTORY`.
Do NOT copy anything until the intended new filenames are
absent (RC28), the original is present, and C is R/W with
ample free 4K blocks. A verified source copy and a
candidate-only `DIRECTXA M173NEW DIRECT C (EDIT` gate will
precede any separate authorization for online activation.
This does **not** prove all active directory extent mappings
or grant permission to format A, C or an uncertain device.

## 2026-10-08 16:20 — M173 DIRECTXA EDIT syntax-only SUCCESS

Actual target, MAINT CMS: `STATE DIRECTXA MODULE *` Ready RC0
16:20:11; `DIRECTXA M173NEW DIRECT C (EDIT` displayed
`z/VM USER DIRECTORY CREATION PROGRAM - VERSION 6 RELEASE 3.0`
and `EOJ DIRECTORY NOT UPDATED`, then Ready RC0 at
16:20:21. No errors. **Candidate syntax compiled, Gate 4
PASS on live installed z/VM 6.3**. Earlier M173DCHK
confirmed precisely one new 600/0600 disk in MAINT-1,
source/backup identity, and no other directory changes.
**Active CP directory STILL UNCHANGED.**

Proceed only with Gate 5 READ-ONLY queries as defined in
`docs/M173_DIRECTORY_CHANGE_PLAN.md`. Need independent
CP CPOWNED/ALLOC extent evidence and a precise rollback
procedure before attempting anything without DIRECTXA EDIT.
IBM notes a non-EDIT compile writes an alternate directory
and changes the CP-owned volume-label pointer, potentially
putting a directory online immediately. The old directory
source backup is protected, but activation/rollback require
separately authorized privileged changes. The EBS source
and region were operator-matched; a guest restore is untested.
Do not LINK/ACCESS/FORMAT, change User DIRECT/MAINT-1 source,
activate CP directory, or run M173 import at this gate.

## 2026-10-08 16:32 — M173 Gate 5b rollback EDIT and DIRMAP PASS

Live target rollback syntax check:
`DIRECTXA M173BAK DIRECT C (EDIT` returned
z/VM directory utility v6r3,
`EOJ DIRECTORY NOT UPDATED` and RC0 16:31:49.
Next `STATE M173NEW MDISKMAP C` confirmed destination
absent RC28; `DIRMAP M173NEW DIRECT C C` completed with
source read and candidate map written without errors
at 16:32:10. Candidate map: F100 394 records,
10 blocks, C1; previous original USER MDISKMAP C
was F100 392 records. `QUERY DISK C`:
MNT2CC C R/W 10 cylinders 4096 bytes/block,
298 used/1502 free of 1800, eight files.

**No CP directory activation**. This is a prospective
source-derived map, not a proof of active or hidden
allocations. Next inspect the VMCOM1 group including
the MAINT-1 600/0600 extent 6000-7599 and
neighboring free-gap boundaries privately.
Canonical instructions are at the TOP of
`docs/M173_DIRECTORY_CHANGE_PLAN.md`.
Do not initialize/format any existing device or
run Git M173 until active directory activation
and independently verified newly-created G disk.
