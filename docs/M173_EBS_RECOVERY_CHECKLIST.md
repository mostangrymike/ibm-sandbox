# M173 EC2 / EBS recovery checkpoint and safe change boundary

Status as of 2026-10-08 (AWS console screenshot): **SNAPSHOT COMPLETION REPORTED AND STATUS COMPLETED/100% VISUALLY CONFIRMED; source-volume match, account/Region and a restoration test not yet independently verified. NO NEW CMS DISK CREATED.**

This document records a human-controlled recovery-point procedure for the Hercules / z/VM environment before any `DIRECTXA`, `MDISK`, or `FORMAT` affecting the proposed M173 stage disk. It does **not** authorize automatic cloud, directory, or disk changes.

## Identified hardware and data

| Item | Verified observation |
| --- | --- |
| Linux EC2 host | Verified EC2 host (private identifier omitted) |
| Host root block device | `/dev/nvme0n1p1` |
| EBS volume serial | Observed NVMe EBS volume serial; identifier omitted from public documentation |
| AWS volume ID | **Privately verified from live NVMe serial and EBS by-id link** |
| Volume size | 16 GiB |
| Host filesystem availability (last observation) | 6.1 GiB |
| Hercules process at verification | PID `7174`, cwd `/home/admin/vm630` |
| Hercules VMCOM1 real device | `0127 3390 dasd5`, live FD 16 |
| VMCOM1 live backing image | `/home/admin/vm630/dasd5`, ~1.9 GiB |
| M01RES backing image | historically `/home/admin/vm630/dasd1`; recheck live PID FD/config |
| Proposed **unallocated** MDISK | VMCOM1 real 0127, cylinders 6000–7599 inclusive, 1600 cylinders |
| Underlying evidence | DIRMAP `USER MDISKMAP C` gap VMCOM1 5936–10016; live CP DASD DETAILS 0127 = 11000 cylinders |
| Live CP cross-checks | MAINT 02CC (start121, len10); 049E (start4104, len250); 0551 (start572, len40): all match DIRMAP |
| Source CP directory | `USER DIRECT C` on MAINT's 02CC; 4282 F80 records; full active-directory equivalence still not established |
| DirMaint | Not operational: `XAUTOLOG DIRMAINT` logged off immediately; DIRM USEDEXT/FREEXT lacked WHERETO DATADVH |

The NVMe serial, `lsblk SERIAL`, and `/dev/disk/by-id/nvme-Amazon_Elastic_Block_Store_<SERIAL>` corroborate EBS identity. The hyphen in the AWS ID is required when using AWS console/API. Do not infer the AWS **Region** or **instance ID** from the hostname or volume serial.

## 1. Identify AWS region, instance, and attachments (read-only)

In the AWS EC2 console, select the correct account and region, then open **Elastic Block Store → Volumes** and find the privately verified EBS volume. Verify its attachment, device, instance ID, state, and encryption. Confirm that it is the root volume of the intended Hercules EC2 instance. Record the AWS account ID, region, instance ID, and Availability Zone privately.

If AWS CLI is already installed, authorized and correctly configured in the operator's local environment, these are optional **read-only** equivalents (specify the actually verified region):

```sh
aws sts get-caller-identity
# Set EBS_VOLUME_ID privately from the verified NVMe serial (format vol-...)
# Set REGION privately from the AWS EC2 console or CLI configuration
aws ec2 describe-volumes --region REGION --volume-ids "$EBS_VOLUME_ID" \
  --query 'Volumes[0].{ID:VolumeId,AZ:AvailabilityZone,Size:Size,State:State,Encrypted:Encrypted,Attachments:Attachments}' --output json
```

Do not install AWS credentials into CMS, the GitHub repository, or a Hercules configuration file.

Before a quiescence attempt, confirm that BOTH VMCOM1 and M01RES active image files plus any shadow/overlay data are covered by the identified volume. On the Linux Hercules host (read-only):

```sh
readlink -f /proc/7174/cwd
grep -nE '^[[:space:]]*012(3|7)[[:space:]]+3390' /home/admin/vm630/hercules.cnf
ls -l /proc/7174/fd | grep -E '(/home/admin/vm630/dasd1|/home/admin/vm630/dasd5)'
findmnt -no SOURCE,TARGET,FSTYPE /home/admin/vm630
```

PID `7174` is historical observation as soon as Hercules restarts: re-obtain actual PID and inspect its FD table. Verify overlays, INCLUDEs, and dynamically attached CKD devices; this check by itself is not a complete inventory of every file Hercules may use.

## 2. Plan a consistent root EBS snapshot

