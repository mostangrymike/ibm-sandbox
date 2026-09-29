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

## M40: atomic path metadata for terminal directories

The M39 read-only tree walk is target-proven. A separate
path-walking edge case remained: PATH could return a canonical,
correctly typed but structurally malformed *terminal* subtree;
LSDIR printed PATH OBJECT TYPE and OID before checking its
tree structure. The SHA-1 of a malformed tree is a valid Git
OID, but should not authenticate it as a directory.

M40 requires the full binary Git tree parser to succeed before
either PATH or LSDIR emits **any** metadata about a terminal
tree. This is in addition to the existing full selected GEN2
audit, referenced object-type check and SGET SHA-1 verification.
Malformed terminal trees return RC8 with
`DIRECTORY TREE STRUCTURE INVALID`; no PATH OBJECT TYPE
or TREE DATA BEGIN is emitted. Plain blob PATH and PATHCAT
semantics, Gitlinks and all existing link-depth commands
are unchanged.

Full host integration adds deliberately malformed terminal
subtree tests for both PATH and LSDIR, including no partial
result checks. One standard `GITRUN M40` adds a positive
real 1,808-object historical `src` directory lookup using
the known first commit and path hex 737263, while retaining
both independent full GEN2 audits, the M39 LINKBATCH test,
the negative cases, two-slot recovery and final protected
STATE checks. Only GITREC.C and GITRUN.EXEC require CMS
transfer. After full host CI succeeds, real target gate:

```sh
git pull
./cms-upload.sh GITREC.C
./cms-upload.sh GITRUN.EXEC
```

```text
CMSCLNK GITREC PLAIN
GITRUN
```

Expected final marker after a genuine target success:
`GITRUN M40 ALL READ ONLY NATIVE GIT TESTS PASSED`.
No protected original generation or pointer is modified.

## M41: fully verified directory listing

`GITREC LSDIRV C0NAME C1NAME COMMIT_OID40 DIRHEX`
extends the target-proven path walker: after real
full GEN2 selection and an authenticated commit-to-directory
path, it checks that *every immediate local directory entry*
references an independently rehashed object of the expected
Git blob/tree type. Linked subtrees are additionally parsed
as complete binary Git trees. Gitlinks represent external
repositories and are not falsely treated as local objects.
The existing 256-entry/tree and shared 1024-visit limits
remain enforced. A missing reference returns RC4, a wrong
type, invalid subtree, malformed terminal directory or limit
violation RC8, and *no* verified marker, path metadata or
directory listing is emitted on failure.

The read-only walker reuses its body buffer for linked
objects, so LSDIRV explicitly reloads and revalidates the
selected directory before producing its listing. The old
LSDIR command retains its original structural-only listing
semantics; PATH and PATHCAT remain unchanged except for
M40's terminal-tree validation. Host integration checks a
valid nested directory and a pair of structurally valid
directories with respectively missing and wrong-type linked
blobs; the legacy LSDIR accepts the latter but LSDIRV must
reject them before any output. A malformed subtree must
also be rejected without leaking metadata.

M41's ONE compact GITRUN combines M40's terminal-tree
hardening, M41's positive actual historical `src` directory
listing and all previously target-proven M39 full audits,
link batch, negatives, fallback and protection checks.
Only GITREC.C and GITRUN.EXEC need uploading. The
expected actual CMS final marker after a real success is
`GITRUN M41 ALL READ ONLY NATIVE GIT TESTS PASSED`.
M40 and M41 must remain host-only until the full CI run
and actual CMS transcript establish the respective results.

## M42: bounded recursive directory verification

`GITREC LSDIRDEPTH C0 C1 COMMIT_OID40 DIRHEX DEPTH`
extends M41's authenticated directory lookup with a strict
one-byte decimal depth from 0 through 4. At depth zero,
the selected directory's immediate local blob/tree entries
are independently authenticated, as in LSDIRV; larger
depths also descend through that many levels of local
subtrees. The existing 256-entry-per-tree and shared
1024-tree-visit limits apply; external Gitlinks are skipped
as external repository references. All operations remain
within one completely audited immutable GEN2 generation,
and no partial metadata/listing is printed if ANY
referenced object fails. Successful output includes
`DIRECTORY LINK DEPTH N VERIFIED`, followed by the
full authenticated directory listing. Invalid depth RC4,
missing referenced objects RC4, wrong type, malformed
subtree or exceeded limits RC8.

