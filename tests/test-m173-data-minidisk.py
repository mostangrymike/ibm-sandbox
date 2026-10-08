#!/usr/bin/env python3
"""Host source guard for isolated generalized CMS stage/index disks."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
specs = (
    ("M173", "STAGE", "180000"),
    ("M174", "INDEX", "4096"),
    ("M175", None, None),
    ("M176", None, None),
)
for m, written, minimum in specs:
    source = (root / "src" / f"{m}CHK.EXEC").read_text()
    assert "parse upper arg datafm extra" in source, m
    assert "verify(datafm,'BCDEFGHIJKLMNOPQRSTUVWXYZ')" in source, m
    assert "STAGE A'" not in source, m
    assert "INDEX A'" not in source, m
    assert "STAGE' datafm" in source, m
    assert "FILEDEF STGIN DISK' stage 'STAGE' datafm" in source or m == "M173"
    assert "STATE' stage 'STAGE' datafm" in source
    if m != "M173":
        assert "STATE' idx 'INDEX' datafm" in source
        assert "FILEDEF IDXIN DISK' idx 'INDEX' datafm" in source or m == "M174"
    if written:
        assert "'PIPE CMS QUERY DISK' datafm" in source
        assert "word(d.di,4)='R/W'" in source
        assert "word(d.di,7)='4096'" in source
        assert f"if avail<{minimum}" in source
        assert "matched\\=1 | datatype(avail,'W')\\=1" in source
    assert "GITFIX" not in source and "M15NEW" not in source
    assert "META A" in source
    for number, line in enumerate(source.splitlines(), 1):
        assert len(line) <= 80, (m, number, len(line))

m173 = (root / "src" / "M173CHK.EXEC").read_text()
assert "'FILEDEF OBJOUT DISK' stage 'STAGE' datafm" in m173
assert "'PIPE CMS GITPIMP IMPORT CHECKED | STEM q.'" in m173
assert "'FILEDEF OBJOUT CLEAR'" in m173

m174 = (root / "src" / "M174CHK.EXEC").read_text()
assert "'FILEDEF IDXOUT DISK' idx 'INDEX' datafm" in m174
assert "'PIPE CMS GITPIDX BUILD CHECKED | STEM b.'" in m174
assert "'FILEDEF IDXOUT CLEAR'" in m174


# The live milestone pages must describe the isolated G-disk contract.
# Historical A-disk failures are retained only below explicit headings.
m173 = (root / "docs" / "M173.md").read_text()
current_m173 = m173.split("## Historical CMS attempt:", 1)[0]
assert "M173CHK G" in current_m173
assert "M173NET STAGE G" in current_m173
assert "M173NET STAGE A" not in current_m173
assert "retains any failed output" in current_m173
m174 = (root / "docs" / "M174.md").read_text()
current_m174 = m174.split("## Historical CMS output guard", 1)[0]
assert "M174CHK G" in current_m174
assert "M173NET STAGE G" in current_m174
assert "M174NET INDEX G" in current_m174
assert "M174NET INDEX A" not in current_m174
assert "retained for diagnosis" in current_m174
for milestone in ("M175", "M176"):
    spec = (root / "docs" / f"{milestone}.md").read_text()
    assert f"{milestone}CHK G" in spec
    assert "M173NET STAGE G" in spec
    assert "M174NET INDEX G" in spec
    assert "M173NET STAGE A" not in spec
    assert "M174NET INDEX A" not in spec

print("M173-M176 SEPARATE CMS DATA MINIDISK SOURCE GATES PASSED")
