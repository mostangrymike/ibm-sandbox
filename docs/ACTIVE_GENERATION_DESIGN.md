# Active generation: two-slot recovery design

The CMS-proven GITFIX STAGE/INDEX/SEEK/GEN files are the
read-only baseline. GENCHECK passed after a fresh CMS login on
September 27, 2026: all 1,808 Git OIDs, IDX2/SIDX2
descriptors, seek cookies and the existing GEN2 seal verified.

A future writer must allocate a **new, unused** CMS filename for
its stage, index, seek and GEN2 files. It must complete and
reopen all four, then run GENCHECK before making them eligible.
Never rewrite the original GITFIX generation during development.

Proposed selector slots: GITSEL0 PTR A and GITSEL1 PTR A. Each
record includes format version, monotonically increasing sequence,
strictly validated 1-8 character generation basename, the
verified GEN2 manifest digest, and a checksum of the selector
record. A selector is not proof of the generation: startup must
read both slots, reject malformed/truncated/duplicate candidates,
and rerun full GENCHECK on each referenced candidate. Choose the
highest-sequence *validated* slot; a damaged newer slot must not
prevent recovery through an older verified slot. If neither slot
verifies, fail closed rather than silently selecting an
unattested generation.

Promotion sequence: leave the active slot untouched; write
and close candidate data, seal/reopen and check its GEN2,
write the inactive selector slot, close/reopen and check the
selector, independently GENCHECK the referenced generation,
then retain the older slot and its generation for rollback.
No claim is made that CMS replacement, rename or close is
power-loss atomic. Concurrent writer exclusion, explicit slot
file persistence, and machine-reset behavior require separate
real-CMS tests before enabling automatic promotion.

Crash-injection host regressions should interrupt each candidate
write and selector write, corrupt either slot, alter its sequence
or digest, truncate GEN2 and modify the selected stage or seek
cookie. Recovery must never return any generation that fails its
own GENCHECK. All tests use disposable fixtures, never GITFIX.

Next existing-target durability test, only after a normal
authorized VM reboot, is read-only GENCHECK against the original
GITFIX STAGE, INDEX, SEEK and GEN files. Cross-logon survival
has already passed; reboot persistence is not yet demonstrated.

## First implemented host-only selector prototype

The repository now contains `tests/active_generation_selector.py`,
a strict, versioned two-slot prototype. It encodes the selector
sequence, uppercase 1–8-character CMS basename, canonical 40-hex
GEN2 digest and CRC32 over explicit ASCII bytes. Its parser
requires exactly one newline-terminated record, valid checksum,
strict grammar and sequence within an unsigned 32-bit range.
Recovery calls an **injected full-generation-verification callback**
for each candidate in descending sequence order. It fails closed if
two different slots claim the same sequence, returns the prior
verified slot if a newer selector is corrupt or its generation fails
full verification, and returns no selection if neither is valid.

`tests/test_active_generation_selector.py` checks every truncated
prefix of the newer slot, checksum corruption, wrong/missing candidate
validation, ambiguous duplicate sequences, identical slots, missing
slots and invalid grammar. Full host regression CI passed:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36329760231 .

**This is a host-only executable specification, not deployed CMS
selector code.** The callback contract is deliberately strict: it
must be backed by real GENCHECK against the candidate's four files.
It cannot be replaced by a filename-exists check or a matching
manifest header. The next implementation step is a CMS C89 parser,
then an explicit read-only candidate verification and controlled
promotion test using separate disposable generations. Never
introduce promotion writes against GITFIX during development.

## Native C89 selector reader now committed

`src/GITSEL.C` is a new bounded native C89 reader for the proposed two-slot `SEL1` records. `GITSEL CHECK` reads FILEDEF `SEL0` and `SEL1`, validates the exact record grammar, unsigned 32-bit sequence, CMS-safe generation basename, uppercase 40-digit digest, record length and CRC32. It computes CRC32 over canonical ASCII bytes even when built on EBCDIC CMS. It rejects conflicting slot records with identical sequence numbers.

