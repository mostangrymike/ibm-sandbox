# M181 — isolated hex lookup for skipped CMS stage records

## Motivation and target status

Actual real z/VM 6.3 CMS output established M180
single-scan correctness (8 trees, 272 blobs, 280 verified,
7736/7736 indexed, no seeks, clean FILEDEF) at 708.52s
elapsed, compared with M179's selective two-scan
459.44s. M180 performed SHA on 2220 indexed blobs vs
272 required; avoiding a 3,864,799-line second scan
did NOT make up for the added SHA work. M179 measured
7,729,598 stage text lines across two scans.

M181 changes **only a hot validation implementation**,
NOT the two-pass selective-SHA logic. This source is an
isolated C89 fork `src/GITPHX.C` of `GITPPRF.C`.
It retains exactly two read-only scans, selected tree
body SHA1/caching on scan 1 and reached blob SHA1
on scan 2. For `skipbody` on nonselected records it
replaces repeated C nibble comparisons with a
256-byte table of valid native character codes.
`inithex()` marks ASCII/EBCDIC-native '0'-'9',
'A'-'F', 'a'-'f' before reading any stage lines.
Every skipped hex character and expected line length
continues to be validated; malformed hex still
fails closed. Header/OID/index checks, EOF, tree
graph, child modes/types, cycle/depth, 64MiB cap
and authenticated reachable blob counts are unchanged.
Object bodies selected for SHA still use the original
`nib()` decoder. The only anticipated difference is
speed of the repeatedly executed skipbody validation.

New `src/GITPHX.EXEC` copies the established
`GITPPROF.EXEC` explicit non-A 4K input disk
and safe FILEDEF ownership/cleanup behavior under
its own module name and M181 counters. No original
module, stage or index changed. New native output:
`M181 HEX LOOKUP VALIDATOR PASS`, plus the normal
`M181 TREE CLOSURE PASS` / wrapper gate marker.
M179's `M181 STAGE LINES PASS1/2` and clock CPU
phase diagnostics are retained, though `clock()`
was UNAVAILABLE on real CMS under M179.

Host test `tests/test-m181-hex-lookup.py` uses
`-std=c89 -Wall -Wextra -Werror`, compares closure
with M178, proves validation of large *unreachable*
indexed blob payload, accepts lowercase hex for
skipped data, and fails closed on invalid hex
skipped body, reached blob SHA corruption, malformed
root and truncated index. CI must pass before CMS.

**M181 NOT YET CMS TARGET-PROVEN.**
A speedup is neither assumed nor guaranteed.
The fastest measured approach remains M179 (459.44s);
M181 is separate experimental code, not replacement.

## Conditional target test after host CI

Mac from `ibm-sandbox/src`:

```sh
git pull
./cms-upload.sh GITPHX.C GITPHX.EXEC
```

CMS MAINT preflight:

```text
QUERY DISK G
STATE M173NET STAGE G
STATE M174NET INDEX G
QUERY FILEDEF
STATE GITPHX C A
CMSCLNK GITPHX PLAIN
STATE GITPHX MODULE A
```

Only proceed after clean 4KB G disk, both
protected files present, no conflicting FILEDEF
and successful new module compilation:

```text
GITPHX G CCB18BEC067E7886D70B82EF138EE56A8B899A61
QUERY FILEDEF
```

Expected: same root, 8 trees, 272 blobs, 279 entries,
280 verified objects, 7736/7736 unique indexed OIDs,
2 forward scans, 15472 object header visits, zero
seeks, 272 authenticated reachable blobs, 3,864,799
stage text lines per pass, M181 terminal closure
and wrapper verified gate. Record elapsed and CPU,
and identical before/after `QUERY FILEDEF`.
The CPU phase `UNAVAILABLE` is acceptable.
Compare one native M181 run to M179 459.44s,
but consider environment variation and avoid
claiming a definitive improvement from one run.

Never ERASE, FORMAT, write G stage/index, reimport,
reindex, repeat original large milestones, or
write-link PMAINT 0141 overlapping VMCOM1 fullpack.
Keep M176–M180 modules available.
