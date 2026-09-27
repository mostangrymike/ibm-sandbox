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