**CHECK deliberately prints candidates as UNTRUSTED; it does not select an active generation.** The actual generation must independently pass full `GENCHECK` before selection or promotion. This prevents the parser from becoming an unsafe shortcut around the complete 1,808-object audit. Never connect the parser to the protected current GITFIX data as a writer.

`tests/test_native_selector.py` compiles production `src/GITSEL.C` as strict C89 with all warnings as errors, generates records with the independent Python protocol, tests every truncated prefix and checksum/grammar corruption and verifies same-sequence conflict rejection. The complete native staging CI passed: https://github.com/mostangrymike/ibm-sandbox/actions/runs/36329974642 . This is **host-compiled only**; the native reader still needs CMS compilation and its full GENCHECK integration before it can safely select any active generation.

## M14 combined native C89 recovery gate implemented (host only)

The standalone GITSEL parser now has a bounded `GITSEL WRITE`
operation for new, disposable SEL1 records, tested byte-for-byte
against Python's independent canonical ASCII CRC32 implementation.
Its optional linked SELECT callback refuses to elect a candidate
until the callback fully validates that generation.

The new `src/GITREC.C` links actual GITSEL and GITCIDX source,
reads slot records from SEL0/SEL1, and maps each independently
named candidate to separate input FILEDEFs C0STG/C0IDX/C0SEEK/C0GEN
or C1STG/C1IDX/C1SEEK/C1GEN. It checks selector identity and the
GEN2 DIGEST record, then invokes the real full `gen_check()`
for every candidate it considers. Only after complete canonical
object/paired-index/seek-cookie/manifest verification can a slot
be selected. A damaged newer slot or incomplete newer generation
causes recovery through the older fully verified candidate.

The host integration runs the *compiled GITREC binary* against
two disposable 1,808-record synthetic candidate generations and
injects corrupt GEN2, corrupt stage, truncated SIDX2, missing IDX2
and spoofed selector identity. It asserts that neither stage
corruption nor selector parsing alone can bypass full GENCHECK.
All these tests passed:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36330993480 .

This code is **not an active pointer writer, not a lock and not
an atomic promotion operation**. Real CMS compilation and the
safe read-only valid-old/invalid-new test remain to be performed.
See [the exact next target gate](NATIVE_RECOVERY_GATE.md), which
uses the actual GEN2 DIGEST from the protected GITFIX generation
and only two disposable selector files. No original stage, index,
seek or manifest file is modified.

## M14 CMS-proven recovery and M15 host interruption matrix

September 27 native CMS tests completed the real GITREC
selector recovery gate on GITFIX: valid older seq41, invalid
newer seq42, full 1808-object SFAST/PAIR/GENCHECK,
failed name matching, absent old GEN2, invalid SEL1
content and both single-slot absence cases. A correct
restored mapping recovered GITFIX and its canonical
DIGEST 493F0896884B28AC4836B88328629B7E95404B46.
All target tests were nondestructive to GITFIX and
existing selector records. Cross-logon durability for
the selectors themselves still requires confirmation,
although GITFIX GEN2 independently survived logoff/logon.

M15 host regression extends tests/native_index_host.c,
which compiles and runs the **actual production GITREC.C**
against separately generated full indexed fixture files.
A valid old candidate stays present. Simulated interrupted
promotion probes five shortened candidate selector prefixes,
then independently withholds each of the four new candidate
files (stage, index, seek, GEN2), and simulates an incomplete
new GEN2 manifest. Every incomplete new candidate must
fall back through actual full GENCHECK to the old verified
candidate. Only the fully restored candidate with an intact
selector can be selected as new. Fixture names, staged data
and slot records are host disposable; this is not a CMS
file-write atomicity or concurrent writer proof.

**Promotion remains disabled.** The currently tested
REXX STATE RC28 / ABSENT28 gate only protects the
controlled single-writer first creation of a new selector.
It is not an atomic create-if-absent or lock. True active
promotion needs an exclusively owned writer protocol,
immutable staged generations, a verified independent
second candidate, new unused slot storage and
interrupted-write testing on CMS before production use.
Never reuse or overwrite GITSEL0/GITSEL1 PTR A or the
four protected GITFIX generation files.

