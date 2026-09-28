# M38: single-audit read-only link validation batch

## Why

The actual z/VM CMS M37 compact regression on September 28, 2026
passed in 693.54 CPU / 708.96 elapsed seconds. Three individual
successful M35/M36/M37 commands each independently ran a complete
native GEN2 verification, even though depth-two success proves
the shallower checks for the same selected immutable generation.
This repeated audit work motivates a narrower native interface.

## LINKBATCH

`GITREC LINKBATCH C0NAME C1NAME COMMIT_OID40` performs exactly
one usual fail-closed selector choice. Each candidate still undergoes
the complete native GENCHECK (including staged-body SHA-1, IDX2 and
SIDX2 pairing, seek cookies and GEN2 seal). After a candidate passes,
the command validates the supplied child commit and every parent
commit (maximum 16), all associated root trees and all locally
referenced root links through depth two within that same generation.
The existing bounded walker enforces 256 links per visited tree and
a shared 1,024-tree visit budget. Gitlinks point into external
repositories and remain excluded from local object resolution.

Only on *complete* success, the command emits three markers:
```
NESTED ROOT LINKS VERIFIED
DEEP ROOT LINKS VERIFIED
LINK DEPTH 2 VERIFIED
```
It then emits the usual framed complete parent list. A missing
object returns RC4; wrong type, malformed structure, failed hash
or exceeded limits return RC8. No partial success markers or parent
lists on failure. The prior ROOTLINKS, NESTLINKS, DEEPLINKS and
DEPTHLINKS commands are unchanged and remain independently
regression-tested on the host.

The command does NOT make a pointer active, write or alter a
generation, establish reboot durability, or implement atomic
promotion or locking.

## Existing proof and outstanding proof

M35, M36 and M37 have all passed actual CMS compilation and the
standard M37 one-page gate. M38 adds a performance-oriented
single-audit batch. The native integration test includes valid
deep links, missing/wrong-type deep links, bad child OIDs, older
generation recovery, both-generation rejection and restored newer
selection. Check actual GitHub Actions CI before describing M38
as host-proven; it has not yet been tested on actual CMS.

## Next safe target gate

On the Mac from `ibm-sandbox/src`:
```sh
git pull
./cms-upload.sh GITREC.C
./cms-upload.sh GITRUN.EXEC
```
On CMS:
```text
CMSCLNK GITREC PLAIN
GITRUN
```
Use only the standard in-memory, one-page compact runner.
M38 keeps both independent original GITFIX/M15NEW 1,808-object
audits and explicit selector selection. It replaces three
separate successful depth-two-or-shallower GITREC checks with one
LINKBATCH. Negative depth, noncommit and missing child checks,
older recovery, both-invalid fail-closed, restored newer selection
and final original STATE checks remain.

Expected final marker, only if every check succeeds:
```
GITRUN M38 ALL READ ONLY NATIVE GIT TESTS PASSED
```

The original GITFIX/M15NEW STAGE, INDEX, SEEK and GEN files,
selector PTRs, and GITPBUF PACK remain protected and read-only.
Only upload GITREC.C and the standard GITRUN.EXEC; the other
native programs do not change.

## M39: skip redundant subtree reads during recursive validation

After M38, the depth-aware walker still read, rehashed and
parsed a referenced subtree as a direct entry, then read,
rehashed and parsed the same subtree again when descending.
At any positive remaining depth, M39 skips the first
redundant body read for tree entries. The existing recursive
call still independently resolves the indexed OID, validates
the exact tree type, rehashes the body, parses its entire Git
binary tree structure and checks every requested descendant.
Every blob is still validated at its original level; at
depth zero every referenced subtree is still validated.
The per-tree 256-entry and shared 1,024-tree budgets and
fail-closed return codes remain unchanged.

The host integration additionally tests missing and wrong-type
linked objects in a nested child tree, corruption in a merge
parent's tree, and the 257-entry root limit, with no partial
success markers or metadata. Native host CI passed on
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36482019995
and M39's implementation was squash-merged to main at
`a359c9c4f72486bf2b69454286d83b1b57123419`.

M39's first real CMS gate is the standard M39-labelled
GITRUN, which also serves as the first actual M38 LINKBATCH
target proof. No separate M38 target run is needed if M39
passes. Use the same two Mac uploads and two CMS commands
above; successful final marker becomes:

```
GITRUN M39 ALL READ ONLY NATIVE GIT TESTS PASSED
```

Do not infer a target performance improvement before
the actual M39 CMS timing. Existing real target proof ends
at M37 until the operator runs this new combined gate.
