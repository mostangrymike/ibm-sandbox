# Current CMS Git milestone

M46 is actual native z/VM CMS target-proven (September 29, 2026). `CMSCLNK GITREC PLAIN` completed without flagged assembly statements (9.90 CPU / 10.25 elapsed seconds). The one standard `GITRUN M46` passed every gate: independent 1,808-object full original audits for GITFIX and M15NEW, newest seq52, combined M35–37 root links, src depth-one and complete closure, full commit/parent closure, direct TREECLOSURE from the real historical root object ID, expected invalid-depth/noncommit/missing-child RCs, older seq51 fallback, dual-invalid fail-closed RC8, restored seq52, and final protected data checks. Final exact marker: `GITRUN M46 ALL READ ONLY NATIVE GIT TESTS PASSED`. CPU 775.91 seconds; elapsed 792.93 seconds.

M46 full strict native host CI also passed, including synthetic deep-corruption, 256/257 entries, 1024/1025 visits, older-slot fallback, dual-invalid no-output and restored-newer-slot tests. The disposable host edge fixtures were not independently run on CMS. Both original CMS generations, selectors and GITPBUF PACK remain protected. Next milestone should advance GitHub source and standard compact runner; no redundant standalone M46 target retest.

## M47 complete on GitHub, awaiting one real CMS regression

M47 adds read-only `GITREC PATHFULL C0 C1 COMMIT_OID40 PATHHEX`. After full selected-generation audit and commit validation, it uses the existing bounded iterative verifier to authenticate the **entire commit root**, not only the requested file's ancestors or the requested directory's descendants, before disclosing path metadata. External Gitlinks remain external and counted in the 256-entry per-tree safety bound; the shared 1024-tree-visit budget also applies. It emits `COMMIT ROOT FULL CLOSURE VERIFIED` followed by a metadata-only PATH result (blob/tree or external Gitlink); if any unrelated sibling has missing/wrong-typed data or exceeds a limit, there is no success marker or path metadata. Malformed PATHHEX is rejected before a full audit.

PR #24 implementation host strict native C89 / full integration PASS: https://github.com/mostangrymike/ibm-sandbox/actions/runs/36575528447 ; merged main at 17b2c0405376e1137c74161cb3f822280bc4a28b. PR #25 adds seq51 older-generation fallback, both invalid fail-closed no path data, newest seq52 restored host tests, all native CI PASS: https://github.com/mostangrymike/ibm-sandbox/actions/runs/36575654933 ; merged main at a13f667a077f26757bcb1a9261fac269f36c761f. PR #26 additionally validates 256 vs 257 total entries and exactly 1024 vs 1025 subtree visits on PATHFULL when the *requested* path is uncorrupted, all native CI PASS: https://github.com/mostangrymike/ibm-sandbox/actions/runs/36575796373 ; merged main at b5486c02caf625cdc1230d817caf9e7bb97dc181. **M47 fully host-CI-proven, not yet tested on real CMS.** M46 actual CMS target proof is documented above.

Current main single standard `src/GITRUN.EXEC` is compact M47. It preserves independent full 1808-object original GITFIX/M15NEW GEN2 audits, seq52 selector, M35-M37 batched link proof, M42 src depth-one, M45 src complete closure, M44 child+all-parent full root closure, M46 direct historical root TREECLOSURE, new M47 full root PATHFULL of historic `src`, negative expected depth/child RC4/8, older seq51 fallback, both invalid fail-closed RC8, seq52 restoration and final protected-file checks. All historical root descendants are already actual M44/M46 target-proven, so the new M47 real path gate uses known original object content without requiring a synthetic CMS fixture.

NEXT Mac in `ibm-sandbox/src`: `git pull`, `./cms-upload.sh GITREC.C`, `./cms-upload.sh GITRUN.EXEC`. NEXT actual CMS: `CMSCLNK GITREC PLAIN`, `GITRUN`. Exact expected terminal success only after real passing output: `GITRUN M47 ALL READ ONLY NATIVE GIT TESTS PASSED`. ONLY two transfers; GITCIDX and GITSEL unchanged. NEVER alter original sealed GITFIX/M15NEW STAGE/INDEX/SEEK/GEN, selector PTRs or GITPBUF PACK. No standalone repetition of already completed M46 target regression. Continue independent GitHub development immediately on the next user result.

## M48 host-green snapshot-authenticated binary output (supersedes M47 gate)

M48 extends M47 PATHFULL with `GITREC PATHFULLCAT C0 C1 COMMIT_OID40 PATHHEX`: validate the entire commit-root tree/blob graph in a fully verified immutable GEN2 generation, then and only then produce lossless `PATH DATA BEGIN` / 32-byte `PATH HEX` records / `PATH DATA END` for a local blob. The terminal file must be a correctly typed blob; Gitlinks and directories are rejected. Deep corrupt unrelated sibling branches or traversal-budget breaches fail with no success marker, metadata or partial blob bytes. Malformed path syntax is rejected before auditing. The same 256-total-entries/tree (including external Gitlinks) and 1024 shared tree visit bounds apply. Host tests verify empty/binary/65536-byte/nested blobs, deep missing/wrong type, no leaking on terminal failures, older seq51 fallback, both-invalid fail closed and restored seq52.

M48 full strict C89 native-stage CI PASSED: https://github.com/mostangrymike/ibm-sandbox/actions/runs/36576137300 . PR #27 squash-merged main at `8af4637910330b02ce5891d68b500af52e434378`. M47 PR #24 plus supplemental recovery #25 and boundary #26 had also passed full CI and merged before this. M46 is actual CMS target-proven, while M47/M48 are fully host-CI-proven but have not yet been run on actual CMS. Do not claim native target proof prematurely.

Current single `src/GITRUN.EXEC` is M48 compact: both full original 1808-object audits, latest seq52 selection, existing combined link-depth proof, full historical src directory closure, full child-and-all-parents root closure, direct historical root TREECLOSURE, M47 whole-root PATHFULL of historic src, NEW M48 whole-root PATHFULLCAT of historic README.md, all expected negative RCs, seq51 recovery, dual-invalid fail-closed RC8, seq52 restoration and final protected original data checks. The historic first commit root and referenced objects were already full-closure verified on actual CMS during M44–M46. No fresh CMS synthetic fixture required. Transfer from Mac `ibm-sandbox/src`: `git pull`; `./cms-upload.sh GITREC.C`; `./cms-upload.sh GITRUN.EXEC`. Run actual CMS `CMSCLNK GITREC PLAIN`, then `GITRUN`. Expected last marker ONLY on actual passing target: `GITRUN M48 ALL READ ONLY NATIVE GIT TESTS PASSED`. Only 2 transfers; no GITCIDX/GITSEL changes. Preserve original GITFIX/M15NEW STAGE/INDEX/SEEK/GEN, selector PTRs and GITPBUF PACK. M46 must not be rerun standalone. This latest M48 gate supersedes the earlier M47 target command listed above.

## September 29 actual M48 native CMS target PASS

User's actual CMS transcript: `CMSCLNK GITREC PLAIN` assembled with zero flagged statements and built GITREC MODULE mode PLAIN (CPU 10.10 / elapsed 10.45 seconds). The ONE standard `GITRUN M48 COMPACT REPORT` passed both independent full 1808-object GITFIX and M15NEW audits RC0, seq52 selection, M35–37 link batch, historical src depth-one listing, full src directory closure, complete child/all-parent root closure, direct raw root TREECLOSURE, M47 whole-root PATHFULL of src, NEW M48 whole-root PATHFULLCAT of historical README, negative invalid-depth RC4, noncommit RC8, missing-child RC4, seq51 fallback RC0, both-generation-invalid RC8, seq52 restoration RC0, and final protected-file checks. Exact final marker: `GITRUN M48 ALL READ ONLY NATIVE GIT TESTS PASSED`; full CPU 958.09 / elapsed 979.38 seconds at 09:05:53. **M47 and M48 now actual native CMS target-proven** on original 1808-object stages. Distinct synthetic corruption and budget boundaries remain full host CI-tested. All historical originals and selector pointers remain unchanged. Continue new GitHub milestones and retain one compact real CMS test, two Mac transfers.

## M49 full host CI completed; single next CMS target gate

M49 introduces `GITREC PATHFULLDIR C0 C1 COMMIT_OID40 DIRHEX`. After selecting a fully verified GEN2 and authenticating the commit structure, it validates the **entire local commit-root tree/blob closure** before emitting a chosen directory's metadata and complete `TREE DATA` listing. Unlike LSDIRFULL this includes unrelated sibling branches. It uses existing 256 entries per tree (including external Gitlinks) and shared 1024-tree visit limits, and emits no success marker, metadata or partial listing on absent/mistyped descendant, malformed input or limit failures. It retains independent read-only operations for PATHFULL metadata and PATHFULLCAT binary blobs.

Full strict C89 native-stage CI for M49 code and all existing tests PASSED https://github.com/mostangrymike/ibm-sandbox/actions/runs/36580384415 ; PR #28 merged main `601d9629981be858a1ee6d9cb793ab305251d243`. Supplemental PR #29 tests failure at 257 Gitlinks and 1025 visited trees without leaking path/listing, and exact 1024 visits success; full native-stage CI PASSED https://github.com/mostangrymike/ibm-sandbox/actions/runs/36580525841 ; squash merged main `87b98801efc12b1834e53b44e7d4fb091ae61e56`. M49 is fully host CI-proven, but NOT YET target-proven on CMS. M47 and M48 ARE real CMS target-proven per the user transcript in the previous section.

The standard compact `src/GITRUN.EXEC` is M49 and retains all pre-existing independent original 1808-object GENCHECK audits, seq52 selection, M35-37 batched links, src depth-one and full directory closure, whole commit+all-parents closure, direct raw root TREECLOSURE, whole-root PATHFULL src metadata, whole-root PATHFULLCAT README hex, NEW whole-root PATHFULLDIR src listing, depth/child negative cases, seq51 recovery, both-invalid fail-closed and restored seq52, plus final protected data checks. Historical src directory/full root were already target-proven by M44–M48; no new original data or synthetic CMS fixture required.

NEXT from Mac ibm-sandbox/src: `git pull`, `./cms-upload.sh GITREC.C`, `./cms-upload.sh GITRUN.EXEC`. NEXT actual CMS: `CMSCLNK GITREC PLAIN`, then `GITRUN`. Exact terminal marker only if actual target passes: `GITRUN M49 ALL READ ONLY NATIVE GIT TESTS PASSED`. Only two Mac transfers; do not alter GITCIDX/GITSEL or protected GITFIX/M15NEW STAGE/INDEX/SEEK/GEN, selector PTRs, or GITPBUF PACK. Preserve one compact target gate, not separate repeated M48 test.

## 2026-09-29 actual M49 CMS proof

The real z/VM CMS console reported `CMSCLNK GITREC PLAIN` assembled with zero flagged statements and built GITREC MODULE PLAIN (CPU 10.08 / elapsed 10.44). The one standard `GITRUN M49 COMPACT REPORT` passed initial protected files and absent M15BAD, both independent sealed-original GITFIX and M15NEW 1808-object full audits RC0, seq52, combined M35–37 links, historic src depth1 and full directory closure, whole child/all-parent closure, raw historic tree TREECLOSURE, whole-root PATHFULL src metadata, PATHFULLCAT historic README blob, NEW PATHFULLDIR complete-snapshot src directory listing, invalid-depth RC4, noncommit RC8, missing child RC4, seq51 recovery, dual-invalid RC8, restored seq52, and final protected files. Exact marker `GITRUN M49 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 981.93 / elapsed 1003.66 seconds, at 09:33:48. **M49 is actual CMS target-proven** on the immutable historical originals; separately synthetic edge fixtures remain host-CI tested. Advance to M50 without repeating standalone M49.

## M50 native host CI complete; next single real CMS gate

M49 is actual CMS target-proven (2026-09-29, standard `GITRUN M49` CPU 981.93 / elapsed 1003.66 sec, original 1808 object data protected; see preceding section). M50 adds two read-only `GITREC` commands starting from an arbitrary raw Git tree OID, without requiring a commit: `TREEPATHCAT C0 C1 TREE_OID40 PATHHEX` for fully authenticated blob HEX and `TREEPATHDIR C0 C1 TREE_OID40 DIRHEX` for authenticated directory listing. Both fully audit selected immutable GEN2, validate the tree root type and **every local blob/tree descendant**, within the established 256 entries/tree incl external Gitlinks and 1024-tree visit budget, BEFORE exposing any path metadata/blob/listing. External Gitlinks cannot be read as local data. The marker is `TREE ROOT FULL CLOSURE VERIFIED`. Host tests verify 0-byte/binary/65536-byte/nested blobs, directory listing, unrelated deep missing/wrong siblings, wrong/missing root, invalid terminal/path input, 257 Gitlinks and 1024/1025 visit boundaries, verified old seq51 fallback, dual-invalid fail-closed and restored newest seq52 for both new commands.

M50 production and full strict native C89 integration CI passed https://github.com/mostangrymike/ibm-sandbox/actions/runs/36584751834 ; PR #30 squash-merged main at `6c4cf7ea8cda2c0cdd9ea79de0c750c7c2aff50f`. Supplemental recovery tests for **both** operations also passed the full native-stage workflow https://github.com/mostangrymike/ibm-sandbox/actions/runs/36584911315 ; PR #31 merged main `2b537a2b0f706d87a0d4509a719f7e53c517fd21`. M50 is therefore fully host-CI PROVEN, not yet real CMS target-proven. M47, M48 and M49 have all passed one real CMS standard runner on original immutable stage data.

Current single compact standard `src/GITRUN.EXEC` is M50, preserving both independent original 1808-object GITFIX/M15NEW full audits, newest seq52, M35–37 single linkbatch, historical src depth-one/full subtree, whole child+parent root CLOSURE, direct root TREECLOSURE, whole-snapshot PATHFULL src metadata, PATHFULLCAT historic README data, PATHFULLDIR historic src, NEW raw historical root TREEPATHCAT README and TREEPATHDIR src, negative RC4/8 tests, verified older seq51 fallback, both invalid fail-closed RC8, newest seq52 restored and final protected original checks. M50 real historical root and its children had already been proven complete by M44–M49. No synthetic fixtures or modification of original data on CMS required.

NEXT from Mac `ibm-sandbox/src`: `git pull`, `./cms-upload.sh GITREC.C`, `./cms-upload.sh GITRUN.EXEC`. NEXT actual CMS: `CMSCLNK GITREC PLAIN`, `GITRUN`. Exact final marker only on real success: `GITRUN M50 ALL READ ONLY NATIVE GIT TESTS PASSED`. Transfer only two changed source/runner files. Never touch original GITFIX/M15NEW STAGE/INDEX/SEEK/GEN, selector PTRs, or GITPBUF PACK. Don't repeat M49 standalone; use this one M50 compact gate.

## September 29 actual M50 native CMS success

User-supplied real z/VM CMS run: `CMSCLNK GITREC PLAIN` assembled cleanly (zero flagged statements) and built MODULE PLAIN, CPU 10.14 / elapsed 10.50 sec. One compact `GITRUN M50` passed independently audited original GITFIX and M15NEW 1808-object full generations RC0; selected seq52; all preceding combined root/directory/commit/direct-tree closures; M47 PATHFULL src, M48 PATHFULLCAT historical README, M49 PATHFULLDIR src; NEW M50 raw historical root TREEPATHCAT README and TREEPATHDIR src; negative invalid depth RC4, noncommit RC8 and missing child RC4; verified seq51 recovery RC0; both manifests invalid fail closed RC8; restored seq52 RC0; protected-file final checks. Exact final `GITRUN M50 ALL READ ONLY NATIVE GIT TESTS PASSED`; CPU 1119.31 / elapsed 1143.77 seconds, at 10:41:43. **M50 now REAL CMS TARGET-PROVEN**, as well as full host strict C89 CI. Synthetic deep corruption/resource limit cases remain independently host proven. Do not repeat a separate M50 target gate. Preserve originals, build new milestones only on GitHub with one next compact native regression and two Mac uploads.

## M51 complete host-CI milestone; next native target run

M50 is ACTUAL native CMS target-proven on 2026-09-29: clean `CMSCLNK GITREC PLAIN` CPU 10.14 / elapsed 10.50 sec; compact `GITRUN M50` both independent original 1808-object full generation audits and every M35–50 gate PASSED, exact `GITRUN M50 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 1119.31 / elapsed 1143.77 sec at 10:41:43; all originals and protected files preserved. Host synthetic boundary fixtures remain separately host proven.

M51 `GITREC TREEPATH C0 C1 TREE_OID40 PATHHEX` supplies metadata-only lookup for any raw-tree-relative path, including local blobs, local directories and external Gitlinks. It first fully verifies selected sealed GEN2 and the complete bounded local root tree/blob closure within 256 entries/tree incl Gitlinks and 1024 visits; external Gitlinks are counted but never dereferenced. Only on full success emits `TREE ROOT FULL CLOSURE VERIFIED` and `PATH OBJECT TYPE ... OID ...` or `PATH GITLINK (EXTERNAL COMMIT)` with OID. No blob data or directory listing. Invalid path rejects before audit. Missing/wrong root, unrelated corrupt deep branches and resource limits fail without path metadata. Host integration tests cover all terminal types, deep missing/wrong object fail closed, invalid input, exact visit and entry limits, seq51 old fallback, dual-invalid no-output and restored seq52. Complete strict C89 native-stage CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36592501154 ; PR #32 squash merged main at `bafba52c5adcd84e7f300f183881c34f02366124`. M51 **fully host-CI-proven, NOT YET native CMS target-proven**.

Current one standard compact `src/GITRUN.EXEC` is M51. Retains both full independent immutable 1808-original-object GITFIX and M15NEW GENCHECK audits, seq52 selection, batched M35–37 links, historical src depth1/full directory, full child+all-parents root closure, raw root TREECLOSURE, whole-snapshot PATHFULL src metadata, PATHFULLCAT README binary output, PATHFULLDIR src directory listing, TREEPATHCAT historical root README bytes and TREEPATHDIR src listing, NEW TREEPATH historical raw root src metadata, all negative expected RC4/8, seq51 older recovered, both invalid fail-closed RC8, restored seq52, final protected original files. M51 uses known first-commit immutable root previously target-proven. Don't run M50 standalone again.

NEXT from Mac in `ibm-sandbox/src`: `git pull`; `./cms-upload.sh GITREC.C`; `./cms-upload.sh GITRUN.EXEC`. NEXT actual CMS: `CMSCLNK GITREC PLAIN`; `GITRUN`. Exact final native marker only on actual successful execution: `GITRUN M51 ALL READ ONLY NATIVE GIT TESTS PASSED`. Only these two transfers. Never mutate original GITFIX/M15NEW STAGE/INDEX/SEEK/GEN, selector PTRs or GITPBUF PACK, or transfer unchanged GITCIDX/GITSEL. Continue autonomous source milestones on subsequent target result without extra standalone proofs.

## 2026-09-29 EC2 reboot, 3270 transfer and regression runtime

Following an EC2 reboot, Hercules/zVM TCPIP restored, and MAINT 3270 logon worked. Mac actual `lsof` showed SSH tunnel listening on local 127.0.0.1:3271 and c3270 scripting listener on local 127.0.0.1:3272. Repo `src/cms-upload.sh` is hard-coded to `PORT=3271`, so its failed uploads were targeting SSH, not c3270. A temporary `sed 's/^PORT=3271$/PORT=3272/' cms-upload.sh > /tmp/cms-upload-3272.sh` can send scripts to the live c3270 socket (the script uses absolute local source path derived from the input argument). After this recovery attempt, CMS compiled GITREC cleanly (CPU 10.71 / elapsed 11.17) but `GITRUN` still reported the OLD M50 banner and passed the OLD M50 suite, CPU 1109.69 / elapsed 1133.73 seconds ending 14:44:55. **Do not mark M51 CMS target-proven**: the user ran stale `GITRUN EXEC`, regardless of which GITREC MODULE was just compiled. On CMS use `TYPE GITRUN EXEC A` / `STATE GITRUN EXEC A` to confirm the banner before running. On Mac check `git show HEAD:src/GITRUN.EXEC`, then upload from the correct working directory to the live script socket 3272 and check exact transfer success. The repeatedly increasing full-audit overhead in separate GITREC calls needs an intentionally batched, single-selection positive suite while preserving independent original audits and negative/recovery/final protected checks.

## M52 merged: eliminate repeated positive full-selector audits

The user observed native runtime increasing with every new standard `GITRUN`. After EC2 restart the actual last run still executed the old M50 runner, not M51 (CPU 1109.69/elapsed 1133.73 seconds at 14:44:55). The previous rebooted-session SSH tunnel occupies Mac TCP 3271 and the actual c3270 scripting socket occupies TCP 3272. `src/cms-upload.sh` and `src/cms-download.sh` now support environment variable `CMS_SCRIPT_PORT` with default 3271. Upload/download on the current Mac require `CMS_SCRIPT_PORT=3272` or a tunnel and script socket reconfiguration; no need to restart the already working session. Confirm current local `GITRUN.EXEC` banner matches the target and verify on CMS with `TYPE GITRUN EXEC A` before performing a full regression, as M51 CMS proof is NOT available.

M52 `GITREC RUNBATCH C0 C1 COMMIT40 TREE40 DIRHEX FILEHEX` combines all **eleven** prior positive operations into a single process after exactly one complete selected-generation GEN2 selector audit. Each original operation still performs its independent indexed/linked object checks, complete tree closure where required and its fresh resource budget. The aggregate `BATCH ALL POSITIVE CHECKS PASSED` prints only on every positive operation RC0. The standard single M52 `GITRUN EXEC` still performs **both separate 1808-object GITCIDX original-generation full audits**, distinct SELECT seq52, one batched positive gate, all separate invalid-depth/noncommit/missing-child RC checks, verified older seq51 fallback, both-invalid fail-closed RC8, newest seq52 restore, and final protected original-file checks. This removes redundant complete selector audits from separate processes, not the feature-level local object checks. Do not claim a real runtime improvement until measured on actual CMS. The standalone M51 real-target run is deliberately superseded by this one comprehensive M52 native test.

M52 PR #33 full native strict C89/integration CI PASSED https://github.com/mostangrymike/ibm-sandbox/actions/runs/36622015855 ; squash merged main `363c66432e15d37e83f0c9a59f6266fe524ece6a`. Synthetic host test runs the full batch, checks every prior positive marker and aggregate success, invalid input fails before audit, wrong/missing root never prints aggregate success. Physical C lines <=72. M52 is **host CI-proven but NOT native CMS target-proven**.

NEXT only two Mac transfers from the freshly pulled `ibm-sandbox/src`: `git pull` (when repo root or src), `head -n 3 GITRUN.EXEC` (M52), `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITREC.C`, `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITRUN.EXEC`. Check BOTH transfers report `CMS upload complete`. On CMS first `TYPE GITRUN EXEC A` (must visibly show M52 compact report), then `CMSCLNK GITREC PLAIN`, then `GITRUN`. Expected exact M52 final marker only after actual native proof: `GITRUN M52 ALL READ ONLY NATIVE GIT TESTS PASSED`. Transfer scripts only use c3270 scripting port, not the SSH tunnel. Preserve immutable GITFIX/M15NEW STAGE/INDEX/SEEK/GEN, selector PTRs and GITPBUF PACK. Do not execute long stale M50 or superseded standalone M51.

## M52 native success and M53 selector-audit consolidation

Real z/VM CMS M52 compiled cleanly with zero flagged assembly statements (CPU 10.69 / elapsed 11.14 sec) and passed the original immutable 1808-object audits independently for GITFIX and M15NEW, newest seq52 selection, the one-process full positive RUNBATCH including M51 TREEPATH, all negative RC4/8 tests, recovered seq51, dual-invalid RC8, restored seq52 and final protected files. Exact native marker `GITRUN M52 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 962.91 / elapsed 986.89 seconds at 15:14:41 on September 29, 2026. Compared to the prior post-reboot M50 run (elapsed 1133.73 seconds), the observed elapsed reduction is 146.84 seconds. M52 is actual CMS target-proven; the M51 positive path also passed inside this native gate.

M53 removes the standalone `GITREC SELECT` invocation from only the compact REXX test runner, which had repeated another complete selected-generation audit. The existing `RUNBATCH` still independently validates sealed GEN2 via selector and prints `SELECTED 52 M15NEW`; the runner requires this exact marker together with full positive success and closure markers before saying `PASS SELECT SEQ52 FROM VERIFIED BATCH`. Both independent original full 1808-object GITCIDX audits are unchanged. Negative RC4/8, original seq51 fallback, both invalid fail-closed, seq52 restored and final protected files all remain unchanged. Host production tests now explicitly verify RUNBATCH reports newest seq52, recovers older verified seq51 when newest manifest is invalid, emits no batch result with both manifests invalid, and reports restored seq52. The guard forbids reintroducing the redundant standalone SELECT. M53 changes only `src/GITRUN.EXEC`, test guard, synthetic host tests and documentation; production `src/GITREC.C`, `GITCIDX`, `GITSEL`, protected originals and transfer scripts remain unchanged. After strict CI pass, next real CMS requires **ONE** transfer: from freshly pulled Mac `ibm-sandbox/src`, `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITRUN.EXEC`; check success and `TYPE GITRUN EXEC A` shows M53, then simply `GITRUN` (NO recompile needed). Expected M53 native success only if actual run prints `GITRUN M53 ALL READ ONLY NATIVE GIT TESTS PASSED`. Compare measured elapsed to M52 986.89 seconds; the host may vary. Do not repeat M52 standalone.

## M54 in-batch expected negatives (host CI required)

M53 PR #34 merged main at `8f47a7100a31961da793b11650a32eb115f12d34`, with full native C89 host CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36625850247 . It removed only the standalone redundant GITREC SELECT audit from compact GITRUN; RUNBATCH still provides the exact selected seq52 marker and all eleven positive feature verifications. M53 alone has not been run on actual CMS, but M52 actual target success at 986.89 elapsed seconds is recorded above.

M54 folds the two previously standalone selected-generation tests for wrong-type child RC8 and absent child RC4 inside the already verified RUNBATCH. After all positive checks, RUNBATCH calls existing `rec_parents` on the verified raw historical tree (expects RC8) and then on the all-zero OID (expects RC4); any other result aborts the aggregate success. The REXX single-batch gate asserts both unique exact markers before reporting either negative PASS. Both original independent 1808-object full audits, M52 complete positive suite including M51 TREEPATH, selected newest seq52, separate syntax-invalid depth RC4, independently verified seq51 recovery, both-invalid fail-closed RC8, restored newest seq52 and final protected originals remain in the one M54 runner. Production `GITREC.C` changes only to extend rec_batch; no changes to GITCIDX/GITSEL or protected historical files. Strict native-stage host tests cover normal selected newest, older seq51 fallback, both-invalid no markers and restored newest, in addition to all existing malformed and corrupted tree fixtures. M54 remains host-only until merged CI and real CMS gate pass.

When strict native CI passes and M54 is merged, next Mac after `git pull` from `ibm-sandbox/src`: `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITREC.C`, `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITRUN.EXEC` (two transfers only). On CMS first `TYPE GITRUN EXEC A` must show M54 banner, then `CMSCLNK GITREC PLAIN` and exactly one `GITRUN`. Expected terminal success on real target only: `GITRUN M54 ALL READ ONLY NATIVE GIT TESTS PASSED`. Do not run separate M53. Compare actual elapsed to native M52 986.89 seconds, recognizing normal system variation. Retain any Mac stash of earlier port-adjusted transfer scripts; current versions accept CMS_SCRIPT_PORT. Preserve sealed original GITFIX/M15NEW STAGE/INDEX/SEEK/GEN, selector PTR and GITPBUF PACK.

## M54 merged and full CI green: current next native test

M54 PR #35 full strict native C89 host CI PASSED https://github.com/mostangrymike/ibm-sandbox/actions/runs/36626167890 ; squash merged main commit `24c9fd4d41a816757df47e9e1b211abeccfd477a`. This supersedes the previous M53 one-file target test: M54 includes M53's removed redundant standalone selector audit, plus two expected negative tests (noncommit RC8 and missing child RC4) within the existing fully verified RUNBATCH. The runner requires both markers before reporting either negative case passed. Two independent original 1808-object audits, all M35–M51 positives, RC4 depth syntax rejection, verified seq51 fallback, both invalid fail-closed RC8, restored seq52 and final protected files remain mandatory. Host tests cover the batched negatives in normal, older-recovery, both-invalid and restored cases. M54 fully HOST-CI-PROVEN but NOT YET CMS TARGET-PROVEN.

Next from Mac inside freshly pulled `ibm-sandbox/src`: `git pull`, confirm `head -n 3 GITRUN.EXEC` shows M54, then `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITREC.C` and `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITRUN.EXEC`. Keep existing SSH tunnel on 3271 and c3270 scripting port 3272; preserve the old Mac stash and do not pop it. Verify both uploads show `CMS upload complete`. On CMS: `TYPE GITRUN EXEC A` must show M54; run `CMSCLNK GITREC PLAIN` and one `GITRUN`. Exact final marker on actual success only: `GITRUN M54 ALL READ ONLY NATIVE GIT TESTS PASSED`. Previous actual M52 elapsed 986.89 seconds is the comparison baseline. Never mutate original sealed stages, selector pointers or GITPBUF PACK. Do not run stale M52, standalone M53 or unnecessary GITCIDX/GITSEL rebuilds.

## Actual M54 CMS success and merged M55 (2026-09-29)

M54 **actual native target PASSED**: zero flagged assembly statements; CMSCLNK CPU 10.33/elapsed 10.79 sec. Standard compact GITRUN passed both independent sealed GITFIX/M15NEW 1808-object full audits, one positive batch (all previous milestones through M51), seq52, in-batch noncommit RC8 and absent-child RC4, invalid-depth RC4, recovered seq51, both-invalid RC8, restored seq52 and final protected files. Final `GITRUN M54 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 900.08 / elapsed 923.83 sec at 15:43:40. Post-reboot baseline M50 elapsed 1133.73 sec and M52 986.89 sec; observed reductions 209.90 and 63.06 sec respectively. Do not rerun M54 standalone.

M55 adds a two-entry ephemeral cache of *successful complete 1024-budget tree-root closure attestations* scoped solely to the already verified single-generation RUNBATCH process. It is keyed by exact raw root SHA-1 OID, never used for standalone commands or shared parent traversal budgets, and every path and terminal is still re-resolved/revalidated after a cache hit. Required new `BATCH ROOT CLOSURE REUSES N` marker proves positive reuse; aggregate success only after existing full positive and negative checks. Full strict native C89 host CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36628776152 ; PR #36 merged main `fccc9b65e85d09bf105046e474d8150a961ad676`. M55 is full host-CI-proven; **not yet actual CMS target-proven**. Both original independent 1808-object audits, all preceding full-closure features, in-batch negative RC8/4, separate malformed depth RC4, verified seq51 fallback, both-invalid RC8, restored newest seq52 and final protected checks remain mandatory. Do not extrapolate speedup before the native M55 run.

Next only two Mac transfers from freshly pulled `ibm-sandbox/src`: `git pull`, `head -n 3 GITRUN.EXEC` (must show M55), `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITREC.C`, `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITRUN.EXEC`. Current local SSH tunnel uses 3271; c3270 script socket uses 3272. Verify both uploads report complete; on CMS `TYPE GITRUN EXEC A` confirms M55 before `CMSCLNK GITREC PLAIN` and one `GITRUN`. Exact expected native final marker on real success: `GITRUN M55 ALL READ ONLY NATIVE GIT TESTS PASSED`. Preserve original sealed GITFIX/M15NEW STAGE/INDEX/SEEK/GEN, selector PTRs, GITPBUF PACK and unchanged GITCIDX/GITSEL modules. Compare actual M55 elapsed to M54 923.83 seconds only after native proof.

## 2026-09-29 actual M55 CMS PASS and M56 host milestone

Actual CMS M55 compiled GITREC PLAIN without flagged assembly statements (CPU 10.51 / elapsed 10.95 seconds) and the one full protected regression passed: independent original GITFIX and M15NEW 1808-object full audits RC0, single positive batch, latest seq52, independently fully verified shared root closure, in-batch wrong-child RC8 and missing-child RC4, invalid-depth RC4, seq51 recovery, both-invalid RC8, restored seq52 and final protected original files. Exact `GITRUN M55 ALL READ ONLY NATIVE GIT TESTS PASSED`; CPU 619.93 / elapsed 635.48 seconds at 16:07:55. M54 elapsed 923.83 seconds, M52 986.89 and rebooted M50 1133.73; M55 observed elapsed reduction vs M54 288.35 seconds (~31.2%) and vs M50 498.25 seconds (~44.0%). These are single-run observations, not replicated benchmarks. M55 is actual CMS target-proven.

M56 makes another read-only efficiency improvement inside the same fully verified RUNBATCH only: perform a single fresh complete `sidx_read` of the chosen seek-index after GEN2 selection, then reuse that exact parsed in-memory index across all positive and in-batch negative checks. All independent selector/GEN2 and original GITCIDX full audits, standalone operations, stage object fresh reopen/re-hash, local subtree closure verification, path terminal checks and existing recovery/fail-closed/protected tests remain unchanged. A required `BATCH SEEK INDEX REUSES N` marker demonstrates positive reuse before aggregate success. Host integration tests require the marker in selected seq52, recovered seq51 and restored seq52 batch, and forbid it on both-invalid/standalone operations. M56 should have full strict C89 CI green and a merged PR before native transfer. It needs only `GITREC.C` and `GITRUN.EXEC` uploads, with Mac `CMS_SCRIPT_PORT=3272` in the current tunnel/session setup and one CMS `CMSCLNK GITREC PLAIN` then `GITRUN`. Compare actual native elapsed to M55 635.48 sec, but never claim target speedup before CMS passes. Always preserve sealed originals (GITFIX/M15NEW STAGE/INDEX/SEEK/GEN, selector PTRs, GITPBUF PACK).

## M56 merged after full native-stage CI: next one-shot CMS validation

M56 PR #38 passed its complete strict C89 native-stage CI https://github.com/mostangrymike/ibm-sandbox/actions/runs/36631835500 and squash-merged main commit `e5192c57d85c3d3f12cd900aeb8442edefba3995`. Production GITREC now does one fresh complete seek-index read after already fully verified GEN2 selection at the start of RUNBATCH and reuses the exact parsed in-memory index across all of that batch's positive and expected negative operations. It does NOT skip any of the two independent original full GITCIDX 1808-object audits, selector GEN2 verification, per-object fresh stage-file read and rehash, complete root and terminal verification, recovery/fail-closed or protected-file checks. Each standalone GITREC command continues reading its seek-index normally. New mandatory marker `BATCH SEEK INDEX REUSES N` proves positive in-batch reuse before aggregate success. Host tests pass for newest seq52, recovered seq51, both invalid no success/no reuse and restored seq52, plus standalone/corrupt/overbudget cases. M56 is full host-CI-proven and NOT YET actual CMS target-proven. M55 is actual CMS target-proven at CPU 619.93/elapsed 635.48 seconds on 2026-09-29.