## M15 next native CMS test: disposable independently sealed candidate

The current reusable `src/GITRUN.EXEC` is committed as the
first isolated CMS candidate-build gate. It guards all four
new `M15NEW STAGE/INDEX/SEEK/GEN A` filenames and both
`M15SL0/M15SL1 PTR A` names with real REXX STATE
RC 28 checks **before writing**. It checks all four
protected GITFIX source files, reports A-disk space,
copies only the existing verified GITFIX STAGE and
IDX2 INDEX into never-before-used M15NEW files, builds a
fresh SIDX2 seek index against the new stage (since
CMS ftell cookies may change when copied), then creates
an independent M15NEW GEN2 manifest **last**.
Afterward GITCIDX GENCHECK must independently reopen
and rehash all 1,808 stored objects, pair both indexes,
check stage seek cookies and verify the seal. Any
failed step exits immediately with no selector writes.

This test is a **disposable candidate build**, not
active promotion and not the host interruption test.
The next separate target gate after successful verification
will use only new unused M15SL0/M15SL1 selector files,
fully verify both candidates with GITREC before and after
a deliberately invalid newer-selector case, and never
write to the existing GITSEL0/GITSEL1 files. The new
candidate should not be called durable or active until
its independent CMS verification and subsequent
persistence/recovery checks pass.

## September 27 superseding status: actual CMS M15 matrix

The complete 10-case M15 native CMS recovery matrix has
now passed. Independently verified seq51 GITFIX and
seq52 M15NEW survived each missing newer component, a
missing older GEN2, both missing GEN2s, one or both
malformed selectors and complete restoration. All selected
generations underwent the full native 1808-object audit
and returned the expected generation name/sequence. The
two independent CMS generations, all four native selector
records, and the captured original PACK remain protected.

The older Python-only selector proof-of-concept files
`tests/active_generation_selector.py` and
`tests/test_active_generation_selector.py` were retired
from current GitHub main after the independent ASCII/CRC
encoder was embedded into `tests/test_native_selector.py`.
Native C89 selector fuzz tests and full native GITREC
integration are the maintained host CI paths; historical
commits preserve the original Python-only prototype.
Latest native CI green:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36338727815 .

The next read-only CMS runner independently rechecks both
GEN2 candidates and the native dual-slot selector. Only
upon success does it optionally remove three explicitly
named historic NONCANONICAL CMS copies: GITSTAGE DATA A,
GITINDEX DATA A and GITSEEK INDEX A. It does not erase
GITPBUF PACK A, GITFIX, M15NEW, GITSEL0/1 or M15SL0/1.
Cleanup remains target-pending until the CMS transcript
shows the expected success. Full CMS interrupted write,
exclusive lock and reboot persistence remain distinct
unproven production requirements.

## September 27 current CMS cleanup verified; M16 in progress

The high-density M15 audit-and-cleanup run succeeded on actual
CMS: independent GEN2 audit of GITFIX and M15NEW (1808
unique each, RC0), deliberate selector swap rejected with
two name mismatches RC8, restored M15 selectors chose seq52
M15NEW after complete GENCHECK RC0. The three old noncanonical
GITSTAGE DATA A, GITINDEX DATA A and GITSEEK INDEX A files
were erased; each subsequent STATE confirmed absence.
The final guards found both complete canonical sealed
generations and both original/disposable pairs of PTR
selector records intact. GITPBUF PACK remains preserved.

M16 advances beyond missing inputs into native selector
protocol attacks, with a single self-cleaning CMS GITRUN:
a correctly checksummed seq60 M15NEW selector with a forged
zero manifest digest must be rejected in favor of verified
seq51 GITFIX; a genuine M15NEW seq50 selector must lose
to verified older-generation seq51 GITFIX; a genuine
same-sequence seq51 M15NEW selector must conflict with the
distinct seq51 GITFIX and fail closed RC8; restoring intact
original seq52 M15NEW must pass complete independent
GENCHECK. All M16 temporary PTR fixtures are created only
under verified-unused names M16BAD/M16LOW/M16CON and erased
after the entire test succeeds. The runner ends by
checking that all eight sealed-generation files and
the original four PTR files remain present.

