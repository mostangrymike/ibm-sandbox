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