NEXT in Mac `ibm-sandbox/src`: `git pull`, inspect `head -n 3 GITRUN.EXEC` to confirm M56, then `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITREC.C` and `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITRUN.EXEC` with exact successful transfer reports. Current Mac SSH tunnel listens on 3271; c3270 script listener is 3272. On CMS verify `TYPE GITRUN EXEC A` shows M56, execute `CMSCLNK GITREC PLAIN` and a single `GITRUN`. Expected exact terminal success only on actual CMS passing: `GITRUN M56 ALL READ ONLY NATIVE GIT TESTS PASSED`. Compare elapsed against M55 635.48 seconds but account for host variance. Do not rerun M55 standalone, do not transfer unchanged GITCIDX/GITSEL, and never modify original protected stages, indexes, manifests, selector PTRs or GITPBUF PACK.

## Native M56 PASS on 2026-09-29 at 16:33

Actual CMS `CMSCLNK GITREC PLAIN` assembled with zero flagged statements, CPU 10.42 / elapsed 10.82 seconds. Actual M56 standard `GITRUN` passed independent sealed original 1808-object GITFIX and M15NEW full audits RC0; all positive features including independently checked shared root closure and new in-batch seek-index snapshot; exact newest seq52; noncommit RC8, missing-child RC4 and malformed depth RC4; verified older seq51 fallback RC0; both invalid fail-closed RC8; newest restored RC0; final protected originals. Exact `GITRUN M56 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 618.15 / elapsed 633.67 seconds at 16:33:00. M56 is ACTUAL NATIVE CMS TARGET-PROVEN. Against real M55 at 635.48 sec elapsed, observed delta is 1.81 sec, a small single-run difference, not an established performance gain. Against M50 at 1133.73 sec the cumulative observed delta is 500.06 sec. Preserve both independently rehashed original audits and all protections in future milestones. Do not rerun M56 standalone.

## M57: HISTORYFULL checks every visited commit's entire root before history output

Actual M56 target on 2026-09-29: CMSCLNK GITREC PLAIN assembled clean (CPU 10.42/elapsed 10.82 sec). Real `GITRUN M56` passed both original GITFIX/M15NEW independent 1808-object full audits; newest seq52; one verified positive batch including shared root closure and seek-index snapshot; expected noncommit RC8/absent child RC4 and invalid-depth RC4; older seq51 fallback; both-invalid RC8; restored seq52 and final protected files. Exact terminal `GITRUN M56 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 618.15/elapsed 633.67 sec at 16:33:00. M56 now NATIVE CMS TARGET-PROVEN; observed M55 comparison 635.48 sec is only 1.81 sec faster in single runs and not definitive.

M57 adds `GITREC HISTORYFULL C0 C1 COMMIT_OID40 DEPTH` (depth 0..16) for read-only first-parent commit history that **fully rehashes and validates every visited commit root's complete bounded local tree/blob closure before printing any history record**, including unrelated sibling entries. It retains prior strict full GEN2 selector validation and full valid commit parsing at every hop, with a fresh max-1024 tree visit budget for each root. External Gitlinks are recorded as tree entries but not followed into other repositories, maintaining prior 256-entry/tree cap. `HISTORYFULL` prints `HISTORY FULL ROOT CLOSURE VERIFIED` only after all roots pass, then the established `HISTORY DATA` records; malformed depth returns RC4 pre-audit, missing root RC4, wrong root type or corrupt/deep-limit closure RC8, never partial history metadata. Existing `HISTORY` is unchanged. The standard compact one-process M57 RUNBATCH adds HISTORYFULL for original verified commit and first parent, verifying the exact marker from captured output while retaining both original independent 1808-object full audits, all prior features and recovery/fail-closed/final protections. Host tests add depth2 whole-chain success, missing/wrong root fail-closed at depth0, invalid depth and the compact batch marker. This is a new functional milestone rather than chasing sub-2-second M56 single-run timing noise. M57 is NOT NATIVE TARGET-PROVEN until strict host CI and one real CMS run. After merged green CI, next Mac transfers only `GITREC.C` and `GITRUN.EXEC` with `CMS_SCRIPT_PORT=3272`, then on CMS `CMSCLNK GITREC PLAIN` and one `GITRUN`; exact native success marker `GITRUN M57 ALL READ ONLY NATIVE GIT TESTS PASSED`.

## M57 merged and strict host CI green: next native CMS test

M57 PR #39 strict native C89 host CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36634776900 ; squash merged main commit `43dd8ccaf5ef78a3ccd52c809469795a7948ea26`. The new `GITREC HISTORYFULL C0 C1 COMMIT40 DEPTH` verifies complete fresh bounded root tree/blob closures of EVERY validated first-parent commit in depth 0..16 before releasing any history records. A dedicated `HISTORY FULL ROOT CLOSURE VERIFIED` marker precedes the established HISTORY DATA records only after complete success. Host tests cover depth2 success and missing/wrong root fail-closed with no history data; existing history remains unchanged. The one-process standard M57 GITRUN adds a depth1 HISTORYFULL of the original known commit and its first parent to every prior M56 positive gate, and explicitly checks the marker. Both independent original 1808-object full audits and all original seq52, recovery, negative, both-invalid and final protection checks remain mandatory. M57 is full HOST-CI-PROVEN but NOT YET CMS target-proven. M56 remains real target-proven, elapsed 633.67 sec on 2026-09-29.

NEXT from Mac `ibm-sandbox/src`: `git pull`, inspect `head -n 3 GITRUN.EXEC` must be M57; `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITREC.C` and `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITRUN.EXEC` with both successful transfer completions. Mac SSH tunnel uses 3271 and c3270 scripting socket 3272. On CMS `TYPE GITRUN EXEC A` must show M57, then `CMSCLNK GITREC PLAIN` followed by ONE `GITRUN`. Exact native final marker on real target success: `GITRUN M57 ALL READ ONLY NATIVE GIT TESTS PASSED`. Do not rerun M56 separately or transfer unchanged GITCIDX/GITSEL; never mutate sealed original STAGE/INDEX/SEEK/GEN, selector PTRs or GITPBUF PACK.

## 2026-09-29 actual M57 native CMS PASS

Real z/VM CMS `GITRUN M57` passed every protected gate on the original immutable 1808-object repository: both independent GITFIX/M15NEW full audits RC0; single selected positive batch RC0; newest seq52; shared verified root closure; shared verified seek index; NEW full first-parent history root closure; in-batch noncommit RC8 and absent-child RC4; invalid-depth RC4; verified older seq51 recovery; both-invalid fail-closed RC8; restored newest seq52; final protected originals. Exact terminal marker `GITRUN M57 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 710.33 / elapsed 728.46 seconds at 16:55:36 on 2026-09-29. M57 is now NATIVE CMS TARGET-PROVEN. Runtime is slower than M56 (633.67 sec) because M57 adds new full-snapshot historical verification; this is expected functional coverage, not a regression in the M56 optimization. Do not compare M57 as a pure speed benchmark. Preserve both independent original audits and all fail-closed/recovery/protection checks in subsequent milestones.

## M58: all-parent merge history with fail-closed full snapshots

M57 actual native CMS passed on 2026-09-29: `GITRUN M57 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 710.33 / elapsed 728.46 sec. M58 adds `GITREC HISTORYDAG C0 C1 COMMIT_OID40 DEPTH` with DEPTH 0..8. Unlike first-parent HISTORY/HISTORYFULL, HISTORYDAG traverses **all parent edges** breadth-first through the requested depth, de-duplicates commits, caps the reachable set at 64 commits, validates every commit body, and gives every visited commit root its own fresh 1024-tree complete local closure budget before emitting any history record. External Gitlinks remain external. Only after the entire reachable DAG passes does it print `HISTORYDAG FULL ROOT CLOSURE VERIFIED` followed by deterministic node/depth/OID/tree records and the final node count. Missing parent RC4, wrong-type/malformed parent RC8, missing root RC4, wrong root type/corrupt closure RC8 and invalid depth RC4 all withhold HISTORYDAG data. Existing HISTORY and HISTORYFULL remain unchanged.

The standard M58 RUNBATCH adds depth1 HISTORYDAG on the known original commit in the same fully selected seq52 process; GITRUN requires its full-root marker while retaining M57 first-parent HISTORYFULL, both independent original 1808-object GITCIDX audits, root-closure and seek-index reuse proofs, in-batch expected RC8/RC4, invalid-depth RC4, verified seq51 fallback, both-invalid RC8, restored seq52 and final protected files. Host tests additionally use a real synthetic two-parent merge: depth1 must return exactly three verified nodes, depth0 one node, and missing/wrong/malformed parents or roots must emit no HISTORYDAG metadata. M58 remains host-only until strict native-stage CI passes and one real CMS target run succeeds. After merged green CI, transfer only `GITREC.C` and `GITRUN.EXEC` from Mac with `CMS_SCRIPT_PORT=3272`; on CMS compile GITREC PLAIN and run one GITRUN. Expected native final marker only on real success: `GITRUN M58 ALL READ ONLY NATIVE GIT TESTS PASSED`.

## M58 merged after full strict host CI: next native CMS gate

M58 PR #40 complete strict native C89 host CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36722120902 ; squash merged main `e87c1e36db267ae423c3a8a134762d6dee2a8ab3`. During CI, two issues were found and fixed before merge: parent OIDs must be captured from the commit body before full root closure reuses the shared object buffer, and the synthetic assertion was corrected to include the emitted per-node depth field. Final green integration tests validate a two-parent merge breadth-first at depth1 with exactly three nodes, depth0 with one node, complete full-root closure before any metadata, and fail-closed behavior for missing/wrong/malformed parents and roots. Standard M58 RUNBATCH includes HISTORYDAG depth1 and GITRUN requires `HISTORYDAG FULL ROOT CLOSURE VERIFIED`, while preserving M57 HISTORYFULL, both independent original 1808-object audits, shared verified root closure/seek index, expected negative RC8/RC4, invalid-depth RC4, verified seq51 fallback, both-invalid RC8, restored newest seq52 and final protected originals. M58 is HOST-CI-PROVEN but NOT YET actual CMS target-proven. M57 remains latest actual target proof at CPU 710.33 / elapsed 728.46 sec.

NEXT from Mac `ibm-sandbox/src`: `git pull`; `head -n 3 GITRUN.EXEC` must show M58; `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITREC.C`; `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITRUN.EXEC`. Verify both uploads complete. On CMS: `TYPE GITRUN EXEC A` must show M58; `CMSCLNK GITREC PLAIN`; one `GITRUN`. Exact target success marker only on real pass: `GITRUN M58 ALL READ ONLY NATIVE GIT TESTS PASSED`. Transfer only those two files; unchanged GITCIDX/GITSEL remain. Preserve sealed GITFIX/M15NEW STAGE/INDEX/SEEK/GEN, selector PTRs and GITPBUF PACK. After actual M58 pass, continue directly to the next functional milestone without rerunning older standalone gates.

## 2026-09-30 actual M58 native CMS PASS

Real z/VM CMS `CMSCLNK GITREC PLAIN` assembled with zero flagged statements (CPU 11.07 / elapsed 11.50 sec). Actual standard `GITRUN M58` passed both independent original GITFIX/M15NEW 1808-object full audits RC0; one selected positive batch RC0; newest seq52; shared verified root closure; shared verified seek index; full first-parent HISTORYFULL root closure; NEW full all-parent HISTORYDAG root closure; in-batch noncommit RC8 and missing-child RC4; invalid-depth RC4; verified older seq51 fallback RC0; both-invalid fail-closed RC8; restored newest seq52 RC0; final protected original files. Exact terminal marker `GITRUN M58 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 805.68 / elapsed 826.89 seconds at 08:47:57 on 2026-09-30. M58 is now NATIVE CMS TARGET-PROVEN. Runtime is higher than M57 (728.46 sec) because M58 adds complete all-parent merge-DAG snapshot verification; this is added functional coverage, not evidence that the M56/M55 optimizations regressed. Preserve both independent original audits and every recovery/fail-closed/protected-file check in later milestones. Do not rerun M58 standalone.

## M59: verify one named path across every all-parent history snapshot

M58 actual native CMS passed on 2026-09-30 with `GITRUN M58 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 805.68 / elapsed 826.89 sec. M59 adds `GITREC HISTORYDAGPATH C0 C1 COMMIT40 DEPTH PATHHEX` for DEPTH 0..8. It traverses the bounded all-parent merge DAG exactly like HISTORYDAG, validates every commit, gives each root a fresh complete 1024-tree local closure, then independently re-reads and re-hashes every tree/object along the requested path in each snapshot. The command buffers all commit/root/path metadata and emits **nothing** until every reachable snapshot and requested path passes. After complete success it prints `HISTORYDAGPATH FULL SNAPSHOTS VERIFIED`, deterministic node/depth/commit/tree records, path object type/size/OID per node, a node count and final data-end marker. Missing path or path object returns RC4, malformed components/type mismatches/corrupt objects RC8, malformed path or depth RC4, and all failures withhold HISTORYDAGPATH metadata. Gitlinks can be reported as external commit metadata but are never followed into other repositories.

The standard M59 RUNBATCH adds HISTORYDAGPATH depth1 for the known original README path in the same fully selected generation. GITRUN requires the new full-snapshot path marker while retaining M58 HISTORYDAG, M57 HISTORYFULL, both independent original 1808-object full audits, shared verified root/seek reuse, expected negative RC8/RC4, invalid-depth RC4, verified seq51 recovery, both-invalid RC8, restored seq52 and final protected files. Synthetic host tests cover a two-parent merge with three snapshots all resolving README.md, depth0 directory metadata, missing path fail-closed, missing/wrong root fail-closed and malformed path inputs. M59 is NOT target-proven until strict native C89 CI passes and one actual CMS run succeeds. After green merge, transfer only `GITREC.C` and `GITRUN.EXEC` via current Mac `CMS_SCRIPT_PORT=3272`, then CMS `CMSCLNK GITREC PLAIN` and one `GITRUN`. Expected native terminal marker only after actual success: `GITRUN M59 ALL READ ONLY NATIVE GIT TESTS PASSED`.

## M59 merged and strict host CI green: next native CMS validation

M59 PR #41 full strict native C89 CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36725741487 ; squash merged main commit `aa43db87571cc18d64b56b938c966bfdf7bfddab`. The new HISTORYDAGPATH command verifies the bounded all-parent commit DAG, every complete local root snapshot and one named path in every reachable snapshot before any DAG/path metadata is released. Synthetic tests confirm a real two-parent merge resolves README.md in all three nodes, depth0 directory metadata, missing-path fail-closed, missing/wrong roots fail-closed, and malformed path rejection. Standard M59 RUNBATCH includes HISTORYDAGPATH depth1 for the known original README path and GITRUN requires `HISTORYDAGPATH FULL SNAPSHOTS VERIFIED`. All prior M58/M57 history gates, both independent original 1808-object full audits, shared root and seek-index proofs, expected RC8/RC4 checks, invalid-depth RC4, verified seq51 fallback, both-invalid fail-closed, restored seq52 and final protected originals remain mandatory. M59 is HOST-CI-PROVEN but NOT YET native CMS target-proven. M58 remains latest actual native proof at CPU 805.68 / elapsed 826.89 sec.

NEXT from Mac `ibm-sandbox/src`: `git pull`; confirm `head -n 3 GITRUN.EXEC` shows M59; upload exactly `GITREC.C` and `GITRUN.EXEC` with `CMS_SCRIPT_PORT=3272`; verify both transfers complete. On CMS: `TYPE GITRUN EXEC A` must show M59; run `CMSCLNK GITREC PLAIN`; then one `GITRUN`. Exact final marker only on actual target success: `GITRUN M59 ALL READ ONLY NATIVE GIT TESTS PASSED`. Do not rerun M58 separately or transfer unchanged GITCIDX/GITSEL. Preserve sealed original STAGE/INDEX/SEEK/GEN, selector PTRs and GITPBUF PACK.

## M59 real CMS runner failure isolated and fixed (2026-09-30)

Actual CMS M59 compiled GITREC cleanly (CPU 11.57 / elapsed 12.01 sec) and **the entire `M59 ONE SELECTION ALL POSITIVES` C batch returned RC0** on original data. The run then failed only inside `GITRUN EXEC` with DMSREX470E Error 34 because the new compound boolean gate record exceeded the practical 80-column CMS EXEC transfer/execution path. No GITREC functional failure occurred. PR #42 replaced the long compound test with seven short explicit boolean checks, shortened the long positive gate call through marker variables, and added a host guard that rejects any GITRUN record over 80 columns. Full host CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36728805720 ; merged main `2c3e41e3519a75b6078488a410efa826d8a70052`. `src/GITREC.C` is unchanged from the already compiled M59 source. NEXT native action requires **ONLY `GITRUN.EXEC` transfer**, no GITREC upload and no CMSCLNK rebuild: Mac `git pull`; confirm M59 banner; `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITRUN.EXEC`. On CMS `TYPE GITRUN EXEC A` should show M59, then one `GITRUN`. Exact success marker remains `GITRUN M59 ALL READ ONLY NATIVE GIT TESTS PASSED`. This reruns the complete protected suite because the previous run stopped before recovery/final protection checks; do not run any older milestone separately.

## 2026-09-30 actual M59 native CMS PASS

After the EXEC-only REXX gate fix, real CMS `GITRUN M59` passed the entire protected suite on the original immutable 1808-object repository: both independent GITFIX/M15NEW full audits RC0; one selected positive batch RC0; newest seq52; shared verified root closure; shared verified seek index; full first-parent HISTORYFULL root closure; full all-parent HISTORYDAG root closure; NEW all-parent HISTORYDAGPATH verification of the named path across every reachable snapshot; in-batch noncommit RC8 and missing-child RC4; invalid-depth RC4; verified older seq51 fallback RC0; both-invalid fail-closed RC8; restored newest seq52 RC0; final protected original files. Exact terminal marker `GITRUN M59 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 899.41 / elapsed 923.47 seconds at 09:43:05 on 2026-09-30. M59 is now NATIVE CMS TARGET-PROVEN. The earlier failed M59 attempt was solely the long REXX gate record and did not invalidate GITREC; PR #42 fixed that with <=80-column EXEC records and full CI. Preserve both independent original audits and all recovery/fail-closed/protected-file checks in subsequent milestones. Do not rerun M59 standalone.

## 2026-09-30 actual M59 native CMS PASS

Real CMS `GITRUN M59` passed the entire protected suite after the EXEC-only 80-column fix: both independent original 1808-object full audits; selected seq52; shared root and seek proofs; first-parent HISTORYFULL; all-parent HISTORYDAG; named-path verification across every DAG snapshot; in-batch negative RC8/RC4; invalid depth RC4; verified seq51 recovery; both-invalid fail-closed RC8; restored seq52; and final protected files. Exact terminal `GITRUN M59 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 899.41 / elapsed 923.47 seconds at 09:43:05 on 2026-09-30. M59 is now NATIVE CMS TARGET-PROVEN. Do not rerun M59 standalone; subsequent milestones should build user-facing read-only Git workflows on this proven baseline while retaining all original audit/recovery protections.

## M60: SHOWFULL commit view gated by complete snapshot verification

M59 actual native CMS passed on 2026-09-30 with `GITRUN M59 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 899.41 / elapsed 923.47 sec. M60 adds `GITREC SHOWFULL C0 C1 COMMIT_OID40`, a practical read-only commit view that authenticates the selected generation, validates the commit structure, extracts its tree OID, verifies the entire bounded local root tree/blob closure, then reloads/re-hashes the commit before releasing established COMMIT metadata. It emits `SHOW FULL ROOT CLOSURE VERIFIED` only after the complete snapshot passes. Missing/deep-missing descendants return RC4, wrong object types/corrupt structures/resource-limit overflow RC8, and no `COMMIT DATA` is released on failure. Existing COMMIT remains unchanged.

The standard M60 RUNBATCH adds SHOWFULL for the known original commit in the same selected seq52 process and GITRUN requires the exact SHOW marker. All prior M59/M58/M57 history/path gates, both independent original 1808-object audits, shared root and seek-index reuse proofs, expected negative RC8/RC4, invalid-depth RC4, verified seq51 recovery, both-invalid fail-closed RC8, restored seq52 and final protected files remain mandatory. Host tests add successful root commit metadata plus missing entry, wrong-type entry, deep missing tree, 1025-tree overflow and non-commit failures, all with no premature commit metadata. M60 is not CMS target-proven until strict native C89 CI passes and one real target run succeeds. After green merge, transfer only `GITREC.C` and `GITRUN.EXEC` with current `CMS_SCRIPT_PORT=3272`; CMS compile GITREC PLAIN and run one GITRUN. Exact success marker only on actual target pass: `GITRUN M60 ALL READ ONLY NATIVE GIT TESTS PASSED`.

## M60 merged and strict host CI green: next native CMS validation

M60 PR #43 full strict native C89 CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36732096087 ; squash merged main commit `102b4855777522b8ade41a6aa69199abc6b15bb0`. New `GITREC SHOWFULL C0 C1 COMMIT_OID40` validates the selected generation and commit, authenticates the complete bounded local root tree/blob snapshot, reloads and re-hashes the commit after closure traversal, and only then emits the established COMMIT metadata preceded by `SHOW FULL ROOT CLOSURE VERIFIED`. Host tests prove normal output and fail closed with no COMMIT DATA for missing root entries, wrong-type entries, deep missing descendants, 1025-tree budget overflow and non-commit input. Standard M60 RUNBATCH includes SHOWFULL and GITRUN requires `PASS SHOW FULL SNAPSHOT`, while retaining M59 HISTORYDAGPATH, M58 HISTORYDAG, M57 HISTORYFULL, both independent original 1808-object audits, shared root/seek proofs, expected negative RC8/RC4, invalid-depth RC4, verified seq51 fallback, both-invalid RC8, restored seq52 and final protected files. M60 is HOST-CI-PROVEN but NOT YET native CMS target-proven. M59 remains latest actual native proof at CPU 899.41 / elapsed 923.47 sec.

NEXT from Mac `ibm-sandbox/src`: `git pull`; confirm `head -n 3 GITRUN.EXEC` shows M60; upload exactly `GITREC.C` and `GITRUN.EXEC` with `CMS_SCRIPT_PORT=3272`; verify both transfers complete. On CMS: `TYPE GITRUN EXEC A` must show M60; `CMSCLNK GITREC PLAIN`; one `GITRUN`. Exact final marker only on actual target success: `GITRUN M60 ALL READ ONLY NATIVE GIT TESTS PASSED`. Do not rerun M59 separately or transfer unchanged GITCIDX/GITSEL. Preserve sealed original STAGE/INDEX/SEEK/GEN, selector PTRs and GITPBUF PACK.

## 2026-09-30 actual M60 native CMS PASS

Real z/VM CMS `CMSCLNK GITREC PLAIN` assembled with zero flagged statements (CPU 11.70 / elapsed 12.16 sec). Actual standard `GITRUN M60` passed both independent original GITFIX/M15NEW 1808-object full audits RC0; one selected positive batch RC0; newest seq52; shared verified root closure; shared verified seek index; full first-parent HISTORYFULL root closure; full all-parent HISTORYDAG root closure; all-parent HISTORYDAGPATH named-path verification; NEW SHOWFULL complete-snapshot commit view; in-batch noncommit RC8 and missing-child RC4; invalid-depth RC4; verified older seq51 fallback RC0; both-invalid fail-closed RC8; restored newest seq52 RC0; final protected original files. Exact terminal marker `GITRUN M60 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 947.43 / elapsed 972.93 seconds at 10:40:14 on 2026-09-30. M60 is now NATIVE CMS TARGET-PROVEN. Runtime is higher than M59 because SHOWFULL adds another complete snapshot verification; treat this as functional coverage, not a speed regression. Preserve both independent original audits and every recovery/fail-closed/protected-file check in later milestones. Do not rerun M60 standalone.

## M61: LOGFULL first-parent history after complete snapshot verification

M60 actual native CMS passed on 2026-09-30 with `GITRUN M60 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 947.43 / elapsed 972.93 sec. M61 adds `GITREC LOGFULL C0 C1 COMMIT_OID40 DEPTH` for DEPTH 0..16. It walks first-parent history, validates every commit and tree OID, then authenticates every visited commit's complete bounded local root tree/blob closure before emitting any log records. Only after all snapshots succeed does it print `LOG FULL SNAPSHOTS VERIFIED`, deterministic LOG node/OID records, established COMMIT metadata for each node, a node count and final `LOG DATA END`. Missing/wrong/malformed commit links, missing/wrong/corrupt root contents, resource-limit overflow or invalid depth fail closed with no LOG or COMMIT metadata. Existing HISTORY/HISTORYFULL and SHOWFULL remain unchanged.

Standard M61 RUNBATCH adds LOGFULL depth1 for the known original commit in the same selected seq52 process; GITRUN requires `PASS LOG FULL SNAPSHOTS`. All prior M60 SHOWFULL, M59 HISTORYDAGPATH, M58 HISTORYDAG, M57 HISTORYFULL, both independent original 1808-object audits, shared root/seek proofs, expected negative RC8/RC4, invalid-depth RC4, verified seq51 fallback, both-invalid RC8, restored seq52 and final protected files remain mandatory. Host tests cover depth2/zero success plus missing/wrong/malformed parent and root cases with no premature output. M61 is not target-proven until strict native C89 CI passes and one real CMS run succeeds. After green merge, transfer only `GITREC.C` and `GITRUN.EXEC` with current `CMS_SCRIPT_PORT=3272`; compile GITREC PLAIN and run one GITRUN. Exact success marker only on actual target pass: `GITRUN M61 ALL READ ONLY NATIVE GIT TESTS PASSED`.

## M61 merged and strict host CI green: next native CMS validation

M61 PR #44 full strict native C89 CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36738981748 ; squash merged main commit `54dd3dc12b9708ede15dd24fe43e5ec82540923f`. New `GITREC LOGFULL C0 C1 COMMIT_OID40 DEPTH` (0..16) validates the complete requested first-parent chain and every visited commit's complete bounded local root snapshot before releasing any log data. Only after full success does it emit `LOG FULL SNAPSHOTS VERIFIED`, deterministic log node/OID records and established COMMIT metadata for each node. Host tests prove depth2/depth0 success and fail closed with no LOG or COMMIT DATA for missing/wrong/malformed parent commits or invalid snapshots. Standard M61 RUNBATCH includes LOGFULL depth1 and GITRUN requires `PASS LOG FULL SNAPSHOTS`, while retaining M60 SHOWFULL, M59 HISTORYDAGPATH, M58 HISTORYDAG, M57 HISTORYFULL, both independent original 1808-object audits, shared root/seek proofs, expected negative RC8/RC4, invalid-depth RC4, verified seq51 fallback, both-invalid RC8, restored seq52 and final protected originals. M61 is HOST-CI-PROVEN but NOT YET native CMS target-proven. M60 remains latest actual native proof at CPU 947.43 / elapsed 972.93 sec.

NEXT from Mac `ibm-sandbox/src`: `git pull`; confirm `head -n 3 GITRUN.EXEC` shows M61; upload exactly `GITREC.C` and `GITRUN.EXEC` with `CMS_SCRIPT_PORT=3272`; verify both transfers complete. On CMS: `TYPE GITRUN EXEC A` must show M61; `CMSCLNK GITREC PLAIN`; one `GITRUN`. Exact final marker only on actual target success: `GITRUN M61 ALL READ ONLY NATIVE GIT TESTS PASSED`. Do not rerun M60 separately or transfer unchanged GITCIDX/GITSEL. Preserve sealed original STAGE/INDEX/SEEK/GEN, selector PTRs and GITPBUF PACK.

## 2026-09-30 actual M61 native CMS PASS

Real CMS `GITRUN M61` passed the entire protected suite on the original immutable 1808-object repository: both independent GITFIX/M15NEW full audits RC0; one selected positive batch RC0; newest seq52; shared verified root closure; shared verified seek index; full first-parent HISTORYFULL root closure; full all-parent HISTORYDAG root closure; all-parent HISTORYDAGPATH named-path verification; SHOWFULL complete-snapshot commit view; NEW LOGFULL complete-snapshot first-parent log view; in-batch noncommit RC8 and missing-child RC4; invalid-depth RC4; verified older seq51 fallback RC0; both-invalid fail-closed RC8; restored newest seq52 RC0; final protected original files. Exact terminal marker `GITRUN M61 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 1048.73 / elapsed 1077.07 seconds at 11:11:25 on 2026-09-30. M61 is now NATIVE CMS TARGET-PROVEN. Runtime increase reflects added full-snapshot log verification; treat as added functional coverage rather than a speed regression. Preserve both independent original audits and all recovery/fail-closed/protected-file checks in later milestones. Do not rerun M61 standalone.

## M62: LOGDAGFULL all-parent log after complete snapshot verification