The companion host regression tests the actual compiled
native GITREC for forged checksummed digest, sequence
ordering, conflict and restoration. Neither these
protocol tests nor the earlier read-only missing-input
matrix prove atomic CMS file replacement or exclusive
writer ownership. Retain both complete sealed generations
and their current selector records until real cross-logon
and normal reboot survival are explicitly established.

## M18 production-facing, read-only selected-generation object GET

`src/GITREC.C` now supports a second command:

```text
GITREC GET C0NAME C1NAME OID40
```

It uses the same explicit read-only `SEL0`/`SEL1`
and independent `C0STG/C0IDX/C0SEEK/C0GEN`,
`C1STG/C1IDX/C1SEEK/C1GEN` file bindings as
`GITREC SELECT`. It validates the 40-hex input
OID before any selector reads, refuses identical
candidate names, evaluates both selector records
including identity and seq conflict rules, and
performs the **complete native GEN2 stage/index/
seek/manifest audit** before permitting a lookup.
Only the successful verified candidate's mapped
seek index and stage are opened by `sidx_read`/
`sidx_get`; a newer unverified generation cannot
leak object bytes. The existing `SGET` independently
rehashes the selected body's Git SHA-1 and prints
`SEEK OBJECT OID` with type, size and prefix.
Absent OID returns RC4; invalid OID grammar
returns RC4; no verified generation returns RC8.

Host regression uses the actual production
`GITREC.C` against independent complete synthetic
1808-record generations: positive new-generation
GET, missing OID and malformed OID rejection,
missing new GEN2 old-generation fallback GET,
both GEN2 files missing with no object disclosure,
and restoration to new-generation GET.
This is the first usable read-only operation
*through* the independently verified generation
selector rather than only displaying its name.

Native CMS execution of this new GET mode is
**on hold** until the documented M01RES/DASD1
filesystem TRKDE-4 incident is preserved and
resolved. No GitHub source change was uploaded
to the possibly damaged CMS A disk, no cleanup
was resumed, and `src/GITRUN.EXEC` remains
an RC12 safety hold. Full OID output, atomic
promotion and exclusive writes are separate
future milestones.

## M19/M20 complete native object output and boundary verification

Production `GITREC CATHEX C0NAME C1NAME OID40` extends
the same full-GEN2-verified and dual-slot-recovered
read-only pathway as `GITREC GET`. It validates the
OID first, verifies the actual selected generation,
seeks through the verified candidate's own SIDX2
index, independently rehashes the entire Git object
body, and **only then** prints the complete body
between `OBJECT DATA BEGIN` and `OBJECT DATA END`.
Each `HEX ` line contains at most 32 body bytes
(64 hex digits), fits within CMS's 80-column output,
and an empty object has no HEX lines. Normal GET
retains its bounded 16-byte prefix behavior, without
the full output. The existing 65,536-byte maximum
is preserved; the native C89 implementation does not
need a malloc or unbounded CMS REXX string.

A second, independently built full-size host fixture
compiles the actual `src/GITCIDX.C` and
`src/GITREC.C` separately, builds and seals a
fresh indexed generation with exactly 1,808
staged objects including a full 65,536-byte
binary object, a zero-length object, a 257-byte
binary object containing NUL and high bytes,
and an ASCII `abc` object. Python independently
computes Git blob object hashes, selector ASCII
CRC32 and verifies every byte reconstructed
from production CATHEX lines. It also tests
the corrupt newer generation's fallback,
both generations invalid with **no** object-body
output, and restoration to intact newer
generation. This complements the original
native-index integration fixture's independent
small-object GET tests. All M19/M20 native
host CI PASSED:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36356523315