The native host suite checks all five valid depths,
invalid depth strings and two groups of fixtures where a
shallower directory check succeeds but a deeper check
discovers a missing or wrong-type object. M41 LSDIRV,
M40 structural-only PATH/LSDIR and all prior read-only
commands remain individually regression-tested.

One standard M42 compact target runner tests the actual
historic `src` directory at depth one. This exercises
M40, M41 and M42 together, in addition to independently
auditing GITFIX and M15NEW, checking M39 LINKBATCH,
negative child/depth errors, seq51 fallback, both-slot
fail-closed handling, seq52 restoration and original
protected data STATE checks. The historic root/depth
objects were previously authenticated by the real M39
depth-two child/parent tree walk, so this target fixture
does not require a new network fetch or test generation.

Only transfer GITREC.C and the standard GITRUN.EXEC:
```sh
git pull
./cms-upload.sh GITREC.C
./cms-upload.sh GITRUN.EXEC
```

```text
CMSCLNK GITREC PLAIN
GITRUN
```

The real target final marker must be
`GITRUN M42 ALL READ ONLY NATIVE GIT TESTS PASSED`
before M40-M42 can be described as target-proven.

## M43: enforce tree-entry budget across external Gitlinks

The bounded recursive walker previously counted only *local* blob/tree references against its 256-entry-per-tree limit. Gitlinks (`160000`) were correctly skipped for local object resolution but also skipped the entry counter; 257 or more external Gitlinks could evade the published bound. M43 separates the total entry count from the local object-array count, rejects the 257th entry of **any** supported mode with `ROOT LINK LIMIT EXCEEDED` RC8, and continues to skip external Gitlink object lookups. Original 1,024-tree visit budget and all fail-closed behavior are unchanged. Tests exercise exactly 256 Gitlinks (success), 257 Gitlinks in a commit root (RC8 without parent or success markers), and 257 Gitlinks in a commit-relative directory via LSDIRDEPTH (RC8 without metadata or partial listing). Both original 1,808-object generation audits and all recovery/protection gates remain in one M43 standard compact runner. The real positive historical directory case is unchanged. M43 requires only GITREC.C and GITRUN.EXEC on the next actual CMS gate; GITCIDX and GITSEL remain unchanged. Expected terminal marker: `GITRUN M43 ALL READ ONLY NATIVE GIT TESTS PASSED`.

## M44: bounded complete tree closure

New read-only `GITREC CLOSURE C0 C1 COMMIT_OID40` traverses the complete local Git tree/blob graph for the supplied child commit and every authenticated parent root, beyond M37's caller-selected depth-four ceiling. It uses a bounded iterative stack instead of unbounded C recursion, independently checks each referenced local object's indexed type and staged-body SHA-1, parses every reached Git binary tree, and skips external Gitlinks without falsely requiring locally stored submodule commits. Both the existing 256-entry per-tree limit (including Gitlinks, per M43) and a single shared 1,024-tree visit budget across the child and all parent roots remain enforced. Trees are allowed to share object IDs but repeated visits count against the budget. On ANY missing object (RC4), wrong type/structure or resource limit (RC8), no `FULL ROOT CLOSURE VERIFIED` marker or framed parent list is emitted. This checks presence and integrity within the same fully audited immutable generation, not any write/promote or restart-durability operation.

Synthetic native C89 host fixtures include six nested tree levels. M37 `DEPTHLINKS 4` intentionally passes while a deepest missing or wrong-type object exists; M44 `CLOSURE` must reject those child or merge-parent cases before any authenticated success output. The standard single-page M44 GITRUN additionally runs full closure of the historical real first commit and all its parents, alongside independent original full 1,808-object audits, M43's existing positive link and directory checks, negative cases, older-slot recovery, both unavailable fail-closed, restoration and final protected-file checks. It supersedes the untested M43 target gate; one M44 target run covers M43/M44 after full host CI. Transfer only GITREC.C and GITRUN.EXEC, compile with `CMSCLNK GITREC PLAIN`, run `GITRUN`; expected final marker `GITRUN M44 ALL READ ONLY NATIVE GIT TESTS PASSED`. If historical full closure is legitimately incomplete, the read-only gate must fail closed without changing either original generation.

## M45: complete closure for a chosen directory