1. Preserve the current CMS console work: complete commands, close active transfers, log off guest users as appropriate, and follow the site-approved z/VM orderly shutdown procedure. Do not improvise a CP system shutdown or interrupt active guest writes.
2. Stop Hercules cleanly and confirm its process and writable CKD images are closed. Record the means to restart Hercules and its guest IPL and terminal access after EC2 resumes.
3. In **EC2 → Instances**, select the verified instance and choose **Instance state → Stop instance** with normal OS shutdown; **do not** select Force/Skip OS shutdown. Wait for the **stopped** state. Stopping the EC2 instance can change its automatically assigned **public IPv4 address** unless an Elastic IP is in use; the private IP and EBS volume persist. Ensure an access/reconnect route before proceeding.
4. In **EC2 → Elastic Block Store → Volumes**, select the privately verified EBS root volume and choose **Actions → Create snapshot** (or **Snapshots → Create snapshot**, resource type **Volume**, correct volume ID). Give it a descriptive name/description, e.g. `ibm-sandbox-pre-M173-2026-10-08`. This is a billable AWS storage operation.
5. Record the returned `snap-...` ID, verified **account**, **region**, **source volume**, snapshot **start time**, and any snapshot tags. Wait for **State: Completed** and check for errors. AWS documents that snapshot creation is asynchronous; when a snapshot enters the pending state, it is not yet a verified completed recovery artifact.
6. Verify the intended restoration path: from the snapshot, **Create volume** in the required EC2 Availability Zone; create a new test volume rather than replacing the live root volume, and test mount/read access on a separate recovery instance when practicable. Record image paths, CKD metadata dependencies, and their versions. A snapshot state of `completed` alone is **not** a demonstrated guest-level restore test.
7. Only after snapshot completion and a credible restoration test/procedure, start the original instance and verify SSH connectivity, the possibly changed public address, Hercules process/cwd/CKD FDs, CMS IPL, and retained M171NET PACK/META and sealed generations. Re-evaluate gap safety before activating any modified CP directory.

**Never snapshot the live writable CKD image and assume full guest consistency without quiescing guest/Hercules I/O.** AWS explicitly recommends stopping an EC2 instance before snapshotting its **root** EBS volume; a live snapshot only captures already-written blocks, not memory or unflushed caches.

## 3. Confirm snapshot status without changing AWS data

In the AWS **EC2 → Snapshots** page, filter by snapshot ID and look for **Completed**, the source volume ID, and region.

Optional AWS CLI read-only confirmation:

```sh
aws ec2 describe-snapshots --region REGION --snapshot-ids SNAPSHOT_ID \
  --query 'Snapshots[0].{ID:SnapshotId,Volume:VolumeId,State:State,Started:StartTime,Progress:Progress}' --output json
```

Supply the real snapshot ID and verified region; do not publish AWS tokens/credentials. If the result does not show source volume `<verified-EBS-volume-ID>` and completed state, **STOP**.

## 4. Safe post-backup gate for M173

With independent recovery proven, recheck all live extents and select a *currently unused* virtual 4-hex-digit MAINT device, then create a reviewed, reversible CP directory change for **only** a new MAINT MDISK on **VMCOM1** real cylinders **6000–7599**, length 1600. DirMaint is offline, so do not use `DIRM AMDISK` or blindly run non-EDIT `DIRECTXA USER DIRECT C`. Full directory activation needs a separate verified rollback plan and user-specified authorization.

**Never format existing** MAINT A 0191, C 02CC, fullpack 0127 or M01RES. The M173 regression requires G to be an independent R/W CMS minidisk with 4096-byte blocks and ≥180,000 free blocks. Use target-side `M173CHK G` only after the new independent G disk is correctly defined, exclusively accessible, and initialized.

## AWS references

- [Create an EBS snapshot](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-create-snapshot.html)
- [EBS snapshot consistency and root-device stop recommendation](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-creating-snapshot.html)
- [Stop and start EC2 instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Stop_Start.html)
- [Public IP changes and persistent EBS/private IP on stop/start](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/how-ec2-instance-stop-start-works.html)


## Operator update — snapshot completion reported

On 2026-10-08, the operator reported **"snapshot is complete"**.
This means a snapshot is now reported as completed; it is
**not** yet independently checked here against the AWS
volume ID, region, creation timestamp, and `State:
Completed`, and no isolated restoration test has
been reported. Do not create a second snapshot merely
because this document once said no snapshot was
recorded. Preserve the snapshot and record its
metadata privately.

Next, verify in **EC2 → Snapshots** that the snapshot
belongs to the previously identified root EBS volume
and is `Completed`, and preserve its identifier and
restore steps. The operator should start EC2 normally
if it remains stopped, confirm the new public IP if
needed, and **before any directory update** verify
Hercules/guest startup and existing protected Git
files. The cloud snapshot step is separate from any
z/VM `DIRECTXA` or new CMS `FORMAT` command.