GITREC still has no atomic multi-writer promotion,
exclusive writer lock, production binary transport
or reboot recovery proof. No new CMS code has
been uploaded after the M01RES TRKDE incident;
the old CMS A-disk copy of GITRUN must not run.

## M20 next native CMS gate is assembled but safety-held

The full selected-generation `CATHEX` implementation and
separately generated 65,536-byte/binary/empty-object
byte-for-byte host integration are complete. All tests
passed in GitHub Actions run
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36356523315 .
The CMS smoke batch `src/GITRCHK.EXEC` is already
committed. It checks both generations, all four
protected selector files and the original captured
PACK; then exercises the real canonical 270-byte
first commit via current selected-generation GET,
complete CATHEX, newer-manifest absence fallback,
both manifests unavailable RC8, and final complete
restoration. It neither generates indexes/manifests
nor creates/deletes any persistent CMS file; a
separate CI source guard rejects such commands.
The entire expanded native suite, including this
guard, passed:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36356602355 .

**Prerequisite for any target invocation**: preserve
and verify the operator-identified actual
`/home/admin/vm630/dasd1` volume M01RES offline,
then repair or reconstruct the CMS A filesystem
after its TRKDE 4 corruption incident and verify
that the target is safe for uploads/compilation.
At that point transfer `src/GITREC.C` and
`src/GITRCHK.EXEC` through the existing single
c3270 uploader, rebuild `GITREC` using the proven
`CMSCLNK GITREC PLAIN` path, and run one
`GITRCHK` batch. Do **not** execute the
previous unsafe CMS-uploaded `GITRUN`; the
repository's current GITRUN is an RC12 safety
hold. Full native CMS CATHEX operation is not
yet target-proven; only its compiled-host output
and native C89 protocol have been tested.

## M21 native CMS result and M22 host-complete binary tree parsing

**M21 passed on actual IBM z/VM 6.3 CMS on September 27**
after `CMSCLNK GITREC PLAIN` compiled the new native module
with no assembler warnings. Standard `GITRUN` verified
both existing GITFIX and M15NEW generations independently
(1,808 unique each); selected seq52 M15NEW with digest
493F0896884B28AC4836B88328629B7E95404B46;
read the real 270-byte commit with GET and full CATHEX;
recovered seq51 GITFIX when the newer manifest was
temporarily rebound to an absent fixture; rejected
both absent manifests RC8; restored seq52 and
full CATHEX; and checked all protected files afterward.
Final user output: `GITRUN M21 ALL READ ONLY NATIVE
GIT TESTS PASSED`, CMS Ready T=150.70/151.97.
Deliberately missing M15BAD GEN and associated
open-error messages are expected negative tests,
not unexpected errors.

**M22 host-complete, CMS pending:** native
`GITREC TREE C0NAME C1NAME OID40` adds a
read-only structured Git binary-tree decode after
full native GEN2/SFAST/PAIR verification and a
second independent full requested object's Git
SHA-1 verification via the selected generation's
SIDX2 direct seek. Only Git type-2 objects are
accepted. Complete records are structurally
validated *before* any TREE data is printed.
Supported Git modes: 100644, 100755, 120000,
160000, and 40000. Tree names, which are raw
Git bytes rather than CMS-native text, are
reported in 32-byte `TREE NAMEHEX` chunks.
Each entry prints mode, name length, and full
40-digit object ID. Empty Git trees correctly
produce `TREE ENTRIES 0`. Truncated/invalid
records, unsupported modes, missing/not-tree
objects and unverified generations fail closed.
These constraints retain existing C89 and
65,536-byte native Git object bounds.

The new host integration `tests/test-native-tree.py`
compiles the actual production native C89 index
and recovery modules against independently
constructed 1,808-object binary tree, empty tree,
malformed tree and blob fixtures. It verifies
all five supported modes, raw non-ASCII name
bytes, exact OIDs/name reconstruction, empty
tree, non-tree and truncated-tree rejection,
seq51 verified old fallback, both manifests
invalid (no TREE data emission), then seq52
restoration. Full GitHub native workflow PASS:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36359383185 .

