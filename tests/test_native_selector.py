#!/usr/bin/env python3
"""Build and test CMS C89 selector parser against the Python protocol."""
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from active_generation_selector import encode  # noqa: E402

SOURCE = Path(__file__).resolve().parents[1] / "src" / "GITSEL.C"
OLD = "A" * 40
NEW = "B" * 40


def invoke(folder, program, a=None, b=None):
    for name, data in (("dd:SEL0", a), ("dd:SEL1", b)):
        target = folder / name
        if data is None:
            target.unlink(missing_ok=True)
        else:
            target.write_text(data, encoding="ascii")
    return subprocess.run(
        [str(program), "CHECK"], cwd=folder, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def check(result, code, *words):
    assert result.returncode == code, (result.returncode, result.stdout)
    for word in words:
        assert word in result.stdout, result.stdout


def main():
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        binary = folder / "native_selector"
        subprocess.run(
            ["cc", "-x", "c", "-std=c89", "-O2", "-Wall",
             "-Wextra", "-Werror", "-o", str(binary), str(SOURCE)],
            check=True
        )
        old = encode(41, "GITOLD", OLD)
        new = encode(42, "GITNEW", NEW)
        check(invoke(folder, binary, old, new), 0,
              "CANDIDATE 41 GITOLD", "CANDIDATE 42 GITNEW",
              "CANDIDATES UNTRUSTED: REQUIRE GENCHECK")
        check(invoke(folder, binary, None, new), 0,
              "CANDIDATE 42 GITNEW")
        check(invoke(folder, binary, None, None), 8,
              "NO VALID SELECTOR SLOT")
        altered = new.replace("GITNEW", "GITBAD")
        check(invoke(folder, binary, old, altered), 0,
              "CANDIDATE 41 GITOLD")
        for length in range(len(new)):
            check(invoke(folder, binary, old, new[:length]), 0,
                  "CANDIDATE 41 GITOLD")
        check(invoke(folder, binary, old,
                     encode(41, "GITNEW", NEW)), 8,
              "CONFLICTING SELECTOR SEQUENCE")
        check(invoke(folder, binary, old,
                     encode(41, "GITOLD", OLD)), 0,
              "CANDIDATE 41 GITOLD")
        invalid = [
            old.replace("GITOLD", "gitold"),
            old.replace("GITOLD", "TOOLONG"),
            old.replace("SEL1", "SEL0"),
            old.replace(" 41 ", " 041 "),
            old.replace("A"*40, "Z"*40),
            old + "\n",
        ]
        for case in invalid:
            check(invoke(folder, binary, case, None), 8,
                  "NO VALID SELECTOR SLOT")
    print("NATIVE C89 SELECTOR PARSER REGRESSION PASSED")


if __name__ == "__main__":
    main()