### First post-snapshot checks (read-only)

On the running Linux host, after reconnecting:

```sh
pgrep -af '[h]ercules'
df -h /home/admin/vm630
ls -l /home/admin/vm630/dasd1 /home/admin/vm630/dasd5
```

On the MAINT CMS session (after z/VM is back):

```text
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
```

Once those pass, inspect an unused MAINT virtual
address before choosing a new permanent `MDISK`.
One possible candidate is virtual `0600` (**not
yet verified free**). Do not confuse the hexadecimal
virtual number with the decimal real start cylinder
6000.

```text
CP QUERY VIRTUAL 0600
CP QUERY MDISK 0600 DIRECTORY
```

A not-found response for either query alone is not
proof of free volume cylinders; both address checks
and the verified DIRMAP gap are separate obligations.
Do not access or format `0600` until a newly added
permanent MDISK definition is properly reviewed,
activated, and proven to resolve to `VMCOM1`
start 6000, size 1600.

A cautious, later administrative change will be
to add **only one new MAINT MDISK statement**;
a format-independent illustration (not a command
to run now):

```text
MDISK <VERIFIED_UNUSED_VDEV> 3390 6000 1600 VMCOM1 MR
```

Ensure that edit is in the correct `USER MAINT`
directory stanza. Keep old `USER DIRECT C`
and active CP directory recovery paths available.
A modified directory should first be syntax-
checked with `DIRECTXA ... (EDIT` using a
properly accessed correct-release utility and
only promoted after a separately reviewed
activation/rollback procedure. IBM states the
`EDIT` option validates syntax without putting
a new directory online. CP's directory update
without `EDIT` can change the active directory,
so it is not part of this preflight.

IBM:
https://www.ibm.com/docs/en/zvm/7.2.0?topic=utilities-directxa
https://www.ibm.com/docs/en/zvm/7.2.0?topic=directory-mdisk-statement


## Confirmed query syntax correction (2026-10-08)

`CP QUERY VIRTUAL 0600` returned HCPQVD040E (no virtual device).
The obsolete command with `MAINT` before `0600` returned HCPQMD022E,
which is a **syntax error**, not evidence about the CP directory.
The verified read-only command from MAINT is
`CP QUERY MDISK 0600 DIRECTORY`; wait for its response before any
new directory entry. Hercules PID 724 and FDs 12 (`dasd1`) / 16
(`dasd5`) now corroborate the active image configuration.
IBM: https://www.ibm.com/docs/en/zvm/7.2.0?topic=commands-query-mdisk


## 2026-10-08 15:01 — VDEV 0600 validation result

On the logged-on MAINT CMS session, both queries completed with
**device absent**, not a syntax error:

    CP QUERY VIRTUAL 0600
    HCPQVD040E Device 0600 does not exist

    CP QUERY MDISK 0600 DIRECTORY
    HCPQMD040E Device 0600 does not exist

Thus the candidate 0600 virtual address is currently unused both
in MAINT's active virtual configuration and permanent directory.
This confirms only *virtual address* availability; the independent
VMCOM1 mapped-gap evidence remains the separate physical extent
case. Check again if the directory or guest configuration changes.

Status remains: operator-reported EBS snapshot completed, but the
snapshot's source volume, region, Completed metadata and restoration
plan have **not been independently attested in this conversation**.
There is still no new G minidisk and no directory activation,
LINK/ACCESS, FORMAT or M173 execution. Perform AWS snapshot
provenance/recovery checks and source-directory/rollback review
before any privileged disk change.


## 2026-10-08 15:07 — post-snapshot permanent-directory comparison

Four MAINT `QUERY MDISK ... LOCATION DIRECTORY` live results
matched `USER MDISKMAP C` exactly: M01RES real 0123;
VDEV 0190 start280 size214; 0191 start494 size175;
0193 start669 size500; 0401 start1961 size292.
All returned Ready. This strengthens, but does not fully prove,
the currency of the `USER DIRECT C` directory source.
The new MAINT virtual 0600 remains absent from active and permanent
views. **No new G disk or changed directory**.

The EBS snapshot remains **operator-reported complete**, not
independently validated against region/source volume/completed state
or a credible restoration path in this conversation. These checks
are still a HARD STOP before live directory activation or FORMAT.
Do not place private AWS IDs or unredacted USER DIRECT records here.


## 2026-10-08 15:11 — LIVE VMCOM1 preceding boundary matches source

Actual MAINT read-only `CP QUERY MDISK USERID 6VMHCD20 0300 LOCATION
DIRECTORY` returned `6VMHCD20 0300 6VMHCD20 0300 3390 VMCOM1
0127 5756 180` with `Ready` at 15:11:52. Exact match against
`USER MDISKMAP C`; occupied cylinders end at 5935 and the
reported physical gap begins at 5936. Candidate VMCOM1 real
0127 cylinders 6000–7599 remains completely inside that
reported gap. The 0600 virtual/directory absence checks and
four M01RES permanent-directory matches previously passed.

