# M164 practical CMS worktree porcelain

M164 is the first practical write-side porcelain milestone after the
read-only/history series.

It adds these public commands:

```text
GIT IMPORT-OBJECT <oid>
GIT CHECKOUT-FILE <ref> <git-path> <cms-fn> <cms-ft> [fm]
GIT STATUS
GIT ADD <git-path>
```

It also adds internal exact-workfile primitives:

```text
GIT HASH-WORKFILE <fn> <ft> <fm> <final-lf-0-or-1>
GIT WRITE-WORKFILE <fn> <ft> <fm> <final-lf-0-or-1>
```

## Verified native-to-loose import

`GIT IMPORT-OBJECT` binds the existing dual selected generations and runs
the target-proven `GITREC CATHEX` path. The selected object is fully
GENCHECK-verified and independently rehashed before its complete body is
emitted. Only COMMIT/TREE/BLOB objects are currently accepted into the loose
`GITOBJ` store. The newly written loose object is then verified again by
`GIT VERIFY-OBJECT`.

The sealed GITFIX/M15NEW generations are never modified.

## CMS worktree model

M164 uses `GITWORK REPO A` as a small persistent worktree index. Each entry
records:
- exact Git path as ASCII hex;
- CMS filename/filetype/filemode;
- whether the Git blob ends with a final LF;
- checkout/base blob OID;
- staged blob OID.

The first implementation deliberately limits mapped paths to 30 ASCII bytes.
It is a safe initial bridge for the current flat CMS-compatible `src/`
subtree and can be extended later without changing the object model.

`CHECKOUT-FILE`:
- resolves HEAD/branch through verified `GITREF2 REPO A`;
- invokes `GITREC PATHFULLCAT` directly;
- requires complete commit-root closure verification;
- accepts text bytes only in M164;
- rejects lines longer than CMS LRECL 80;
- refuses to overwrite any existing CMS file;
- writes a fixed-record CMS workfile;
- immediately re-hashes the CMS workfile and requires the original Git blob
  OID before recording the mapping.

`STATUS` independently hashes each mapped CMS file and compares worktree,
stage, and base OIDs. It reports CLEAN, MODIFIED, STAGED, or
STAGED+MODIFIED.

`ADD` writes the exact current CMS text representation as a loose Git blob,
updates only the staged OID in GITWORK, and leaves the base OID unchanged.

CMS fixed-record padding is removed only at the record tail; leading
indentation is preserved. The final-LF bit preserves normal Git text-file
round trips.

## Disposable real-CMS gate

`M164CHK` is self-cleaning and refuses to start unless both
`M164TST DATA A` and `GITWORK REPO A` are absent.

It performs:
1. authenticated checkout of `src/GITVREF.EXEC` at HEAD to disposable
   `M164TST DATA A`;
2. initial STATUS and base=stage map verification;
3. replacement of the disposable file with one test record;
4. independent modified workfile hash;
5. STATUS showing the modified state;
6. `GIT ADD src/GITVREF.EXEC`;
7. staged OID verification and STATUS;
8. `GIT VERIFY-OBJECT` of the new loose blob;
9. erasure of only the disposable CMS file, worktree map, and newly-created
   loose object.

The protected GITFIX/M15NEW generations and selector files are read-only
throughout.

## Host proof

GitHub Actions native-stage run `37637566550` completed successfully on
M164 code head `39659841c49bfaee8589a863c9cad5af30ef41d9`.
The run included all earlier M156-M163 checks, the M164 independent worktree
model, native selector tests, full CATHEX/tree recovery, and native
PACK/index tests.

The remaining acceptance boundary is real CMS execution of `M164CHK`.
