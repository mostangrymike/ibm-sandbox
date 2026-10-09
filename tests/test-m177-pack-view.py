#!/usr/bin/env python3
"""M177 non-mutating CMS wrapper structural/host contract.

Static checks cannot establish actual z/VM QUERY FILEDEF semantics or
prove a real CMS execution. Target validation remains mandatory.
"""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
src = (root / "src/GITPVIEW.EXEC").read_text()
plan = (root / "docs/M177_READONLY_PACK_ACCESS_PLAN.md").read_text()

assert len("GITPVIEW") <= 8
assert max(map(len, src.splitlines())) <= 80
assert "address cms" in src
assert "parse upper arg op datafm oid extra" in src
assert "Usage: GITPVIEW INFO|TREE data-filemode 40-hex-oid" in src
assert "verify(datafm,'BCDEFGHIJKLMNOPQRSTUVWXYZ')" in src
assert "verify(oid,'0123456789ABCDEF')" in src
assert "length(oid)\\=40" in src
assert "'PIPE CMS QUERY DISK' datafm '| STEM d.'" in src
assert "word(d.i,7)='4096'" in src

# Source and index are checked for existence before FILEDEF binds.
assert "'STATE M173NET STAGE' datafm" in src
assert "'STATE M174NET INDEX' datafm" in src
assert "'STATE GITPCAT MODULE A'" in src
assert "'STATE GITPTRE MODULE A'" in src

q = src.index("'PIPE CMS QUERY FILEDEF | STEM f.'")
guard = src.index("if dd='STGIN' | dd='IDXIN' then do")
bind_stage = src.index("'FILEDEF STGIN DISK M173NET STAGE' datafm")
bind_index = src.index("'FILEDEF IDXIN DISK M174NET INDEX' datafm")
run_info = src.index("'PIPE CMS GITPCAT INFO' oid '| STEM o.'")
run_tree = src.index("'PIPE CMS GITPTRE WALK' oid '| STEM o.'")
cleanup_idx = src.index("'FILEDEF IDXIN CLEAR'", bind_index)
cleanup_stage = src.rindex("'FILEDEF STGIN CLEAR'")
assert q < guard < bind_stage < bind_index < run_info
assert q < guard < bind_stage < bind_index < run_tree
assert run_info < cleanup_idx < cleanup_stage
assert run_tree < cleanup_idx < cleanup_stage
assert "M177 DD ALREADY DEFINED" in src
assert "M177 FILEDEF QUERY FAILED" in src
assert src.count("'FILEDEF STGIN CLEAR'") == 2
assert src.count("'FILEDEF IDXIN CLEAR'") == 1

# Explicitly forbid any storage, repository, or CP writes.
for prohibited in (
    "FORMAT ", "DIRECTXA", "ERASE ", "COPYFILE ",
    "FILEDEF OBJOUT", "FILEDEF IDXOUT",
    "GITPIMP IMPORT", "GITPIDX BUILD",
    "CMSCLNK ", "CP LINK", "FILEDEF * CLEAR",
):
    assert prohibited not in src, prohibited
assert not re.search(r"^\s*'FILEDEF\s+(?:OBJOUT|IDXOUT)\b", src, re.M)
assert "M175 PACK INFO PASS" in src
assert "M176 TREE CLOSURE PASS" in src
assert "M177 PACK VIEW CROSSCHECK FAIL" in src
assert "M177 PACK VIEW' op 'PASS' oid datafm" in src

# No hidden default to A or implicit filemode selection.
assert "datafm='A'" not in src
assert "M173NET STAGE A" not in src
assert "M174NET INDEX A" not in src

# Host interpretation of real target evidence, not made-up results.
trees, blobs, links, entries, verified = 8, 272, 0, 279, 280
assert verified == trees + blobs
assert entries == blobs + trees - 1 + links
assert "M176 LIVE ROOT TREE CLOSURE TARGET GATE PASS" in plan
assert "M177 INFO + TREE live CMS PASS" in plan
assert "GITPVIEW INFO G" in plan
assert "GITPVIEW TREE G" in plan

# Real CMS now proves BOTH INFO and TREE; retain fixed-80 source guards.
state = (root / "CHAT_STATE.md").read_text()
readme = (root / "README.md").read_text()
for note in (plan, state, readme):
    assert "M177 PACK VIEW TREE PASS" in note
    assert "CCB18BEC067E7886D70B82EF138EE56A8B899A61" in note
    assert "280" in note and "272" in note
for note in (plan, state):
    assert "15:32:00" in note
    assert "393767" in note and "394058" in note
    assert "7736" in note and "M175CHK G" in note
    assert "T=*.**/*.**" in note
assert "INFO" in plan and "FILEDEF" in plan
assert "M177 INFO + TREE live CMS PASS" in plan
assert "INFO" in readme and "FILEDEF" in readme
# The original stage and index are source-only references; any
# expensive M173/M174 rebuild remains outside the M177 interface.
assert "M173NET STAGE G" in plan
assert "M174NET INDEX G" in plan


# Independent real CMS INFO + FILEDEF-state restoration checkpoint.
for note in (plan, state, readme):
    for marker in (
        "M177 PACK VIEW INFO PASS",
        "M175 VERIFIED RANDOM ACCESS TARGET GATE PASS",
        "41.52",
        "124.65",
    ):
        assert marker in note, marker
for note in (plan, state):
    assert "15:47:16" in note
    assert "15:51:13" in note
    assert "No user defined FILEDEF in effect" in note
    assert "B81D3CE7BAC08420BF7DB862E93F82FB3968DDC0" in note
    assert "8B7134918D12ED07D60E3CB28A1803EBCA7DB65B" in note
assert "full M175CHK G PASS" in (
    root / "docs/M178_PACK_TREE_PERFORMANCE_PLAN.md"
).read_text()

print("M177 READONLY G STAGE/INDEX VIEW SOURCE GUARD PASS")