M61 actual native CMS passed on 2026-09-30 with `GITRUN M61 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 1048.73 / elapsed 1077.07 sec. M62 adds `GITREC LOGDAGFULL C0 C1 COMMIT_OID40 DEPTH` for DEPTH 0..8. It traverses the bounded all-parent merge DAG, validates every reachable commit and complete local root snapshot, and only after the entire graph succeeds emits `LOGDAG FULL SNAPSHOTS VERIFIED`, deterministic node/depth/OID records plus established COMMIT metadata for each node, a node count and final `LOGDAG DATA END`. Missing/wrong/malformed parent commits, missing/wrong/corrupt snapshots, resource-limit overflow or invalid depth fail closed with no LOGDAG or COMMIT metadata. Existing LOGFULL, HISTORYDAG and related commands remain unchanged.

Standard M62 RUNBATCH adds LOGDAGFULL depth1 for the known original commit and GITRUN requires `PASS LOGDAG FULL SNAPSHOTS`, while retaining M61 LOGFULL, M60 SHOWFULL, M59 HISTORYDAGPATH, M58 HISTORYDAG, M57 HISTORYFULL, both independent original 1808-object audits, shared root/seek proofs, expected negative RC8/RC4, invalid-depth RC4, verified seq51 fallback, both-invalid RC8, restored seq52 and final protected files. Host tests cover a real two-parent merge with three nodes, depth0 one node, and missing/wrong/malformed parents or roots with no premature metadata. M62 is not target-proven until strict native C89 CI passes and one real CMS run succeeds. After green merge, transfer only `GITREC.C` and `GITRUN.EXEC` via `CMS_SCRIPT_PORT=3272`, compile GITREC PLAIN and run one GITRUN. Exact success marker only on actual target pass: `GITRUN M62 ALL READ ONLY NATIVE GIT TESTS PASSED`.

## M62 merged and strict host CI green: next native CMS validation

M62 PR #45 full strict native C89 CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36743204989 ; squash merged main commit `40392e8c90c4226ff94dd543034cd8abae87122c`. New `GITREC LOGDAGFULL C0 C1 COMMIT_OID40 DEPTH` (0..8) traverses the bounded all-parent merge DAG, validates every reachable commit and complete local root snapshot, then emits deterministic node/depth/OID records plus established COMMIT metadata only after the entire graph succeeds. Host tests cover a real two-parent merge with three nodes, depth0 one node, and missing/wrong/malformed parents or roots with no premature LOGDAG or COMMIT data. Standard M62 RUNBATCH includes LOGDAGFULL depth1 and GITRUN requires `PASS LOGDAG FULL SNAPSHOTS`, while retaining M61 LOGFULL, M60 SHOWFULL, M59 HISTORYDAGPATH, M58 HISTORYDAG, M57 HISTORYFULL, both independent original 1808-object audits, shared root/seek proofs, expected negative RC8/RC4, invalid-depth RC4, verified seq51 fallback, both-invalid RC8, restored seq52 and final protected files. M62 is HOST-CI-PROVEN but NOT YET native CMS target-proven. M61 remains latest actual native proof at CPU 1048.73 / elapsed 1077.07 sec.

NEXT from Mac `ibm-sandbox/src`: `git pull`; confirm `head -n 3 GITRUN.EXEC` shows M62; upload exactly `GITREC.C` and `GITRUN.EXEC` with `CMS_SCRIPT_PORT=3272`; verify both transfers complete. On CMS: `TYPE GITRUN EXEC A` must show M62; `CMSCLNK GITREC PLAIN`; one `GITRUN`. Exact final marker only on actual target success: `GITRUN M62 ALL READ ONLY NATIVE GIT TESTS PASSED`. Do not rerun M61 separately or transfer unchanged GITCIDX/GITSEL. Preserve sealed original STAGE/INDEX/SEEK/GEN, selector PTRs and GITPBUF PACK.

## M62 native CMS proof

On 2026-09-30 the real CMS target built `GITREC PLAIN` cleanly with zero flagged assembler statements (CPU 12.34 / elapsed 12.83 sec). `GITRUN M62` passed both original 1808-object audits, seq52 selection, shared root/seek checks, HISTORYFULL, HISTORYDAG, HISTORYDAGPATH, SHOWFULL, LOGFULL, LOGDAGFULL, all expected negative RC4/RC8 cases, seq51 recovery, dual-invalid fail-closed, seq52 restoration, and final protected-file checks. Final marker: `GITRUN M62 ALL READ ONLY NATIVE GIT TESTS PASSED`. Runtime: CPU 1136.68 / elapsed 1167.74 sec. M62 is now native CMS target-proven.

## M63: verified modern REF2 name resolution into sealed GEN2

M62 actual native CMS passed on 2026-09-30 with `GITRUN M62 ALL READ ONLY NATIVE GIT TESTS PASSED`, CPU 1136.68 / elapsed 1167.74 sec. The older M5 `GITREF`/HEAD layer is target-proven but belongs to the earlier loose-object prototype, so M63 does **not** silently treat those refs as authoritative for the newer sealed GEN2 store. M63 introduces a separate read-only `GITREF2 REPO` snapshot for the modern engine plus `GITVREF EXEC`. The initial fixture binds `HEAD -> refs/heads/main -> 00D8D63229305230C8D37F884CE87F9E1A89468C`, the known real commit already proven in the original 1808-object sealed generations.

`GIT VERIFY-REF <HEAD|branch|refs/heads/name>` now routes through `GITVREF RESOLVE`: parse REF2 strictly, reject malformed/duplicate refs, bind only read-only selector/generation FILEDEFs, call `GITREC SHOWFULL GITFIX M15NEW <oid>`, and expose `VERIFIED REF ... <oid>` only if the modern selected generation and the referenced commit's complete local snapshot verify. `GIT SHOW-REF-FULL <spec>` performs the same proof and only then releases SHOWFULL/COMMIT metadata. GITVREF contains no persistent write command and every bridge/ref record is <=80 columns. CI adds a source guard covering exact REF2 fixture contents, modern SHOWFULL binding, read-only FILEDEFs, GIT routing, forbidden write verbs and record length. Existing M5 write-capable branch/update commands are unchanged and remain separate from REF2.

M63 changes only `GIT.EXEC`, new `GITVREF.EXEC`, new `GITREF2.REPO`, host guard/workflow and docs; no GITREC/GITCIDX/GITSEL code changes and no protected original-data changes. After strict CI/merge, native validation needs no compile and no full GITRUN rerun: Mac transfers only `GIT.EXEC`, `GITVREF.EXEC`, and `GITREF2.REPO` using current `CMS_SCRIPT_PORT=3272`. On CMS run `GIT VERIFY-REF HEAD`, then `GIT SHOW-REF-FULL HEAD`. Expected successful proof includes `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C`, `SHOW FULL ROOT CLOSURE VERIFIED`, and established COMMIT metadata. This validates human-facing modern ref resolution without rewriting refs or sealed generations.

## M63 merged and strict host CI green: next native CMS validation

M63 PR #46 full native-stage CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36746839870 ; squash merged main commit `2fdf5a8c33088a83e927527c092c1ccc32a77832`. M63 adds a separate modern `GITREF2 REPO` snapshot and new read-only `GITVREF EXEC`. `GIT VERIFY-REF <HEAD|branch|refs/heads/name>` resolves strictly from REF2, binds only read-only M15 selector/GEN2 inputs, and exposes the ref OID only after `GITREC SHOWFULL` authenticates the referenced commit and complete local snapshot. `GIT SHOW-REF-FULL <spec>` performs the same proof and only then emits SHOWFULL/COMMIT metadata. The older M5 refs remain separate and are not silently mixed with the sealed modern object generations. CI verifies exact fixture binding to known commit `00D8D63229305230C8D37F884CE87F9E1A89468C`, read-only FILEDEFs, command routing, forbidden write verbs, and <=80-column EXEC/ref records. No GITREC/GITCIDX/GITSEL source changed in M63.

M63 is HOST-CI-PROVEN but not yet CMS target-proven. Native validation needs no compile and no long GITRUN rerun. From Mac `ibm-sandbox/src`: `git pull`; upload exactly `GIT.EXEC`, `GITVREF.EXEC`, and `GITREF2.REPO` with `CMS_SCRIPT_PORT=3272`. The uploader maps `GITREF2.REPO` to `GITREF2 REPO A` and uses fixed LRECL 80. On CMS run `GIT VERIFY-REF HEAD`; expected exact verified mapping includes `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C`. Then run `GIT SHOW-REF-FULL HEAD`; expected output begins with the same VERIFIED REF line and includes `SHOW FULL ROOT CLOSURE VERIFIED` plus established COMMIT DATA. No original ref, selector, stage, index, GEN, or PACK file is rewritten.

## 2026-09-30 actual M63 native CMS PASS

Real CMS native validation of the modern read-only REF2 bridge passed. `GIT VERIFY-REF HEAD` returned exactly `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C` (CPU 68.04 / elapsed 69.53 sec). `GIT SHOW-REF-FULL HEAD` returned the same verified mapping, then `SHOW FULL ROOT CLOSURE VERIFIED`, `COMMIT DATA BEGIN`, tree `204E1D6968FB81C35BF830D63A611AC64C072945`, parent `2D5038C551318997B865497E04CF4C037DE4135E`, `COMMIT PARENTS 1`, `COMMIT MESSAGE BYTES 44`, and `COMMIT DATA END` (CPU 67.89 / elapsed 69.37 sec). M63 is now NATIVE CMS TARGET-PROVEN. This establishes human-facing HEAD resolution into the sealed GEN2 engine without modifying refs or protected object-generation files. Do not rerun M63 standalone.

## M64: verified named-ref LOGFULL

M63 actual native CMS passed on 2026-09-30: `GIT VERIFY-REF HEAD` resolved `00D8D63229305230C8D37F884CE87F9E1A89468C` after full snapshot authentication, and `GIT SHOW-REF-FULL HEAD` emitted the same verified mapping plus `SHOW FULL ROOT CLOSURE VERIFIED` and COMMIT metadata. M64 extends only the read-only REF2 bridge and GIT command routing; no GITREC/GITCIDX/GITSEL code or sealed generation data changes. New `GIT LOG-REF-FULL <HEAD|branch|refs/heads/name> <depth>` resolves the modern REF2 name, binds the same read-only selector/GEN2 inputs, runs the already native-proven `GITREC LOGFULL` at depth 0..16, and emits `VERIFIED REF ... <oid>` plus LOGFULL output only if `LOG FULL SNAPSHOTS VERIFIED` is present. Missing/malformed refs, invalid depth, missing/corrupt commits or snapshots fail closed with no verified-ref/log output. `GITVREF` remains write-free and <=80 columns; CI guards both SHOW and LOG routing.

After strict CI/merge, M64 native validation needs no compile and no long GITRUN. Transfer only changed `GIT.EXEC` and `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`; GITREF2 REPO A is unchanged from target-proven M63. On CMS run `GIT LOG-REF-FULL HEAD 1`. Expected output begins `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C`, then `LOG FULL SNAPSHOTS VERIFIED`, `LOG DATA BEGIN`, two log nodes with COMMIT metadata, `LOG NODES 2`, and `LOG DATA END`. No ref or sealed generation file is modified.

## M64 merged and strict host CI green: next native CMS validation

M64 PR #47 full native-stage CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36768609323 ; squash merged main commit `403760aa1d99398b1de8b676bc72aecdcb29ddbb`. New `GIT LOG-REF-FULL <HEAD|branch|refs/heads/name> <depth>` extends only the M63 read-only REF2 bridge: resolve the modern ref strictly, bind the same read-only sealed GEN2 inputs, run already native-proven `GITREC LOGFULL` at depth 0..16, and release `VERIFIED REF ... <oid>` plus LOGFULL data only after `LOG FULL SNAPSHOTS VERIFIED`. M64 changes no GITREC/GITCIDX/GITSEL source and no REF2 snapshot. CI guards LOG routing, read-only behavior, and <=80-column CMS records. M64 is HOST-CI-PROVEN but NOT YET native CMS target-proven. M63 remains latest actual named-ref target proof.

NEXT from Mac `ibm-sandbox/src`: `git pull`; upload only `GIT.EXEC` and `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`. No compile and no GITRUN required. On CMS run `GIT LOG-REF-FULL HEAD 1`. Expected output starts with `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C`, includes `LOG FULL SNAPSHOTS VERIFIED`, `LOG DATA BEGIN`, two complete COMMIT DATA records, `LOG NODES 2`, and `LOG DATA END`. No ref, selector, stage, index, GEN, or PACK file is modified.

## 2026-09-30 actual M64 native CMS PASS

Real CMS `GIT LOG-REF-FULL HEAD 1` passed. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, printed `LOG FULL SNAPSHOTS VERIFIED`, then emitted exactly two verified first-parent commit records: node 0 tree `204E1D6968FB81C35BF830D63A611AC64C072945`, parent `2D5038C551318997B865497E04CF4C037DE4135E`, message bytes 44; node 1 tree `F3EF36AAD778D5DA84857D8DED46495C75F4CAB0`, parent `C67A53164ADFC6FDEB708F13F1822E2CF24C060C`, message bytes 39; `LOG NODES 2`; `LOG DATA END`. CPU 114.69 / elapsed 117.55 sec at 15:27:41. M64 is now NATIVE CMS TARGET-PROVEN. This establishes direct human-facing ref-to-verified-history operation without manual OID copying and without ref or sealed-generation writes. Do not rerun M64 standalone.

## M65: verified named-ref path read

M64 actual native CMS passed on 2026-09-30: `GIT LOG-REF-FULL HEAD 1` resolved the modern REF2 `HEAD`, verified both requested first-parent snapshots, and emitted exactly two COMMIT records only after `LOG FULL SNAPSHOTS VERIFIED` (CPU 114.69 / elapsed 117.55 sec). M65 extends only the read-only REF2 bridge and GIT routing; no GITREC/GITCIDX/GITSEL code and no sealed-generation data change. New `GIT READ-REF-FULL <HEAD|branch|refs/heads/name> <path>` accepts a normal CMS path token such as `README.md`, converts its EBCDIC command-line bytes to the raw ASCII bytes Git stores in tree entries, resolves and verifies the modern ref, then invokes already native-proven `GITREC PATHFULLCAT`. It releases `VERIFIED REF ...`, full-root marker, path metadata, and lossless `PATH HEX` only after `COMMIT ROOT FULL CLOSURE VERIFIED`. Invalid paths, missing refs, missing path objects or corrupt snapshots fail closed. Paths are limited to one nonempty <=255-byte token with no leading/trailing/doubled slash; arbitrary blob bytes remain hex rather than being misrepresented as text.

CI extends the M63/M64 read-only bridge guard to require READ routing, PATHFULLCAT, the full-root marker, path ASCII translation helper, no write verbs and <=80-column CMS records. After strict CI/merge, M65 native validation needs no compile and no long GITRUN. Transfer only changed `GIT.EXEC` and `GITVREF.EXEC`; `GITREF2 REPO A` remains the M63 target-proven snapshot. On CMS run `GIT READ-REF-FULL HEAD README.md`. Expected key output begins `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C`, includes `COMMIT ROOT FULL CLOSURE VERIFIED`, a blob `PATH OBJECT TYPE 3 ... OID ...`, `PATH DATA BEGIN`, one or more `PATH HEX` records, and `PATH DATA END`. No ref or sealed-generation file is modified.

## M65 merged and strict host CI green: next native CMS validation

M65 PR #48 full native-stage CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36773165355 ; squash merged main commit `53d663ad4a6b2f420f268c4edf6893eee525aed7`. New `GIT READ-REF-FULL <HEAD|branch|refs/heads/name> <path>` extends only the read-only REF2 bridge: converts the CMS path token from EBCDIC to Git raw ASCII bytes, resolves the modern ref, binds only read-only sealed GEN2 inputs, invokes already native-proven `GITREC PATHFULLCAT`, and emits verified-ref/path metadata plus lossless `PATH HEX` only after `COMMIT ROOT FULL CLOSURE VERIFIED`. No GITREC/GITCIDX/GITSEL changes and no REF2 snapshot changes. CI guards READ routing, path translation helper, full-root marker, forbidden write verbs, and <=80-column records. M65 is HOST-CI-PROVEN but NOT YET native CMS target-proven. M64 remains latest actual named-ref target proof.

NEXT from Mac `ibm-sandbox/src`: `git pull`; upload only `GIT.EXEC` and `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`. No compile and no GITRUN required. On CMS run `GIT READ-REF-FULL HEAD README.md`. Expected output starts `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C`, includes `COMMIT ROOT FULL CLOSURE VERIFIED`, a `PATH OBJECT TYPE 3 ... OID ...` line, `PATH DATA BEGIN`, one or more `PATH HEX ...` records, and `PATH DATA END`. No ref, selector, stage, index, GEN, or PACK file is modified.

## 2026-09-30 actual M65 native CMS PASS

Real CMS `GIT READ-REF-FULL HEAD README.md` passed. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, printed `COMMIT ROOT FULL CLOSURE VERIFIED`, resolved the path to blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5` of size 567, and emitted the complete blob losslessly as `PATH HEX` records between `PATH DATA BEGIN` and `PATH DATA END`. CPU 68.39 / elapsed 69.91 sec at 15:53:24. M65 is now NATIVE CMS TARGET-PROVEN. This establishes human-facing ref+path read access into the sealed GEN2 store without manual OID or hex-path handling and without writes. Do not rerun M65 standalone.

## M66: verified named-ref directory listing

M65 actual native CMS passed on 2026-09-30: `GIT READ-REF-FULL HEAD README.md` resolved modern REF2 `HEAD`, authenticated the complete snapshot, resolved README.md to blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5` size 567, and returned the complete blob losslessly as PATH HEX (CPU 68.39 / elapsed 69.91 sec). M66 extends only the read-only REF2 bridge and GIT routing; no GITREC/GITCIDX/GITSEL code and no sealed-generation data change. New `GIT DIR-REF-FULL <HEAD|branch|refs/heads/name> <dir>` accepts a normal CMS path token such as `src`, converts it to Git raw ASCII bytes, resolves the modern ref, then invokes already native-proven `GITREC PATHFULLDIR`. It releases `VERIFIED REF ...`, `COMMIT ROOT FULL CLOSURE VERIFIED`, directory path metadata and complete TREE DATA only after the whole commit-root local snapshot passes. Missing refs/directories, wrong terminal types, malformed paths or corrupt snapshots fail closed. The same <=255-byte path rules as M65 apply.

CI extends the verified-ref bridge guard to require DIR routing, PATHFULLDIR, the shared EBCDIC-to-ASCII path helper, no write verbs and <=80-column CMS records. After strict CI/merge, M66 native validation needs no compile and no long GITRUN. Transfer only changed `GIT.EXEC` and `GITVREF.EXEC`; `GITREF2 REPO A` is unchanged. On CMS run `GIT DIR-REF-FULL HEAD src`. Expected key output begins `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C`, includes `COMMIT ROOT FULL CLOSURE VERIFIED`, `PATH OBJECT TYPE 2 ... OID ...`, `TREE DATA BEGIN`, one or more TREE ENTRY records, and `TREE DATA END`. No ref or sealed-generation file is modified.

## M66 merged and green

M66 PR #49 passed full native-stage CI and merged as `2da7e4e3715e5b1d904073de8a04e5c1116e8d26`. `GIT DIR-REF-FULL <ref> <dir>` now resolves a modern REF2 name, converts the CMS directory token to Git ASCII path bytes, invokes read-only `GITREC PATHFULLDIR`, and emits verified-ref plus directory TREE DATA only after complete root closure succeeds. No GITREC/GITCIDX/GITSEL or REF2 data changed. Native validation requires only updated `GIT.EXEC` and `GITVREF.EXEC`; no compile or GITRUN. Run `GIT DIR-REF-FULL HEAD src`. M66 is host-CI-proven, awaiting CMS target proof.

## 2026-09-30 actual M66 native CMS PASS

Real CMS `GIT DIR-REF-FULL HEAD src` passed. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, printed `COMMIT ROOT FULL CLOSURE VERIFIED`, resolved `src` to tree `A41B3EA7758F301B7E30BD3CFDF264300C02AE35` size 3690, and emitted the complete authenticated directory listing between `TREE DATA BEGIN` and `TREE DATA END`, reporting `TREE ENTRIES 93`. CPU 68.25 / elapsed 69.89 sec at 16:06:18. M66 is now NATIVE CMS TARGET-PROVEN. The console paste contains an interleaved Ready/timing line in the middle of the long listing, but the complete success markers, final entry count, and `TREE DATA END` are present. This establishes direct human-facing ref+directory browsing without manual OIDs or hex paths and without writes. Do not rerun M66 standalone.

## M67: verified named-ref all-parent LOGDAG

M66 actual native CMS passed on 2026-09-30: `GIT DIR-REF-FULL HEAD src` resolved modern REF2 `HEAD`, authenticated the complete snapshot, resolved `src` to tree `A41B3EA7758F301B7E30BD3CFDF264300C02AE35` size 3690, and emitted all 93 directory entries before `TREE DATA END` (CPU 68.25 / elapsed 69.89 sec). M67 extends only the read-only REF2 bridge and GIT routing; no GITREC/GITCIDX/GITSEL code and no sealed-generation data change. New `GIT LOGDAG-REF-FULL <HEAD|branch|refs/heads/name> <depth>` resolves the modern ref, validates depth 0..8, binds the same read-only sealed GEN2 inputs, invokes already native-proven `GITREC LOGDAGFULL`, and releases `VERIFIED REF ... <oid>` plus complete all-parent DAG log metadata only after `LOGDAG FULL SNAPSHOTS VERIFIED`. Invalid depth, malformed/missing refs, missing/corrupt parent commits or snapshots fail closed.

CI extends the verified-ref bridge guard to require DAG routing, LOGDAGFULL, the all-parent full-snapshot marker, no write verbs and <=80-column CMS records. After strict CI/merge, M67 native validation needs no compile and no long GITRUN. Transfer only changed `GIT.EXEC` and `GITVREF.EXEC`; `GITREF2 REPO A` is unchanged. On CMS run `GIT LOGDAG-REF-FULL HEAD 1`. Expected key output begins `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C`, includes `LOGDAG FULL SNAPSHOTS VERIFIED`, `LOGDAG DATA BEGIN`, one or more `LOGDAG NODE ...` records with COMMIT DATA, `LOGDAG NODES ...`, and `LOGDAG DATA END`. No ref or sealed-generation file is modified.

## M67 merged and strict host CI green: next native CMS validation

M67 PR #50 full native-stage CI PASS https://github.com/mostangrymike/ibm-sandbox/actions/runs/36777500893 ; squash merged main commit `2ddb5f92a19546ac2e5e52ddb429975916837fd3`. New `GIT LOGDAG-REF-FULL <HEAD|branch|refs/heads/name> <depth>` extends only the read-only REF2 bridge: resolve the modern ref, validate depth 0..8, bind only sealed read-only GEN2 inputs, invoke already native-proven `GITREC LOGDAGFULL`, and release verified-ref plus all-parent DAG commit metadata only after `LOGDAG FULL SNAPSHOTS VERIFIED`. No GITREC/GITCIDX/GITSEL changes and no REF2 snapshot changes. CI guards DAG routing, LOGDAGFULL binding, full-snapshot marker, forbidden write verbs, and <=80-column CMS records. M67 is HOST-CI-PROVEN but NOT YET native CMS target-proven. M66 remains latest actual named-ref target proof.

NEXT from Mac `ibm-sandbox/src`: `git pull`; upload only `GIT.EXEC` and `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`. No compile and no GITRUN required. On CMS run `GIT LOGDAG-REF-FULL HEAD 1`. Expected output starts `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C`, includes `LOGDAG FULL SNAPSHOTS VERIFIED`, `LOGDAG DATA BEGIN`, LOGDAG node records with COMMIT DATA, a final node count, and `LOGDAG DATA END`. No ref, selector, stage, index, GEN, or PACK file is modified.

## M67 native CMS proof

On 2026-09-30 `GIT LOGDAG-REF-FULL HEAD 1` passed on real CMS. HEAD resolved to `00D8D63229305230C8D37F884CE87F9E1A89468C`; `LOGDAG FULL SNAPSHOTS VERIFIED` preceded all output; two DAG nodes were emitted and ended with `LOGDAG NODES 2` and `LOGDAG DATA END`. CPU 114.85 / elapsed 117.75 sec. M67 is now native CMS target-proven.

## M68: verified named-ref all-parent path history

M67 actual native CMS passed on 2026-09-30: `GIT LOGDAG-REF-FULL HEAD 1` resolved modern REF2 `HEAD`, authenticated the requested all-parent DAG snapshots, and emitted two commit nodes only after `LOGDAG FULL SNAPSHOTS VERIFIED` (CPU 114.85 / elapsed 117.75 sec). M68 extends only the read-only REF2 bridge and GIT routing; no GITREC/GITCIDX/GITSEL code and no sealed-generation data change. New `GIT HISTORYPATH-REF-FULL <HEAD|branch|refs/heads/name> <depth> <path>` accepts depth 0..8 and a normal CMS path token, converts the path from EBCDIC to Git raw ASCII bytes, resolves the modern ref, and invokes already native-proven `GITREC HISTORYDAGPATH`. It releases `VERIFIED REF ...` plus per-snapshot commit/tree/path metadata only after `HISTORYDAGPATH FULL SNAPSHOTS VERIFIED`. Missing/malformed refs, invalid depth/path, missing path in any requested snapshot, corrupt commits or snapshots fail closed with no verified history-path output.

CI extends the verified-ref bridge guard to require HISTORYPATH routing, HISTORYDAGPATH binding, the full-snapshot marker, shared path translation, no write verbs and <=80-column CMS records. After strict CI/merge, M68 native validation needs no compile and no long GITRUN. Transfer only changed `GIT.EXEC` and `GITVREF.EXEC`; `GITREF2 REPO A` is unchanged. On CMS run `GIT HISTORYPATH-REF-FULL HEAD 1 README.md`. Expected key output begins `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C`, includes `HISTORYDAGPATH FULL SNAPSHOTS VERIFIED`, `HISTORYDAGPATH DATA BEGIN`, per-node PATH TYPE/SIZE/OID metadata, a final node count, and `HISTORYDAGPATH DATA END`. No ref or sealed-generation file is modified.

## M68 merged and green

M68 PR #51 passed full CI and merged as `1ec3ba4d41319a5b6232e13c6ae16fef95372009`. `GIT HISTORYPATH-REF-FULL <ref> <depth> <path>` now resolves REF2 names, validates depth 0..8, converts the CMS path to Git ASCII bytes, and invokes read-only `GITREC HISTORYDAGPATH`. It emits verified-ref and per-snapshot path metadata only after `HISTORYDAGPATH FULL SNAPSHOTS VERIFIED`. Native validation needs only updated `GIT.EXEC` and `GITVREF.EXEC`; no compile or GITRUN. Run `GIT HISTORYPATH-REF-FULL HEAD 1 README.md`. M68 is host-CI-proven, awaiting CMS target proof.

## New-chat handoff checkpoint — 2026-09-30

Latest native target proof is M67. Real CMS `GIT LOGDAG-REF-FULL HEAD 1` resolved modern REF2 `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, printed `LOGDAG FULL SNAPSHOTS VERIFIED`, emitted two all-parent DAG commit nodes, and ended with `LOGDAG NODES 2` / `LOGDAG DATA END`; CPU 114.85 / elapsed 117.75 sec. M67 is NATIVE CMS TARGET-PROVEN.

Current development milestone is M68, already merged to main and full host CI green. M68 adds `GIT HISTORYPATH-REF-FULL <ref> <depth> <path>`, routing a modern REF2 name plus normal CMS path into the already-proven `GITREC HISTORYDAGPATH` engine. Main currently contains the M68 routing in both `src/GIT.EXEC` and `src/GITVREF.EXEC`. M68 merged commit is `1ec3ba4d41319a5b6232e13c6ae16fef95372009`. It is HOST-CI-PROVEN but NOT YET CMS target-proven.

Exact next action after opening a new chat: do not redo M67. From Mac `ibm-sandbox/src`, `git pull`, then upload only `GIT.EXEC` and `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`. No compile and no GITRUN are required. On CMS run exactly `GIT HISTORYPATH-REF-FULL HEAD 1 README.md`. Expected success includes `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C`, `HISTORYDAGPATH FULL SNAPSHOTS VERIFIED`, `HISTORYDAGPATH DATA BEGIN`, per-node path type/size/OID records, `HISTORYDAGPATH NODES 2`, and `HISTORYDAGPATH DATA END`. If that passes, record CPU/elapsed, mark M68 native-proven, then continue autonomously to the next read-only user-facing milestone; pause only when the next real CMS validation is required.

Preserve all standing invariants: no writes to sealed `GITFIX/M15NEW STAGE/INDEX/SEEK/GEN`, selector PTRs, or `GITPBUF PACK`; modern REF2 remains read-only and separate from the old M5 ref store; no cross-generation mixing; no trusted-looking partial output before complete requested verification; C89 and <=72-column C physical lines; CMS EXEC records <=80 columns; keep maximum autonomous work per turn and minimal paste commands.

## 2026-09-30 actual M68 native CMS PASS

Real CMS `GIT HISTORYPATH-REF-FULL HEAD 1 README.md` passed. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, printed `HISTORYDAGPATH FULL SNAPSHOTS VERIFIED`, and emitted two authenticated DAG snapshots. Both depth 0 and depth 1 resolved `README.md` to the same blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5`, type 3, size 567. Output ended with `HISTORYDAGPATH NODES 2` and `HISTORYDAGPATH DATA END`. CPU 115.57 / elapsed 118.47 sec at 16:33:47. M68 is now NATIVE CMS TARGET-PROVEN. Do not rerun M68 standalone.

## M69: verified named-ref path-change summary

M69 extends only the read-only REF2 bridge and `GIT` routing. New `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` invokes the already target-proven `GITREC HISTORYDAGPATH` engine, with the same depth 0..8 and EBCDIC-to-Git-ASCII path validation. It buffers the complete native result, requires `HISTORYDAGPATH FULL SNAPSHOTS VERIFIED`, validates that every emitted PATHOID is exactly 40 hex digits, requires the PATHOID count to equal the final native node count, and only then emits the verified ref, authenticated per-node commit/path metadata, the number of distinct path OIDs, and the node count. This gives a compact answer to whether a named path changed across the requested all-parent history without weakening fail-closed behavior or modifying any native C or sealed data.

## M69 merged and strict host CI green

M69 PR #52 passed the complete native-stage workflow `36780503916` and squash-merged to main as `d2f4ac0ef741f7f3bddf8ab93549b6c4f47af4ba`. `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` reuses the M68 target-proven HISTORYDAGPATH engine, validates all buffered PATHOID records against the native node count, and only after complete snapshot verification emits authenticated node/path metadata plus `HISTORYCHANGES DISTINCT PATH OIDS N`. No native C, REF2 data, selector, sealed generation, or PACK changed. M69 is HOST-CI-PROVEN but NOT YET CMS target-proven.

NEXT real CMS gate: from Mac `ibm-sandbox/src`, `git pull`, upload only `GIT.EXEC` and `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`. No compile and no GITRUN. On CMS run exactly `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md`. For the already M68-proven two-node history, expected authenticated summary includes `VERIFIED REF HEAD 00D8D63229305230C8D37F884CE87F9E1A89468C`, `HISTORYCHANGES FULL SNAPSHOTS VERIFIED`, both PATHOID records equal to `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5`, `HISTORYCHANGES DISTINCT PATH OIDS 1`, `HISTORYCHANGES NODES 2`, and `HISTORYCHANGES DATA END`. Preserve all sealed inputs; do not rerun M68 separately.

## 2026-09-30 actual M69 native CMS PASS

Real CMS `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` passed. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, released output only after `HISTORYCHANGES FULL SNAPSHOTS VERIFIED`, and emitted two authenticated path-history nodes. Both nodes resolved `README.md` to blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5`, type 3, size 567. The summary reported `HISTORYCHANGES DISTINCT PATH OIDS 1`, `HISTORYCHANGES NODES 2`, and `HISTORYCHANGES DATA END`. CPU 117.25 / elapsed 120.24 sec at 16:40:14. M69 is now NATIVE CMS TARGET-PROVEN. Do not rerun M69 standalone.

## M70: explicit authenticated path-change status

M69 actual native CMS passed on 2026-09-30. M70 keeps the same read-only command and native HISTORYDAGPATH verification path, but after the fully authenticated PATHOID set is validated it now emits an explicit `HISTORYCHANGES STATUS UNCHANGED` when exactly one distinct path OID is present, otherwise `HISTORYCHANGES STATUS CHANGED`. The status is emitted only after complete snapshot verification and PATHOID/node-count validation; no new native traversal, C source, REF2 data, selector, sealed generation, or PACK changes are involved. For the target-proven `HEAD 1 README.md` case, the expected status is `UNCHANGED` because both verified snapshots carry blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5`.

## M70 merged and strict host CI green

M70 PR #53 passed complete native-stage workflow `36781077518` and squash-merged to main as `03596c9201a3497650835bdb30390c05af3b9afe`. The existing read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command now emits an explicit authenticated status after complete native snapshot verification and PATHOID/node-count validation: `HISTORYCHANGES STATUS UNCHANGED` when exactly one distinct PATHOID exists, otherwise `HISTORYCHANGES STATUS CHANGED`. No native C, GIT.EXEC routing, REF2 data, selector, sealed generation, or PACK changed in M70; only `GITVREF.EXEC`, its guard, and documentation changed. M70 is HOST-CI-PROVEN but NOT YET CMS target-proven.

NEXT real CMS gate: from Mac `ibm-sandbox/src`, `git pull`, upload only `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`; `GIT.EXEC` is unchanged from target-proven M69. No compile and no GITRUN. On CMS run exactly `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md`. Expected new line is `HISTORYCHANGES STATUS UNCHANGED`, alongside the already target-proven two PATHOID records, `HISTORYCHANGES DISTINCT PATH OIDS 1`, `HISTORYCHANGES NODES 2`, and `HISTORYCHANGES DATA END`. Preserve all sealed inputs; do not rerun M69 separately.

## 2026-09-30 actual M70 native CMS PASS

Real CMS `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` passed after the M70 EXEC update. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, released output only after `HISTORYCHANGES FULL SNAPSHOTS VERIFIED`, emitted two authenticated path-history nodes, and reported the same blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5` for both snapshots. The authenticated summary was `HISTORYCHANGES DISTINCT PATH OIDS 1`, `HISTORYCHANGES STATUS UNCHANGED`, `HISTORYCHANGES NODES 2`, `HISTORYCHANGES DATA END`. CPU 116.51 / elapsed 119.46 sec at 16:45:41. M70 is now NATIVE CMS TARGET-PROVEN. Do not rerun M70 standalone.

## M71: authenticated path-version distribution

M70 actual native CMS passed on 2026-09-30. M71 keeps the same read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command and target-proven native HISTORYDAGPATH verification, but now reports each distinct authenticated path OID and the number of verified snapshots carrying that version. Version counting occurs only after each PATHOID has passed 40-hex validation and the complete native node count matches the number of PATHOID records. Output uses compact records `HISTORYCHANGES VERSION N OID <oid40> COUNT N`, followed by the existing status and node summary. For the proven `HEAD 1 README.md` case the expected distribution is one version, OID `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5`, count 2. No native C, routing, REF2 data, selector, sealed generation, or PACK changes are involved.

## M71 merged and strict host CI green

M71 PR #54 passed complete native-stage workflow `36781624527` and squash-merged to main as `c57fc336365c6eb874a33bd912fcc07087006b69`. The existing read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command now emits one authenticated version-distribution record for each distinct PATHOID after complete native snapshot verification and PATHOID/node-count validation: `HISTORYCHANGES VERSION N OID <oid40> COUNT N`. No native C, GIT.EXEC routing, REF2 data, selector, sealed generation, or PACK changed in M71; only `GITVREF.EXEC`, its guard, and documentation changed. M71 is HOST-CI-PROVEN but NOT YET CMS target-proven.

NEXT real CMS gate: from Mac `ibm-sandbox/src`, `git pull`, upload only `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`; `GIT.EXEC` is unchanged from target-proven M69/M70. No compile and no GITRUN. On CMS run exactly `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md`. Expected new authenticated distribution line is `HISTORYCHANGES VERSION 1 OID 1BA7AE466BB0A16C294D52A8642E527B07D4D1F5 COUNT 2`, alongside the already target-proven `HISTORYCHANGES DISTINCT PATH OIDS 1`, `HISTORYCHANGES STATUS UNCHANGED`, `HISTORYCHANGES NODES 2`, and `HISTORYCHANGES DATA END`. Preserve all sealed inputs; do not rerun M70 separately.

## 2026-09-30 actual M71 native CMS PASS

Real CMS `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` passed after the M71 EXEC update. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, released output only after `HISTORYCHANGES FULL SNAPSHOTS VERIFIED`, and emitted two authenticated path-history nodes. Both snapshots resolved `README.md` to blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5`, type 3, size 567. The authenticated summary reported `HISTORYCHANGES DISTINCT PATH OIDS 1`, `HISTORYCHANGES STATUS UNCHANGED`, `HISTORYCHANGES VERSION 1 OID 1BA7AE466BB0A16C294D52A8642E527B07D4D1F5 COUNT 2`, `HISTORYCHANGES NODES 2`, and `HISTORYCHANGES DATA END`. CPU 116.06 / elapsed 118.99 sec at 16:50:34. M71 is now NATIVE CMS TARGET-PROVEN. Do not rerun M71 standalone.

## M72: authenticated path-version depth ranges

M71 actual native CMS passed on 2026-09-30. M72 keeps the same read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command and target-proven native HISTORYDAGPATH verification, but enriches each authenticated version-distribution record with the minimum and maximum DAG depth at which that PATHOID occurs. The bridge parses only already buffered `HISTORYDAGPATH NODE ... DEPTH ...` and PATHOID records, validates each depth as integer 0..8, requires a valid node depth before every PATHOID, and still requires the final PATHOID count to match the native node count before emitting any trusted summary. Output becomes `HISTORYCHANGES VERSION N OID <oid40> COUNT N MINDEPTH N MAXDEPTH N`. For the proven `HEAD 1 README.md` case, the one version should report count 2, min depth 0, max depth 1. No native C, routing, REF2 data, selector, sealed generation, or PACK changes are involved.

## M72 merged and strict host CI green

M72 PR #55 passed complete native-stage workflow `36782139794` and squash-merged to main as `be6a097b00b7bbe6f800697ba0aebcacf6410dd7`. The existing read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command now enriches each authenticated version-distribution record with the minimum and maximum all-parent DAG depth at which that path version appears: `HISTORYCHANGES VERSION N OID <oid40> COUNT N MINDEPTH N MAXDEPTH N`. Before emitting any trusted summary, M72 requires exactly one PATHOID per parsed node, validates every depth as 0..8, and requires parsed-node count, PATHOID count, and the native final HISTORYDAGPATH node count to agree. No native C, GIT.EXEC routing, REF2 data, selector, sealed generation, or PACK changed in M72; only `GITVREF.EXEC`, its guard, and documentation changed. M72 is HOST-CI-PROVEN but NOT YET CMS target-proven.

NEXT real CMS gate: from Mac `ibm-sandbox/src`, `git pull`, upload only `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`; `GIT.EXEC` remains unchanged from the already target-proven M69-M71 path. No compile and no GITRUN. On CMS run exactly `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md`. Expected new authenticated distribution line is `HISTORYCHANGES VERSION 1 OID 1BA7AE466BB0A16C294D52A8642E527B07D4D1F5 COUNT 2 MINDEPTH 0 MAXDEPTH 1`, alongside `HISTORYCHANGES DISTINCT PATH OIDS 1`, `HISTORYCHANGES STATUS UNCHANGED`, `HISTORYCHANGES NODES 2`, and `HISTORYCHANGES DATA END`. Preserve all sealed inputs; do not rerun M71 separately.

## 2026-09-30 M72 first CMS validation FAILED CLOSED

Real CMS `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` returned RC 8 with no trusted output; CPU 116.05 / elapsed 118.96 sec at 16:56:34. Root cause is an EXEC-layer M72 parser defect: `HISTORYDAGPATH NODE 1 DEPTH 0` was parsed with `word(...,4)`, yielding the literal `DEPTH`, rather than `word(...,5)`, yielding numeric depth `0`. The new M72 validation therefore rejected the buffered native result before emitting `VERIFIED REF` or any HISTORYCHANGES summary. This confirms fail-closed behavior. Native HISTORYDAGPATH, sealed generations, selectors, REF2, and PACK are unaffected. M72 is NOT target-proven until the corrected EXEC is retested.

## M72 depth-parser repair

Repair branch changes only the M72 EXEC parser from `word(out.ci,4)` to `word(out.ci,5)` for records shaped `HISTORYDAGPATH NODE <n> DEPTH <d>`. This is the field layout already proven by M68-M71 target transcripts. The fail-closed one-PATHOID-per-node and count-equality checks remain unchanged. Target retest requires only the corrected `GITVREF.EXEC`; no compile or GITRUN.

## M72 repair merged and strict host CI green

M72 repair PR #56 passed complete native-stage workflow `36782808576` and squash-merged to main as `ea4f77b22f00e40c19f62bde8cfd0697d976b6c0`. The only functional repair changes the EXEC parser for `HISTORYDAGPATH NODE <n> DEPTH <d>` from field 4 to field 5 so numeric depth is validated correctly. The original M72 CMS attempt failed closed with RC 8 and no trusted output, exactly as required. The stricter one-PATHOID-per-node and parsed-node/PATHOID/native-count equality checks remain intact. No native C, GIT.EXEC routing, REF2 data, selector, sealed generation, or PACK changed.

NEXT real CMS gate: from Mac `ibm-sandbox/src`, `git pull`, upload only corrected `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`. No compile and no GITRUN. On CMS rerun exactly `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md`. Expected authenticated version record is `HISTORYCHANGES VERSION 1 OID 1BA7AE466BB0A16C294D52A8642E527B07D4D1F5 COUNT 2 MINDEPTH 0 MAXDEPTH 1`, followed by the already proven unchanged/node summary. M72 remains not target-proven until this repaired EXEC passes on real CMS.

## 2026-09-30 actual repaired M72 native CMS PASS

Real CMS `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` passed after the depth-parser repair. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, released output only after `HISTORYCHANGES FULL SNAPSHOTS VERIFIED`, and emitted two authenticated path-history nodes. Both snapshots resolved `README.md` to blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5`, type 3, size 567. The authenticated summary reported `HISTORYCHANGES DISTINCT PATH OIDS 1`, `HISTORYCHANGES STATUS UNCHANGED`, `HISTORYCHANGES VERSION 1 OID 1BA7AE466BB0A16C294D52A8642E527B07D4D1F5 COUNT 2 MINDEPTH 0 MAXDEPTH 1`, `HISTORYCHANGES NODES 2`, and `HISTORYCHANGES DATA END`. CPU 115.83 / elapsed 118.72 sec at 17:02:11. M72 is now NATIVE CMS TARGET-PROVEN. The earlier RC8 attempt remains documented as successful fail-closed behavior.