**No G disk, source edit, directory activation, LINK, ACCESS,
FORMAT or M173 execution.** The existing EBS snapshot is still
reported complete by the operator but not independently
verified for *the correct original root volume, region, completed
state and recoverability*. Keep that gate closed.

Optional AWS CLI **read-only** confirmation (run only with
already-configured AWS credentials and with IDs kept private):

```sh
# Populate these locally from the verified AWS console; do not post them.
# AWS_REGION=...
# EBS_SNAPSHOT_ID=...
aws ec2 describe-snapshots --region "$AWS_REGION" \
  --snapshot-ids "$EBS_SNAPSHOT_ID" \
  --query 'Snapshots[0].{State:State,SourceVolume:VolumeId,Created:StartTime,SizeGiB:VolumeSize,Progress:Progress}' \
  --output json
```

The operator must **compare SourceVolume privately** against
the previously verified Hercules host root EBS volume, and
establish how to create/attach a recovery volume in the proper
Availability Zone. A `completed` state alone is not a
tested guest-level recovery. If metadata or restoration
procedure is uncertain, stop; do not create another snapshot
or overwrite the source merely to advance this checkpoint.
Official AWS documentation:
https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-snapshots.html


## 2026-10-08 — AWS screenshot independently confirms snapshot completion

The operator supplied a screenshot of AWS EC2 **Snapshots** with
snapshot scope **Owned by me** and one listed snapshot. The visible
fields establish the following **snapshot lifecycle facts**:

| Field | Screenshot observation |
| --- | --- |
| Snapshot status | **Completed** |
| Progress | **100%** |
| Snapshot storage tier | Standard |
| Original volume size | **16 GiB** |
| Full snapshot size (AWS display) | **10.66 GiB** |
| Started (console display) | **2026/10/08 14:10 GMT-5** |
| Encryption | Not encrypted |
| Description | Begins with `ibm-sandbox-pre-M173` (truncated in view) |

**SNAPSHOT COMPLETION UI GATE PASS.** A screenshot confirms the
listed snapshot's status, not the source EBS volume or recovery
correctness. **The snapshot's Volume ID, AWS Region, account
identity, root-volume attachment, and restoration test are NOT
visible in the supplied screenshot.** The account/region/source
match is therefore **PENDING**, not PASS. Keep the snapshot ID
and any AWS identifiers out of this public document and do not
commit the screenshot itself.

### Next read-only console checks, no guest operations

1. In **EC2 → Snapshots**, select the completed snapshot and open
   the snapshot **Details** area. Read the **Volume ID** for the
   original source and confirm the actual Region in the console
   Region selector; do not infer either from the snapshot's name.
2. Under **EC2 → Instances**, select the Hercules instance and
   inspect its **Storage** tab to identify the current root EBS
   volume (or follow that attachment under **EC2 → Volumes**).
   Privately compare the root volume ID with the snapshot source
   Volume ID, and confirm the correct account and Region.
3. Retain an actual recovery procedure: create an EBS volume **from
   this snapshot** in the same Availability Zone as a separate
   recovery instance, attach and inspect it without touching the
   running Hercules host. Actual restore verification is **not
   yet performed**. AWS notes the volume and receiving instance
   must share an Availability Zone. See
   https://docs.aws.amazon.com/ebs/latest/userguide/ebs-creating-volume.html

**NO new G disk, USER DIRECT edit, DIRECTXA activation, LINK,
ACCESS, FORMAT or M173 run is authorized by this screenshot.**


## 2026-10-08 — operator attests correct EBS source/Region and recovery steps

After the AWS console screenshot had established `Completed` and `100%`,
the operator explicitly confirmed: **"Source volume and region match;
recovery procedure understood."** This is an operator-performed
independent check that the completed snapshot's source Volume ID and
AWS Region agree with the Hercules EC2 root volume. No AWS identifiers
are recorded in this public repository.

**Recovery provenance gate: OPERATOR VERIFIED.**
This does **not** assert an isolated restore test or certify the
complete guest-level consistency of every CKD image/overlay; those
were not tested independently. No new G minidisk or directory edit,
activation, LINK, ACCESS, FORMAT or M173 execution has taken place.

Next phase is preparation only. See
`docs/M173_DIRECTORY_CHANGE_PLAN.md` for a staged, collision-safe
source-directory backup and candidate-only test workflow.
Before authorizing any privileged change, keep `USER DIRECT C`
unmodified, create separately named backups only after confirming
their target filenames are absent, and use `DIRECTXA ... (EDIT`
rather than activation for initial syntax validation.