New read-only `GITREC LSDIRFULL C0 C1 COMMIT_OID40 DIRHEX` extends the target-proven M42 path traversal with M44's iterative **complete local closure** of the chosen terminal directory. After full selected-generation GEN2 verification, commit structure and commit-relative path checks, it traverses every local tree/blob descendant (no depth-four ceiling), verifies indexed object type and SHA-1 body, parses every tree, counts all modes including external Gitlinks toward 256 entries/tree, and enforces a shared 1,024-tree visit budget. Gitlinks are external and are not dereferenced. After full closure, it reloads the chosen directory because linked lookups reuse the body buffer and emits `DIRECTORY FULL CLOSURE VERIFIED`, authenticated path metadata and one complete directory listing. Missing data RC4; bad type/syntax/budget RC8, with no marker, metadata or partial listing. Existing LSDIR/LSDIRV/LSDIRDEPTH behavior remains unchanged.

Synthetic host tests verify that depth-four listing succeeds on a six-level tree with a missing or mistyped deepest object, while LSDIRFULL rejects it without partial output; a valid long tree succeeds, 257-Gitlink directories are rejected, and malformed path syntax is rejected before a selected-generation audit. The one standard M45 compact GITRUN adds a real complete closure of the historical `src` directory alongside M44 full child/all-parent root closure, both independent original 1,808-object GEN2 audits, original single-link batch, bounded depth-one src proof, fail-closed negatives, older fallback, both unavailable and restored newer selection and final protected-state checks. The actual M44 target already authenticated the entire historical first-commit graph, so this positive M45 path reuses a known original tree, not a synthetic CMS fixture. Once full native host CI passes, transfer only GITREC.C and GITRUN.EXEC and run CMSCLNK GITREC PLAIN, then GITRUN. Expected last marker, only after actual native success: `GITRUN M45 ALL READ ONLY NATIVE GIT TESTS PASSED`.

## M46: complete closure from a raw tree object ID

`GITREC TREECLOSURE C0 C1 TREE_OID40` authenticates any indexed Git tree without requiring an associated commit or commit-relative path. It first selects a fully verified sealed GEN2 generation, then reuses the M44 bounded iterative full-closure walker with the M43 256-total-entries/tree (Gitlinks count) and shared 1024-tree visit budget. Every local blob/tree reference must have the expected indexed type and a rehashed staged object body; all encountered subtrees must have structurally valid binary Git records. External Gitlinks are counted toward the entry limit but never falsely dereferenced as local objects. Only after the entire closure succeeds does it reload the root tree and emit `TREE FULL CLOSURE VERIFIED` and a complete direct tree listing. Missing tree/blob RC4, malformed root or descendants, wrong types and resource limits RC8, without partial listing or success marker.

Host production-C89 integration covers a valid six-deep tree, corrupt deeply nested blobs, malformed root, missing tree, wrong root type, 256/257 Gitlinks, and exact 1024/1025 tree-visit limits. One standard compact M46 GITRUN adds a real historic first-commit root tree closure to the existing independently audited 1808-object original generations, M39 linked-depth batch, M42 src depth-one, M45 src full closure, M44 complete child+all-parent closure, negative child/depth, old-slot fallback, both-invalid fail-closed, restored new slot and final protected files. This historical root's complete closure was already target-proven in the real M44 test; M46 tests that it can be requested directly by raw tree OID. Only GITREC.C and GITRUN.EXEC require transfer. Do not mark M46 actual target-proven until a real `CMSCLNK GITREC PLAIN` and `GITRUN` print `GITRUN M46 ALL READ ONLY NATIVE GIT TESTS PASSED`.

## Actual CMS proof through M45

On September 28, the real z/VM CMS `CMSCLNK GITREC PLAIN` compiled M45 with no flagged statements, then its complete standard compact `GITRUN M45` passed all checks, including two independent full original 1,808-object audits, historic src complete closure, complete child/parent closure, fallback, both-generation-invalid rejection, restoration and all final protected files. Full run was 705.89 CPU / 721.23 elapsed sec. M45 is ACTUAL CMS target-proven. Synthetic M43/M44 resource boundaries and deep M45 corruption cases were proven in separate host C89 integration; do not conflate those fixtures with the real immutable stage. M46's direct tree-OID closure reuses the existing bounded verifier and remains host-only until one real `GITRUN M46` success is supplied.

## M47: require entire commit-root closure before path metadata