The **standard `src/GITRUN.EXEC`**, as explicitly
required by the user, is now M22's combined
read-only CMS batch: checks every protected
generation, selector and PACK; independently
audits two full generations; verifies seq52;
GET of the known first commit; TREE decode of
that actual commit's tree OID
204E1D6968FB81C35BF830D63A611AC64C072945;
refuses to treat the commit itself as a tree
(RC8); deliberately makes newer/both
manifests unavailable through read-only
FILEDEF rebindings, verifies fallback/fail-closed,
restores original mappings, and rechecks
protected files. No ERASE/COPYFILE, persistent
index/manifest writes or selector writes.
This new batch's native CMS target execution
is PENDING, not yet claimed passed.

## September 28 M22 target-proven; M23 structured commit reader

M22 `CMSCLNK GITREC PLAIN` compiled with no assembler
warnings and the standard M22 `GITRUN` completed
successfully on real z/VM CMS on September 28 at
09:28 (T=172.16/173.64). Both GITFIX and M15NEW
passed full 1,808-object native GENCHECK, selected
seq52 M15NEW, decoded actual first-commit tree
204E1D6968FB81C35BF830D63A611AC64C072945
with four entries: CHAT_STATE.md, README.md, docs
and src; rejected non-tree commit (RC8), recovered
seq51 GITFIX when newer GEN2 was absent, refused
both missing GEN2s (RC8), and reselected seq52
after restoring full input mappings. Final all
protected-file checks passed. Git's raw ASCII
modes and delimiters are decoded using explicit
0x20, 0x2f and mode-digit byte values, avoiding
the earlier CMS EBCDIC comparison bug.

M23 introduces
`GITREC COMMIT C0NAME C1NAME OID40` in actual
production C89 source. Like TREE and CATHEX, it
first audits and authenticates the entire selected
generation (GEN2, SFAST, PAIR), uses the selected
generation's direct seek index, rehashes the
requested whole Git commit object and only then
parses the binary header. All Git on-disk OID
digits, line endings and header names are tested
as explicit ASCII bytes, not CMS-native C text.
It validates exactly one first `tree` OID,
zero or more contiguous parent OIDs, author and
committer headers, the blank separator, normal
Git header keys and optional folded header lines.
No metadata is printed until the complete header
is validated. The output contains COMMIT DATA
BEGIN/END, TREE OID, every PARENT OID, parent
count, and message byte count. It does not
materialize the commit message or claim all
parent/tree dependencies are locally available.

M23 host regressions added a valid synthetic
root commit, two-parent merge, invalid parent,
missing committer and a not-commit negative
fixture to the actual 1,808-record native stage.
They verify the production compiled C89 source,
correct metadata, no parsed output on malformed
content, selected-generation fallback and
both-invalid fail-closed behavior.
Full native CI passed:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36436943632 .

The one reusable standard `src/GITRUN.EXEC`
now contains M23's read-only CMS gate against
the already protected original GITFIX and
M15NEW. It tests the real first commit
00D8D63229305230C8D37F884CE87F9E1A89468C
and independently its actual root tree, rejects
a non-commit tree (RC8), verifies older-seal
fallback for COMMIT, both unavailable (RC8)
and intact restoration. No stage, index,
manifest, selector or PACK files are written.
This new COMMIT mode is HOST-PROVEN, awaiting
real CMS execution via standard GITRUN.

## September 28 — M23 CMS pass; M24 native linked read-only paths

M23's new native `GITREC COMMIT` and standard `GITRUN`
PASSED on actual CMS, with `CMSCLNK GITREC PLAIN`
reporting no assembler issues. The target verified
both immutable 1,808-object sealed generations,
selected M15NEW seq52, decoded the actual
270-byte first commit to tree
204E1D6968FB81C35BF830D63A611AC64C072945,
parent 2D5038C551318997B865497E04CF4C037DE4135E
and message length 44 bytes. A tree passed to
COMMIT was correctly rejected RC8. Simulated
newer GEN2 absence recovered seq51 GITFIX and
returned the same commit metadata; both absent
rejected RC8; restoring both reselected seq52
and decoded the commit again. Final all-original
protected-file checks passed. Actual target end:
`GITRUN M23 ALL READ ONLY NATIVE GIT TESTS PASSED`,
T=172.06/173.45 at 09:41:52.