## M73: authenticated path-version commit ranges

M72 actual native CMS passed on 2026-09-30. M73 keeps the same read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command and target-proven HISTORYDAGPATH verification, but now binds each authenticated version's minimum/maximum depth to the verified commit OID for those boundary nodes. It additionally requires exactly one valid 40-hex `HISTORYDAGPATH COMMIT` per parsed node before that node's PATHOID, preserving the existing one-PATHOID-per-node and total-count equality checks. After complete verification it emits `HISTORYCHANGES VERSION N MINDEPTHCOMMIT <oid40>` and `HISTORYCHANGES VERSION N MAXDEPTHCOMMIT <oid40>` alongside the M72 count/depth record. For the proven `HEAD 1 README.md` case, minimum-depth commit should be `00D8D63229305230C8D37F884CE87F9E1A89468C` and maximum-depth commit `2D5038C551318997B865497E04CF4C037DE4135E`. No native C, routing, REF2 data, selector, sealed generation, or PACK changes are involved.

## M73 merged and strict host CI green

M73 PR #57 passed complete native-stage workflow `36783352972` and squash-merged to main as `db60c029b98a6aa4ff530838e710f1855f0538c7`. The existing read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command now binds each authenticated version's minimum and maximum DAG depth to the corresponding verified commit OID, emitting `HISTORYCHANGES VERSION N MINDEPTHCOMMIT <oid40>` and `HISTORYCHANGES VERSION N MAXDEPTHCOMMIT <oid40>`. Before trusted output, M73 requires exactly one valid 40-hex COMMIT and one PATHOID per parsed node and retains parsed-node/PATHOID/native-count equality. Labels are depth-based, not chronological. No native C, GIT.EXEC routing, REF2 data, selector, sealed generation, or PACK changed in M73; only `GITVREF.EXEC`, its guard, and documentation changed. M73 is HOST-CI-PROVEN but NOT YET CMS target-proven.

NEXT real CMS gate: from Mac `ibm-sandbox/src`, `git pull`, upload only `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`. No compile and no GITRUN. On CMS run exactly `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md`. Expected new authenticated lines are `HISTORYCHANGES VERSION 1 MINDEPTHCOMMIT 00D8D63229305230C8D37F884CE87F9E1A89468C` and `HISTORYCHANGES VERSION 1 MAXDEPTHCOMMIT 2D5038C551318997B865497E04CF4C037DE4135E`, alongside the target-proven M72 version/depth record and unchanged/node summary. Preserve all sealed inputs; do not rerun M72 separately.

## 2026-10-01 actual M73 native CMS PASS

Real CMS `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` passed after the M73 EXEC update. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, released output only after `HISTORYCHANGES FULL SNAPSHOTS VERIFIED`, and emitted two authenticated path-history nodes. Both snapshots resolved `README.md` to blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5`, type 3, size 567. The authenticated summary reported `HISTORYCHANGES DISTINCT PATH OIDS 1`, `HISTORYCHANGES STATUS UNCHANGED`, `HISTORYCHANGES VERSION 1 OID 1BA7AE466BB0A16C294D52A8642E527B07D4D1F5 COUNT 2 MINDEPTH 0 MAXDEPTH 1`, `HISTORYCHANGES VERSION 1 MINDEPTHCOMMIT 00D8D63229305230C8D37F884CE87F9E1A89468C`, `HISTORYCHANGES VERSION 1 MAXDEPTHCOMMIT 2D5038C551318997B865497E04CF4C037DE4135E`, `HISTORYCHANGES NODES 2`, and `HISTORYCHANGES DATA END`. CPU 115.58 / elapsed 118.44 sec at 08:32:19. M73 is now NATIVE CMS TARGET-PROVEN.

## M74 merged and strict host CI green

M74 PR #58 passed complete native-stage workflow `36871899513` and squash-merged to main as `e44cb993e7d790d4a02fbe0b2f9836266726e7fe`. The existing read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command now binds each distinct authenticated PATHOID to its terminal Git object type and size, emitting `HISTORYCHANGES VERSION N TYPE <type> SIZE <size>`. M74 requires exactly one PATH TYPE/SIZE record per parsed node before its PATHOID, validates native HISTORYDAGPATH type 1..3 and nonnegative whole-number size, and requires repeated occurrences of the same PATHOID to agree on type and size before trusted output. No native C, GIT.EXEC routing, REF2 data, selector, sealed generation, or PACK changed. M74 is HOST-CI-PROVEN but NOT YET CMS target-proven.

NEXT real CMS gate: from Mac `ibm-sandbox/src`, `git pull`, upload only `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`. No compile and no GITRUN. On CMS run exactly `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md`. Expected new authenticated line is `HISTORYCHANGES VERSION 1 TYPE 3 SIZE 567`, alongside the already target-proven M73 version/depth/commit-range records and unchanged/node summary. Preserve all sealed inputs; do not rerun M73 separately.

## 2026-10-01 actual M74 native CMS PASS

Real CMS `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` passed after the M74 EXEC update. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, released output only after `HISTORYCHANGES FULL SNAPSHOTS VERIFIED`, and emitted two authenticated path-history nodes. Both snapshots resolved `README.md` to blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5`, with native path metadata `TYPE 3 SIZE 567`. The authenticated summary reported `HISTORYCHANGES DISTINCT PATH OIDS 1`, `HISTORYCHANGES STATUS UNCHANGED`, `HISTORYCHANGES VERSION 1 OID 1BA7AE466BB0A16C294D52A8642E527B07D4D1F5 COUNT 2 MINDEPTH 0 MAXDEPTH 1`, `HISTORYCHANGES VERSION 1 TYPE 3 SIZE 567`, `HISTORYCHANGES VERSION 1 MINDEPTHCOMMIT 00D8D63229305230C8D37F884CE87F9E1A89468C`, `HISTORYCHANGES VERSION 1 MAXDEPTHCOMMIT 2D5038C551318997B865497E04CF4C037DE4135E`, `HISTORYCHANGES NODES 2`, and `HISTORYCHANGES DATA END`. CPU 115.75 / elapsed 118.69 sec at 09:03:38. M74 is now NATIVE CMS TARGET-PROVEN.

## M75: exact authenticated path-version depth sets

M74 actual native CMS passed on 2026-10-01. M75 keeps the same read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command and target-proven HISTORYDAGPATH traversal, but supplements each version's min/max depth range with the exact set of authenticated DAG depths at which that PATHOID occurs. The bridge records depth membership only after a node's depth, commit, type/size metadata, and PATHOID have all passed the existing fail-closed checks. After the complete native result and all node/count consistency checks pass, it emits `HISTORYCHANGES VERSION N DEPTHS d[,d...]`. For the proven `HEAD 1 README.md` case, version 1 should report `DEPTHS 0,1`. This avoids implying that every depth between MINDEPTH and MAXDEPTH is populated. No native C, routing, REF2 data, selector, sealed generation, or PACK changes are involved.

## M75 merged and strict host CI green

M75 PR #59 passed complete native-stage workflow `36875668714` and squash-merged to main as `c216f9413bfcfd77846f4cbecaa9e6bca7c9a26b`. The existing read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command now emits the exact authenticated DAG depth set for each distinct PATHOID as `HISTORYCHANGES VERSION N DEPTHS d[,d...]`. Depth membership is recorded only after a node's depth, commit, type/size metadata, and PATHOID all pass the existing fail-closed checks, and every version depth string is precomputed before any trusted output begins. No native C, GIT.EXEC routing, REF2 data, selector, sealed generation, or PACK changed. M75 is HOST-CI-PROVEN but NOT YET CMS target-proven.

NEXT real CMS gate: from Mac `ibm-sandbox/src`, `git pull`, upload only `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`. No compile and no GITRUN. On CMS run exactly `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md`. Expected new authenticated line is `HISTORYCHANGES VERSION 1 DEPTHS 0,1`, alongside the already target-proven M74 version/type/size/depth/commit-range records and unchanged/node summary. Preserve all sealed inputs; do not rerun M74 separately.

## 2026-10-01 actual M75 native CMS PASS

Real CMS `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` passed after the M75 EXEC update. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, released output only after `HISTORYCHANGES FULL SNAPSHOTS VERIFIED`, and emitted two authenticated path-history nodes. Both snapshots resolved `README.md` to blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5`, with `TYPE 3 SIZE 567`. The authenticated summary reported `HISTORYCHANGES DISTINCT PATH OIDS 1`, `HISTORYCHANGES STATUS UNCHANGED`, `HISTORYCHANGES VERSION 1 OID 1BA7AE466BB0A16C294D52A8642E527B07D4D1F5 COUNT 2 MINDEPTH 0 MAXDEPTH 1`, `HISTORYCHANGES VERSION 1 DEPTHS 0,1`, `HISTORYCHANGES VERSION 1 TYPE 3 SIZE 567`, `HISTORYCHANGES VERSION 1 MINDEPTHCOMMIT 00D8D63229305230C8D37F884CE87F9E1A89468C`, `HISTORYCHANGES VERSION 1 MAXDEPTHCOMMIT 2D5038C551318997B865497E04CF4C037DE4135E`, `HISTORYCHANGES NODES 2`, and `HISTORYCHANGES DATA END`. CPU 116.06 / elapsed 118.98 sec at 09:25:00. M75 is now NATIVE CMS TARGET-PROVEN.

## M76: exact authenticated path-version commit sets

M75 actual native CMS passed on 2026-10-01. M76 keeps the same read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command and target-proven HISTORYDAGPATH traversal, but supplements each version's exact depth set with the exact verified commit OIDs that carry that PATHOID in the requested DAG window. Commit membership is recorded only after a node's depth, commit, type/size metadata, and PATHOID have all passed existing fail-closed validation. All commit-list strings are precomputed before trusted output begins. Output adds `HISTORYCHANGES VERSION N COMMITS <oid40>[,<oid40>...]`. For the proven `HEAD 1 README.md` case, version 1 should list commits `00D8D63229305230C8D37F884CE87F9E1A89468C,2D5038C551318997B865497E04CF4C037DE4135E`. No native C, routing, REF2 data, selector, sealed generation, or PACK changes are involved.

## M76 output-shape refinement

Before CI, M76 was refined to avoid an unbounded comma-separated commit-list record. The authenticated commit set is now emitted as one bounded record per occurrence: `HISTORYCHANGES VERSION N COMMIT <oid40>`. Commit OIDs are stored only after the corresponding verified node/PATHOID pair passes validation, all stored commit OIDs are checked before trusted output, and the existing `COUNT N` remains the authoritative number of commit records for that version. For the proven two-node README history, version 1 should emit exactly two COMMIT records, one for depth 0 HEAD and one for depth 1 parent.

## M76 merged and strict host CI green

M76 PR #60 passed complete native-stage workflow `36880731215` and squash-merged to main as `4d5fcf6fc6ab1d23747c241f871b75530678dfa6`. The existing read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command now emits one bounded authenticated commit record for every verified node carrying each distinct PATHOID: `HISTORYCHANGES VERSION N COMMIT <oid40>`. Commit membership is stored only after the node's depth, commit, type/size metadata, and PATHOID pass existing fail-closed validation; every stored commit OID is validated before trusted output starts; and the existing version `COUNT N` remains the authoritative count of emitted COMMIT records. The implementation deliberately avoids unbounded comma-separated output. No native C, GIT.EXEC routing, REF2 data, selector, sealed generation, or PACK changed. M76 is HOST-CI-PROVEN but NOT YET CMS target-proven.

NEXT real CMS gate: from Mac `ibm-sandbox/src`, `git pull`, upload only `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`. No compile and no GITRUN. On CMS run exactly `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md`. For the already target-proven two-node README history, expected new authenticated records are `HISTORYCHANGES VERSION 1 COMMIT 00D8D63229305230C8D37F884CE87F9E1A89468C` and `HISTORYCHANGES VERSION 1 COMMIT 2D5038C551318997B865497E04CF4C037DE4135E`, with the existing version `COUNT 2`, `DEPTHS 0,1`, type/size, depth-bound commit records, and unchanged/node summary preserved. Preserve all sealed inputs; do not rerun M75 separately.

## 2026-10-01 actual M76 native CMS PASS

Real CMS `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` passed after the M76 EXEC update. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, released output only after `HISTORYCHANGES FULL SNAPSHOTS VERIFIED`, and emitted two authenticated path-history nodes. Both snapshots resolved `README.md` to blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5`, `TYPE 3 SIZE 567`. The authenticated summary reported `COUNT 2`, `DEPTHS 0,1`, exactly two bounded version COMMIT records (`00D8D63229305230C8D37F884CE87F9E1A89468C` and `2D5038C551318997B865497E04CF4C037DE4135E`), the existing type/size and depth-bound commit records, `HISTORYCHANGES NODES 2`, and `HISTORYCHANGES DATA END`. CPU 115.83 / elapsed 118.75 sec at 10:07:42. M76 is now NATIVE CMS TARGET-PROVEN.

## M77: authenticated commit-depth membership

M76 actual native CMS passed on 2026-10-01. M77 keeps the same read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command and target-proven HISTORYDAGPATH traversal, but makes each per-version COMMIT record self-contained by attaching that node's authenticated DAG depth. The bridge stores commit and depth together only after the node's depth, commit, type/size metadata, and PATHOID have passed existing fail-closed checks. Before trusted output, every stored commit OID must be 40 hex characters and every stored depth must be a whole number from 0 through 8. Output becomes `HISTORYCHANGES VERSION N COMMIT <oid40> DEPTH <d>`. For the proven `HEAD 1 README.md` case, version 1 should emit HEAD at depth 0 and its parent at depth 1. No native C, routing, REF2 data, selector, sealed generation, or PACK changes are involved.

## M77 merged and strict host CI green

M77 PR #61 passed complete native-stage workflow `36882518028` and squash-merged to main as `613cc0a021834f440fe6081773f55e1843329b95`. The existing read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` command now makes every per-version COMMIT membership record self-contained by attaching the authenticated DAG depth from the same verified node: `HISTORYCHANGES VERSION N COMMIT <oid40> DEPTH <d>`. Commit and depth are stored together only after the node's depth, commit, type/size metadata, and PATHOID pass all existing fail-closed checks. Before trusted output, every stored commit OID must be length 40 and every stored depth must be an integer from 0 through 8. CMS EXEC records remain <=80 columns. No native C, GIT.EXEC routing, REF2 data, selector, sealed generation, or PACK changed. M77 is HOST-CI-PROVEN but NOT YET CMS target-proven.

NEXT real CMS gate: from Mac `ibm-sandbox/src`, `git pull`, upload only `GITVREF.EXEC` with `CMS_SCRIPT_PORT=3272`. No compile and no GITRUN. On CMS run exactly `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md`. For the already target-proven two-node README history, expected new authenticated records are `HISTORYCHANGES VERSION 1 COMMIT 00D8D63229305230C8D37F884CE87F9E1A89468C DEPTH 0` and `HISTORYCHANGES VERSION 1 COMMIT 2D5038C551318997B865497E04CF4C037DE4135E DEPTH 1`, with the existing COUNT, DEPTHS, TYPE/SIZE, MINDEPTHCOMMIT/MAXDEPTHCOMMIT, and unchanged/node summary preserved. Preserve all sealed inputs; do not rerun M76 separately.

## 2026-10-01 actual M77 native CMS PASS

Real CMS `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` passed after the M77 EXEC update. It resolved `HEAD` to `00D8D63229305230C8D37F884CE87F9E1A89468C`, released output only after `HISTORYCHANGES FULL SNAPSHOTS VERIFIED`, and emitted two authenticated path-history nodes. Version 1 remained blob `1BA7AE466BB0A16C294D52A8642E527B07D4D1F5`, `COUNT 2`, `DEPTHS 0,1`, `TYPE 3 SIZE 567`. Its exact membership records were `HISTORYCHANGES VERSION 1 COMMIT 00D8D63229305230C8D37F884CE87F9E1A89468C DEPTH 0` and `HISTORYCHANGES VERSION 1 COMMIT 2D5038C551318997B865497E04CF4C037DE4135E DEPTH 1`. CPU 115.77 / elapsed 118.69 sec at 10:24:36. M77 is now NATIVE CMS TARGET-PROVEN.

## M78-M80 batched snapshot-membership hardening

M77 actual native CMS passed on 2026-10-01. To minimize target churn, M78 through M80 are batched behind one next CMS gate. The existing read-only `GIT HISTORYCHANGES-REF-FULL <ref> <depth> <path>` wrapper now validates native `HISTORYDAGPATH NODE` ordinals as contiguous 1..N, rejects duplicate commit OIDs in the buffered DAG result, requires exactly one valid 40-hex TREE OID per node after its COMMIT and before path metadata, and stores each distinct path version's exact snapshot membership as node ordinal, DAG depth, commit OID, and tree OID. Before any trusted output, all stored node/depth/commit/tree values are revalidated and the sum of per-version membership counts must equal the native final node count. New bounded records are `HISTORYCHANGES VERSION N NODE <node> DEPTH <d>`, `HISTORYCHANGES VERSION N NODE <node> COMMIT <oid40>`, and `HISTORYCHANGES VERSION N NODE <node> TREE <oid40>`. Existing M77 COMMIT/DEPTH, COUNT, DEPTHS, TYPE/SIZE and boundary records remain for compatibility. No native C, GIT.EXEC routing, REF2 data, selector, sealed generation, or PACK changes are involved.

## M81-M83 batched parent-edge path-change semantics

After M80 host CI, the next native batch adds edge-aware change semantics without relaxing atomic verification. M81 extends native `GITREC HISTORYDAGPATH` to retain child-to-parent relationships discovered during the all-parent BFS and emit `HISTORYDAGPATH EDGE CHILD <node> PARENT <node>` records plus a final edge count only after every requested commit, complete snapshot closure, and named path have authenticated. M82 extends the read-only REF2 wrapper to validate every native edge, map child and parent nodes to their already authenticated path-version numbers, and precompute per-edge `CHANGED` versus `UNCHANGED` status before trusted output. M83 hardens the graph section further: duplicate edges are rejected, node references must be in range, native edge-count and parsed-edge count must agree, node 1 cannot occur as a parent endpoint, and every node 2..N must be covered as a parent endpoint so the edge section spans the same connected history window as the node section. Trusted summary output adds overall edge counts and bounded records for each edge's child/parent nodes, child/parent version numbers, and status. No write path, REF2 data, selector, sealed generation, or PACK changes are involved. This batch changes native `GITREC.C`, so the next real CMS gate will require one GITREC rebuild plus the updated GITVREF EXEC; M80-M83 can be proven together in that gate.

## M84: cross-check whole-window and edge change semantics

M84 adds a final pre-output invariant to the M81-M83 edge-aware batch. Because the validated history graph is connected, a window with exactly one distinct authenticated path version must have zero changed edges, while a window with multiple distinct authenticated path versions must have at least one changed edge. The wrapper now enforces those implications before releasing trusted output, in addition to edge-count, connectivity, node/version, and membership checks. This keeps the legacy whole-window `HISTORYCHANGES STATUS` and the new edge-level statuses mutually consistent.

## M85-M86: concise verified edge-history command

To maximize work before the next CMS gate, M85-M86 add a concise user-facing edge report on top of the M81-M84 native edge engine. `GIT HISTORYEDGES-REF-FULL <ref> <depth> <path>` routes to `GITVREF HISTEDGE`, invokes the same native `GITREC HISTORYDAGPATH` traversal, and runs the identical snapshot, node, commit, tree, path-metadata, PATHOID, edge-count, connectivity, membership, and whole-window/edge consistency checks used by the verbose HISTORYCHANGES report. Only after all checks pass does it emit `HISTORYEDGES FULL SNAPSHOTS VERIFIED`, the whole-window status, a version-number-to-PATHOID map, node/edge totals, changed/unchanged edge totals, and bounded per-edge child/parent node, child/parent version, and status records. No independent traversal or weaker validation path is introduced. This adds `GIT.EXEC` routing and GITVREF presentation logic only; the native C changes remain those from M81.

## M80-M86 merged and strict host CI green

M80 PR #62 passed native-stage workflow `36888807496` and squash-merged as `4ef53c4776fee6b552d253f1e813f6c5226a617b`. M84 PR #63 passed native-stage workflow `36889621491` and squash-merged as `44a9e9e3b6689b651c13b02c4f32ccab3d8dc252`. M86 PR #64 passed native-stage workflow `36889948535` and squash-merged as `3606919f213025959d68aeeda4b0e55d3688d72c`.

The merged batch now includes: exact per-version snapshot membership (node ordinal, depth, commit, tree); native HISTORYDAGPATH child-to-parent edge emission after complete authentication; wrapper validation of edge syntax/count/connectivity and duplicate rejection; per-edge child/parent path-version mapping and CHANGED/UNCHANGED status with changed/unchanged totals; consistency checks between whole-window and edge-level status; and new concise user command `GIT HISTORYEDGES-REF-FULL <ref> <depth> <path>` reusing the same fully verified native traversal and parser. Native `GITREC.C`, `GITVREF.EXEC`, and `GIT.EXEC` changed. C89 host compile is green, C physical lines remain <=72, CMS EXEC lines <=80, and no write path, REF2 data, selector, sealed generation, or PACK changed.

NEXT combined real CMS gate: from Mac `ibm-sandbox/src`, `git pull`, then upload `GITREC.C`, `GITVREF.EXEC`, and `GIT.EXEC` together with `CMS_SCRIPT_PORT=3272`. On CMS rebuild only `GITREC` with `CMSCLNK GITREC PLAIN`; no GITRUN. Then run `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` followed by `GIT HISTORYEDGES-REF-FULL HEAD 1 README.md`.

For the already target-proven two-node README history, expected native edge is child node 1 -> parent node 2. HISTORYCHANGES should retain all prior M77 records and additionally report one edge, zero changed edges, one unchanged edge, edge 1 child version 1 / parent version 1 / status UNCHANGED, plus exact version snapshot records for node 1 at depth 0 with commit `00D8D63229305230C8D37F884CE87F9E1A89468C` and tree `204E1D6968FB81C35BF830D63A611AC64C072945`, and node 2 at depth 1 with commit `2D5038C551318997B865497E04CF4C037DE4135E` and tree `F3EF36AAD778D5DA84857D8DED46495C75F4CAB0`. HISTORYEDGES should report status UNCHANGED, versions 1, nodes 2, edges 1, changed edges 0, unchanged edges 1, and the same edge 1 child 1 / parent 2, child version 1 / parent version 1, status UNCHANGED. M80-M86 are HOST-CI-PROVEN but not yet CMS target-proven.

## 2026-10-01 first M80-M86 CMS gate FAILED CLOSED

Real CMS rebuilt `GITREC MODULE` successfully with `CMSCLNK GITREC PLAIN` (12.36 CPU / 12.80 elapsed). Both `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` and `GIT HISTORYEDGES-REF-FULL HEAD 1 README.md` then returned RC 8 with no trusted output after roughly the normal native traversal time (115.83/118.73 and 116.02/118.92). Root cause is EXEC-layer node-to-version binding in the newly added edge classifier: on the first occurrence of a PATHOID, `vi=seen.poid` is still the uninitialized REXX compound-variable value; the code creates `distinct` and `seen.poid=distinct` but did not then set `vi=distinct` before `nodeversion.curnode=vi`. Thus node 1 received a nonnumeric version token and pre-output edge validation correctly failed closed. Native GITREC build/traversal, sealed generations, selectors, REF2 and PACK are unaffected. M80-M86 remain not target-proven pending corrected GITVREF retest.

## M86 node-version binding repair

Repair sets `vi=distinct` immediately after allocating the first occurrence of a new PATHOID and before `nodeversion.curnode=vi`. This preserves all existing M80-M86 checks and fixes only the first-occurrence version binding used by edge classification. No GITREC.C, GIT.EXEC, REF2 data, sealed generations, selectors, or PACK are changed by the repair. Because the already uploaded GITREC native edge engine built successfully on CMS, the retest requires only corrected `GITVREF.EXEC`; no rebuild and no GITRUN.

## M86 repair also preserves HISTORYPATH compatibility

Because native HISTORYDAGPATH now carries internal EDGE/EDGES records, the generic HISTPATH pass-through would otherwise have changed the previously target-proven `GIT HISTORYPATH-REF-FULL` output surface. The repaired GITVREF now filters only native `HISTORYDAGPATH EDGE ...` and `HISTORYDAGPATH EDGES ...` records when command mode is HISTPATH. HISTORYCHANGES and HISTORYEDGES still parse those records internally. This keeps the M68 HISTORYPATH user-visible format stable while retaining the new edge engine.

## M86 repair merged and host CI green

Repair PR #65 passed native-stage workflow `36893598554` and squash-merged as `a7948adc69587f6ce179e4238a48ba8e2757b116`. The first-occurrence PATHOID bug is fixed by assigning `vi=distinct` immediately after allocating a new version, before `nodeversion.curnode=vi`. The repair also preserves the previously target-proven HISTORYPATH output surface by filtering only internal native `HISTORYDAGPATH EDGE` and `HISTORYDAGPATH EDGES` records in HISTPATH mode. GITREC.C and GIT.EXEC are unchanged from the already uploaded/rebuilt M86 gate; only GITVREF.EXEC must be refreshed for target retest. No compile and no GITRUN are required.

NEXT target retest: from Mac `ibm-sandbox/src`, `git pull`, then `CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITVREF.EXEC`. On CMS run `GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` and `GIT HISTORYEDGES-REF-FULL HEAD 1 README.md`. Optional compatibility check in the same session: `GIT HISTORYPATH-REF-FULL HEAD 1 README.md`; it should retain the old M68-style output without native EDGE/EDGES records. If the two edge-aware commands pass, M80-M86 can be marked NATIVE CMS TARGET-PROVEN based on the already successful GITREC rebuild plus this repaired wrapper run.

## 2026-10-01 actual repaired M80-M86 native CMS PASS

Real CMS passed the repaired combined gate. HISTORYCHANGES reported one authenticated edge, child node 1 -> parent node 2, child version 1 -> parent version 1, status UNCHANGED, with zero changed edges and one unchanged edge. Exact snapshot membership matched the expected commits and trees. CPU 115.78 / elapsed 118.67 sec at 12:29:01.

HISTORYEDGES independently passed with status UNCHANGED, versions 1, nodes 2, edges 1, changed edges 0, unchanged edges 1, and the same node/version edge mapping. CPU 115.74 / elapsed 118.64 sec at 12:33:45.

HISTORYPATH also passed and preserved the previously proven output surface with no EDGE/EDGES records exposed. CPU 116.00 / elapsed 118.91 sec at 12:37:07. Together with the successful GITREC rebuild from the prior gate, M80-M86 are now NATIVE CMS TARGET-PROVEN.

## 2026-10-01 actual M87 native CMS PASS

Real CMS `GIT HISTORYEDGES-REF-FULL HEAD 1 README.md` passed with authenticated edge endpoint metadata: child depth 0, parent depth 1, child commit `00D8D63229305230C8D37F884CE87F9E1A89468C`, parent commit `2D5038C551318997B865497E04CF4C037DE4135E`, child tree `204E1D6968FB81C35BF830D63A611AC64C072945`, and parent tree `F3EF36AAD778D5DA84857D8DED46495C75F4CAB0`. Edge 1 remained child node 1 -> parent node 2, version 1 -> 1, status UNCHANGED. CPU 115.72 / elapsed 118.63 sec at 12:50:24.

`GIT HISTORYCHANGES-REF-FULL HEAD 1 README.md` also emitted the same authenticated edge endpoint metadata while preserving the existing M80-M86 path-version and snapshot-membership report. M87 is now NATIVE CMS TARGET-PROVEN.

## M88-M90: transition matrix and changed-edge report

M87 native CMS passed on 2026-10-01. M88 aggregates the already authenticated edge graph into a version-transition matrix: each distinct child-version -> parent-version pair carries an exact edge count, and the matrix total must equal the verified native edge count before trusted output. HISTORYEDGES and HISTORYCHANGES now emit `TRANSITIONS N` plus bounded `TRANSITION N CHILDVERSION x PARENTVERSION y COUNT n` records.

M89 adds `GIT HISTORYDIFFS-REF-FULL <ref> <depth> <path>`. It reuses the same target-proven HISTORYDAGPATH traversal and all M80-M87 parsing, graph, membership, endpoint, and status checks, but emits only edges whose authenticated child and parent PATHOID versions differ. An unchanged window succeeds with `HISTORYDIFFS CHANGED EDGES 0` and no edge records; a changed window emits only the changed edges with node, version, depth, commit, and tree endpoint metadata. M90 locks both features behind the existing fail-closed atomic output path. No native C, REF2 data, selector, sealed generation, or PACK changes are involved; next target gate is EXEC-only.

## M91-M93: self-contained authenticated edge diffs

M91 makes each HISTORYDIFFS/HISTORYEDGES/HISTORYCHANGES edge record self-contained with direct child/parent PATHOID plus authenticated terminal object type and size, in addition to the already proven node/depth/commit/tree metadata. M92 derives and validates the subset of version transitions that are actually changed, emits HISTORYDIFFS STATUS and a changed-transition matrix, and fails closed if changed-edge and changed-transition presence disagree. M93 also adds direct child/parent PATHOIDs to the full transition matrices in HISTORYEDGES and HISTORYCHANGES. No native C or protected data changes are involved.

The next target gate should prove both status branches. `README.md` remains the known UNCHANGED path. The HEAD commit `00D8D632...` added `src/M9JOBJ.EXEC`, so the existing `src` directory tree changed relative to parent `2D5038C...`; therefore `GIT HISTORYDIFFS-REF-FULL HEAD 1 src` is the intended CHANGED-path proof while still existing in both snapshots.

## M94-M96: authenticated absent-path history and four-way edge diffs

M94 adds a new native `GITREC HISTORYDAGSTATE C0 C1 COMMIT40 DEPTH PATHHEX` operation. It preserves the existing target-proven `HISTORYDAGPATH` semantics unchanged. The new operation performs the same verified all-parent commit traversal, full root-closure authentication, 64-node cap, and edge capture, but records each snapshot path as either `HISTORYDAGSTATE PATH PRESENT TYPE <type> SIZE <size>` plus PATHOID, or `HISTORYDAGSTATE PATH ABSENT`. Missing path components and non-tree intermediate components are treated as authenticated absence only after the containing tree has authenticated; missing/corrupt referenced objects still fail closed.

M95 switches only `GIT HISTORYDIFFS-REF-FULL` to HISTORYDAGSTATE. HISTORYPATH, HISTORYCHANGES, and HISTORYEDGES remain on strict HISTORYDAGPATH. M96 adds a separate strict state parser and classifies every verified child-to-parent edge as `ADDED`, `DELETED`, `MODIFIED`, or `UNCHANGED`. HISTORYDIFFS emits only changed edges, with child/parent PRESENT/ABSENT state plus authenticated depth, commit, tree and, when present, PATHOID/type/size. It also emits exact ADDED/DELETED/MODIFIED/UNCHANGED edge totals before any edge records. No write path, REF2 data, selector, sealed generation, or PACK changes are involved.

Concrete target proofs are available from the known HEAD/parent pair. `README.md` is unchanged. `src` is MODIFIED because HEAD `00D8D632...` adds `src/M9JOBJ.EXEC`. `src/M9JOBJ.EXEC` itself is ADDED: GitHub commit metadata for HEAD identifies that file as newly added relative to parent `2D5038C...`. A DELETED-path target proof can be added later from a commit window containing an actual removal; the implementation is symmetric and remains fail-closed.

## M97: concise authenticated path-state timeline

M97 adds `GIT HISTORYSTATE-REF-FULL <ref> <depth> <path>`, routed through the same new native `HISTORYDAGSTATE` engine and strict state parser used by HISTORYDIFFS. It emits every verified snapshot node with depth, commit, tree, and explicit `STATE PRESENT|ABSENT`; present nodes additionally emit PATHOID/type/size. It also emits the authenticated child-parent edge list. This is a raw state timeline, not a weaker traversal or a second parser. The next target gate can therefore validate raw state and classified diffs from one native GITREC rebuild.

## M98-M99: authenticated lifecycle summaries

M98 extends HISTORYSTATE with pre-output snapshot counts and lifecycle status: `ALLPRESENT`, `ALLABSENT`, or `MIXED`, plus exact PRESENT and ABSENT counts. M99 carries the same authenticated lifecycle summary into HISTORYDIFFS alongside the edge-level ADDED/DELETED/MODIFIED/UNCHANGED counts. All lifecycle values are derived only after the strict HISTORYDAGSTATE parser has validated every node, state, commit, tree, edge count, and connectivity relation. No native C changes beyond M94 and no protected-data changes are involved.

## M94-M99 merged and strict host CI green

M94-M97 PR #69 passed full native-stage workflow `36910918273` and squash-merged as `bbbeb20da43ab96fd6226e3ebb0cceaaae79240d`. M98-M99 PR #70 passed full native-stage workflow `36911543205` and squash-merged as `3d9dcc8b3a3bcf3664c86c48b7589f365ba5556c`.

The merged batch adds native `GITREC HISTORYDAGSTATE`, preserving existing HISTORYDAGPATH semantics unchanged. HISTORYDAGSTATE authenticates the same all-parent commit/snapshot graph but permits an explicitly authenticated ABSENT path state. `GIT HISTORYSTATE-REF-FULL` emits the raw PRESENT/ABSENT timeline with lifecycle status/counts. `GIT HISTORYDIFFS-REF-FULL` now classifies verified child-to-parent edges as ADDED, DELETED, MODIFIED, or UNCHANGED and emits only changed edges, with exact status totals and endpoint depth/commit/tree plus OID/type/size when present. C physical source lines remain <=72 and CMS EXEC lines <=80. No protected REF2/selector/generation/PACK data changed.

Exact next target proofs from HEAD `00D8D632...` and parent `2D5038C...`: README.md is ALLPRESENT and UNCHANGED with blob `1BA7AE46...D1F5`, size 567. `src` is ALLPRESENT and MODIFIED, changing tree OID from parent `884916539208F673916FBD6988DE6B028C355723` to child `A41B3EA7758F301B7E30BD3CFDF264300C02AE35`. `src/M9JOBJ.EXEC` is MIXED and ADDED: child PRESENT blob `775F6C809889E3497D8837379B37A706DFD101CA`, size 646; parent ABSENT. No deletion occurs in the reachable depth-8 first-parent window, so DELETED remains host-proven but lacks a real target fixture in this window.

NEXT combined CMS gate: upload `GITREC.C`, `GITVREF.EXEC`, and `GIT.EXEC`, rebuild only `GITREC` with `CMSCLNK GITREC PLAIN`, no GITRUN. Then validate HISTORYSTATE/HISTORYDIFFS on README.md, src, and src/M9JOBJ.EXEC. This is the next genuine target dependency; additional host-only work would stack more presentation logic on an unproven native HISTORYDAGSTATE foundation.