`GITREC PATHFULL C0 C1 COMMIT_OID40 PATHHEX` first verifies the selected generation and commit structure, then runs the existing bounded iterative full-root closure on the commit's tree **before any path-specific result**. It independently checks every local tree and blob in the entire snapshot, including unrelated sibling branches; 256 entries/tree including external Gitlinks and the shared 1,024-tree-visit limit still apply. It then traverses the requested commit-relative path and returns authenticated metadata (`PATH OBJECT TYPE ... OID ...`) or external Gitlink reference, preceded by `COMMIT ROOT FULL CLOSURE VERIFIED`. This is metadata only; no blob HEX or tree listing. For missing descendants or path RC4, malformed/wrong-type descendants, noncommit or budget failure RC8, it never emits the success marker or path metadata. Invalid `PATHHEX` is rejected before auditing. This is stronger than ordinary PATH, which only validates the traversed path, and different from LSDIRFULL, which verifies the requested directory's descendants but not other sibling branches.

Synthetic tests confirm that ordinary PATH successfully reports a valid README.md while PATHFULL refuses to disclose it if an unrelated deeply nested sibling blob is missing or wrong-type. Positive fixtures cover blob, tree and external Gitlink terminal paths, missing names and malformed inputs. The only standard M47 native gate adds the target-proven historic first-commit `src` path with whole-root closure; M46 already demonstrated native complete closure of that root. All preceding independent original full audits, dir/commit/raw-tree closure checks, expected negative RCs, older-generation fallback, both-invalid fail-closed, restoration, and final protected-state checks remain intact. Full host CI required before main merge; then transfer only GITREC.C and GITRUN.EXEC for one actual M47 CMS run.

## M48: snapshot-authenticated binary blob retrieval

`GITREC PATHFULLCAT C0 C1 COMMIT_OID40 PATHHEX` extends M47 PATHFULL with full raw hex blob data output. It first fully verifies the selected sealed generation and commit structure, then authenticates the **entire commit root** using the bounded iterative closure verifier before walking the requested path. Only a correctly typed, SHA-1 authenticated local blob is accepted; a tree or external Gitlink cannot be read as a blob. After all verification succeeds it emits `COMMIT ROOT FULL CLOSURE VERIFIED`, canonical `PATH OBJECT TYPE 3 SIZE ... OID ...`, `PATH DATA BEGIN`, 32-byte `PATH HEX` chunks, and `PATH DATA END`. Empty and 64-KiB blobs use the same lossless format as PATHCAT, but missing or mistyped unrelated sibling objects and resource-limit breaches now fail without any path metadata or blob content. Every read is from the fully validated immutable selected generation. Malformed hex input is rejected before auditing. No persistent files or selector writes.

Host C89 regressions cover zero-length, binary (0x00 to 0xFF), maximum 64-KiB, nested paths, missing/wrong-type deep siblings that ordinary PATHCAT does not inspect, forbidden tree/Gitlink terminals, malformed paths, older seq51 recovery, both-generation-invalid RC8 with no content and restored seq52. The only standard M48 compact target GITRUN adds the real historical first-commit README.md snapshot-authenticated blob read, retaining M47 PATHFULL of the real `src` tree plus all earlier full audits, full closures, negative RCs, recovery and protected originals. Original historic root SHA and descendants were already target-proven in M44–M46; only GITREC.C and GITRUN.EXEC need CMS transfer after full host CI is green. Exact final marker requires real CMS success: `GITRUN M48 ALL READ ONLY NATIVE GIT TESTS PASSED`.

## M49: complete-snapshot authenticated directory listing

`GITREC PATHFULLDIR C0 C1 COMMIT_OID40 DIRHEX` verifies the entire local Git tree/blob closure of a commit in the same fully audited immutable selected GEN2 generation before disclosing the requested directory's metadata or listing. It uses M44's bounded iterative closure verifier with M43's 256-entry/tree bound counting external Gitlinks and one 1024-tree visit budget. Unlike LSDIRFULL, corruption in an unrelated sibling subtree prevents disclosure. A valid directory prints `COMMIT ROOT FULL CLOSURE VERIFIED`, authenticated `PATH OBJECT TYPE 2 ... OID ...` and one complete `TREE DATA BEGIN`/`TREE DATA END` listing. Non-tree terminal entries, missing paths, missing local siblings, wrong type or traversal limits fail without a success marker or partial metadata/listing. Empty and malformed hex paths are rejected before a full audit; Gitlink terminal entries cannot be mistaken for local directories.

