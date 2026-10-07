#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]

def read(path):
    return (root / path).read_text()

def write(path, text):
    (root / path).write_text(text)

gpath = "src/GIT.EXEC"
g = read(gpath)
g = g.replace("GIT EXEC LEVEL M164", "GIT EXEC LEVEL M165")
g = g.replace("GITVREF EXEC LEVEL M164", "GITVREF EXEC LEVEL M165")
g = g.replace("'EXEC GITCMIT' rest", "'EXEC GITWT COMMIT' rest")
assert "'EXEC GITWT COMMIT' rest" in g
assert "WRITE-TREE-HEXFILE" in g
write(gpath, g)

vpath = "src/GITVREF.EXEC"
v = read(vpath)
v = v.replace("/* M164: practical CMS worktree porcelain bridge. */",
              "/* M165: staged commit porcelain bridge. */")
v = v.replace("GITVREF EXEC LEVEL M164", "GITVREF EXEC LEVEL M165")
assert "GITVREF EXEC LEVEL M165" in v
write(vpath, v)

wpath = "src/GITWT.EXEC"
w = read(wpath)
w = w.replace("/* M164: exact single-file CMS worktree checkout/status/add. */",
              "/* M165: exact CMS worktree checkout/status/add/commit. */")
if "rootfor:" not in w:
    anchor = "loadmap:\n drop mapfn. mapft. mapfm. maplf."
    helpers = read("scripts/m165/gitwt_helpers.txt")
    assert anchor in w
    w = w.replace(anchor, helpers)
write(wpath, w)

write("src/M165CHK.EXEC", read("scripts/m165/M165CHK.txt"))

doc = """# M165 staged commit milestone

M165 creates a loose child commit from exactly one staged tracked CMS path.

Safety boundaries:
- HEAD and every base tree are authenticated through GITREC.
- The staged path must still match its checkout base in current HEAD.
- The workfile must exactly match the staged blob; unstaged changes fail.
- Only ancestor trees on the staged path are rewritten.
- The current HEAD commit is imported as the parent.
- The new commit is verified after creation.
- M165 does not update any ref. Ref compare-and-swap is a later milestone.

The real-CMS checker retains the verified loose commit candidate so the next
ref-CAS milestone can advance an isolated ref to the proven commit.
"""
write("docs/M165.md", doc)

wfpath = ".github/workflows/native-stage.yml"
wf = read(wfpath)
anchor = "      - 'tests/test-m164-worktree.py'\n"
extra = (
    "      - 'src/M165CHK.EXEC'\n"
    "      - 'tests/test-m165-staged-commit.py'\n"
    "      - 'docs/M165.md'\n"
)
if "      - 'src/M165CHK.EXEC'\n" not in wf:
    assert wf.count(anchor) == 2
    wf = wf.replace(anchor, anchor + extra)
step = (
    "      - name: Check M164 practical CMS worktree porcelain\n"
    "        run: python3 tests/test-m164-worktree.py\n"
)
m165 = (
    "      - name: Check M165 staged commit object\n"
    "        run: python3 tests/test-m165-staged-commit.py\n"
)
if "Check M165 staged commit object" not in wf:
    assert step in wf
    wf = wf.replace(step, step + m165)
write(wfpath, wf)

for path in ("src/GIT.EXEC", "src/GITVREF.EXEC",
             "src/GITWT.EXEC", "src/M165CHK.EXEC"):
    for number, line in enumerate(read(path).splitlines(), 1):
        assert len(line) <= 80, (path, number, len(line))

for path in ("scripts/m165/gitwt_helpers.txt",
             "scripts/m165/M165CHK.txt",
             "scripts/apply-m165.py",
             ".github/workflows/m165-apply.yml"):
    (root / path).unlink(missing_ok=True)
(root / "scripts/m165").rmdir()

print("M165 branch patch applied")