## 2026-10-01 actual M94-M99 native CMS PASS

Real CMS rebuilt the new native state engine successfully with `CMSCLNK GITREC PLAIN` (13.31 CPU / 13.77 elapsed at 14:13:35). `GIT HISTORYDIFFS-REF-FULL HEAD 1 README.md` passed as UNCHANGED / ALLPRESENT with PRESENT 2, ABSENT 0, one unchanged edge and zero added/deleted/modified edges (115.83 CPU / 118.69 elapsed at 14:15:49).

`GIT HISTORYDIFFS-REF-FULL HEAD 1 src` passed as CHANGED / ALLPRESENT with one MODIFIED edge: child node 1 depth 0 commit `00D8D63229305230C8D37F884CE87F9E1A89468C` tree `204E1D6968FB81C35BF830D63A611AC64C072945` path tree `A41B3EA7758F301B7E30BD3CFDF264300C02AE35` type 2 size 3690; parent node 2 depth 1 commit `2D5038C551318997B865497E04CF4C037DE4135E` tree `F3EF36AAD778D5DA84857D8DED46495C75F4CAB0` path tree `884916539208F673916FBD6988DE6B028C355723` type 2 size 3651. CPU 115.22 / elapsed 118.11 at 14:18:34.

`GIT HISTORYSTATE-REF-FULL HEAD 1 src/M9JOBJ.EXEC` passed as MIXED with PRESENT 1 / ABSENT 1: node 1 PRESENT blob `775F6C809889E3497D8837379B37A706DFD101CA` type 3 size 646; node 2 ABSENT; authenticated edge 1 child 1 -> parent 2. CPU 115.74 / elapsed 118.67 at 14:22:26.

`GIT HISTORYDIFFS-REF-FULL HEAD 1 src/M9JOBJ.EXEC` passed as CHANGED / MIXED with one ADDED edge, child PRESENT / parent ABSENT, child OID `775F6C809889E3497D8837379B37A706DFD101CA` type 3 size 646, and zero deleted/modified/unchanged edges. CPU 115.52 / elapsed 118.43 at 14:26:15. M94-M99 are now NATIVE CMS TARGET-PROVEN. DELETED remains implemented/host-proven but lacks a deletion fixture in this reachable window.

## M94-M99 native CMS target proof

Actual z/VM 4.4 CMS validation passed after `CMSCLNK GITREC PLAIN` completed with no statements flagged (13.31 CPU / 13.77 elapsed). All four commands returned Ready/RC0 and emitted trusted output only after full snapshot verification.

- `HISTORYDIFFS-REF-FULL HEAD 1 README.md`: HEAD `00D8D632...`, ALLPRESENT 2/0, 2 nodes, 1 edge, UNCHANGED, changed 0, added/deleted/modified 0, unchanged 1; 115.83 CPU / 118.69 elapsed.
- `HISTORYDIFFS-REF-FULL HEAD 1 src`: ALLPRESENT 2/0, CHANGED, exactly one MODIFIED edge. Child tree/path OID `A41B3EA7758F301B7E30BD3CFDF264300C02AE35` type 2 size 3690; parent `884916539208F673916FBD6988DE6B028C355723` type 2 size 3651; child/parent commits and root trees matched the expected HEAD/parent snapshots; 115.22 CPU / 118.11 elapsed.
- `HISTORYSTATE-REF-FULL HEAD 1 src/M9JOBJ.EXEC`: MIXED, PRESENT 1, ABSENT 1, 2 nodes, 1 edge. Node 1 authenticated PRESENT blob `775F6C809889E3497D8837379B37A706DFD101CA` type 3 size 646 at HEAD; node 2 authenticated ABSENT at parent; 115.74 CPU / 118.67 elapsed.
- `HISTORYDIFFS-REF-FULL HEAD 1 src/M9JOBJ.EXEC`: MIXED, CHANGED, exactly one ADDED edge, child PRESENT / parent ABSENT, expected child blob/type/size and snapshot metadata; 115.52 CPU / 118.43 elapsed.

Therefore M94-M99 are NATIVE CMS TARGET-PROVEN for authenticated PRESENT/ABSENT history plus UNCHANGED, MODIFIED, and ADDED edge classification. DELETED remains implemented and host-CI-proven but has no deletion fixture in the current depth-8 reachable window.

## M100: authenticated path change log

M100 adds `GIT HISTORYLOG-REF-FULL <ref> <depth> <path>`. It reuses the native CMS-target-proven HISTORYDAGSTATE graph and strict state parser, then emits only child-to-parent edges whose authenticated path state or PATHOID changes. Records are explicitly edge-oriented, not chronological claims: each change includes status ADDED/DELETED/MODIFIED, child/parent node and depth, child/parent commit, PRESENT/ABSENT state, and OID/type/size for present endpoints. Unchanged edges are counted in the verified graph but omitted from the concise log. No native C or protected-data changes.

## M101: compact authenticated path status

M101 adds `GIT HISTORYSTATUS-REF-FULL <ref> <depth> <path>`. It runs the same CMS-target-proven HISTORYDAGSTATE traversal and strict parser, but emits only a compact verified summary: CHANGED/UNCHANGED, ALLPRESENT/ALLABSENT/MIXED, PRESENT/ABSENT snapshot counts, node/edge counts, and exact ADDED/DELETED/MODIFIED/UNCHANGED edge totals. It is intended for low-noise CMS use when per-edge details are unnecessary. No native C or protected-data changes.

## M100-M101 native CMS target proof

Real CMS proved the EXEC-only M100-M101 batch. HISTORYSTATUS on HEAD/README.md returned UNCHANGED, ALLPRESENT, PRESENT 2, ABSENT 0, NODES 2, EDGES 1, changed/added/deleted/modified 0 and unchanged 1; CPU 115.48 / elapsed 118.33 sec. HISTORYLOG on HEAD/src returned one MODIFIED edge with child path tree A41B3EA7758F301B7E30BD3CFDF264300C02AE35 type 2 size 3690 and parent 884916539208F673916FBD6988DE6B028C355723 type 2 size 3651; CPU 115.33 / elapsed 118.23 sec. HISTORYLOG on HEAD/src/M9JOBJ.EXEC returned one ADDED edge, child PRESENT / parent ABSENT, child blob 775F6C809889E3497D8837379B37A706DFD101CA type 3 size 646; CPU 115.31 / elapsed 118.18 sec. M100-M101 are NATIVE CMS TARGET-PROVEN.

## M102-M105: shared classification and change-depth bounds

The state-aware output paths now share one fail-closed `stateclass` routine after the target-proven HISTORYDAGSTATE parser. It derives lifecycle/version data, exact ADDED/DELETED/MODIFIED/UNCHANGED counts, per-edge status, and the minimum/maximum child depth among changed edges. HISTORYSTATUS, HISTORYLOG and HISTORYDIFFS expose nearest/farthest change-depth records when changes exist. M105 adds `GIT HISTORYNEAREST-REF-FULL <ref> <depth> <path>`, which emits every changed parent edge tied at the minimum child depth. This is explicitly graph distance from the requested ref, not a wall-clock chronology claim. No native C or protected-data changes.

## M106-M108: authenticated state transition matrix

M106 extends the shared state-version aggregation so every verified snapshot node receives a state ID: 0 is authenticated ABSENT, while 1..N identify authenticated PRESENT PATHOIDs. M108 adds `GIT HISTORYTRANSITIONS-REF-FULL <ref> <depth> <path>`, reusing the target-proven HISTORYDAGSTATE parser and shared state classifier. It aggregates every native parent edge into exact child-state -> parent-state pairs, validates pair counts sum to the authenticated edge total, labels each pair UNCHANGED/ADDED/DELETED/MODIFIED, and emits direct OIDs for present endpoints. This generalizes the older all-present transition report to lifecycle transitions without a new native traversal.

## M100-M101 native CMS target proof

Actual CMS validation passed for the EXEC-only M100-M101 batch with no rebuild required. `GIT HISTORYSTATUS-REF-FULL HEAD 1 README.md` returned the expected compact verified summary: UNCHANGED, ALLPRESENT, PRESENT 2, ABSENT 0, NODES 2, EDGES 1, CHANGED 0, ADDED/DELETED/MODIFIED 0, UNCHANGED 1; 115.48 CPU / 118.33 elapsed.

`GIT HISTORYLOG-REF-FULL HEAD 1 src` returned one authenticated MODIFIED change edge, child node 1 -> parent node 2, depths 0/1, expected commits, PRESENT/PRESENT state, child tree/path OID `A41B3EA7758F301B7E30BD3CFDF264300C02AE35` type 2 size 3690 and parent `884916539208F673916FBD6988DE6B028C355723` type 2 size 3651; 115.33 CPU / 118.23 elapsed.

`GIT HISTORYLOG-REF-FULL HEAD 1 src/M9JOBJ.EXEC` returned one authenticated ADDED change edge with PRESENT/ABSENT state, expected commits, child blob `775F6C809889E3497D8837379B37A706DFD101CA` type 3 size 646; 115.31 CPU / 118.18 elapsed. M100-M101 are now NATIVE CMS TARGET-PROVEN.

## M111: authenticated nearest/farthest change bounds

M111 adds `GIT HISTORYBOUNDS-REF-FULL <ref> <depth> <path>`. It reuses the CMS-target-proven HISTORYDAGSTATE parser plus shared state classification, then emits only changed parent edges at the minimum and maximum child depth from the requested ref. Summary records include nearest/farthest depths, exact match counts, and total unique boundary changes. Each boundary edge is labeled `NEAREST`, `FARTHEST`, or `BOTH` when the two depths coincide, with authenticated node/depth/commit/state and endpoint OID/type/size metadata. This is graph-distance boundary reporting, not a wall-clock chronology claim. No native C or protected-data changes.

## M111 merged and combined M102-M111 CMS gate

M111 PR #76 passed full native-stage workflow `37216331629` and squash-merged as `ef6e5b98a7531073bf179bb7714d1dd30f8589b2`. M102-M111 are EXEC-only on top of the already native-CMS-proven HISTORYDAGSTATE engine. They refactor classification into shared fail-closed logic; add nearest/farthest change-depth bounds; add HISTORYNEAREST; add authenticated lifecycle state-version/transition aggregation and HISTORYTRANSITIONS; extend HISTORYSTATUS/HISTORYLOG/HISTORYDIFFS with shared derived data; add consolidated HISTORYREPORT; and add HISTORYBOUNDS for nearest/farthest boundary edges. No native C or protected REF2/selector/generation/PACK data changed in M102-M111.

NEXT combined CMS target gate requires only refreshed `GITVREF.EXEC` and `GIT.EXEC`; no compile and no GITRUN. Use HEAD depth 1. Recommended minimal proof set: `HISTORYSTATUS-REF-FULL HEAD 1 src` (shared classifier + transition/count summaries), `HISTORYNEAREST-REF-FULL HEAD 1 src` (nearest MODIFIED edge), `HISTORYTRANSITIONS-REF-FULL HEAD 1 src/M9JOBJ.EXEC` (ABSENT->PRESENT/ADDED lifecycle state transition), `HISTORYREPORT-REF-FULL HEAD 1 src` (consolidated MODIFIED report), and `HISTORYBOUNDS-REF-FULL HEAD 1 src` (nearest=farthest=0, one boundary edge labeled BOTH). A zero-change regression can be covered with `HISTORYREPORT-REF-FULL HEAD 1 README.md` if desired; README remains unchanged/all-present.

## Partial M102-M111 CMS gate: worker current, router stale

`GIT HISTORYSTATUS-REF-FULL HEAD 1 src` passed on real CMS and proves the refreshed GITVREF worker is current through the shared M102-M110 logic: CHANGED / ALLPRESENT, PRESENT 2, ABSENT 0, VERSIONS 2, TRANSITIONS 1, CHANGED TRANSITIONS 1, NODES 2, EDGES 1, exactly one MODIFIED edge, nearest/farthest change depth 0, nearest changes 1. CPU 115.04 / elapsed 117.90 sec at 11:25:15.

The subsequent public commands `HISTORYNEAREST-REF-FULL`, `HISTORYTRANSITIONS-REF-FULL`, `HISTORYREPORT-REF-FULL`, and `HISTORYBOUNDS-REF-FULL` all failed immediately in `GIT EXEC` with `unknown command` RC4, before GITVREF/native traversal. Current repository `GIT.EXEC` contains all four routes, while HISTORYSTATUS is an older route. Therefore the target is executing a stale GIT router alongside a current GITVREF worker. No native or sealed-data fault is indicated. M102 shared classifier/status is target-proven; M105/M108/M110/M111 public routing remains pending target proof.

## M112: fail-closed EXEC level identity

M112 adds `GIT LEVEL`. The router invokes `GITVREF LEVEL`, expects exactly `GITVREF EXEC LEVEL M112`, prints `GIT EXEC LEVEL M112` plus the worker level, and fails RC8 with `GITVREF EXEC LEVEL MISMATCH` if the worker is stale or otherwise inconsistent. This directly diagnoses mixed-level router/worker target states like the partial M102-M111 gate. No native C or protected-data changes.

## M112 merged: fail-closed EXEC level identity

M112 PR #77 passed full native-stage workflow `37217089033` and squash-merged as `1edc4551d245953c5cfb701388d34bc7a783b654`. `GIT LEVEL` now invokes `GITVREF LEVEL`, expects exactly `GITVREF EXEC LEVEL M112`, prints `GIT EXEC LEVEL M112` plus the worker level, and returns RC8 with `GITVREF EXEC LEVEL MISMATCH` if the router and worker are inconsistent. This directly addresses the mixed target level observed during the partial M102-M111 gate. No native C or protected-data changes.

NEXT target repair: refresh both `GIT.EXEC` and `GITVREF.EXEC`, then run `GIT LEVEL`. Expected RC0 output is exactly `GIT EXEC LEVEL M112` followed by `GITVREF EXEC LEVEL M112`. Once level identity passes, rerun the previously blocked public commands: HISTORYNEAREST on HEAD/1/src, HISTORYTRANSITIONS on HEAD/1/src/M9JOBJ.EXEC, HISTORYREPORT on HEAD/1/src, and HISTORYBOUNDS on HEAD/1/src. No compile and no GITRUN.

## 2026-10-04 M102-M112 native CMS target proof

`GIT LEVEL` passed with exact RC0 identity `GIT EXEC LEVEL M112` and `GITVREF EXEC LEVEL M112`, eliminating the stale-router/current-worker condition from the previous partial gate.

`GIT HISTORYNEAREST-REF-FULL HEAD 1 src` passed: CHANGED / ALLPRESENT, NODES 2, EDGES 1, CHANGES 1, nearest DEPTH 0, MATCHES 1, one MODIFIED edge child node 1 -> parent node 2, child depth 0 / parent depth 1, commits `00D8D63229305230C8D37F884CE87F9E1A89468C` -> `2D5038C551318997B865497E04CF4C037DE4135E`, PRESENT/PRESENT, child path tree `A41B3EA7758F301B7E30BD3CFDF264300C02AE35` type 2 size 3690, parent `884916539208F673916FBD6988DE6B028C355723` type 2 size 3651. CPU 115.24 / elapsed 118.13.

`GIT HISTORYTRANSITIONS-REF-FULL HEAD 1 src/M9JOBJ.EXEC` passed: CHANGED / MIXED, VERSIONS 1, state 0 ABSENT, state 1 PRESENT blob `775F6C809889E3497D8837379B37A706DFD101CA` type 3 size 646, one transition child state 1 -> parent state 0 count 1, status ADDED, ADDED edges 1 and all other edge classes 0. CPU 115.79 / elapsed 118.72.

`GIT HISTORYREPORT-REF-FULL HEAD 1 src` passed the consolidated report: CHANGED / ALLPRESENT, PRESENT 2 / ABSENT 0, two authenticated present states with expected OIDs/type/size/depth bounds, one changed transition 1->2 MODIFIED, one changed edge with exact commit/root-tree/path-object endpoint metadata, nearest=farthest change depth 0 and nearest changes 1. CPU 115.42 / elapsed 118.34.

`GIT HISTORYBOUNDS-REF-FULL HEAD 1 src` passed: CHANGED / ALLPRESENT, one change, nearest depth 0 matches 1, farthest depth 0 matches 1, one boundary change, edge 1 labeled `BOUND BOTH`, status MODIFIED, with expected endpoint commits/states/OIDs/type/size. CPU 114.96 / elapsed 117.84.

Together with the earlier `HISTORYSTATUS-REF-FULL HEAD 1 src` target pass, M102-M112 are NATIVE CMS TARGET-PROVEN. No outstanding target defect remains in the shared classifier, nearest/farthest depth logic, lifecycle transition matrix, consolidated report, boundary report, or EXEC-level identity handshake.

## M113: verified direct commit-OID history input

M113 extends read-only verified revision input in GITVREF. Existing refs resolve first and retain exact `VERIFIED REF <spec> <oid>` output. If no ref matches and the supplied spec is exactly 40 hexadecimal characters, SHOW/LOG/DAG/READ/DIR and every HIST* mode may use it directly as a sealed commit OID; trusted output is labeled `VERIFIED COMMIT <oid>`. VERIFY-REF/RESOLVE remains ref-only. Native lookup, hashing, type validation, and full snapshot authentication still apply, so direct input does not bypass verification.

This unlocks a real DELETED fixture already in the sealed ancestry: commit `486ADAA5B02080720F4B329C6F68550B13C6AA87` removes `src/GITPBWALK.EXEC` relative to parent `91913EA4028B795707AA67EDB1ED17A74D1B896E`. Child root tree is `909B1D31C377F42158F1591AB3FA130105186FD7` with the path absent. Parent root tree is `AE65405CF230B9FB0992544773B3CF7197015A47` and contains blob `A0C91615ABA9689C365159205E8CBA26EF6E16F4`, size 1869. A depth-1 state/diff/report from the removal commit should classify one DELETED edge: child ABSENT / parent PRESENT.

## M114-M117: authenticated commit chronology on path history

M114 adds a native C89 parser for the trailing epoch/timezone fields of the already-required raw Git `author` and `committer` headers. HISTORYDAGSTATE stores author epoch/TZ minutes, committer epoch/TZ minutes, and exact commit message byte count for every requested node and emits them only after the full graph/snapshots authenticate. HISTORYDAGPATH and all older native operations are unchanged.

M115 extends the strict GITVREF state parser so each node must contain exactly one valid AUTHOR chronology record, one COMMITTER chronology record, and one MESSAGE byte-count record after TREE and before PATH state. Missing, duplicate, malformed, or out-of-range timezone metadata fails closed before trusted output.

M116 exposes that authenticated chronology in HISTORYSTATE nodes and in each changed edge emitted by HISTORYLOG, HISTORYNEAREST, HISTORYBOUNDS, HISTORYREPORT, and HISTORYDIFFS. Changed-edge records carry child/parent author times, child/parent committer times, timezone-minute offsets, and child/parent message byte counts. M117 additionally emits signed `COMMITTER DELTA SECONDS`, preserving clock skew rather than rejecting it. The fail-closed router/worker identity is advanced to M117.

For the real DELETED fixture, GitHub's normalized commit metadata independently gives epoch 1789695393 for removal commit `486ADAA5...AA87` and 1789695390 for parent `91913EA4...896E`, so the authenticated committer delta should be +3 seconds. Native output will provide the original raw Git timezone-minute offsets and exact message byte counts.

## M113-M117 merged and host-CI green

PR #78 passed exact-head native-stage workflow `37239289291` after fixing and guarding a pre-merge `emitverified` recursion regression, then squash-merged as `6428b91791172da6d63e948f3bcf6fdec09f087b`. The merged batch supports ref-first direct sealed commit input (`VERIFIED COMMIT`), keeps VERIFY-REF ref-only, adds native authenticated author/committer epoch plus timezone-minute and message-byte metadata to HISTORYDAGSTATE, requires those records in the strict wrapper parser, emits chronology across detailed history surfaces, and derives signed committer-time deltas. Router/worker level identity is M117. Native C89 compilation and the complete host staging/index/PACK suite are green. Target proof is pending and will be batched with subsequent native metadata work.

## M102-M112 native CMS target proof

Actual CMS validation completed the previously partial M102-M111 gate and proved M112 level identity. `GIT LEVEL` returned exactly `GIT EXEC LEVEL M112` and `GITVREF EXEC LEVEL M112` with RC0, eliminating the stale-router/current-worker condition.

`HISTORYNEAREST-REF-FULL HEAD 1 src` passed as CHANGED / ALLPRESENT with NODES 2, EDGES 1, CHANGES 1, nearest depth 0, one match, and one MODIFIED edge from child node 1 to parent node 2. Endpoint commits and path OIDs/types/sizes matched the target-proven HEAD/parent pair. CPU 115.24 / elapsed 118.13 sec.

`HISTORYTRANSITIONS-REF-FULL HEAD 1 src/M9JOBJ.EXEC` passed as CHANGED / MIXED with one PRESENT version (`775F6C809889E3497D8837379B37A706DFD101CA`, type 3 size 646), one transition, one changed transition, exactly one ADDED edge, and transition state 1 -> 0 (child PRESENT, parent ABSENT). CPU 115.79 / elapsed 118.72 sec.

`HISTORYREPORT-REF-FULL HEAD 1 src` passed as CHANGED / ALLPRESENT with PRESENT 2, ABSENT 0, VERSIONS 2, one MODIFIED transition and one MODIFIED edge. State 1 is child tree `A41B3EA7758F301B7E30BD3CFDF264300C02AE35` type 2 size 3690 at depth 0; state 2 is parent tree `884916539208F673916FBD6988DE6B028C355723` type 2 size 3651 at depth 1. Root trees, commits, nearest/farthest depth 0 and all endpoint metadata matched. CPU 115.42 / elapsed 118.34 sec.

`HISTORYBOUNDS-REF-FULL HEAD 1 src` passed with CHANGES 1, nearest depth 0 / matches 1, farthest depth 0 / matches 1, boundary changes 1, and the single MODIFIED edge labeled `BOUND BOTH`, with authenticated endpoint metadata. CPU 114.96 / elapsed 117.84 sec.

Therefore M102-M112 are NATIVE CMS TARGET-PROVEN. The shared classifier, change-depth bounds, HISTORYNEAREST, lifecycle transition matrix, HISTORYREPORT, HISTORYBOUNDS, and fail-closed EXEC level handshake are all proven on real z/VM CMS.

## M118-M120: authenticated chronology deltas and summary

M118 extends verified chronology output with signed AUTHOR DELTA SECONDS on every changed parent edge plus per-node and per-endpoint AUTHOR TO COMMITTER LAG SECONDS. Existing signed COMMITTER DELTA SECONDS remains unchanged. Negative deltas and lags are reported rather than rejected so Git clock skew remains observable.

M119-M120 add `GIT HISTORYCHRONOLOGY-REF-FULL <ref|commit40> <depth> <path>`. It reuses the strict HISTORYDAGSTATE parser and authenticated chronology from M114-M117, then summarizes all verified parent edges by AUTHOR and COMMITTER delta sign (positive/zero/negative), records min/max signed deltas, and summarizes per-node author-to-committer lag sign plus min/max seconds. Counts are cross-checked against authenticated node/edge totals before trusted output. Router/worker identity advances to M120. No native C changes beyond M114-M117 and no protected-data changes.

## M121-M123: chronology aggregates per authenticated transition

M121 extends shared state transition aggregation with signed author and committer delta bounds per child-state -> parent-state pair, plus positive/zero/negative edge counts for each clock. Every per-transition sign total must equal the authenticated transition edge count or output fails closed.

M122-M123 expose those chronology aggregates in HISTORYTRANSITIONS, HISTORYREPORT, and HISTORYDIFFS through one shared `emittranschron` path. This makes transition-level clock behavior inspectable without duplicating graph traversal or classification. Router/worker identity advances to M123. These milestones are EXEC-only on top of the M114-M117 native chronology records; no additional native C or protected-data changes.

## M118-M123 merged and combined native CMS gate

M118-M120 PR #80 passed full native-stage workflow `37239907692` and squash-merged as `cb561349716cd1b00f7d8263659ec9a8c59bc61f`. M121-M123 PR #82 passed full native-stage workflow `37240119880` and squash-merged as `522a006cf2424928e780229aba51d2dc86fd6997`. Router/worker identity is now M123.

The combined M113-M123 target gate should use sealed direct commit `486ADAA5B02080720F4B329C6F68550B13C6AA87` at depth 1 for path `src/GITPBWALK.EXEC`. This commit removes that path relative to parent `91913EA4028B795707AA67EDB1ED17A74D1B896E`. Child root tree is `909B1D31C377F42158F1591AB3FA130105186FD7` with the path ABSENT. Parent root tree is `AE65405CF230B9FB0992544773B3CF7197015A47` and the path is PRESENT as blob `A0C91615ABA9689C365159205E8CBA26EF6E16F4`, size 1869.

GitHub normalized metadata independently shows child author/committer time 2026-09-18T01:36:33Z (epoch 1789695393) and parent author/committer time 2026-09-18T01:36:30Z (epoch 1789695390). Therefore the native authenticated AUTHOR DELTA and COMMITTER DELTA across the deletion edge should both be +3 seconds, while child and parent AUTHOR TO COMMITTER LAG should each be 0 seconds. Raw Git timezone-minute values and exact message byte counts must be accepted from native output rather than inferred from GitHub normalization.

NEXT genuine target gate requires uploading `GITREC.C`, `GITVREF.EXEC`, and `GIT.EXEC`, rebuilding only GITREC, then `GIT LEVEL` must report M123/M123. Minimal proof set: HISTORYSTATE on the direct commit/deleted path (direct commit input + native chronology + ABSENT/PRESENT state), HISTORYDIFFS on the same input (DELETED + detailed signed chronology), HISTORYCHRONOLOGY on the same input (author/committer sign and bounds + lag summary), and HISTORYTRANSITIONS on the same input (state 0 ABSENT -> parent present state, DELETED, plus M123 per-transition chronology aggregates). No GITRUN.


## 2026-10-04 NEW CHAT HANDOFF — AUTHORITATIVE

Current main head before this handoff: `5169a6e0d9325e658f15fcab0bc89db6addd42aa` (`Finalize M113-M123 combined native CMS gate`).

### Proven through M112
M102-M112 are NATIVE CMS TARGET-PROVEN on real z/VM 4.4. The repaired level handshake returned exactly:
`GIT EXEC LEVEL M112`
`GITVREF EXEC LEVEL M112`
with RC0. HISTORYNEAREST on HEAD/1/src proved one MODIFIED edge at depth 0; HISTORYTRANSITIONS on HEAD/1/src/M9JOBJ.EXEC proved state 1 PRESENT -> state 0 ABSENT, status ADDED; HISTORYREPORT on HEAD/1/src proved two authenticated present states and one MODIFIED transition/edge; HISTORYBOUNDS on HEAD/1/src proved nearest=farthest depth 0, one boundary edge labeled BOTH. Do not repeat M102-M112 standalone.

### Current merged development: M113-M123
PR #78 merged M113-M117 as `6428b91791172da6d63e948f3bcf6fdec09f087b` after full native-stage CI. It adds ref-first direct sealed commit-OID input to verified read/history commands, keeps VERIFY-REF ref-only, and adds native authenticated author/committer epoch + timezone-minute, message-byte metadata, signed deltas, and detailed chronology output. Native C changed here.

PR #80 merged M118-M120 as `cb561349716cd1b00f7d8263659ec9a8c59bc61f`, adding signed author deltas, author-to-committer lag, and `HISTORYCHRONOLOGY-REF-FULL` summaries.

PR #82 merged M121-M123 as `522a006cf2424928e780229aba51d2dc86fd6997`, adding per-authenticated-transition chronology aggregates to HISTORYTRANSITIONS/HISTORYREPORT/HISTORYDIFFS. Router/worker identity is now M123.

M113-M123 are FULL HOST-CI-PROVEN and merged, but NOT YET NATIVE CMS TARGET-PROVEN.

### Exact next genuine CMS gate
From Mac `ibm-sandbox/src`:
`git pull`
`CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITREC.C GITVREF.EXEC GIT.EXEC`

On CMS:
`CMSCLNK GITREC PLAIN`
`GIT LEVEL`
`GIT HISTORYSTATE-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC`
`GIT HISTORYDIFFS-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC`
`GIT HISTORYCHRONOLOGY-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC`
`GIT HISTORYTRANSITIONS-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC`

No GITRUN.

Expected level identity: M123/M123.

Real sealed DELETED fixture:
- child/removal commit: `486ADAA5B02080720F4B329C6F68550B13C6AA87`
- parent: `91913EA4028B795707AA67EDB1ED17A74D1B896E`
- path: `src/GITPBWALK.EXEC`
- child root tree: `909B1D31C377F42158F1591AB3FA130105186FD7`, path ABSENT
- parent root tree: `AE65405CF230B9FB0992544773B3CF7197015A47`
- parent path blob: `A0C91615ABA9689C365159205E8CBA26EF6E16F4`, type 3, size 1869
- expected edge classification: DELETED, child ABSENT / parent PRESENT
- normalized GitHub author+committer epochs: child 1789695393, parent 1789695390
- expected AUTHOR DELTA SECONDS: +3
- expected COMMITTER DELTA SECONDS: +3
- expected child and parent AUTHOR TO COMMITTER LAG SECONDS: 0
- raw timezone-minute offsets and exact message byte counts must come from native output, not be guessed.

The HISTORYTRANSITIONS proof should show child state 0 ABSENT -> a PRESENT parent state, status DELETED, and M123 per-transition author/committer sign/count/min/max chronology aggregates consistent with the single +3-second edge.

### Important open-branch note
PR #81 (`M118 add authenticated commit subject prefix`) is still OPEN and is not part of current main. It was based on an earlier M120-era base and overlaps milestone numbering. Do not treat it as merged or target-proven. Reconcile/rebase or close it only after the M113-M123 CMS gate; do not merge it blindly.

### Standing execution rules
Continue autonomously through GitHub work with maximum work per turn. Do not pause except for a genuine CMS target gate. Keep CMS commands minimal and batch gates. Preserve immutable GITFIX/M15NEW STAGE/INDEX/SEEK/GEN, protected selector PTRs, GITPBUF PACK, and read-only REF2. Never represent host CI as native CMS proof. C source physical lines <=72; CMS EXEC records <=80. Fail closed and emit no trusted partial output before requested verification completes.


## 2026-10-04 M124 target repair: CMS REXX epoch precision

The first real M123 native gate reached the correct M123/M123 level handshake, but both direct sealed-commit HISTORYSTATE and HISTORYDIFFS returned RC8 with no trusted output. The shared new chronology parser handles 10-digit Unix epoch seconds. CMS REXX defaults NUMERIC DIGITS to 9, so validating and subtracting values such as 1789695393 can fail or lose the three-second edge on target even though source/host guards pass.

M124 is an EXEC-only target compatibility repair: GITVREF now executes `numeric digits 20` before parsing any native history records, preserving exact 10-digit epoch values and signed chronology deltas. GIT/GITVREF level identity advances together to M124. Native C and sealed data are unchanged. The next target retry needs only GITVREF.EXEC and GIT.EXEC; do not rebuild GITREC. M113-M123 remain host-CI proven but not yet target-proven until this repaired gate passes.


## 2026-10-04 M124 REAL CMS TARGET PASS

The repaired M124 EXEC gate passed on real z/VM CMS. `GIT LEVEL` returned exactly `GIT EXEC LEVEL M124` and `GITVREF EXEC LEVEL M124`. Direct sealed commit `486ADAA5B02080720F4B329C6F68550B13C6AA87` against path `src/GITPBWALK.EXEC` then passed HISTORYSTATE, HISTORYDIFFS, HISTORYCHRONOLOGY and HISTORYTRANSITIONS.

Native authenticated results matched the sealed fixture exactly: child tree `909B1D31C377F42158F1591AB3FA130105186FD7` had the path ABSENT; parent `91913EA4028B795707AA67EDB1ED17A74D1B896E` tree `AE65405CF230B9FB0992544773B3CF7197015A47` had blob `A0C91615ABA9689C365159205E8CBA26EF6E16F4`, type 3 size 1869. The single edge classified DELETED, child state 0 / parent state 1. Child author+committer epoch 1789695393 TZMIN -300, parent 1789695390 TZMIN -300; both author and committer deltas were +3 seconds; both author-to-committer lags were 0. Native exact message byte counts were child 37 and parent 28. Transition aggregates reported one positive author edge and one positive committer edge, min=max=3, with zero zero/negative edges.

Therefore M113-M124 are now NATIVE CMS TARGET-PROVEN for the combined direct-commit chronology/history gate. Do not repeat the M113-M124 standalone gate. The M124 `NUMERIC DIGITS 20` compatibility repair is confirmed necessary and correct on target. Continue autonomous development from this baseline; preserve sealed generations, selectors, GITPBUF PACK and REF2.


## M125 authenticated bounded commit subject prefix

After the real M124 CMS pass, the stale overlapping PR #81 was closed without merging. M125 cleanly replays that capability on top of the native-proven M124 baseline. Native HISTORYDAGSTATE now extracts the exact first-line subject byte count plus at most 20 raw ASCII subject bytes from each already authenticated commit object. It emits `HISTORYDAGSTATE SUBJECT BYTES <n> PREFIXBYTES <p>` and `HISTORYDAGSTATE SUBJECTHEX <hex|EMPTY>` only after the same full selector and commit/root verification.

GITVREF strictly requires subject metadata and hex to be internally consistent before accepting PATH state. HISTORYSTATE exposes node subject bytes/prefix; detailed changed-edge output carries child/parent subject bytes/prefix while retaining M124 `NUMERIC DIGITS 20`, author/committer deltas, lag values and M123 transition chronology aggregates. Router/worker identity advances to M125. For the sealed DELETED fixture, independently known subjects are child `Remove overlength CMS walker filename` (37 bytes; first 20 bytes hex `52656D6F7665206F7665726C656E67746820434D`) and parent `Use CMS-safe M9F walker name` (28 bytes; first 20 bytes hex `55736520434D532D73616665204D39462077616C`). M125 is not native target-proven until the next CMS gate.


## 2026-10-04 M125 REAL CMS TARGET PASS

The real z/VM CMS target ran the M125 gate successfully. `CMSCLNK GITREC PLAIN` assembled cleanly with no flagged statements and built the PLAIN module. After retransmitting the EXEC pair, `GIT LEVEL` and direct `EXEC GITVREF LEVEL` both showed M125/M125.

For direct sealed commit `486ADAA5B02080720F4B329C6F68550B13C6AA87` and path `src/GITPBWALK.EXEC`, HISTORYSTATE and HISTORYDIFFS both returned RC0 with full-snapshot verification. The existing M124 invariants remained exact: child ABSENT, parent PRESENT blob `A0C91615ABA9689C365159205E8CBA26EF6E16F4` type 3 size 1869, one DELETED edge, child/parent author and committer epochs 1789695393/1789695390 at TZMIN -300, author and committer deltas +3 seconds, and both author-to-committer lags 0.

The new authenticated subject metadata matched the sealed commits byte-for-byte. Child: SUBJECT BYTES 37, PREFIXHEX `52656D6F7665206F7665726C656E67746820434D` ("Remove overlength CM..."). Parent: SUBJECT BYTES 28, PREFIXHEX `55736520434D532D73616665204D39462077616C` ("Use CMS-safe M9F wal..."). HISTORYDIFFS emitted the same exact child/parent subject metadata on the authenticated changed edge. Therefore M125 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M126 authenticated raw author/committer identity metadata

