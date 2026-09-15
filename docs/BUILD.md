# CMS/z/VM build and transfer workflow

## Host side

Clone or pull this repository on the Mac. Source files in Git are ordinary ASCII stream files; do not store artificial 80-column trailing padding in Git.

Transfer files to CMS with c3270 IND$FILE. For assembler source use:

- Host: VM
- Mode: ASCII
- CR: Remove
- Remap: Yes
- DFT buffer: 16384
- Destination: `GITCORE ASSEMBLE A`

The transferred assembler source must be suitable for CMS fixed-record assembly. Verify it with XEDIT if necessary before building.

## CMS environment

`PROFILE EXEC` globalizes the preferred CMS macro library:

    GLOBAL MACLIB DMSGPI

## Build GITCORE

    ASSEMBLE GITCORE
    LOAD GITCORE
    GENMOD GITCORE

Do not replace a known-good MODULE after an assembly failure. Assemble first, inspect the result, then LOAD/GENMOD only after `NO STATEMENTS FLAGGED IN THIS ASSEMBLY`.

## Smoke tests

    GITCORE VERSION
    GIT VERSION
    GIT FOO
    GIT

Expected baseline behavior:

- `GITCORE VERSION` -> `GITCORE 0.1 CMS/ZVM`, RC 0
- `GIT VERSION` -> same version, RC 0
- unknown or missing public Git command -> RC 4