Host production C89 fixtures check valid six-level trees, unrelated missing/wrong-type deep branches, forbidden blob/Gitlink terminals, malformed path strings, fully verified older seq51 fallback, both invalid fail-closed output and restored seq52. The one standard M49 GITRUN adds complete-snapshot historic `src` listing and retains both independent original full 1808-object audits and every M39–M48 positive/negative, fallback, fail-closed, restored and final protected-file check. The historical first-commit root closure was already independently actual CMS target-proven in M44–M48. This M49 command still requires its own real CMS proof before being called target-proven. Transfer only GITREC.C and GITRUN.EXEC after complete native-stage host CI passes; GITCIDX/GITSEL and all protected original files remain unchanged.

## M50: complete-closure paths from an arbitrary raw tree OID

`GITREC TREEPATHCAT C0 C1 TREE_OID40 PATHHEX` and `GITREC TREEPATHDIR C0 C1 TREE_OID40 DIRHEX` accept a tree's raw SHA-1 and a HEX path relative to that tree; no commit is needed. After full selected-generation GEN2 attestation, each validates the root's type and runs the existing complete iterative tree/blob closure over the **entire supplied root** before traversing the requested path. Tree visits share the 1024 limit; all entries including external Gitlinks count toward 256/tree. TREEPATHCAT returns fully authenticated binary blob bytes in the established `PATH HEX` 32-byte chunk format; TREEPATHDIR returns fully authenticated directory metadata and complete tree listing. Both print `TREE ROOT FULL CLOSURE VERIFIED` only after all local tree/blob links and selected terminal type have passed. Missing roots/links return RC4; wrong types, invalid structure and resource limits RC8 without success marker or path metadata/blob bytes/tree listing. A Gitlink remains external and cannot be mistaken for a local blob or directory. Bad PATHHEX is rejected before a full audit.

Production strict C89 host tests cover binary/empty/64-KiB/nested files, raw tree directory listings, unrelated missing/wrong deep subtree rejection, absent/wrong-type root, invalid terminals and hex, 257 Gitlinks, 1024 versus 1025 tree visits, older fully verified seq51 fallback, dual invalid fail-closed and restored seq52. The one M50 compact native gate adds raw historical root README and src directory traversal to all previous real original 1808-object audits, M35–49 full closures, negative RC4/8, fallback and protected original checks. The actual historical root's closure was already proven on real CMS by M44–M49, but M50's new commands remain host-only until real native `GITRUN M50` succeeds. Transfer only GITREC.C and GITRUN.EXEC; preserve every sealed original, selector PTR and PACK.

## M51: complete raw-tree closure before arbitrary path metadata

`GITREC TREEPATH C0 C1 TREE_OID40 PATHHEX` expands M50 raw-tree-relative binary and directory commands with metadata-only lookup for blobs, subtrees and external Gitlinks. The selected sealed GEN2 generation is fully audited and the raw root must be a valid tree; all local tree/blob descendants of that root are verified within 1024 tree visits and 256 entries per tree (external Gitlinks count but are never dereferenced locally). Only after the entire closure and selected path are valid does it release `TREE ROOT FULL CLOSURE VERIFIED` and authenticated `PATH OBJECT TYPE ... OID ...` metadata or `PATH GITLINK (EXTERNAL COMMIT)` and `PATH OID` for an external Gitlink. No content or listing is emitted. Missing roots/descendants return RC4; wrong root type, invalid descendants and limits return RC8, with no metadata leakage. Bad hex paths are rejected before a full generation audit. Host strict C89 regressions exercise terminal blob, directory and external Gitlink, deep missing/wrong sibling rejection, invalid hex/root, resource boundaries, older seq51 recovery, dual-invalid fail-closed and restored seq52. The compact M51 CMS runner adds historic raw root `src` metadata proof while retaining every protected preceding milestone's original-data test. M50 actual CMS target proof is recorded in docs/CURRENT_STATE.md; M51 requires real CMS target verification after full host CI.

## M52: one selector audit for the complete positive regression