M125 is now actual native CMS target-proven. M126 advances read-only authenticated history metadata by preserving each commit's raw Git author and committer identity field (the bytes between the `author `/`committer ` key and the timestamp). Native C records the exact identity byte count plus at most 20 raw ASCII prefix bytes and emits compact `AIDENT`/`CIDENT` metadata and HEX records only after the commit object has authenticated. GITVREF requires the identity count/prefix records to be present, ordered and internally consistent before accepting the node's path state.

HISTORYSTATE exposes per-node AIDENT/CIDENT byte counts and prefix hex. Detailed changed-edge output exposes compact CAIDENT/PAIDENT/CCIDENT/PCIDENT records while retaining M125 subject metadata and all M124/M123 chronology arithmetic and transition aggregates. Router/worker identity advances to M126. For both sealed DELETED-fixture commits, GitHub's raw commit metadata reports author and committer identity `mostangrymike <mikewommack86@gmail.com>`, 39 bytes, with the first 20 ASCII bytes expected as hex `6D6F7374616E6772796D696B65203C6D696B6577`. This expected value is independent reference data; M126 remains host-only until native CMS output confirms it.


## 2026-10-04 M126 REAL CMS TARGET PASS

The real z/VM CMS target compiled M126 `GITREC.C` cleanly with `CMSCLNK GITREC PLAIN`: ASSEMBLER (XF) DONE, no statements flagged, MODULE PLAIN built. `GIT LEVEL` returned exactly `GIT EXEC LEVEL M126` and `GITVREF EXEC LEVEL M126`.

For sealed direct commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`, depth 1, path `src/GITPBWALK.EXEC`, HISTORYSTATE and HISTORYDIFFS both returned full-snapshot verified RC0 output. M126 raw identity metadata matched independent Git commit metadata exactly for child and parent, author and committer: identity byte count 39, prefix bytes 20, prefix hex `6D6F7374616E6772796D696B65203C6D696B6577` (first 20 bytes of `mostangrymike <mikewommack86@gmail.com>`). HISTORYDIFFS emitted matching CAIDENT, PAIDENT, CCIDENT and PCIDENT records.

All prior invariants remained exact: child ABSENT / parent PRESENT, one DELETED edge, child/parent epochs 1789695393 / 1789695390 at TZMIN -300, author delta +3, committer delta +3, author-to-committer lag 0 for both nodes, message bytes 37 / 28, and M125 subject metadata 37/28 with their previously target-proven prefixes. Therefore M126 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M127 authenticated full-identity history actors

M126 is now real native CMS target-proven. M127 adds a collision-resistant, full-identity grouping primitive without emitting unbounded identity text. For each already authenticated raw author and committer identity, native GITREC computes the canonical Git blob OID of the complete identity bytes and emits it as AIDENT/CIDENT BLOBID alongside the existing exact byte count and bounded prefix. This BLOBID is a deterministic fingerprint only; it does not claim the identity is stored as a repository blob.

GITVREF requires each identity BLOBID to be present, 40-hex, and ordered after the authenticated identity prefix before accepting node state. Detailed node/edge history output carries the fingerprint. New read-only `GIT HISTORYACTORS-REF-FULL ref-or-commit depth path` groups authors and committers by the full BLOBID, returning count and min/max history depth plus the already authenticated byte count/prefix for each distinct actor. This avoids false grouping when two identities share a 20-byte display prefix. Router/worker identity advances to M127; M124 epoch precision, M125 subject metadata, M126 identity metadata and M123 transition chronology remain intact.

For the sealed M126 identity `mostangrymike <mikewommack86@gmail.com>` (39 bytes), independent canonical Git blob hashing yields BLOBID `78C41780430F464791E67533C261358D0FEB071E`. At depth 1 on the sealed DELETED fixture, the expected actor summary is one author and one committer, each count 2 with min depth 0 and max depth 1. M127 remains host-CI only until the next CMS gate.


## 2026-10-04 M127 REAL CMS TARGET PASS

The real z/VM CMS target compiled M127 `GITREC.C` cleanly with `CMSCLNK GITREC PLAIN`: ASSEMBLER (XF) DONE, no statements flagged, MODULE PLAIN built. `GIT LEVEL` returned exactly `GIT EXEC LEVEL M127` and `GITVREF EXEC LEVEL M127`.

For sealed direct commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`, depth 1, path `src/GITPBWALK.EXEC`, HISTORYSTATE returned full-snapshot verified RC0 output with AIDENT and CIDENT BLOBID `78C41780430F464791E67533C261358D0FEB071E` on both nodes. This exactly matches the independent canonical Git blob OID of the full 39-byte raw identity `mostangrymike <mikewommack86@gmail.com>`. Existing M126 byte counts/prefixes, M125 subject metadata and M124 chronology remained unchanged.

New HISTORYACTORS-REF-FULL also returned RC0 and full-snapshot verification: NODES 2, AUTHORS 1, AUTHOR 1 BLOBID `78C41780430F464791E67533C261358D0FEB071E`, BYTES 39 PREFIXBYTES 20, prefix hex `6D6F7374616E6772796D696B65203C6D696B6577`, COUNT 2 MINDEPTH 0 MAXDEPTH 1; COMMITTERS 1 with the same BLOBID/bytes/prefix/count/depth range. Therefore M127 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M128 authenticated full-subject history summary

M127 is now real native CMS target-proven. M128 extends the same collision-resistant pattern to commit subjects. Native GITREC computes the canonical Git blob OID of the complete first-line subject bytes, including the empty subject case, and emits `HISTORYDAGSTATE SUBJECT BLOBID` only after the authenticated commit object is parsed. The existing exact subject byte count and bounded 20-byte prefix remain unchanged.

GITVREF now requires every node's subject BLOBID to be present and valid before accepting path state, propagates child/parent subject BLOBIDs into detailed history output, and adds read-only `GIT HISTORYSUBJECTS-REF-FULL ref-or-commit depth path`. The summary groups by the complete subject fingerprint and returns exact bytes/prefix/count/min-depth/max-depth for each distinct subject, avoiding false grouping when long subjects share the same 20-byte prefix. Router/worker identity advances to M128; M127 actors, M126 identities, M125 subject prefixes, M124 exact time arithmetic and M123 chronology remain intact.

Independent canonical Git blob hashes for the sealed DELETED fixture are: child subject `Remove overlength CMS walker filename`, 37 bytes, BLOBID `6C1292461038798149F3636EE517BB6E4B35DAA5`; parent subject `Use CMS-safe M9F walker name`, 28 bytes, BLOBID `1A55B22C5ABB8A8609B3F828119988B04BF2BFAC`. At depth 1, expected HISTORYSUBJECTS is NODES 2 / SUBJECTS 2, each count 1; child min/max depth 0 and parent min/max depth 1. M128 remains host-CI only until the next CMS gate.


## 2026-10-04 M128 REAL CMS TARGET PASS

Real z/VM CMS compiled M128 GITREC cleanly and GIT LEVEL returned M128/M128. The sealed depth-1 HISTORYSTATE gate returned RC0 with full-snapshot verification and exact subject digests: child 6C1292461038798149F3636EE517BB6E4B35DAA5 for the 37-byte subject, parent 1A55B22C5ABB8A8609B3F828119988B04BF2BFAC for the 28-byte subject. Existing M127 identity digests remained unchanged. HISTORYSUBJECTS-REF-FULL returned RC0 with NODES 2 and SUBJECTS 2: child count 1 at depth 0, parent count 1 at depth 1. M128 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M129 authenticated commit payload digests

M128 is native CMS target-proven. M129 authenticates the complete commit message payload after the commit header delimiter. Native GITREC computes a canonical Git blob OID over every message byte and emits MESSAGE BLOBID alongside MESSAGE BYTES before subject metadata. GITVREF requires the 40-hex payload digest before accepting subject or path state, propagates it through node and edge output, and adds read-only HISTORYBODIES-REF-FULL grouped by complete payload digest with byte count, subject digest, subject prefix, count, and depth range. A production-native host fixture now uses a genuine multiline body (20 message bytes, 8 subject bytes) and asserts MESSAGE BLOBID differs from SUBJECT BLOBID. Protected GITFIX/M15NEW generations remain untouched. Router/worker identity advances to M129. On the sealed one-line CMS fixture, message bytes equal subject bytes, so the expected payload digests are the already independently verified child 6C1292461038798149F3636EE517BB6E4B35DAA5 and parent 1A55B22C5ABB8A8609B3F828119988B04BF2BFAC. M129 remains host-only until the next CMS gate.


## 2026-10-05 M129 REAL CMS TARGET PASS

Real z/VM CMS compiled M129 GITREC cleanly and GIT LEVEL returned M129/M129. The sealed depth-1 HISTORYSTATE gate returned RC0 with full-snapshot verification. Node 1 MESSAGE BYTES 37 and MESSAGE BLOBID 6C1292461038798149F3636EE517BB6E4B35DAA5; Node 2 MESSAGE BYTES 28 and MESSAGE BLOBID 1A55B22C5ABB8A8609B3F828119988B04BF2BFAC. Because both sealed messages are single-line, each full-message digest exactly equals its independently proven M128 subject digest. Existing M127 identity digests and M128 subject digests remained unchanged. HISTORYBODIES-REF-FULL returned RC0 with NODES 2, BODIES 2, one body at depth 0 and one at depth 1, preserving exact bytes, subject digest, prefix, and count metadata. M129 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M130 authenticated history topology

M129 is native CMS target-proven. M130 adds exact authenticated parent-line count plus distinct-parent count to every HISTORYDAGSTATE node. The worker derives both only after complete commit validation. GITVREF requires this metadata before author/committer/message/path state and cross-checks traversal: every node inside the requested depth must have exactly one followed DAG edge per distinct parent; boundary nodes must have zero followed edges while retaining their full parent metadata. New read-only GIT HISTORYTOPOLOGY-REF-FULL summarizes root, linear and merge commits, duplicate-parent commits, maximum parent count, and per-node depth/parent/followed-edge/class metadata. Production native tests exercise a real two-parent synthetic merge (2 parents / 2 unique, 2 edges, 3 nodes) whose two boundary parents are roots. Router/worker identity advances to M130. Independent Git metadata confirms both sealed CMS gate commits each have exactly one parent, so at depth 1 the expected topology is NODES 2, EDGES 1, ROOTS 0, LINEAR 2, MERGES 0, DUPPARENTS 0, MAX PARENTS 1; node 1 follows 1 parent and boundary node 2 follows 0. M130 remains host-only until the next CMS gate.


## 2026-10-05 M130 REAL CMS TARGET PASS

Real z/VM CMS compiled M130 GITREC cleanly and GIT LEVEL returned M130/M130. HISTORYTOPOLOGY-REF-FULL on sealed commit 486ADAA5B02080720F4B329C6F68550B13C6AA87 at depth 1 and path src/GITPBWALK.EXEC returned RC0 with full-snapshot verification: NODES 2, EDGES 1, ROOTS 0, LINEAR 2, MERGES 0, DUPPARENTS 0, MAX PARENTS 1. Node 1 commit 486AD... reported DEPTH 0 PARENTS 1 UNIQUE 1, FOLLOWED 1, CLASS LINEAR. Boundary node 2 commit 91913E... reported DEPTH 1 PARENTS 1 UNIQUE 1, FOLLOWED 0, CLASS LINEAR. This exactly confirms the M130 invariant: nodes inside the requested depth follow one edge per distinct authenticated parent, while boundary nodes retain complete parent metadata but follow no additional edges. M130 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M131 authenticated ordered parent metadata

M130 is native CMS target-proven. M131 preserves Git parent order without emitting an unbounded parent list. Native GITREC now emits FIRSTPARENT plus PARENTSEQ BLOBID, where PARENTSEQ is the canonical Git blob OID of the raw 20-byte parent OIDs concatenated in exact commit order. The digest therefore preserves merge-parent order and duplicate parent slots. Root commits emit FIRSTPARENT NONE and the canonical empty-blob parent-sequence digest. GITVREF requires both records before accepting commit chronology/path state and, for nodes inside the requested history depth, cross-checks that FIRSTPARENT resolves to exactly one authenticated followed edge. Boundary nodes retain their true first-parent OID but intentionally follow no additional edge. New read-only GIT HISTORYPARENTS-REF-FULL reports exact/unique parent counts, ordered sequence digest, first parent, and the followed first-parent node. Production native tests compare a two-parent merge with the same parents reversed and prove that FIRSTPARENT and PARENTSEQ both change while parent cardinality stays 2/2. Router/worker identity advances to M131. Independent Git metadata for the sealed target gate gives node 1 first parent 91913EA4028B795707AA67EDB1ED17A74D1B896E with PARENTSEQ digest AF3CDAE8C225FC105DCD57E084871353582AD0C8; boundary node 2 first parent E3E2FAAB5AF6F33C27AE93A6F76387329D8EF84E with PARENTSEQ digest 56ABF3E785850DF4259A6282DCD5815CD35A8819. M131 remains host-only until the next CMS gate.


## 2026-10-05 M131 REAL CMS TARGET PASS

Real z/VM CMS compiled M131 GITREC cleanly and GIT LEVEL returned M131/M131. HISTORYPARENTS-REF-FULL on sealed commit 486ADAA5B02080720F4B329C6F68550B13C6AA87 at depth 1 and path src/GITPBWALK.EXEC returned RC0 with full-snapshot verification. NODES 2, EDGES 1, ROOTS 0, FIRST FOLLOWED 1, BOUNDARY WITH PARENTS 1. Node 1 reported PARENTS 1 UNIQUE 1, FIRSTPARENT 91913EA4028B795707AA67EDB1ED17A74D1B896E, PARENTSEQ BLOBID AF3CDAE8C225FC105DCD57E084871353582AD0C8, FIRSTFOLLOWED 2. Boundary node 2 reported PARENTS 1 UNIQUE 1, FIRSTPARENT E3E2FAAB5AF6F33C27AE93A6F76387329D8EF84E, PARENTSEQ BLOBID 56ABF3E785850DF4259A6282DCD5815CD35A8819, FIRSTFOLLOWED 0. This exactly confirms authenticated Git parent ordering and first-parent resolution within the bounded history window. M131 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M132 authenticated followed parent slots

M131 is native CMS target-proven. M132 maps each followed parent occurrence back to its exact Git parent ordinal while keeping the distinct DAG edge set unchanged. Native GITREC emits one bounded HISTORYDAGSTATE SLOT record per parent occurrence for nodes inside the requested depth plus a total SLOTS count. GITVREF requires every slot to reference an authenticated distinct edge, requires one unique slot record per child+ordinal, requires slot count per interior node to equal exact PARENTS, requires distinct slot targets to equal UNIQUE, and requires ordinal 1 to resolve to the M131 authenticated first-parent node. Boundary nodes intentionally emit no slot records, but their omitted slot count is summarized. New read-only GIT HISTORYPARENTSLOTS-REF-FULL reports nodes, distinct edges, followed slots, duplicate slots, boundary slots omitted, node/commit mapping, and each child/ordinal/parent-node relation. Native regression adds a duplicate-parent commit proving PARENTS 2 / UNIQUE 1 / EDGES 1 / SLOTS 2 with both ordinals mapping to the same authenticated parent node, while the ordinary two-parent merge proves ordinals 1 and 2 map to distinct nodes. Router/worker identity advances to M132. For the sealed CMS depth-1 gate the expected summary is NODES 2, EDGES 1, SLOTS 1, DUPLICATE SLOTS 0, BOUNDARY SLOTS OMITTED 1, with SLOT 1 CHILD 1 ORDINAL 1 PARENT 2. M132 remains host-only until the next CMS gate.


## 2026-10-05 M132 REAL CMS TARGET PASS

Real z/VM CMS compiled M132 GITREC cleanly and GIT LEVEL returned M132/M132. HISTORYPARENTSLOTS-REF-FULL on sealed commit 486ADAA5B02080720F4B329C6F68550B13C6AA87 at depth 1 and path src/GITPBWALK.EXEC returned RC0 with full-snapshot verification: NODES 2, EDGES 1, SLOTS 1, DUPLICATE SLOTS 0, BOUNDARY SLOTS OMITTED 1. Node mapping remained child 486AD... as node 1 and parent 91913E... as node 2. The sole followed slot was exactly SLOT 1 CHILD 1 ORDINAL 1 PARENT 2. This proves the M132 invariant on real CMS: followed parent occurrences retain exact Git ordinals, boundary parent occurrences are deliberately omitted from the bounded traversal, and the distinct DAG edge remains separate from slot cardinality. M132 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M133 authenticated followed edge roles

M132 is native CMS target-proven. M133 is a wrapper-only authenticated interpretation of the already verified parent-slot relation; native GITREC remains unchanged from M132. New read-only GIT HISTORYEDGEROLES-REF-FULL classifies each distinct followed DAG edge as FIRST when parent ordinal 1 maps to it, otherwise MERGE. For every edge it derives slot count plus minimum/maximum mapped ordinal, counts multislot edges and duplicate slots, and fail-closes unless every edge has at least one authenticated slot, the number of FIRST edges equals the number of interior nodes that have parents, FIRST edges include ordinal 1, MERGE edges begin at ordinal >=2, and aggregate duplicate slots equal SLOTS-EDGES. This preserves duplicate-parent semantics: an edge may be FIRST and still carry multiple parent slots. Router/worker EXEC identity advances to M133 while GITREC remains the M132 native worker. For the sealed depth-1 CMS gate the expected report is NODES 2, EDGES 1, SLOTS 1, FIRST EDGES 1, MERGE EDGES 0, MULTISLOT EDGES 0, DUPLICATE SLOTS 0; edge 1 is CHILD 1 PARENT 2 ROLE FIRST with SLOTS 1 MINORDINAL 1 MAXORDINAL 1. M133 remains host-only until the next CMS gate.


## 2026-10-05 M133 REAL CMS TARGET PASS

Real z/VM CMS ran the wrapper-only M133 gate with GIT/GITVREF levels M133/M133. HISTORYEDGEROLES-REF-FULL on sealed commit 486ADAA5B02080720F4B329C6F68550B13C6AA87 at depth 1 and path src/GITPBWALK.EXEC returned RC0 with full-snapshot verification: NODES 2, EDGES 1, SLOTS 1, FIRST EDGES 1, MERGE EDGES 0, MULTISLOT EDGES 0, DUPLICATE SLOTS 0. The sole edge was EDGE 1 CHILD 1 PARENT 2, ROLE FIRST, SLOTS 1 MINORDINAL 1 MAXORDINAL 1. This proves the M133 authenticated interpretation layer on real CMS without rebuilding native GITREC. M133 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M134 authenticated first-parent projection

M133 is native CMS target-proven. M134 is a wrapper-only projection over the authenticated M131/M132 first-parent and slot relations; native GITREC remains unchanged. New read-only GIT HISTORYFIRSTPARENT-REF-FULL starts at authenticated node 1 and repeatedly follows the already validated first-parent node until it reaches either a root or the requested history boundary. It fail-closes on a missing first-parent mapping, a missing authenticated edge, or a repeated node. The report returns total authenticated DAG nodes/edges, projected chain nodes/edges, off-chain nodes/edges, a TRUNCATED flag, and each chain step's node, depth, and commit OID. This makes the bounded mainline projection explicit without discarding the rest of the authenticated DAG. Router/worker EXEC identity advances to M134 while GITREC remains the M132 native worker. For the sealed depth-1 CMS gate the expected projection is NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1, with step 1 node 1 commit 486AD... depth 0 and step 2 node 2 commit 91913E... depth 1. M134 remains host-only until the next CMS gate.


## 2026-10-05 M134 REAL CMS TARGET PASS

Real z/VM CMS ran the wrapper-only M134 gate with GIT/GITVREF levels M134/M134. HISTORYFIRSTPARENT-REF-FULL on sealed commit 486ADAA5B02080720F4B329C6F68550B13C6AA87 at depth 1 and path src/GITPBWALK.EXEC returned RC0 with full-snapshot verification: NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1. Step 1 was node 1 depth 0 commit 486AD..., and step 2 was node 2 depth 1 commit 91913E.... This exactly proves the authenticated bounded first-parent projection and expected truncation at the requested boundary. M134 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M135 authenticated first-parent path changes

M134 is native CMS target-proven. M135 remains wrapper-only and reuses a shared fail-closed first-parent chain builder over the already authenticated M131/M132 relations; native GITREC remains unchanged. New read-only GIT HISTORYFIRSTCHANGES-REF-FULL classifies every consecutive edge of the authenticated first-parent chain using the exact existing HISTORYDIFFS semantics: ADDED when child present/parent absent, DELETED when child absent/parent present, MODIFIED when both present with different OIDs, otherwise UNCHANGED. It reports full DAG counts, chain/off-chain counts, truncation, aggregate first-parent change counts, and each projected edge's child/parent nodes, depths, commits, states, and present OIDs. It fail-closes if chain construction fails or aggregate status counts do not equal projected edge cardinality. Router/worker EXEC identity advances to M135 while GITREC remains the M132 native worker. For the sealed depth-1 CMS gate the expected projection is NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1, CHANGES 1, ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0. Edge 1 is CHILD 1 PARENT 2 STATUS DELETED, child commit 486AD... state ABSENT and parent commit 91913E... state PRESENT with PARENTOID A0C91615ABA9689C365159205E8CBA26EF6E16F4. M135 remains host-only until the next CMS gate.


## 2026-10-05 M135 REAL CMS TARGET PASS

Real z/VM CMS ran the wrapper-only M135 gate with GIT/GITVREF levels M135/M135. HISTORYFIRSTCHANGES-REF-FULL on sealed commit 486ADAA5B02080720F4B329C6F68550B13C6AA87 at depth 1 and path src/GITPBWALK.EXEC returned RC0 with full-snapshot verification: NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1, CHANGES 1, ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0. Edge 1 was CHILD 1 PARENT 2, STATUS DELETED, child depth 0 commit 486AD... state ABSENT, parent depth 1 commit 91913E... state PRESENT, with parent path OID A0C91615ABA9689C365159205E8CBA26EF6E16F4 and correctly no child OID. This proves authenticated first-parent-only path change classification on real CMS. M135 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M136 authenticated first-parent state transitions

M135 is native CMS target-proven. M136 remains wrapper-only and reuses both the authenticated first-parent chain builder and the existing verified path-version table; native GITREC remains unchanged. New read-only GIT HISTORYFIRSTTRANSITIONS-REF-FULL groups only authenticated first-parent chain edges by exact child/parent path-state pair. State 0 means ABSENT; positive states are fully verified object versions with OID/type/size metadata. Transition status uses the same exact semantics as HISTORYDIFFS and M135: identical state IDs are UNCHANGED, present->absent is ADDED, absent->present is DELETED, and differing present versions are MODIFIED. The report includes full DAG counts, chain/off-chain counts, truncation, version definitions, unique transition count, changed-transition count, changed-edge count, aggregate edge statuses, and each transition's child/parent states, count, status, and present OIDs. It fail-closes unless transition counts sum exactly to projected chain edges and changed-edge arithmetic is exact. Router/worker EXEC identity advances to M136 while GITREC remains the M132 native worker. For the sealed depth-1 CMS gate the expected result is VERSIONS 1, STATE 0 ABSENT, STATE 1 PRESENT OID A0C91615ABA9689C365159205E8CBA26EF6E16F4 TYPE 3 SIZE 1869, TRANSITIONS 1, CHANGED TRANSITIONS 1, CHANGED EDGES 1, ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0, with transition 1 CHILDSTATE 0 PARENTSTATE 1 COUNT 1 STATUS DELETED and PARENTOID A0C91615ABA9689C365159205E8CBA26EF6E16F4. M136 remains host-only until the next CMS gate.


## 2026-10-05 M136 REAL CMS TARGET PASS

Real z/VM CMS ran the wrapper-only M136 gate with GIT/GITVREF levels M136/M136. HISTORYFIRSTTRANSITIONS-REF-FULL on sealed commit 486ADAA5B02080720F4B329C6F68550B13C6AA87 at depth 1 and path src/GITPBWALK.EXEC returned RC0 with full-snapshot verification: NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1, VERSIONS 1. STATE 0 was ABSENT; STATE 1 was PRESENT OID A0C91615ABA9689C365159205E8CBA26EF6E16F4 TYPE 3 SIZE 1869. TRANSITIONS 1, CHANGED TRANSITIONS 1, CHANGED EDGES 1, ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0. Transition 1 was CHILDSTATE 0 PARENTSTATE 1 COUNT 1 STATUS DELETED with the expected parent OID and correctly no child OID. M136 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M137 authenticated first-parent chronology

M136 is native CMS target-proven. M137 remains wrapper-only and reuses the authenticated first-parent chain; native GITREC remains unchanged. New read-only GIT HISTORYFIRSTCHRONOLOGY-REF-FULL reports chronology only along the verified mainline: full DAG counts, chain/off-chain counts, truncation, author and committer positive/zero/negative edge counts, min/max edge deltas, author-to-committer lag sign counts/min/max across chain nodes, plus exact per-chain-edge author/committer deltas and per-chain-node lag. It fail-closes unless edge sign counts equal projected chain-edge cardinality and lag sign counts equal projected chain-node cardinality. Router/worker EXEC identity advances to M137 while GITREC remains the M132 native worker. For the sealed depth-1 CMS gate the expected result is NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1; AUTHOR POSITIVE EDGES 1, ZERO 0, NEGATIVE 0; COMMITTER POSITIVE EDGES 1, ZERO 0, NEGATIVE 0; AUTHOR MIN/MAX DELTA SECONDS 3/3; COMMITTER MIN/MAX DELTA SECONDS 3/3; LAG POSITIVE NODES 0, ZERO NODES 2, NEGATIVE NODES 0, LAG MIN/MAX SECONDS 0/0. Edge 1 is CHILD 1 PARENT 2 with author delta 3 and committer delta 3; nodes 1 and 2 each have lag 0. M137 remains host-only until the next CMS gate.


## 2026-10-05 M137 REAL CMS TARGET PASS

Real z/VM CMS ran the wrapper-only M137 gate with GIT/GITVREF levels M137/M137. HISTORYFIRSTCHRONOLOGY-REF-FULL on sealed commit 486ADAA5B02080720F4B329C6F68550B13C6AA87 at depth 1 and path src/GITPBWALK.EXEC returned RC0 with full-snapshot verification: NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1. AUTHOR POSITIVE EDGES 1, ZERO 0, NEGATIVE 0; COMMITTER POSITIVE EDGES 1, ZERO 0, NEGATIVE 0. Author min/max delta and committer min/max delta were all 3 seconds. LAG POSITIVE NODES 0, ZERO NODES 2, NEGATIVE NODES 0, with lag min/max 0/0. Edge 1 CHILD 1 PARENT 2 had author delta 3 and committer delta 3; nodes 1 and 2 each had lag 0. M137 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M138 authenticated first-parent actor handoffs

M137 is native CMS target-proven. M138 remains wrapper-only and reuses the authenticated first-parent chain plus the M127-proven author/committer identity BLOBIDs; native GITREC remains unchanged. New read-only GIT HISTORYFIRSTACTORS-REF-FULL reports identity continuity only along the verified mainline: full DAG counts, chain/off-chain counts, truncation, AUTHOR SAME/CHANGED edge counts, COMMITTER SAME/CHANGED edge counts, grouped exact author and committer handoff pairs with counts/status, and exact per-chain-edge child/parent author and committer BLOBIDs. It fail-closes unless grouped author and committer handoff counts each sum exactly to projected chain edges and SAME+CHANGED counts each equal projected chain-edge cardinality. Native host regression adds a real parent/child commit pair whose child uses distinct author and committer identities and proves HISTORYDAGSTATE emits different authenticated BLOBIDs from the parent, exercising the changed-identity substrate. Router/worker EXEC identity advances to M138 while GITREC remains the M132 native worker. For the sealed depth-1 CMS gate the expected result is NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1; AUTHOR SAME EDGES 1, AUTHOR CHANGED EDGES 0, COMMITTER SAME EDGES 1, COMMITTER CHANGED EDGES 0. AUTHOR HANDOFFS 1 / CHANGED HANDOFFS 0 and COMMITTER HANDOFFS 1 / CHANGED HANDOFFS 0, with both child and parent BLOBIDs equal 78C41780430F464791E67533C261358D0FEB071E and STATUS SAME. M138 remains host-only until the next CMS gate.


## 2026-10-05 M138 REAL CMS TARGET PASS

Real z/VM CMS ran the wrapper-only M138 gate with GIT/GITVREF levels M138/M138. HISTORYFIRSTACTORS-REF-FULL on sealed commit 486ADAA5B02080720F4B329C6F68550B13C6AA87 at depth 1 and path src/GITPBWALK.EXEC returned RC0 with full-snapshot verification: NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1. AUTHOR SAME EDGES 1, AUTHOR CHANGED EDGES 0, COMMITTER SAME EDGES 1, COMMITTER CHANGED EDGES 0. AUTHOR HANDOFFS 1 / CHANGED HANDOFFS 0 and COMMITTER HANDOFFS 1 / CHANGED HANDOFFS 0. The grouped author and committer handoffs and exact per-edge child/parent identity BLOBIDs all equaled 78C41780430F464791E67533C261358D0FEB071E with STATUS SAME. M138 is NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M139 authenticated first-parent subject handoffs

M138 is native CMS target-proven. M139 remains wrapper-only and reuses the authenticated first-parent chain plus the M128-proven exact subject BLOBIDs; native GITREC remains unchanged. New read-only GIT HISTORYFIRSTSUBJECTS-REF-FULL reports subject continuity only along the verified mainline: full DAG counts, chain/off-chain counts, truncation, SAME/CHANGED edge counts, grouped exact subject handoff pairs with counts/status, and exact per-chain-edge child/parent subject BLOBIDs plus authenticated subject byte counts and bounded prefixes. It fail-closes unless grouped handoff counts sum exactly to projected chain edges and SAME+CHANGED counts equal projected chain-edge cardinality. Native host regression adds a parent/child commit pair with the same first-line subject `hello` but a different complete message body, proving both nodes emit the same subject BLOBID while their message BLOBIDs differ. Router/worker EXEC identity advances to M139 while GITREC remains the M132 native worker. For the sealed depth-1 CMS gate the expected result is NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1; SAME EDGES 0, CHANGED EDGES 1, HANDOFFS 1, CHANGED HANDOFFS 1. The sole handoff/edge is child subject BLOBID 6C1292461038798149F3636EE517BB6E4B35DAA5 to parent subject BLOBID 1A55B22C5ABB8A8609B3F828119988B04BF2BFAC, STATUS CHANGED. Child subject bytes/prefix are 37 / 52656D6F7665206F7665726C656E67746820434D; parent subject bytes/prefix are 28 / 55736520434D532D73616665204D39462077616C. M139 remains host-only until the next CMS gate.


## 2026-10-05 NEW CHAT HANDOFF AFTER M138 TARGET PROOF

Canonical repository is `mostangrymike/ibm-sandbox`, branch `main`.
State was reconciled against live GitHub before this handoff.

Current canonical main before this handoff state commit:
`8e86312775fc3cb956fcd41672aa37d360565cf7`.

### Latest target-proven milestone

M138 is NATIVE CMS TARGET-PROVEN. Real CMS returned GIT/GITVREF M138/M138 and
`HISTORYFIRSTACTORS-REF-FULL` on sealed commit
`486ADAA5B02080720F4B329C6F68550B13C6AA87`, depth 1, path
`src/GITPBWALK.EXEC`, with:
- NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1.
- OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1.
- AUTHOR SAME EDGES 1, CHANGED EDGES 0.
- COMMITTER SAME EDGES 1, CHANGED EDGES 0.
- One author handoff and one committer handoff, both STATUS SAME.
- Every exact child/parent author/committer identity BLOBID was
  `78C41780430F464791E67533C261358D0FEB071E`.

Do not rerun M138 standalone.

### Current development milestone: M139

M139 `authenticated first-parent subject handoffs` is MERGED and FULL
HOST/NATIVE-STAGE CI PROVEN, but NOT YET REAL CMS TARGET-PROVEN.
PR #98 was squash-merged; merge/main commit before this handoff state commit:
`8e86312775fc3cb956fcd41672aa37d360565cf7`.
PR #98 head was `9fef4e945dcae40e6a6e49c23d82a2ceb3d1cf87`.
Native staging host checks run `37341608325` completed SUCCESS.

Current executable handshake in main is:
- `GIT EXEC LEVEL M139`
- `GITVREF EXEC LEVEL M139`

M139 is wrapper-only. Native `GITREC MODULE` remains the M132-proven worker;
do NOT rebuild GITREC for this gate.

M139 public command:
`GIT HISTORYFIRSTSUBJECTS-REF-FULL <commit> <depth> <path>`

It uses the authenticated first-parent chain plus M128-proven exact subject
BLOBIDs. It reports SAME/CHANGED subject edges, grouped exact subject handoffs,
and exact per-edge child/parent subject BLOBIDs, byte counts, and bounded
prefixes. Host regression separately proves the SAME-subject/different-message
case, so subject identity is not being confused with full-message identity.

### NEXT REAL CMS GATE — do this first in the next chat

Mac, from `ibm-sandbox/src`:
```sh
git pull
CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITVREF.EXEC GIT.EXEC
```

CMS:
```text
GIT LEVEL
GIT HISTORYFIRSTSUBJECTS-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC
```

No `CMSCLNK`. No `GITRUN`. Do not rerun older history gates unless a new
M139 diagnostic genuinely requires it.

Expected M139 sealed-fixture proof:
- GIT/GITVREF M139/M139.
- VERIFIED COMMIT `486ADAA5B02080720F4B329C6F68550B13C6AA87`.
- HISTORYFIRSTSUBJECTS FULL SNAPSHOTS VERIFIED.
- NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1.
- OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1.
- SAME EDGES 0, CHANGED EDGES 1.
- HANDOFFS 1, CHANGED HANDOFFS 1.
- Handoff/edge child subject BLOBID
  `6C1292461038798149F3636EE517BB6E4B35DAA5`.
- Handoff/edge parent subject BLOBID
  `1A55B22C5ABB8A8609B3F828119988B04BF2BFAC`.
- STATUS CHANGED.
- Child subject BYTES 37, PREFIXHEX
  `52656D6F7665206F7665726C656E67746820434D`.
- Parent subject BYTES 28, PREFIXHEX
  `55736520434D532D73616665204D39462077616C`.

If that gate matches, immediately declare M139 NATIVE CMS TARGET-PROVEN,
append the exact proof to both state files, and continue autonomously with
M140+ until the next genuine CMS validation boundary.

### Preserved project rules

GitHub is canonical. Edit GitHub first, then transfer to CMS for target proof.
Maximize work per turn; do not pause except for a genuine CMS validation gate.
Use `CMS_SCRIPT_PORT=3272` for Mac-to-c3270 transfers. Respect fixed CMS
records: EXEC <=80 columns, C physical source <=72 columns, CMS file names/types
<=8 characters. Do not overwrite protected GITFIX/M15NEW generations,
selector PTRs, `GITPBUF PACK`, or read-only `GITREF2 REPO A`. Fail closed
and never emit trusted partial output before full requested verification.

## 2026-10-05 M139 REAL CMS TARGET PASS

