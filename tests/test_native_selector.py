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
        verifier_source = SOURCE.parents[0].parent / "tests" / (
            "native_selector_verify_host.c"
        )
        verify_binary = folder / "native_verify"
        subprocess.run(
            ["cc", "-x", "c", "-std=c89", "-O2", "-Wall",
             "-Wextra", "-Werror", "-o", str(verify_binary),
             str(verifier_source)],
            check=True,
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
        # SELECT uses a replaceable full-verification callback. The
        # host simulator uses marker files, NOT actual CMS GENCHECK.
        (folder / "verified_GITOLD.txt").write_text(OLD + "\\n")
        (folder / "verified_GITNEW.txt").write_text(NEW + "\\n")

        def select(slot0, slot1):
            for name, data in (("dd:SEL0", slot0), ("dd:SEL1", slot1)):
                path = folder / name
                if data is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_text(data, encoding="ascii")
            return subprocess.run(
                [str(verify_binary), "SELECT"], cwd=folder,
                capture_output=True, text=True,
            )

        check(select(old, new), 0, "SELECTED 42 GITNEW")
        (folder / "verified_GITNEW.txt").unlink()
        check(select(old, new), 0, "RECOVERED 41 GITOLD")
        (folder / "verified_GITOLD.txt").unlink()
        check(select(old, new), 8, "NO FULLY VERIFIED GENERATION")
        (folder / "verified_GITOLD.txt").write_text(OLD + "\\n")
        for length in range(len(new)):
            check(select(old, new[:length]), 0,
                  "SELECTED 41 GITOLD")
        check(select(old, encode(41, "GITNEW", NEW)), 8,
              "CONFLICTING SELECTOR SEQUENCE")
        check(select(None, None), 8,
              "NO FULLY VERIFIED GENERATION")
    print("NATIVE C89 SELECTOR PARSER REGRESSION PASSED")


if __name__ == "__main__":
    main()