M24 advances from manual independent tree IDs to
**linked, native commit-relative object access**,
with two new production C89 commands:

```text
GITREC LSROOT C0NAME C1NAME COMMIT_OID40
GITREC PATH C0NAME C1NAME COMMIT_OID40 PATHHEX
```

LSROOT validates and rehashes the commit, reads
its canonical first ASCII tree header, then
verifies and decodes the linked tree using the
**same full GEN2-selected generation**, without
trusting the caller to supply the tree OID.
It emits tree entries only after independently
verifying both linked objects and the tree's
complete binary structure.

PATH accepts the relative path encoded as Git
raw-byte hex, not CMS-native text. It resolves
each component in a fully verified type-2 tree,
checks the required mode and referenced object
type, recursively follows nested subtrees and
rehashes the final blob/tree body using its
selected SIDX2 direct-seek cookie before printing
the result. A Gitlink (mode 160000) returns
its external commit OID and does not claim the
external commit is staged locally. Missing
paths or unstaged linked targets return RC4;
invalid hex/absolute/empty path components
return RC4; invalid linked types/structure and
non-tree intermediates fail closed RC8. No
mutable stage or selector operations occur.

Strict C89 host integration now uses a real
1808-object GEN2 test generation with an
authenticated commit, six-mode binary tree
and nested child tree, empty/malformed trees,
known staged blob and gitlink, wrong-type and
malformed linked trees, and the captured real
first-commit fixture. It tests root decoding,
blob/nested-tree resolution, missing paths,
invalid path hex, non-tree intermediate,
external gitlink, both invalid fail-closed,
verified older fallback and reselected newer
restoration. All native GitHub host CI passed:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36438588523 .

The single standard `src/GITRUN.EXEC` now holds
M24's read-only actual CMS tests, including
independent dual-generation audit and seq52
selector validation; LSROOT of the known first
commit; PATH of its real README.md; nested
PATH of docs/STATUS.md; non-commit LSROOT RC8;
missing-path RC4; non-tree intermediate RC8;
older-generation fallback, both-unavailable
RC8, and restored nested path; final all
protected generation/selector/PACK checks.
The actual GitHub historical first-commit
root and nested docs trees were checked when
selecting the names for this batch; the
new M24 native code has **not yet** executed
on CMS and is not claimed target-proven.

## M24 target pass; M25 full verified file bytes by relative path

M24 ran successfully on real CMS on September 28:
`CMSCLNK GITREC PLAIN` assembled with no flagged
statements and the single standard `GITRUN`
completed all ten linked-root/path tests.
Both original 1,808-object generations reaudited
fully; seq52 M15NEW selected; the first commit's
root tree decoded; `README.md` resolved to the
567-byte blob 1BA7AE466BB0A16C294D52A8642E527B07D4D1F5;
nested `docs/STATUS.md` resolved to the 5,737-byte
blob 46135A22C7394D8090619C6C70453C58A24F5239.
Wrong input types, missing files and non-tree
intermediates returned their expected RCs;
missing new-generation GEN2 recovered seq51
GITFIX; both unavailable failed closed RC8;
restoration selected seq52; all protected file
STATE tests passed. Final target line:
`GITRUN M24 ALL READ ONLY NATIVE GIT TESTS PASSED`,
Ready T=239.20/240.98 at 10:07:02.