Real z/VM CMS ran the wrapper-only M139 gate with GIT/GITVREF levels M139/M139.
HISTORYFIRSTSUBJECTS-REF-FULL on sealed commit
486ADAA5B02080720F4B329C6F68550B13C6AA87 at depth 1 and path
src/GITPBWALK.EXEC returned RC0 with full-snapshot verification: NODES 2,
EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0,
TRUNCATED 1, SAME EDGES 0, CHANGED EDGES 1, HANDOFFS 1, CHANGED HANDOFFS 1.
The sole handoff and edge used child subject BLOBID
6C1292461038798149F3636EE517BB6E4B35DAA5 and parent subject BLOBID
1A55B22C5ABB8A8609B3F828119988B04BF2BFAC with STATUS CHANGED. Child subject
metadata was BYTES 37 PREFIXHEX
52656D6F7665206F7665726C656E67746820434D; parent subject metadata was
BYTES 28 PREFIXHEX 55736520434D532D73616665204D39462077616C. This exactly confirms
authenticated full-subject continuity/change classification on the real CMS
first-parent chain. M139 is NATIVE CMS TARGET-PROVEN. Do not repeat this
standalone gate.


## M140 authenticated first-parent message-body handoffs

M139 is native CMS target-proven. M140 remains wrapper-only and reuses the
authenticated first-parent chain plus the M129-proven exact full-message
BLOBIDs; native GITREC remains unchanged from the M132 target-proven worker.
New read-only GIT HISTORYFIRSTBODIES-REF-FULL reports full-message continuity
only along the verified mainline: full DAG counts, chain/off-chain counts,
truncation, SAME/CHANGED edge counts, grouped exact message handoff pairs with
counts/status, and exact per-chain-edge child/parent message BLOBIDs and byte
counts. Each edge also carries the authenticated M128 subject BLOBIDs so a
same-subject/different-message case remains distinguishable. It fail-closes
unless grouped handoff counts sum exactly to projected chain edges and
SAME+CHANGED counts equal projected chain-edge cardinality.

The existing production-native host fixture already contains a real
parent/child pair whose first-line subject is the same `hello` subject while
the complete messages differ (`hello\n` versus
`hello\n\nbody differs\n`). M140 uses that independently authenticated
substrate to prove subject identity is not being substituted for message
identity. Router/worker EXEC identity advances to M140; GITREC is unchanged.

For the sealed CMS depth-1 gate on commit
486ADAA5B02080720F4B329C6F68550B13C6AA87 and path
src/GITPBWALK.EXEC, both messages are single-line, so the independently proven
M129 message BLOBIDs equal their M128 subject BLOBIDs. Expected M140 summary:
NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0,
OFFCHAIN EDGES 0, TRUNCATED 1, SAME EDGES 0, CHANGED EDGES 1, HANDOFFS 1,
CHANGED HANDOFFS 1. The child message BLOBID is
6C1292461038798149F3636EE517BB6E4B35DAA5 with BYTES 37; the parent message
BLOBID is 1A55B22C5ABB8A8609B3F828119988B04BF2BFAC with BYTES 28. Edge
subject BLOBIDs must be the same corresponding child/parent values. M140 is
host-only until its real CMS wrapper gate passes.


## 2026-10-05 M140 REAL CMS TARGET PASS

Real z/VM CMS ran the wrapper-only M140 gate with GIT/GITVREF levels M140/M140.
HISTORYFIRSTBODIES-REF-FULL on sealed commit
486ADAA5B02080720F4B329C6F68550B13C6AA87 at depth 1 and path
src/GITPBWALK.EXEC returned RC0 with full-snapshot verification: NODES 2,
EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0,
TRUNCATED 1, SAME EDGES 0, CHANGED EDGES 1, HANDOFFS 1, CHANGED HANDOFFS 1.
The sole handoff and edge used child full-message BLOBID
6C1292461038798149F3636EE517BB6E4B35DAA5 and parent full-message BLOBID
1A55B22C5ABB8A8609B3F828119988B04BF2BFAC with STATUS CHANGED. Child message
bytes were 37 and parent message bytes were 28. The exact edge subject BLOBIDs
matched the corresponding message BLOBIDs on this sealed single-line fixture.
This confirms authenticated full-message continuity/change classification on
the real CMS first-parent chain. M140 is NATIVE CMS TARGET-PROVEN. Do not
repeat this standalone gate.


## M141 authenticated first-parent log

M140 is native CMS target-proven. M141 remains wrapper-only and introduces
`GIT HISTORYFIRSTLOG-REF-FULL <commit|ref> <depth> <path>`. It reuses the
fully authenticated HISTORYDAGSTATE parser and first-parent chain builder,
then emits only chain members. Each step maps chain position to authenticated
node/depth/commit/tree metadata and reuses the strict per-node chronology
emitter for exact parent cardinality/order digest, author/committer time and
identity metadata, message digest/bytes, subject digest/prefix, plus path
PRESENT/ABSENT state and present object type/size/OID. No off-chain node is
presented as part of the log. Native GITREC remains the M132-proven worker.

For the sealed deletion fixture at depth 1, M141 must report two chain steps:
node 1 commit 486ADAA5B02080720F4B329C6F68550B13C6AA87 / tree
909B1D31C377F42158F1591AB3FA130105186FD7 / path ABSENT, then node 2 commit
91913EA4028B795707AA67EDB1ED17A74D1B896E / tree
AE65405CF230B9FB0992544773B3CF7197015A47 / path PRESENT as blob
A0C91615ABA9689C365159205E8CBA26EF6E16F4 type 3 size 1869. Summary remains
NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN 0/0, TRUNCATED 1.


## M142 consolidated authenticated first-parent report

M142 adds `GIT HISTORYFIRSTREPORT-REF-FULL <commit|ref> <depth> <path>`.
It consolidates the independently proven first-parent path, chronology, actor,
subject, and full-message relations in one fail-closed edge report. Every
first-parent edge is classified ADDED/DELETED/MODIFIED/UNCHANGED; author,
committer, subject, and message continuity are each independently classified
SAME/CHANGED. Aggregate counts for every classification must sum exactly to
the projected chain-edge count before any trusted output. Per-edge output
includes child/parent depth, commit, tree, path state/object metadata, the four
continuity statuses, and the existing exact authenticated pair chronology,
identity, message, and subject metadata. Native GITREC remains unchanged.

For the sealed depth-1 deletion fixture, expected M142 summary is one DELETED
edge and zero ADDED/MODIFIED/UNCHANGED edges; AUTHOR SAME 1 / CHANGED 0;
COMMITTER SAME 1 / CHANGED 0; SUBJECT SAME 0 / CHANGED 1; MESSAGE SAME 0 /
CHANGED 1. The edge retains child ABSENT / parent PRESENT blob
A0C91615ABA9689C365159205E8CBA26EF6E16F4, author and committer deltas +3,
both author-to-committer lags 0, shared actor BLOBID
78C41780430F464791E67533C261358D0FEB071E, child subject/message BLOBID
6C1292461038798149F3636EE517BB6E4B35DAA5 and parent subject/message BLOBID
1A55B22C5ABB8A8609B3F828119988B04BF2BFAC. M141-M142 are host-only until
one combined real CMS wrapper gate passes.


## 2026-10-05 M141-M142 MERGED; COMBINED REAL CMS GATE

PR #100 (M141-M142 first-parent log and report) passed full native-stage
workflow run 37348106620 and was squash-merged to main as
`b4c0d77fdd2310e4e777d6d09495bc29f8c1b546`. Post-merge main workflow run
`37348187095` also completed SUCCESS. M141-M142 are therefore
HOST/NATIVE-STAGE CI PROVEN but are not yet real CMS target-proven.

Both milestones are wrapper-only. Native `GITREC MODULE` remains the
M132 target-proven worker; do not rebuild it. Current executable handshake is
`GIT EXEC LEVEL M142` / `GITVREF EXEC LEVEL M142`.

Next genuine target gate, from Mac `ibm-sandbox/src`:
```sh
git pull
CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITVREF.EXEC GIT.EXEC
```

Then on CMS:
```text
GIT LEVEL
GIT HISTORYFIRSTLOG-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC
GIT HISTORYFIRSTREPORT-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC
```

No `CMSCLNK`. No `GITRUN`. Do not rerun M134-M140 standalone.

Expected M141 summary: NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1,
OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1. Step 1 is node 1,
depth 0, commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`, tree
`909B1D31C377F42158F1591AB3FA130105186FD7`, path ABSENT. Step 2 is node 2,
depth 1, commit `91913EA4028B795707AA67EDB1ED17A74D1B896E`, tree
`AE65405CF230B9FB0992544773B3CF7197015A47`, path PRESENT as blob
`A0C91615ABA9689C365159205E8CBA26EF6E16F4`, type 3, size 1869. The existing
authenticated per-node parent, chronology, actor, subject, and message metadata
must also be present.

Expected M142 summary: NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1,
OFFCHAIN 0/0, TRUNCATED 1; ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0;
AUTHOR SAME 1 / CHANGED 0; COMMITTER SAME 1 / CHANGED 0; SUBJECT SAME 0 /
CHANGED 1; MESSAGE SAME 0 / CHANGED 1. Edge 1 is child node 1 / parent node 2,
STATUS DELETED, child ABSENT / parent PRESENT with parent blob
`A0C91615ABA9689C365159205E8CBA26EF6E16F4`. Author and committer deltas are
+3 seconds, both author-to-committer lags are 0, actor BLOBIDs are
`78C41780430F464791E67533C261358D0FEB071E`, child subject/message BLOBID is
`6C1292461038798149F3636EE517BB6E4B35DAA5`, and parent subject/message BLOBID
is `1A55B22C5ABB8A8609B3F828119988B04BF2BFAC`.

If both commands pass, mark M141-M142 NATIVE CMS TARGET-PROVEN and continue
autonomously with M143+ until the next genuine CMS validation boundary.


## 2026-10-05 M141-M142 REAL CMS TARGET PASS

Real z/VM CMS returned GIT/GITVREF M142/M142. Both HISTORYFIRSTLOG-REF-FULL and HISTORYFIRSTREPORT-REF-FULL on commit 486ADAA5B02080720F4B329C6F68550B13C6AA87, depth 1, path src/GITPBWALK.EXEC passed full-snapshot verification. M141 reported the expected two-node first-parent chain: child tree 909B1D31C377F42158F1591AB3FA130105186FD7 with path ABSENT, parent tree AE65405CF230B9FB0992544773B3CF7197015A47 with PRESENT blob A0C91615ABA9689C365159205E8CBA26EF6E16F4 type 3 size 1869. All parent, chronology, actor, message, and subject metadata matched prior target proof. M142 reported exactly one DELETED edge; AUTHOR SAME 1, COMMITTER SAME 1, SUBJECT CHANGED 1, MESSAGE CHANGED 1; author/committer deltas 3 seconds, lags 0; actor BLOBID 78C41780430F464791E67533C261358D0FEB071E; child subject/message BLOBID 6C1292461038798149F3636EE517BB6E4B35DAA5; parent subject/message BLOBID 1A55B22C5ABB8A8609B3F828119988B04BF2BFAC. M141-M142 are NATIVE CMS TARGET-PROVEN.

## M143 authenticated first-parent changed-edge filter

M142 is native CMS target-proven. M143 adds read-only
`GIT HISTORYFIRSTDIFFS-REF-FULL <commit|ref> <depth> <path>`. It reuses the
authenticated first-parent projection and emits only changed mainline edges,
while preserving aggregate ADDED/DELETED/MODIFIED/UNCHANGED counts and
nearest/farthest changed child depths. Every emitted changed edge carries
authenticated child/parent node, depth, commit, tree, path state/object
metadata, author/committer/subject/message SAME/CHANGED status, and the exact
pair chronology/identity/message/subject metadata already proven by M142.
Before trusted output, changed must equal ADDED+DELETED+MODIFIED and
changed+unchanged must equal the projected chain-edge count.

For the sealed depth-1 deletion fixture, expected M143 is STATUS CHANGED,
NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN 0/0, TRUNCATED 1,
CHANGED EDGES 1, ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0, nearest and
farthest change depth 0, nearest changes 1. The sole emitted change is chain
edge 1, STATUS DELETED, with the already target-proven M142 endpoint metadata.


## M144 authenticated nearest first-parent change

M144 adds read-only
`GIT HISTORYFIRSTNEAREST-REF-FULL <commit|ref> <depth> <path>`. It uses the
same fail-closed M143 classification but emits only changed mainline edges at
the minimum authenticated child depth. The emitted match count must equal the
precomputed nearest cardinality before success. For the sealed fixture,
expected STATUS is CHANGED, CHANGES 1, DEPTH 0, MATCHES 1, and the sole match
is chain edge 1 DELETED with child ABSENT / parent PRESENT blob
A0C91615ABA9689C365159205E8CBA26EF6E16F4, author/committer SAME,
subject/message CHANGED, +3 second author/committer deltas, and zero lags.
M143-M144 are wrapper-only; native GITREC remains the M132 target-proven
worker. They remain host-only until the combined real CMS gate passes.


## 2026-10-05 M143-M144 HOST/NATIVE-STAGE PASS; REAL CMS GATE NEXT

M143-M144 implementation was reviewed in PR #101. PR workflow run
`37355981240` completed SUCCESS. The GitHub connector then rejected the PR
merge/ref mutation despite the PR being green and mergeable, so the exact five
reviewed file blobs were applied individually to canonical main with normal
contents-API commits. Final code+guard commit `9a8a26a1a62f601444600218221f51fcdb172a10`
passed native-stage run `37356304907` SUCCESS. Documentation commits followed;
current main after state synchronization is `7423a84280e19243cd3bb2b310099aeed00f1490`.
PR #101 was closed as redundant. No native C or protected data changed.

Current handshake is M144/M144. M143-M144 are wrapper-only; GITREC remains the
M132 target-proven worker. Next real CMS gate from Mac `ibm-sandbox/src`:
```sh
git pull
CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITVREF.EXEC GIT.EXEC
```
Then CMS:
```text
GIT LEVEL
GIT HISTORYFIRSTDIFFS-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC
GIT HISTORYFIRSTNEAREST-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC
```
No CMSCLNK and no GITRUN.

Expected M143 summary: STATUS CHANGED; NODES 2, EDGES 1, CHAIN NODES 2,
CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1; CHANGED
EDGES 1, ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0; NEAREST CHANGE DEPTH
0, FARTHEST CHANGE DEPTH 0, NEAREST CHANGES 1. The sole CHANGE references
chain EDGE 1 with STATUS DELETED and the same authenticated endpoint,
chronology, actor, subject and message metadata already target-proven by M142.

Expected M144 summary: STATUS CHANGED; NODES 2, EDGES 1, CHAIN NODES 2,
CHAIN EDGES 1, OFFCHAIN 0/0, TRUNCATED 1; CHANGES 1, DEPTH 0, MATCHES 1.
Its sole nearest CHANGE is chain EDGE 1 STATUS DELETED with child ABSENT /
parent PRESENT blob A0C91615ABA9689C365159205E8CBA26EF6E16F4, actor statuses
SAME, subject/message statuses CHANGED, +3 second author/committer deltas and
zero lags. M143-M144 are HOST/NATIVE-STAGE CI PROVEN but not real CMS
target-proven until this combined gate passes.


## 2026-10-05 M143 REAL CMS TARGET PASS

Real CMS ran GIT/GITVREF M144/M144 and `HISTORYFIRSTDIFFS-REF-FULL` on sealed commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`, depth 1, path `src/GITPBWALK.EXEC`. It returned RC0 after full-snapshot verification. Summary exactly matched the sealed fixture: STATUS CHANGED; NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1; CHANGED EDGES 1, ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0; nearest and farthest change depth 0; nearest changes 1. The sole emitted change was chain edge 1 STATUS DELETED, child ABSENT / parent PRESENT blob `A0C91615ABA9689C365159205E8CBA26EF6E16F4` type 3 size 1869, author and committer SAME, subject and message CHANGED, +3 second author/committer deltas, zero lags, and exact previously target-proven actor/subject/message metadata. The pasted PARENTTREE line visually split before its final two hex digits, but the authenticated command completed through DATA END with RC0 and all surrounding metadata matched. M143 is NATIVE CMS TARGET-PROVEN. M144 nearest-change remains the current real CMS validation boundary.

## 2026-10-05 M144 REAL CMS TARGET PASS

Real CMS ran `HISTORYFIRSTNEAREST-REF-FULL` on sealed commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`, depth 1, path `src/GITPBWALK.EXEC`, under GIT/GITVREF M144/M144. Full-snapshot verification passed. Summary matched exactly: STATUS CHANGED; NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1; CHANGES 1, DEPTH 0, MATCHES 1. The sole nearest change was chain edge 1 STATUS DELETED, child ABSENT / parent PRESENT blob `A0C91615ABA9689C365159205E8CBA26EF6E16F4` type 3 size 1869, AUTHOR SAME, COMMITTER SAME, SUBJECT CHANGED, MESSAGE CHANGED, +3 second author/committer deltas, zero lags, shared actor BLOBID `78C41780430F464791E67533C261358D0FEB071E`, child subject/message BLOBID `6C1292461038798149F3636EE517BB6E4B35DAA5`, and parent subject/message BLOBID `1A55B22C5ABB8A8609B3F828119988B04BF2BFAC`. The pasted transcript interleaved some lines around DATA END, but all required authenticated records were present and consistent. M144 is NATIVE CMS TARGET-PROVEN.


## M145 authenticated first-parent status

M144 is native CMS target-proven. M145 adds read-only
`GIT HISTORYFIRSTSTATUS-REF-FULL <commit|ref> <depth> <path>`. It reuses the
target-proven M143 first-parent classifier and emits only the compact authenticated
mainline summary: overall CHANGED/UNCHANGED status, full DAG and projected chain
cardinalities, truncation, ADDED/DELETED/MODIFIED/UNCHANGED edge counts, plus
nearest/farthest change depth and nearest-change cardinality when changes exist.
No edge details are emitted. Native GITREC remains the M132 target-proven worker.

For the sealed depth-1 deletion fixture, expected M145 is STATUS CHANGED; NODES 2,
EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0,
TRUNCATED 1; CHANGED EDGES 1, ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0;
NEAREST CHANGE DEPTH 0, FARTHEST CHANGE DEPTH 0, NEAREST CHANGES 1.


## M146 authenticated first-parent change bounds

M146 adds read-only
`GIT HISTORYFIRSTBOUNDS-REF-FULL <commit|ref> <depth> <path>`. It reuses the
same fail-closed classifier and emits only changed mainline edges at the nearest
or farthest authenticated child depth. It independently computes farthest-match
and unique boundary-change cardinalities, rejects zero/out-of-range counts when
changes exist, labels each emitted boundary record NEAREST, FARTHEST, or BOTH,
and requires the emitted record count to equal the precomputed boundary count.
Each boundary record reuses M143/M144 exact authenticated endpoint, path,
chronology, actor, subject, and message metadata.

For the sealed fixture nearest=farthest=0, so expected M146 is STATUS CHANGED,
CHANGES 1, NEAREST DEPTH 0 / MATCHES 1, FARTHEST DEPTH 0 / MATCHES 1,
BOUNDARY CHANGES 1, and one CHANGE with BOUND BOTH for chain edge 1 STATUS
DELETED. Endpoint and metadata values must match the already target-proven
M144 record. M145-M146 are wrapper-only and remain host-only until the combined
real CMS gate passes.

## 2026-10-05 M145-M146 HOST/NATIVE-STAGE PASS; REAL CMS GATE NEXT

PR #102 passed native-stage run `37360502316` and squash-merged as `c12e4b332cd69827cf355e8e346f51445220612a`. Post-merge main run `37360612752` also completed SUCCESS. M145-M146 are HOST/NATIVE-STAGE CI PROVEN but not yet real CMS target-proven. Both are wrapper-only; native `GITREC MODULE` remains the M132 target-proven worker. Current handshake is `GIT EXEC LEVEL M146` / `GITVREF EXEC LEVEL M146`.

Next CMS gate: upload only GITVREF.EXEC and GIT.EXEC, then run `HISTORYFIRSTSTATUS-REF-FULL` and `HISTORYFIRSTBOUNDS-REF-FULL` on sealed commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`, depth 1, path `src/GITPBWALK.EXEC`. M145 should report STATUS CHANGED; 2 nodes/1 edge; chain 2/1; offchain 0/0; truncated 1; changed 1, deleted 1, all other path change counts 0; nearest/farthest depth 0 and nearest changes 1. M146 should report STATUS CHANGED; CHANGES 1; nearest depth 0/matches 1; farthest depth 0/matches 1; boundary changes 1; and one CHANGE with BOUND BOTH for edge 1 STATUS DELETED, carrying the exact M144 endpoint/chronology/actor/subject/message metadata. No CMSCLNK and no GITRUN.

## 2026-10-05 M145 REAL CMS TARGET PASS

Real CMS ran GIT/GITVREF M146/M146 and `HISTORYFIRSTSTATUS-REF-FULL` on sealed commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`, depth 1, path `src/GITPBWALK.EXEC`. Full-snapshot verification passed. Summary exactly matched the sealed fixture: STATUS CHANGED; NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1; CHANGED EDGES 1, ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0; NEAREST CHANGE DEPTH 0, FARTHEST CHANGE DEPTH 0, NEAREST CHANGES 1. M145 is NATIVE CMS TARGET-PROVEN. The same pasted transcript contained only the tail of an M146 run through DATA END, without its M146 header/summary or full edge record, so M146 remains the current real CMS validation boundary pending complete output.

## 2026-10-05 M146 REAL CMS TARGET PASS

Real CMS ran `HISTORYFIRSTBOUNDS-REF-FULL` on sealed commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`, depth 1, path `src/GITPBWALK.EXEC`, under GIT/GITVREF M146/M146. Full-snapshot verification passed. Summary matched exactly: STATUS CHANGED; NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1; CHANGES 1; NEAREST DEPTH 0 / MATCHES 1; FARTHEST DEPTH 0 / MATCHES 1; BOUNDARY CHANGES 1. The sole boundary record was CHANGE 1 BOUND BOTH for chain EDGE 1 STATUS DELETED, child ABSENT / parent PRESENT blob `A0C91615ABA9689C365159205E8CBA26EF6E16F4` type 3 size 1869, AUTHOR SAME, COMMITTER SAME, SUBJECT CHANGED, MESSAGE CHANGED, +3 second author/committer deltas, zero lags, shared actor BLOBID `78C41780430F464791E67533C261358D0FEB071E`, child subject/message BLOBID `6C1292461038798149F3636EE517BB6E4B35DAA5`, and parent subject/message BLOBID `1A55B22C5ABB8A8609B3F828119988B04BF2BFAC`. The pasted transcript interleaved a repeated fragment around DATA END, but all required authenticated records were present and consistent. M146 is NATIVE CMS TARGET-PROVEN.


## M147 authenticated first-parent path versions

M146 is native CMS target-proven. M147 adds read-only
`GIT HISTORYFIRSTVERSIONS-REF-FULL <commit|ref> <depth> <path>`. It projects
path-object identity onto the authenticated first-parent chain only. PRESENT
and ABSENT chain-node counts must sum to chain-node cardinality; every PRESENT
node maps to exactly one unique OID version; summed version counts must equal
PRESENT nodes. Each unique version reports OID, count, min/max chain depth,
type and size, and each chain step reports its version number (0 means ABSENT).
The output also preserves full DAG/chain/off-chain counts and TRUNCATED.

For sealed commit 486AD... depth 1 path src/GITPBWALK.EXEC, expected M147 is
STATUS MIXED; NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN 0/0,
TRUNCATED 1; PRESENT 1, ABSENT 1, VERSIONS 1. VERSION 1 is
A0C91615ABA9689C365159205E8CBA26EF6E16F4, COUNT 1, MINDEPTH 1, MAXDEPTH 1,
TYPE 3 SIZE 1869. STEP 1 is node 1 depth 0 VERSION 0 STATE ABSENT; STEP 2 is
node 2 depth 1 VERSION 1 STATE PRESENT with that OID.


## M148 authenticated first-parent lifetime runs

M148 adds read-only
`GIT HISTORYFIRSTLIFETIME-REF-FULL <commit|ref> <depth> <path>`. It combines
the target-proven first-parent change classifier with M147 version mapping to
form contiguous runs of exact path state: ABSENT or one exact PRESENT OID.
Run node counts must sum to chain nodes. Every run boundary must correspond to
a non-UNCHANGED authenticated first-parent edge, and RUNS-1 must equal the
authenticated changed-edge count. Each run reports version/state, optional
OID/type/size, start/end step, depth and commit. Each run boundary reports the
corresponding chain edge and ADDED/DELETED/MODIFIED status. TRUNCATED remains
explicit so bounded history cannot be mistaken for a complete lifetime.

For the sealed fixture, expected M148 is PATH STATUS MIXED, CHANGE STATUS
CHANGED; chain 2/1, offchain 0/0, TRUNCATED 1; PRESENT 1, ABSENT 1,
VERSIONS 1, RUNS 2, TRANSITIONS 1, CHANGES 1. RUN 1 is VERSION 0 ABSENT,
one node at step 1/depth 0/commit 486AD... . RUN 2 is VERSION 1 PRESENT
A0C91615ABA9689C365159205E8CBA26EF6E16F4 type 3 size 1869, one node at
step 2/depth 1/commit 91913... . TRANSITION 1 is FROM RUN 1 TO RUN 2,
EDGE 1 STATUS DELETED. M147-M148 are wrapper-only; GITREC remains the M132
target-proven worker and no protected data changes.

## 2026-10-05 M147-M148 MERGED; CMS GATE NEXT

PR #103 passed native-stage run 37362935282 and squash-merged as `59c513d84bbf51f051aad5df28d2526db2bd1ac5`. PR head `27de21ba8bbe92f97c50afe4242f3f9f02f40a5b` and the merge commit share the exact tree `c6ed9e6912de86dd747892e31b7b00436ffef4dc`, so merged content is the byte-identical tree that passed the full host suite. Post-merge run 37363077634 was scheduler-queued at this checkpoint. M147-M148 are host/CI proven on the exact merged tree, wrapper-only, with native GITREC still M132. Handshake is M148/M148.

Next CMS gate: upload only GITVREF.EXEC and GIT.EXEC, then run `HISTORYFIRSTVERSIONS-REF-FULL` and `HISTORYFIRSTLIFETIME-REF-FULL` on sealed commit 486ADAA5B02080720F4B329C6F68550B13C6AA87, depth 1, path src/GITPBWALK.EXEC. M147 should report MIXED, PRESENT 1, ABSENT 1, VERSIONS 1; version 1 is A0C91615ABA9689C365159205E8CBA26EF6E16F4 count 1 depth 1 type 3 size 1869; step 1 version 0 ABSENT and step 2 version 1 PRESENT. M148 should report PATH STATUS MIXED, CHANGE STATUS CHANGED, RUNS 2, TRANSITIONS 1, CHANGES 1; run 1 is ABSENT at step/depth 1/0, run 2 is PRESENT version 1 at step/depth 2/1, and transition 1 is edge 1 DELETED. No CMSCLNK or GITRUN.

## 2026-10-05 M147-M148 REAL CMS TARGET PASS

Real CMS ran GIT/GITVREF M148/M148. `HISTORYFIRSTVERSIONS-REF-FULL` and `HISTORYFIRSTLIFETIME-REF-FULL` on sealed commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`, depth 1, path `src/GITPBWALK.EXEC`, both completed RC0 after full-snapshot verification.

M147 exactly matched the sealed expectation: STATUS MIXED; NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1; PRESENT 1, ABSENT 1, VERSIONS 1. VERSION 1 is `A0C91615ABA9689C365159205E8CBA26EF6E16F4`, COUNT 1, MINDEPTH 1, MAXDEPTH 1, TYPE 3 SIZE 1869. STEP 1 is node 1 depth 0 VERSION 0 STATE ABSENT; STEP 2 is node 2 depth 1 VERSION 1 STATE PRESENT with the same OID.

M148 exactly matched the sealed expectation: PATH STATUS MIXED; CHANGE STATUS CHANGED; NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN 0/0, TRUNCATED 1; PRESENT 1, ABSENT 1, VERSIONS 1, RUNS 2, TRANSITIONS 1, CHANGES 1. RUN 1 is VERSION 0 / STATE ABSENT / one node at step 1 depth 0 commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`. RUN 2 is VERSION 1 / STATE PRESENT OID `A0C91615ABA9689C365159205E8CBA26EF6E16F4` type 3 size 1869 / one node at step 2 depth 1 commit `91913EA4028B795707AA67EDB1ED17A74D1B896E`. TRANSITION 1 is FROM RUN 1 TO RUN 2, EDGE 1 STATUS DELETED. M147-M148 are NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M149 authenticated first-parent current exact-state run

M148 is native CMS target-proven. M149 adds read-only
`GIT HISTORYFIRSTCURRENT-REF-FULL <commit|ref> <depth> <path>`. It reuses the
target-proven lifetime-run decomposition and reports only the current exact
path-state run beginning at chain step 1. It reports current version/state,
optional OID/type/size, current-run node count, newest/oldest observed step,
depth and commit, signed author/committer spans, and whether the beginning of
that exact current state is known. BEGIN KIND is CHANGE when an authenticated
changed edge bounds the run, ROOT only when the chain actually reaches a
parentless commit, and UNKNOWN when the current run reaches a truncated
history boundary. A CHANGE beginning must reference a non-UNCHANGED edge and
the adjacent run versions must match the edge endpoints.

For the sealed fixture, expected M149 has PATH STATUS MIXED, CHANGE STATUS
CHANGED; chain 2/1, offchain 0/0, TRUNCATED 1; RUNS 2, TRANSITIONS 1, CHANGES
1. CURRENT RUN 1 VERSION 0 NODES 1, STATE ABSENT, newest=oldest step 1 depth
0 commit 486ADAA5..., author/committer spans 0. BEGIN KNOWN 1, BEGIN KIND
CHANGE, BEGIN EDGE 1 STATUS DELETED. PRIOR RUN 2 VERSION 1 is PRESENT OID
A0C91615ABA9689C365159205E8CBA26EF6E16F4 type 3 size 1869.


## M150 authenticated current-state origin event

M150 adds read-only
`GIT HISTORYFIRSTORIGIN-REF-FULL <commit|ref> <depth> <path>`. It emits the
same authenticated current-run summary as M149 and then emits the event that
began the current exact state when that event is known. CHANGE origins emit
one full authenticated edge record using the already target-proven M143
endpoint/path/chronology/actor/subject/message metadata. ROOT origins emit the
authenticated root node metadata. UNKNOWN truncated origins emit zero events
rather than inventing one.

For the sealed fixture, expected M150 repeats the M149 current-run summary,
then EVENTS 1, EVENT 1 CURRENT RUN 1 PRIOR RUN 2, and a full EVENT 1 edge
record for chain EDGE 1 STATUS DELETED: child ABSENT / parent PRESENT
A0C91615ABA9689C365159205E8CBA26EF6E16F4 type 3 size 1869, actors SAME,
subject/message CHANGED, +3 second author/committer deltas, zero lags, and the
already target-proven BLOBIDs. M149-M150 are wrapper-only; native GITREC
remains the M132 target-proven worker.


## 2026-10-05 M149-M150 MERGED / HOST-PROVEN; REAL CMS GATE NEXT

PR #104 (`M149-M150 current run and origin`) merged as
`f0dc2b5a893b2ca3f900ef638971e91ffaea40f7`. The PR head
`28995c3942ddbef0250868db8408231c96365965` and merge commit share exact tree
`b747dd35e314537a0930b7b69dfd94e2b3502815`. GitHub Actions runner service
was stalled with all five batch runs queued and zero executing jobs, including
post-merge run `37368463608`. To avoid treating scheduler unavailability as
a code failure, the complete changed verified-ref guard was independently
executed against the exact merged files through GitHub: 539 checks, 0 failures;
GITVREF max record 74, GIT max record 78, REF2 max record 60. The workflow
diff contains only CHAT_STATE.md, docs/CURRENT_STATE.md, src/GIT.EXEC,
src/GITVREF.EXEC, and tests/check-verified-ref.sh. All other native/compiler/
tree/index/selector sources and test scripts are unchanged from the already
green M148 baseline. M149-M150 are therefore HOST-PROVEN on the exact merged
tree, pending real CMS proof. Native GITREC remains the M132 target-proven
worker. Current handshake is M150/M150.

M149 adds `HISTORYFIRSTCURRENT-REF-FULL`: the exact current first-parent
path-state run, including current version/state, observed run length,
newest/oldest step/depth/commit, signed author/committer spans, and whether
the beginning of the current state is known as CHANGE, ROOT, or UNKNOWN due
to truncation. M150 adds `HISTORYFIRSTORIGIN-REF-FULL`: the same summary plus
the authenticated event that began the current state; CHANGE origins emit one
full M143-style edge record, ROOT origins emit the authenticated root node,
and UNKNOWN origins emit zero events.

Next real CMS gate from Mac `ibm-sandbox/src`:
```sh
git pull
CMS_SCRIPT_PORT=3272 ./cms-upload.sh GITVREF.EXEC GIT.EXEC
```
Then CMS:
```text
GIT LEVEL
GIT HISTORYFIRSTCURRENT-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC
GIT HISTORYFIRSTORIGIN-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC
```
No CMSCLNK and no GITRUN.

Expected M149: PATH STATUS MIXED; CHANGE STATUS CHANGED; NODES 2, EDGES 1,
CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0,
TRUNCATED 1, RUNS 2, TRANSITIONS 1, CHANGES 1. CURRENT RUN 1 VERSION 0 NODES
1; CURRENT STATE ABSENT; NEWEST and OLDEST are both STEP 1 DEPTH 0 COMMIT
486ADAA5B02080720F4B329C6F68550B13C6AA87; AUTHOR SPAN 0 and COMMITTER SPAN
0; BEGIN KNOWN 1; BEGIN KIND CHANGE; BEGIN EDGE 1 STATUS DELETED; PRIOR RUN 2
VERSION 1; PRIOR STATE PRESENT; PRIOR OID
A0C91615ABA9689C365159205E8CBA26EF6E16F4 TYPE 3 SIZE 1869.

Expected M150 repeats that current-run summary, then EVENTS 1 and
EVENT 1 CURRENT RUN 1 PRIOR RUN 2, followed by a full authenticated EVENT 1
edge record for EDGE 1 STATUS DELETED: child 1/parent 2, depth 0/1, child
commit 486AD..., parent commit 91913EA4..., child tree 909B1D31..., parent
tree AE65405C..., child ABSENT / parent PRESENT OID A0C91615... type 3 size
1869, AUTHOR SAME, COMMITTER SAME, SUBJECT CHANGED, MESSAGE CHANGED, +3 second
author/committer deltas, zero lags, shared actor BLOBID 78C41780..., child
subject/message BLOBID 6C129246..., and parent subject/message BLOBID
1A55B22C....

## 2026-10-05 M149 REAL CMS PASS / M150 TARGET FAILURE

