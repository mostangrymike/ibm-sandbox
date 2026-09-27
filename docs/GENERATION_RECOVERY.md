# GEN2 candidate-generation seal and restart validation

## Status and safety boundary

The canonical 1,808-object GITFIX stage, IDX2 index, and SIDX2
seek index have each passed complete real-CMS readback and hash
verification. GITCIDX SFAST and PAIR also passed on the target
with every saved seek position reconciled against the actual
unchanged staging file.

New `GITCIDX GENWRITE` and `GENCHECK` are **host-tested only**.
They provide a candidate-generation **completion manifest**, not
an atomic CMS object-store transaction or an active-generation
pointer. No code changes or truncates the existing stage/index/seek
files. A manifest must be written to a *new* candidate filename,
not over a previously verified active generation.

`GENWRITE` first runs PAIR (full independent stage readback,
canonical SHA verification and IDX2/SIDX2 metadata/cookie matching).
Only after this passes does it write the separate GEN2 manifest
through FILEDEF `GENOUT`. Its record grammar is:

```text
GEN2 1808 1808
DIGEST <40 uppercase hex bytes>
MINOID <40 uppercase hex bytes>
MAXOID <40 uppercase hex bytes>
GEND2 1808 1808
```

The unique count is derived rather than assumed; `1808` is the
currently verified real-PACK value. The digest binds every
**sorted** canonical OID plus its object ordinal, type, size,
and saved seek-position cookie. Each descriptor is encoded as
20 raw OID bytes, 2-byte big-endian ordinal, 1-byte type,
4-byte big-endian length, and 4-byte big-endian cookie.
Canonical Git blob hashing over these concatenated metadata bytes
generates the 40-character DIGEST. All records fit LRECL 80.
No CMS-native EBCDIC type/decimal header enters that hash.

`GENCHECK` must reject an absent, truncated, malformed, legacy
or extra-record manifest. It independently reopens all three
candidate data files, runs the complete paired canonical content
audit, recomputes the deterministic descriptor digest, and requires
matching unique count, min/max OID, and digest. The final GEND2
record detects incomplete manifest writes. A changed stage,
inconsistent index, altered cookie or mismatched manifest fails
closed.

Host CI passed synthetic 1,808-object sealing and reopening,
deliberate header corruption, truncated-manifest rejection,
restoration, corrupt staged body and mismatched seek descriptor:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36282365907 .
This is not yet CMS compilation or cross-logon/reboot evidence.

## Isolated CMS gate

The canonical GITFIX STAGE/INDEX/SEEK files are unchanged;
do not rerun the saved PACK or rewrite either index.

On the Mac, in `/Users/mikewommack/ibm-sandbox/src`:

```sh
git pull
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/GITCIDX.C
```

On CMS, compile before FILEDEFs and choose a **new manifest**
file `GITFIX GEN A`, rather than replacing any old generation:

```text
CMSCLNK GITCIDX PLAIN
FILEDEF STGIN DISK GITFIX STAGE A
FILEDEF IDXIN DISK GITFIX INDEX A
FILEDEF FIDXIN DISK GITFIX SEEK A
FILEDEF GENOUT DISK GITFIX GEN A (RECFM V LRECL 80
FILEDEF GENIN DISK GITFIX GEN A
GITCIDX GENWRITE
GITCIDX GENCHECK
```

These operations are intentionally redundant:
GENWRITE hashes every staged body via PAIR before writing
the manifest, and GENCHECK reopens everything and does so again.
Both must return RC 0 and report:

```text
FAST AUDIT VERIFIED 1808 UNIQUE 1808
PAIR VERIFIED UNIQUE 1808
GENERATION SEALED 1808 UNIQUE 1808
GENERATION VERIFIED 1808 UNIQUE 1808
```

To prove *cross-logon* persistence later, log off and back on,
reaccess A and rebind STGIN, IDXIN, FIDXIN and GENIN to the
same existing GITFIX files. Re-run only `GITCIDX GENCHECK`;
do not rewrite the manifest. For a reboot test, repeat after
an authorized system restart, not as part of this initial gate.
The manifest intentionally binds saved ftell cookies, so moving
or rewriting the stage can invalidate the seek index even when
the content OIDs remain unchanged. Rebuild/verify a **new**
candidate generation instead of overwriting an attested one.

## Remaining transaction work

GEN2 is a completion proof for one unmodified candidate dataset,
not an atomic multi-file rename, lock, active-generation selector,
concurrent writer protocol or automatic rollback. Those need
separate design and recovery tests before claiming a durable
transactional Git object database. GitHub issue #2 remains open.