M25 production native C89 `GITREC PATHCAT C0NAME
C1NAME COMMIT_OID40 PATHHEX` now reuses the
verified M24 nested path traversal and complete
GEN2-selected-generation audit. It independently
rehashes each linked tree and the final type-3
blob before output. Only after full success
does it print `PATH OBJECT TYPE 3 SIZE n OID ...`,
`PATH DATA BEGIN`, up to 32 exact raw bytes per
`PATH HEX` line and `PATH DATA END`. Empty
blobs produce zero HEX lines. A tree/gitlink
target is not accepted as a blob; wrong-type,
missing intermediate, invalid path, bad input
and unverified candidate fail closed without
any PATH DATA bytes. The output is textual
hex and safe for CMS console transfer; the
implementation does not assume unverified CMS
binary record semantics.

Host integration uses actual compiled production
GITCIDX/GITREC with fully sealed 1,808-record
synthetic dual generations. It byte-for-byte
reconstructs PATHCAT outputs for ASCII, nested
ASCII, empty, full 257-byte binary including
NUL/high-bit bytes, and max 65,536-byte binary
blobs. It exercises non-blob negatives, malformed
path input, missing targets, old-generation
fallback, both candidates unavailable and
restoration. A second pinned fixture preserves
the exact historical first-commit `README.md`
contents; the test reconstructs its Git blob
SHA1 and original four-entry root tree SHA1
independently, then feeds the exact previously
captured 270-byte real first commit through
production LSROOT and PATHCAT. All native host
CI passing:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36441754586 .

The single reusable `src/GITRUN.EXEC` is M25's
read-only CMS gate: independent audits for both
protected generations, seq52 selection,
PATHCAT the real first commit's README.md and
nested docs/STATUS.md, type/missing/non-tree
negative cases, seq51 fallback, both absent
fail-closed and seq52 restoration, final
all-protected file checks. Host CI verifies
that this batch has no persistent CMS writes.
M25 has not yet run on CMS.

## September 28 M25 target pass; M26 nested-directory listing

M25 passed on actual CMS: `CMSCLNK GITREC PLAIN`
compiled the updated production module with no assembler
statements flagged. The standard read-only `GITRUN M25`
independently audited both original GITFIX/M15NEW
1,808-object sealed generations; selected M15NEW seq52;
successfully emitted the entire first commit's README.md
(567-byte blob 1BA7AE466BB0A16C294D52A8642E527B07D4D1F5)
and nested docs/STATUS.md (5,737-byte blob
46135A22C7394D8090619C6C70453C58A24F5239)
as framed raw-byte hex. Wrong-type and missing-path
tests failed as expected, the absent newer manifest
recovered the verified older generation, and both absent
manifests failed closed. Restoration retrieved the
complete README again; final protected file checks
passed. Actual last line: `GITRUN M25 ALL READ ONLY
NATIVE GIT TESTS PASSED` (CMS T=218.04/220.32 at
10:28:26). The pasted terminal capture is interleaved,
but the final batch completion is unambiguous.

M26 adds native `GITREC LSDIR C0NAME C1NAME
COMMIT_OID40 DIRHEX`. This read-only command resolves
a relative directory from the verified commit's tree
through authenticated nested trees in the same
GEN2-selected generation, independently rehashes the
target tree, validates the full tree structure, and
emits all entries in the established `TREE DATA`
framing. A regular blob, external gitlink, missing
directory, malformed path, non-tree intermediate,
corrupt tree or unavailable verified generation cannot
emit tree data. Names remain raw Git bytes encoded
as `TREE NAMEHEX`, with explicit ASCII mode decoding
for native CMS/EBCDIC compatibility.

The actual compiled C89 host tests now verify `LSDIR`
of a nested directory (including exact child mode,
name and OID), missing/invalid/non-directory targets,
older-generation recovery, both-manifests-unavailable
fail-closed behavior and restored newer selection.
Standard `src/GITRUN.EXEC` has been updated to the
M26 single read-only target suite. Its positive live
CMS case lists the actual first commit's `docs`
directory, containing the historical BUILD.md and
STATUS.md. All host native regressions and the
read-only EXEC source guard passed:
https://github.com/mostangrymike/ibm-sandbox/actions/runs/36444249032 .
M26 is host-proven only until the new GITRUN is
actually executed on CMS.