`GITREC RUNBATCH C0 C1 COMMIT_OID40 TREE_OID40 DIRHEX FILEHEX` runs the existing production positive checks sequentially **inside one selected GITREC process**, after a single complete strict GEN2 selector verification. Its eleven operations are: LINKBATCH depth2 (combined M35–37), LSDIRDEPTH directory depth1, LSDIRFULL, CLOSURE child and all direct parents, standalone raw TREECLOSURE, commit-root PATHFULL metadata, PATHFULLCAT blob data, PATHFULLDIR directory listing, raw-root TREEPATHCAT blob, TREEPATHDIR directory and TREEPATH metadata. Each operation still performs independent full local object/link validation, with its own fresh resource budget, but does not repeat the selected-generation audit in a new process. The final `BATCH ALL POSITIVE CHECKS PASSED` is printed only if **every** operation returns RC0; failures abort immediately and never print that aggregate marker. The compact standard M52 `GITRUN.EXEC` preserves both original independent GITCIDX GENCHECK 1808-object audits, the standalone selector check and the distinct negative, older seq51 fallback, both-invalid fail-closed, restored newest seq52 and final protected-file tests. Only eleven redundant full-selector audit runs are collapsed into one. No sealed original files are touched. The previous M50 actual native run was CPU 1109.69/elapsed 1133.73 sec on the post-reboot host; the user noticed the tests taking longer. M51 real native test still has NOT been confirmed: the post-reboot CMS terminal reported `GITRUN M50`, indicating a stale runner was executed.

Mac `src/cms-upload.sh` and `src/cms-download.sh` now accept `CMS_SCRIPT_PORT` (default 3271), so with the present SSH tunnel on 3271 and c3270 script socket on 3272 use `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITREC.C` and `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITRUN.EXEC`. Before any native M52 regression, confirm on Mac that `GITRUN.EXEC` begins `/* M52` after git pull, that each upload reports success, and on CMS that `TYPE GITRUN EXEC A` starts with the M52 banner. Then `CMSCLNK GITREC PLAIN` and one `GITRUN`. Host strict C89 integration tests must pass before merging the M52 branch. Runtime savings on real CMS remain to be measured; this architecture removes repeated selector audits, not the per-feature descendant checks or original independent audits.

## M53–M54: avoid redundant selected-generation audits

M52 passed actual CMS on 2026-09-29 (CPU 962.91 / elapsed 986.89 seconds). M53 removes the redundant separate `GITREC SELECT` from the one compact REXX test runner; `RUNBATCH` independently verifies and reports `SELECTED 52 M15NEW` and the compact test asserts that exact selection before printing `PASS SELECT SEQ52 FROM VERIFIED BATCH`. Both independent 1,808-object original GITCIDX full audits remain unchanged. Strict host native-stage CI for M53 passed. M54 adds expected wrong-type and missing-child tests *inside* the same fully verified `RUNBATCH`, after the eleven positive operations. It requires `rec_parents` called on the already verified raw tree OID to return RC8, then on an absent all-zero child OID to return RC4. Each gets an explicit `BATCH NON COMMIT CHILD RC8 VERIFIED` / `BATCH MISSING CHILD RC4 VERIFIED` marker only for the exact expected return code. Any unexpected RC aborts and withholds final `BATCH ALL POSITIVE CHECKS PASSED`. The REXX gate captures both markers from the single batch before reporting those negative tests passed, removing two redundant separate GITREC selector verifications. It keeps the invalid-depth RC4 syntax test, older seq51 recovered audit, both invalid fail-closed RC8, seq52 restored audit, both separate original full audits, and final protected files. Exact C89 host regression checks new markers under normal selected seq52, older seq51 recovery, restored seq52 and their absence when both generations are invalid. M54 is NOT target-proven until an actual CMS `GITRUN M54` passes.

## M55: bounded cache inside single immutable-generation RUNBATCH

Actual M54 CMS full regression passed, CPU 900.08 / elapsed 923.83 seconds. M55 keeps two in-memory entries keyed by the exact 20-byte raw tree OID. The cache operates **only within RUNBATCH after complete selected GEN2 attestation**, remembers exclusively successful complete root closures under a fresh 1024-visit budget, and never spans a new process, selector choice, standalone command, partial verification or parent-shared traversal budget. Repeated PATHFULL, PATHFULLCAT, PATHFULLDIR and TREEPATH variants reuse the authenticated complete root while still re-reading and checking their own path and terminal object. RUNBATCH emits `BATCH ROOT CLOSURE REUSES N` only after successful reuses and requires that N be positive before final aggregate success. Native C89 host integration tests include latest selection, older seq51 fallback, dual-invalid no-output and restored seq52. The compact regression retains two independent 1808-object original full audits, every previous feature, wrong-type RC8 and missing-child RC4 inside batch, invalid-depth RC4, recovered seq51, both-invalid RC8, restored seq52 and final protected files. A new native runtime comparison is valid only after actual CMS completion.