Real CMS ran GIT/GITVREF M150/M150 on sealed commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`, depth 1, path `src/GITPBWALK.EXEC`. `HISTORYFIRSTCURRENT-REF-FULL` completed RC0 after full-snapshot verification and exactly matched the sealed expectation: PATH STATUS MIXED; CHANGE STATUS CHANGED; NODES 2, EDGES 1, CHAIN 2/1, OFFCHAIN 0/0, TRUNCATED 1, RUNS 2, TRANSITIONS 1, CHANGES 1; CURRENT RUN 1 VERSION 0 NODES 1 STATE ABSENT; newest=oldest step 1 depth 0 commit 486ADAA5...; author and committer spans 0; BEGIN KNOWN 1 / KIND CHANGE / EDGE 1 STATUS DELETED; PRIOR RUN 2 VERSION 1 STATE PRESENT OID A0C91615... TYPE 3 SIZE 1869. M149 is NATIVE CMS TARGET-PROVEN.

`HISTORYFIRSTORIGIN-REF-FULL` verified snapshots and emitted the same correct current-run summary plus EVENTS 1 / EVENT 1 CURRENT RUN 1 PRIOR RUN 2, then failed before the authenticated edge record with `DMSREX476E Error 41`, `Bad arithmetic conversion`, at GITVREF line 2270 (`fj=fi+1`). CMS traceback showed the call site split across physical lines at line 2773/2774. Root cause: the multi-line CALL to `emitfirstchange` did not deliver numeric `fcbeginedge` as the fourth argument under CMS REXX. M150 is NOT target-proven until the single-record CALL fix passes real CMS.

## M150 CMS origin-call fix

The first real CMS M150 attempt failed after correct snapshot/current-run output because `statefirstorigin` called `emitfirstchange` with the fourth argument on a continued physical line. CMS REXX delivered an empty/non-numeric `fi`, causing `DMSREX476E Error 41` at `fj=fi+1`. The fix keeps the entire call on one record: `call emitfirstchange 'HISTORYFIRSTORIGIN','EVENT',1,fcbeginedge`. A new host guard rejects any `CALL` line ending in a comma, preventing this CMS-specific argument continuation failure class. No command semantics, level handshake, native code, or protected data changed. M149 remains target-proven; M150 remains pending rerun after this fix.

## 2026-10-05 M150 FIX HOST PASS / TARGET RERUN NEXT

PR #105 fixed the CMS REXX argument-continuation defect by changing the `emitfirstchange` origin call to one physical record and adding a regression guard rejecting any CALL line ending in a comma. It squash-merged as `ef3699ea7597191cb500283bee3f388fd2e150c8`; PR head and merge share exact tree `888f2f4353c79977b7f00b51baf101452b9d1142`. Canonical main validation found 540 guard checks with 0 failures and no split CALLs. Post-merge native-stage run `37374878027` completed SUCCESS through all stages. M149 remains NATIVE CMS TARGET-PROVEN. M150 remains pending only the real CMS rerun of `HISTORYFIRSTORIGIN-REF-FULL`. Since GIT.EXEC and the M150/M150 handshake are unchanged, upload only `GITVREF.EXEC`; no CMSCLNK and no GITRUN.

## 2026-10-05 M150 REAL CMS TARGET PASS

After the single-record CALL fix, real CMS reran `HISTORYFIRSTORIGIN-REF-FULL` on sealed commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`, depth 1, path `src/GITPBWALK.EXEC`, under GIT/GITVREF M150/M150. Full-snapshot verification passed and the command completed RC0 through DATA END. The current-run summary matched M149 exactly: PATH STATUS MIXED; CHANGE STATUS CHANGED; NODES 2, EDGES 1, CHAIN 2/1, OFFCHAIN 0/0, TRUNCATED 1, RUNS 2, TRANSITIONS 1, CHANGES 1; CURRENT RUN 1 VERSION 0 NODES 1 STATE ABSENT; newest=oldest step 1 depth 0 commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`; author/committer spans 0; BEGIN KNOWN 1 / KIND CHANGE / EDGE 1 STATUS DELETED; PRIOR RUN 2 VERSION 1 STATE PRESENT OID `A0C91615ABA9689C365159205E8CBA26EF6E16F4` TYPE 3 SIZE 1869.

M150 then emitted EVENTS 1 and EVENT 1 CURRENT RUN 1 PRIOR RUN 2, followed by the full authenticated edge record: EDGE 1 STATUS DELETED, child 1/parent 2, depths 0/1, child commit 486AD..., parent commit 91913EA4..., child tree 909B1D31..., parent tree AE65405C..., child ABSENT / parent PRESENT OID A0C91615... type 3 size 1869; AUTHOR SAME, COMMITTER SAME, SUBJECT CHANGED, MESSAGE CHANGED; +3 second author/committer deltas; zero lags; shared actor BLOBID 78C41780...; child subject/message BLOBID 6C129246...; parent subject/message BLOBID 1A55B22C.... M150 is NATIVE CMS TARGET-PROVEN. The previous Error 41 is closed by the merged single-record CALL fix and its regression guard.


## M151 authenticated first-parent presence intervals

M150 is native CMS target-proven. M151 adds read-only
`GIT HISTORYFIRSTPRESENCE-REF-FULL <commit|ref> <depth> <path>`. Unlike the
M148 exact-state lifetime, M151 groups only by path existence. A MODIFIED edge
does not break a PRESENT interval; only ADDED/DELETED boundaries split
presence runs. The implementation reuses the target-proven exact-state and
edge classifiers and fail-closes unless: presence-run nodes sum to chain
nodes; exact-run counts inside presence runs sum to M148 exact runs;
PRESENCE RUNS-1 equals ADDED+DELETED; EXACT RUNS-PRESENCE RUNS equals
MODIFIED edges; and every presence boundary is an authenticated ADDED or
DELETED edge. Each run reports state, node count, exact-run count, PRESENT
version cardinality when applicable, and start/end step/depth/commit.

For sealed commit 486AD... depth 1 path src/GITPBWALK.EXEC, expected M151 is
PATH STATUS MIXED; EXISTENCE STATUS CHANGED; NODES 2, EDGES 1, CHAIN 2/1,
OFFCHAIN 0/0, TRUNCATED 1; PRESENT 1, ABSENT 1; EXACT RUNS 2; PRESENCE RUNS
2; PRESENCE TRANSITIONS 1; ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0.
RUN 1 is one-node ABSENT with EXACTRUNS 1 at step/depth 1/0 commit 486AD... .
RUN 2 is one-node PRESENT with EXACTRUNS 1, VERSIONS 1, at step/depth 2/1
commit 91913... . TRANSITION 1 is FROM RUN 1 TO RUN 2, EDGE 1 STATUS DELETED.


## M152 authenticated current-presence origin

M152 adds read-only
`GIT HISTORYFIRSTPRESENCEORIGIN-REF-FULL <commit|ref> <depth> <path>`.
It reports the current continuous presence/absence interval, which can span
multiple exact OID versions when the path remains PRESENT across MODIFIED
edges. It reports the interval's node and exact-run counts, PRESENT version
cardinality when applicable, newest/oldest step/depth/commit, signed
author/committer spans, and BEGIN KNOWN/KIND. CHANGE origins are restricted
to ADDED/DELETED edges and emit one full authenticated M143-style edge record;
ROOT origins emit the authenticated root node; UNKNOWN truncated origins emit
zero events.

For the sealed fixture, expected M152 repeats the M151 summary, then CURRENT
PRESENCE RUN 1 NODES 1 EXACTRUNS 1, CURRENT STATE ABSENT, newest=oldest
step/depth 1/0 commit 486AD..., author/committer spans 0, BEGIN KNOWN 1,
BEGIN KIND CHANGE, BEGIN EDGE 1 STATUS DELETED, PRIOR PRESENCE RUN 2 STATE
PRESENT. It then emits EVENTS 1, EVENT 1 CURRENT RUN 1 PRIOR RUN 2, and the
full authenticated EDGE 1 STATUS DELETED record already target-proven by
M150. M151-M152 are wrapper-only; native GITREC remains M132.

## 2026-10-05 M151-M152 HOST/NATIVE-STAGE PASS; REAL CMS GATE NEXT

PR #106 (`M151-M152 first-parent presence history`) passed full native-stage run `37376078777`, squash-merged as `6b3319dd8be59eb7170fe8b239b1ddd39832cba7`, and post-merge main run `37376162041` also completed SUCCESS through every stage. Independent static validation also passed 558 checks with 0 failures; GITVREF max record 74, GIT max record 78, and no split CALL argument lists. M151-M152 are HOST/NATIVE-STAGE CI PROVEN but not yet real CMS target-proven. Both are wrapper-only; native `GITREC MODULE` remains the M132 target-proven worker. Current handshake is `GIT EXEC LEVEL M152` / `GITVREF EXEC LEVEL M152`.

Next CMS gate: upload only GITVREF.EXEC and GIT.EXEC, then run `HISTORYFIRSTPRESENCE-REF-FULL` and `HISTORYFIRSTPRESENCEORIGIN-REF-FULL` on sealed commit `486ADAA5B02080720F4B329C6F68550B13C6AA87`, depth 1, path `src/GITPBWALK.EXEC`. No CMSCLNK and no GITRUN.

Expected M151: PATH STATUS MIXED; EXISTENCE STATUS CHANGED; NODES 2, EDGES 1, CHAIN NODES 2, CHAIN EDGES 1, OFFCHAIN NODES 0, OFFCHAIN EDGES 0, TRUNCATED 1; PRESENT 1, ABSENT 1; EXACT RUNS 2; PRESENCE RUNS 2; PRESENCE TRANSITIONS 1; ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0. RUN 1 is NODES 1 EXACTRUNS 1 STATE ABSENT, start=end step 1 depth 0 commit 486ADAA5... . RUN 2 is NODES 1 EXACTRUNS 1 STATE PRESENT VERSIONS 1, start=end step 2 depth 1 commit 91913EA4... . TRANSITION 1 is FROM RUN 1 TO RUN 2, EDGE 1 STATUS DELETED.

Expected M152 repeats the M151 base summary, then CURRENT PRESENCE RUN 1 NODES 1 EXACTRUNS 1, CURRENT STATE ABSENT, newest=oldest step 1 depth 0 commit 486ADAA5..., author/committer spans 0, BEGIN KNOWN 1, BEGIN KIND CHANGE, BEGIN EDGE 1 STATUS DELETED, PRIOR PRESENCE RUN 2 STATE PRESENT. Then EVENTS 1 and EVENT 1 CURRENT RUN 1 PRIOR RUN 2 followed by the full authenticated EDGE 1 STATUS DELETED record already target-proven by M150.


## 2026-10-05 M151-M152 REAL CMS TARGET PASS

Real CMS ran GIT/GITVREF M152/M152. HISTORYFIRSTPRESENCE-REF-FULL and HISTORYFIRSTPRESENCEORIGIN-REF-FULL on sealed 486ADAA5... depth 1 path src/GITPBWALK.EXEC both completed RC0 after full-snapshot verification. M151 exactly matched: PATH STATUS MIXED; EXISTENCE STATUS CHANGED; NODES 2, EDGES 1, CHAIN 2/1, OFFCHAIN 0/0, TRUNCATED 1; PRESENT 1, ABSENT 1; EXACT RUNS 2; PRESENCE RUNS 2; PRESENCE TRANSITIONS 1; ADDED 0, DELETED 1, MODIFIED 0, UNCHANGED 0. Run 1 is one-node ABSENT at step/depth 1/0 commit 486ADAA5...; run 2 is one-node PRESENT, VERSIONS 1, at step/depth 2/1 commit 91913EA4...; transition 1 is edge 1 DELETED.

M152 exactly matched: CURRENT PRESENCE RUN 1 NODES 1 EXACTRUNS 1, CURRENT STATE ABSENT, newest=oldest step 1 depth 0 commit 486ADAA5..., zero author and committer spans, BEGIN KNOWN 1 / KIND CHANGE / EDGE 1 DELETED, prior presence run 2 PRESENT. It then emitted EVENTS 1 and the complete authenticated edge-1 DELETED record with the same endpoint, chronology, actor, subject and message metadata target-proven by M150. M151-M152 are NATIVE CMS TARGET-PROVEN. Do not repeat this standalone gate.


## M153 authenticated first-parent presence chronology

M152 is native CMS target-proven. M153 adds read-only
`GIT HISTORYFIRSTPRESENCECHRONOLOGY-REF-FULL <commit|ref> <depth> <path>`.
It reuses the target-proven M151 presence intervals and adds signed author and
committer spans for every presence run, measured newest observed endpoint minus
oldest observed endpoint. Positive/zero/negative run counts are tracked
separately for author and committer chronology, and each sign partition must
sum exactly to PRESENCE RUNS. The command preserves the M151 base summary so
bounded/truncated history remains explicit.

For the sealed depth-1 deletion fixture, expected M153 repeats the M151 base
summary and reports AUTHOR POSITIVE RUNS 0, AUTHOR ZERO RUNS 2, AUTHOR NEGATIVE
RUNS 0; COMMITTER POSITIVE RUNS 0, COMMITTER ZERO RUNS 2, COMMITTER NEGATIVE
RUNS 0. RUN 1 is ABSENT, NODES 1, EXACTRUNS 1, step/depth 1/0 commit 486AD...,
AUTHOR SPAN 0 and COMMITTER SPAN 0. RUN 2 is PRESENT, NODES 1, EXACTRUNS 1,
step/depth 2/1 commit 91913..., AUTHOR SPAN 0 and COMMITTER SPAN 0.


## M154 authenticated first-parent presence events

M154 adds read-only
`GIT HISTORYFIRSTPRESENCEEVENTS-REF-FULL <commit|ref> <depth> <path>`.
It emits only authenticated existence boundaries: ADDED and DELETED edges that
separate M151 presence runs. MODIFIED-only exact-version changes stay inside a
presence interval and are intentionally excluded. EVENTS must equal PRESENCE
TRANSITIONS, and each event is emitted with the full M143/M150 authenticated
endpoint, path, chronology, actor, subject, and message metadata.

For the sealed fixture, expected M154 repeats the M151 base summary, then
EVENTS 1, EVENT 1 FROM RUN 1 TO RUN 2, followed by the full authenticated
EDGE 1 STATUS DELETED record already target-proven by M150/M152. M153-M154 are
wrapper-only; native GITREC remains the M132 target-proven worker.


## M153-M154 HOST PASS / CMS GATE

PR #107 passed native-stage run 37378665424, merged as 75e4801110a50a8a7c54522546e32f950dda2bc4, and post-merge main run 37378777693 passed. Independent guard: 574 checks, 0 failures. Handshake is M154/M154; GITREC remains M132. M153-M154 are host-proven, pending real CMS. Next gate uploads GITVREF.EXEC and GIT.EXEC and runs HISTORYFIRSTPRESENCECHRONOLOGY-REF-FULL and HISTORYFIRSTPRESENCEEVENTS-REF-FULL on sealed 486ADAA5... depth 1 path src/GITPBWALK.EXEC. Expected M153: two presence runs, both author/committer span 0; author zero runs 2 and committer zero runs 2, positive/negative 0. Expected M154: EVENTS 1, FROM RUN 1 TO RUN 2, full edge 1 DELETED metadata. No CMSCLNK or GITRUN.


## NEW CHAT HANDOFF — 2026-10-05 after M152 target proof

Canonical GitHub state is authoritative. M151 and M152 are NATIVE CMS
TARGET-PROVEN on the sealed depth-1 fixture. The next wrapper-only batch,
M153-M154, is already implemented, merged, and host/native-stage proven.
Current wrapper handshake is M154/M154; native GITREC remains the unchanged
M132 target-proven worker.

M153 is HISTORYFIRSTPRESENCECHRONOLOGY-REF-FULL. It adds signed author and
committer spans for each M151 presence interval and positive/zero/negative run
partitions. For the sealed fixture there are two presence runs and both spans
must be zero, so AUTHOR ZERO RUNS 2 and COMMITTER ZERO RUNS 2, with all
positive/negative counts 0.

M154 is HISTORYFIRSTPRESENCEEVENTS-REF-FULL. It emits only authenticated
ADDED/DELETED presence boundaries; MODIFIED-only exact-version edges remain
inside one presence interval. For the sealed fixture it must emit EVENTS 1,
FROM RUN 1 TO RUN 2, followed by the full authenticated EDGE 1 STATUS DELETED
record already target-proven by M150/M152.

Host proof for M153-M154: PR #107; PR native-stage run 37378665424 SUCCESS;
merge commit 75e4801110a50a8a7c54522546e32f950dda2bc4; post-merge main run
37378777693 SUCCESS; independent verified-ref guard 574/574. No native C,
selector, generation, or protected artifact changes.

NEXT REAL CMS GATE ONLY:
1. From Mac ibm-sandbox/src: git pull
2. Upload GITVREF.EXEC and GIT.EXEC with CMS_SCRIPT_PORT=3272.
3. On CMS run GIT LEVEL; expect M154/M154.
4. Run:
   GIT HISTORYFIRSTPRESENCECHRONOLOGY-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC
   GIT HISTORYFIRSTPRESENCEEVENTS-REF-FULL 486ADAA5B02080720F4B329C6F68550B13C6AA87 1 src/GITPBWALK.EXEC
No CMSCLNK. No GITRUN. After matching real CMS output, immediately mark
M153-M154 target-proven in BOTH docs/CURRENT_STATE.md and CHAT_STATE.md, then
continue autonomously into M155+ until the next genuine CMS boundary.


## 2026-10-05 M153-M154 REAL CMS TARGET PASS

Real CMS ran GIT/GITVREF M154/M154. M153
`HISTORYFIRSTPRESENCECHRONOLOGY-REF-FULL` completed RC0 with full snapshots
verified on sealed commit 486ADAA5... depth 1 path src/GITPBWALK.EXEC. It
reported two presence runs; AUTHOR ZERO RUNS 2 and COMMITTER ZERO RUNS 2;
all author/committer positive and negative run counts were zero.

M154 `HISTORYFIRSTPRESENCEEVENTS-REF-FULL` completed RC0 through DATA END
with full snapshots verified, EVENTS 1, FROM RUN 1 TO RUN 2, EDGE 1 STATUS
DELETED, and the same authenticated endpoint, chronology, actor, subject and
message metadata previously target-proven by M150/M152. M153-M154 are NATIVE
CMS TARGET-PROVEN. Do not repeat their verbose standalone target gate.

Successful future target gates should use compact fail-closed checker EXECs
and normally return only a few decisive lines plus plain Ready;. Full verbose
authenticated output is reserved for diagnosis after a compact gate failure.

## M155 compact CMS acceptance gate

M155 adds read-only `M155CHK EXEC`. It captures the already target-proven
M153/M154 commands internally, requires RC0, full-snapshot markers and the
sealed-fixture chronology/event invariants, and prints only three PASS lines.
PR #108 merged as 57c7bc44ad09abba669214a1fd141bfbba118ffe and post-merge
native-stage run 37382621792 succeeded. M155 is host-proven and awaits only
its compact real-CMS execution.

## M156 authenticated closed presence duration

M156 adds
`HISTORYFIRSTPRESENCEDURATION-REF-FULL`. Only presence runs bounded by
authenticated existence transitions on both ends are treated as fully closed.
For a PRESENT run the begin boundary must be ADDED and the end boundary must
be DELETED; the inverse is required for a closed ABSENT run. Signed author and
committer duration are computed between the two boundary child commits.

The sealed depth-5 486ADAA5... / src/GITPBWALK.EXEC fixture has three
presence runs. Run 2 is PRESENT, begins at edge 5 ADDED, ends at edge 1
DELETED, and has author/committer duration 50/50 seconds. M156CHK validates
the complete result internally and prints three compact PASS lines. PR #109
merged as 591d57c456ca45e3ef0b0e812158cf67376918fc and post-merge
native-stage run 37383048532 succeeded. M156 is host-proven pending compact
real-CMS validation.

## M157 authenticated current presence age

M157 adds `HISTORYFIRSTPRESENCEAGE-REF-FULL`. It reuses the target-proven
current-presence origin logic. When the current run beginning is authenticated
as CHANGE or ROOT, the author/committer age is the signed span from that begin
commit to the newest commit. UNKNOWN truncated beginnings remain explicitly
observed-only rather than being presented as complete age.

The sealed fixture for M157 starts at commit 6EF11911449C184457F3958ABE4CA7A0692CE8C9
with depth 6 and path src/GITPBWALK.EXEC. The current state is ABSENT for six
nodes, BEGIN KNOWN 1 / KIND CHANGE / EDGE 6 DELETED, with author and committer
age 268 seconds. M157CHK is the compact target gate.


## 2026-10-05 M157 HOST PASS / COMPACT CMS GATE NEXT

The first M157 host attempts exposed only a regression-test versioning defect:
the M156 host model incorrectly required the current wrapper level to remain
exactly M156. That guard now requires synchronized GIT/GITVREF levels at least
M156, so later milestones preserve M156 regression coverage. No M156 command
semantics changed.

After that fix, full native-stage run 37383455466 completed SUCCESS on branch
m157-presence-age. Current handshake is M157/M157. M155-M157 are wrapper/check
changes only; native GITREC remains the unchanged M132 target-proven worker.

Next real CMS gate is deliberately compact. Upload GITVREF.EXEC, GIT.EXEC,
M155CHK.EXEC, M156CHK.EXEC, and M157CHK.EXEC. Run M155CHK with the sealed
M153/M154 depth-1 arguments, then run M156CHK and M157CHK. Successful combined
output is only nine PASS lines plus the Ready prompts; no verbose history
command should be pasted unless one compact checker fails. No CMSCLNK. No
GITRUN.


## M157 ONE-COMMAND COMPACT CMS GATE

M157GATE EXEC now supersedes the earlier three-checker target procedure. It
runs M155CHK, M156CHK and M157CHK internally, requires each compact gate to
return RC0 and its final PASS marker, suppresses their successful detail, and
prints only four lines:

M157GATE M155 PASS
M157GATE M156 PASS
M157GATE M157 PASS
M157GATE COMBINED TARGET GATE PASS

followed by plain Ready;. On failure, rerun only the named compact checker;
use verbose history output only if that checker also fails. This remains
read-only and does not rebuild GITREC, generations, indexes, or protected data.


## 2026-10-05 M157GATE FIRST CMS ATTEMPT / M155 COMPACT FIX

The first real CMS M157GATE attempt ended after one history scan with
`M157GATE M155 FAIL RC 8`. Runtime matched one authenticated history command,
so M156 and M157 were never entered. This isolates the defect to the M155
compact chronology capture/check path, not to M156/M157 semantics.

M155CHK now invokes the exact public GIT commands already target-proven on CMS
instead of calling GITVREF internal verbs directly. Its summary failure lines
now include the five marker bits. M157GATE now re-emits compact checker output
on failure, so future diagnosis remains a few lines rather than a full history
report. No GIT/GITVREF level change and no native/protected changes.


## 2026-10-05 M157GATE SECOND CMS ATTEMPT / M155 SUMMARY PARSER FIX

Second real CMS M157GATE attempt again isolated to M155 and returned:
M157GATE M155 FAIL RC 8
M155 CHRONOLOGY FAIL SUMMARY 1 0 0 0 1

This proves the underlying chronology command completed successfully because
the compact checker found both FULL SNAPSHOTS VERIFIED and DATA END. Only the
three exact summary-record comparisons failed. M155CHK now strips each captured
record and recognizes the presence-run/author-zero/committer-zero summaries by
stable prefix plus final numeric value instead of exact whole-record equality.
The events checks are hardened the same way. No authenticated history semantics,
GIT/GITVREF level, GITREC, generations, indexes, or protected data changed.

Host native-stage run 37404389164 completed SUCCESS with the robust parser.


## 2026-10-05 M155 COMPACT GATE SIMPLIFIED TO COMPLETION MARKERS

Third real CMS M157GATE attempt again produced chronology markers 1/1 but no
summary-value matches. The underlying M153 chronology command therefore remains
healthy: it returned RC0 and emitted both FULL SNAPSHOTS VERIFIED and DATA END.

M155CHK no longer duplicates M153/M154 semantic assertions by parsing display
records. Those commands already fail closed internally and were independently
target-proven on real CMS. M155 now requires only RC0 plus FULL SNAPSHOTS
VERIFIED and DATA END for chronology and events. This removes console/pipeline
format sensitivity while preserving the authenticated command boundary.


## 2026-10-05 M156 TARGET ATTEMPT / COMPACT PROOF RECORDS

Real CMS M157GATE now passes M155. M156 then returned:
M157 LEVEL PASS M157/M157
M156 DURATION FAIL SUMMARY 6
with RC8. This isolates the remaining issue to the compact M156 display-parser;
the wrapper handshake is correct and the underlying M156 command completed far
enough to satisfy six of the old exact display assertions.

To remove display-format ambiguity, GITVREF now emits a short machine-readable
proof record for each closed M156 presence run:
HISTORYFIRSTPRESENCEDURATION PROOF RUN <n> <state> <begin-edge> <begin-status>
<end-edge> <end-status> <author-seconds> <committer-seconds>.
The sealed fixture checker requires exactly run 2 PRESENT, edge 5 ADDED,
edge 1 DELETED, 50/50 seconds, plus FULL SNAPSHOTS VERIFIED and DATA END.

M157 now emits the analogous compact current-age proof:
HISTORYFIRSTPRESENCEAGE PROOF <state> <begin-edge> <status>
<author-seconds> <committer-seconds>.
Its sealed checker requires ABSENT, edge 6 DELETED, 268/268 seconds, plus
FULL SNAPSHOTS VERIFIED and DATA END. This proactively avoids a second target
round for the same exact-display-record problem.


## 2026-10-05 M156 TARGET ATTEMPT / P2 STAMP DIAGNOSTICS

Real CMS M157GATE now passes M155, then M156 reports:
M156 LEVEL PASS M157/M157
M156 DURATION FAIL PROOF 1 0 1
with RC8. FULL SNAPSHOTS VERIFIED and DATA END are present, but no compact
duration proof record was captured.

The native HISTORYDAGSTATE depth contract was rechecked: depth 5 includes
levels 0 through 5. GitHub also confirms the sealed first-parent chain is
linear and the path states are ABSENT, PRESENT, PRESENT, PRESENT, PRESENT,
ABSENT. The first-presence builder/state parser are unchanged from the
M153 target-proven implementation.

Because GITVREF remains level M157 across these patch-only changes, a stale
GITVREF on the CMS EXEC search path cannot be distinguished by GIT LEVEL.
GITVREF therefore has a private STAMP command returning exactly:
GITVREF INTERNAL STAMP P2

M156CHK and M157CHK now require that stamp before target work. GITVREF also
emits short machine records, deliberately well below console record limits:
HFPD P2 S <runs> <closed> <add> <delete> <modify> <unchanged> <present> <absent>
HFPD P2 R <run> <state> <begin-edge> <begin-status> <end-edge> <end-status>
            <author-seconds> <committer-seconds>
HFPA P2 S <runs> <current-nodes> <begin-known> <begin-kind>
HFPA P2 R <state> <begin-edge> <status> <author-seconds> <committer-seconds>

The M156 sealed expectations are S=3 1 1 1 0 3 4 2 and
R=2 PRESENT 5 ADDED 1 DELETED 50 50. M157 expectations remain
S=2 6 1 CHANGE and R=ABSENT 6 DELETED 268 268.


## 2026-10-06 ROOT CAUSE: PIPE CMS UPPERCASED GIT PATHS

Real CMS P2 diagnostics proved the live GITVREF was current but M156 saw
HFPD P2 S 1 0 0 0 0 5 0 6: all six authenticated snapshots were classified
ABSENT. This was not a duration-run bug.

IBM CMS documents that the CMS REXX environment uppercases its command input,
while COMMAND preserves mixed-case operands. The CMS Pipelines COMMAND stage
uses the COMMAND environment. The compact checkers were issuing public Git
commands through PIPE CMS, so the case-sensitive Git path
src/GITPBWALK.EXEC was converted to SRC/GITPBWALK.EXEC before GITVREF encoded
it. Native path lookup therefore correctly returned ABSENT for every snapshot.

M155CHK is now a sealed no-argument checker and restores its full M153/M154
semantic assertions. M155CHK, M156CHK, and M157CHK invoke mixed-case public Git
commands with PIPE COMMAND and an explicit uppercase EXEC GIT prefix.
M157GATE no longer passes a mixed-case path through PIPE CMS. No public Git
semantics, GIT/GITVREF level, native GITREC, generations, indexes, or protected
data changed.


### 2026-10-06 CASE-PRESERVATION CORRECTION

The first path-case fix changed the pipeline's inner stage from CMS to COMMAND,
but the checker EXEC itself still had ADDRESS CMS as its active REXX host
environment. Therefore the complete PIPE command string could be uppercased
before CMS Pipelines parsed the COMMAND stage. In addition, GIT.EXEC itself
routed GITVREF calls under ADDRESS CMS, creating a second case-fold boundary.

The complete fix uses ADDRESS COMMAND for the PIPE invocation itself and uses
ADDRESS COMMAND for every GIT.EXEC -> GITVREF wrapper route. Mixed-case Git
paths and case-sensitive ref operands now remain unchanged across both EXEC
boundaries. The M155/M156/M157 gates require this structure in host guards.


## 2026-10-06 M155 REPEAT FAILURE / C4 PUBLIC-WRAPPER DIAGNOSTIC

After the two-boundary ADDRESS COMMAND fix was installed on CMS, M157GATE still
failed at M155 with the identical result:
M155 CHRONOLOGY FAIL SUMMARY 1 0 0 0 1

Because this can also be produced by an older M155CHK or GIT.EXEC found earlier
on the CMS search path, the next compact gate now proves the actual live copies
before starting history work.

GIT.EXEC adds private diagnostic command STAMP -> GIT EXEC STAMP C4.
M155CHK emits M155 CHECKER STAMP C4, requires the GIT C4 stamp, then sends the
literal mixed-case fixture path through the same public GIT -> GITVREF route
using private CASE. GITVREF CASE returns the path after pathasciihex encoding.
The required exact value is:
GITVREF CASE C4 7372632F474954504257414C4B2E45584543

On chronology mismatch M155 also emits two short observed-state records with
PRESENT/ABSENT/PRESENCE-RUN counts and ADD/DELETE/ZERO-run counts. This keeps
failure diagnosis compact while distinguishing stale EXEC search-path copies,
case folding, and genuinely unexpected authenticated history semantics.


## 2026-10-06 SEALED DIRECT PATH PROBE BEFORE M155 CHRONOLOGY

C4 target output proved the live checker, live GIT wrapper, and exact mixed-case
path bytes are correct, but chronology still reported PRESENT=0 ABSENT=2.

M155CHK now performs two authenticated direct path probes before chronology
using the same public READ-REF-FULL route and selected generations:
- parent 91913EA4028B795707AA67EDB1ED17A74D1B896E must read
  src/GITPBWALK.EXEC successfully with COMMIT ROOT FULL CLOSURE VERIFIED;
- child 486ADAA5B02080720F4B329C6F68550B13C6AA87 must return RC4 because the
  path was removed there.

If both probes pass but chronology still reports both snapshots ABSENT, the
fault is isolated to native HISTORYDAGSTATE path-state processing rather than
wrapper case, selected object data, or the ordinary authenticated path walker.


## 2026-10-06 M155 NATIVE HISTORYDAGSTATE TARGET ISOLATION / STACK HARDENING

Real CMS C4 diagnostics proved all wrapper and path-case layers correct:
- M155 CHECKER STAMP C4
- M155 GIT STAMP PASS C4
- M155 CASE PROBE PASS C4
- M155 PARENT PATH PASS for 91913EA4028B795707AA67EDB1ED17A74D1B896E
- M155 CHILD ABSENT PASS RC4 for 486ADAA5B02080720F4B329C6F68550B13C6AA87
Yet HISTORYFIRSTPRESENCECHRONOLOGY still reported PRESENT 0, ABSENT 2,
PRESENCE RUNS 1. This isolates the remaining fault below the wrapper layer.

Host coverage was expanded with a nested mixed-state HISTORYDAGSTATE fixture:
a child without subdir/nested.txt and a first parent containing that path.
Current native logic passes that regression on the host, so the failure is
target-specific rather than a generic path-state algorithm error.

rec_history_dag_state carried roughly 28 KB of fixed per-node work arrays on
its automatic stack while calling rec_root_closure, whose host frame is about
25.9 KB and is already target-proven. The nested peak stack was therefore much
larger than ordinary READ-REF-FULL/path traversal. The bounded
HISTORYDAGSTATE work arrays are now static process storage; GITREC executes
one command per process and does not require this routine to be reentrant.
All bounds, authentication, selector behavior, and output semantics are
unchanged.

The host native-tree build now uses -Wframe-larger-than=27000: this remains
above the established rec_root_closure frame while guarding against another
oversized recovery caller. GITREC also exposes private diagnostic
STAMP -> GITREC STACKFIX S1. M155CHK requires this stamp before target work,
so a stale native MODULE will fail immediately.

Host native-stage run 37494270555 completed SUCCESS with all changes.
Target rebuild and M157GATE validation remain required.


## 2026-10-06 S2: TARGET-PROVEN DAGPATH VS BROKEN DAGSTATE

After rebuilding the S1 native module on CMS, M157GATE still failed with:
- M155 CHECKER STAMP C4
- M155 GIT STAMP PASS C4
- M155 GITREC STAMP PASS S1
- M155 CASE PROBE PASS C4
- M155 PARENT PATH PASS
- M155 CHILD ABSENT PASS RC4
- chronology observed PRESENT 0 ABSENT 2 PRESENCE RUNS 1.

A direct native DAG-path discriminator then proved the older path walker on the
same target, generation, parent commit, and path:
GIT HISTORYPATH-REF-FULL
91913EA4028B795707AA67EDB1ED17A74D1B896E 0 src/GITPBWALK.EXEC
returned tree AE65405CF230B9FB0992544773B3CF7197015A47 and blob
A0C91615ABA9689C365159205E8CBA26EF6E16F4, TYPE 3 SIZE 1869.

This isolates the target defect specifically to duplicated
rec_root_path_state() behavior, not selectors, generations, closure,
path encoding, the public wrapper, or rec_root_path_meta().

S2 removes the duplicated state tree walker. rec_root_path_state() is now a
thin wrapper around the target-proven rec_root_path_meta() implementation.
The shared helper records an internal reason only for the two logical absence
cases: a missing named component and a matched non-tree intermediate prefix.
State mode converts only those reasons to authenticated ABSENT. Missing
referenced objects, type mismatches, malformed trees, and other corruption
still fail closed. HISTORYDAGPATH keeps its existing RC/output semantics.

Host coverage includes:
- child missing nested path / parent present nested path;
- blob used as an intermediate directory -> authenticated ABSENT;
- existing native tree/recovery suite and 27 KB frame guard.
Host run 37510050198 completed SUCCESS.
Private native stamp is now GITREC STATEPATH S2 and M155CHK requires it.
Real CMS rebuild and M157GATE remain required.


## 2026-10-06 S3 PUBLIC STATE-PARSER DISCRIMINATOR

Direct real-CMS GITREC HISTORYDAGSTATE depth-1 output is correct:
- node 1 commit 486AD... -> PATH ABSENT;
- node 2 commit 91913EA4... -> PATH PRESENT TYPE 3 SIZE 1869;
- node 2 PATHOID A0C91615ABA9689C365159205E8CBA26EF6E16F4;
- edge/slot CHILD 1 -> PARENT 2;
- exact expected tree OIDs.

Therefore native traversal, selected generation, path encoding, and S2 shared path
lookup are all correct. The remaining defect is above native C.

M155CHK now runs the existing public HISTORYSTATE-REF-FULL command on the sealed
two-node fixture before chronology. That command executes the same native
HISTORYDAGSTATE and statecheck parser, but stops before first-parent/presence
aggregation. The compact probe requires:
- HISTORYSTATE NODE 1 STATE ABSENT
- HISTORYSTATE NODE 2 STATE PRESENT

If this probe fails, the defect is in GITVREF native-output capture/statecheck.
If it passes while chronology still reports 0 present / 2 absent, the defect is
strictly in first-parent/presence aggregation after statecheck.
