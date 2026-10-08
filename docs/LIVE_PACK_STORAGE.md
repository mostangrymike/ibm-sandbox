# Live PACK stage and index storage after the full A-disk incident

## Verified 2026-10-08 CMS evidence

The CMS MAINT A minidisk is virtual 0191, MNT191, 175 cylinders, 3390,
4 KiB block size, total 31,500 blocks. The M173 generalized stage file
M173NET STAGE A grew to 1,193,994 records and 19,213 blocks before disk
exhaustion/abend; a separate GITPIMP VERIFY 7736 independently verified
objects 1-2624, then failed at object 2625. This stage was **not** a
verified complete generation and was unsuitable for M174.

After the operator executed the exact-file ERASE M173NET STAGE A, CMS
QUERY DISK reported MNT191 with 298 files, 12,229 used and **19,271
free** blocks. The 75 MiB class failed stage was reclaimed. GITFIX,
M15NEW, historical PACK and the retained M171NET PACK/META were not
targets of this cleanup.

The retained input is M171NET PACK A, 2,171,129 bytes, PACK v2,
7,736 objects, SHA1 A705122BC39A3383BC05ABC6C888A1F788B1D067.
M172's independent target census counted 2,432 ordinary, 5,304 OFS,
and zero REF deltas. No M173 real CMS import pass has yet occurred.

## Target layout and safety

A contains existing EXEC/MODULE code, sealed fixtures, and the
M171NET PACK/META. Do **not** place the new generalized M173 stage
on A. The M173 and M174 generated objects belong on a separately
provisioned persistent writable CMS disk, accessed for example as
filemode G. The generalized stages are named M173NET STAGE G and
M174NET INDEX G. M175 and M176 read those artifacts on G, while
M171NET META A stays on the original A disk.

M173CHK, M174CHK, M175CHK, and M176CHK take a mandatory single
non-A CMS filemode letter as their only argument; the new target
checks refuse A or an omitted/malformed argument. M173CHK uses the
native GITPIMP IMPORT CHECKED with its own OBJOUT FILEDEF; M174CHK
uses native GITPIDX BUILD CHECKED with its own IDXOUT FILEDEF.
Both retain CMS STATE RC28 absence protection.

A new M173 run additionally uses CMS QUERY DISK to validate that
the requested filemode is accessed R/W with at least 180,000
4-KiB blocks free (about 703 MiB). This is a *minimum admission
threshold*, not a guarantee about the final stage size; a fresh
1 GiB (or larger) minidisk is a sensible target if supported by
the actual physical storage. M174 requires at least 4,096 blocks
free when building its index on the same disk. The two read-only
M175/M176 gates accept the same explicit data filemode.

C has only 1,694 free blocks and F only 2,052. Other accessed CMS
disks in the reported inventory are R/O. None is a suitable
target for this stage.

## Disk provisioning boundary

Do not assume free unallocated cylinders exist on M01RES, MNT191,
or any of the other actual volumes; their file sizes and CP MDISK
directory allocations are distinct from the CMS free-block count.
Earlier forensic mapping identified MAINT virtual 0191 as real
Rdev 0123, volume M01RES, start cylinder 494, 175 cylinders,
backed by the running Hercules real 0123 dasd1 image under
/home/admin/vm630. This mapping must not be mistaken for a free
allocation range. The September 27 TRKDE 4 allocation-map error
is still a reason to keep a verified independent backup.

Read-only inventory before disk definition:

    CP QUERY VIRTUAL DASD
    CP QUERY MDISK 191 LOCATION
    QUERY DISK

An administrator must inventory all existing allocations on the
proposed CKD real volume(s), their extents and free capacity;
identify an unused virtual device address, correctly reserve the
minidisk in the CP directory (or via authorized DirMaint AMDISK);
verify the underlying Hercules 3390 image and available host
storage; and take an independent backup/snapshot as appropriate.
Do NOT run FORMAT on any existing or uncertain virtual minidisk.
If a *newly allocated* persistent disk has been verified as safe
to initialize, use the version-appropriate IBM CMS FORMAT and
ACCESS procedures with 4 KiB blocks. Avoid any automatic
formatting of virtual device 192 because CMS has special
auto-access behavior for that address.

After a new disk is mounted as G, verify with:

    QUERY DISK G

It must say G and R/W, with at least 180,000 BLKS LEFT before
M173CHK can proceed.

Once a properly sized G exists, on Mac from ibm-sandbox/src:

    git pull
    ./cms-upload.sh M173CHK.EXEC M174CHK.EXEC
    ./cms-upload.sh M175CHK.EXEC M176CHK.EXEC

On CMS, after QUERY DISK G confirms capacity and read/write mode:

    M173CHK G

If and only if M173 passes and retains M173NET STAGE G, build the
M174 GITPIDX module (CMSCLNK GITPIDX PLAIN) before M174CHK G.
Likewise build GITPCAT and GITPTRE per their own PLAIN build
contracts before M175CHK G and M176CHK G. The source of truth
for native module linkage is CMSCLNK and each milestone doc.

Do not rerun M173CHK with no argument or against A. No new
network PACK download is required.
