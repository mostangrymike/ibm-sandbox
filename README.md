# IBM Sandbox

Native IBM platform development experiments.

## CMS Git client

The current project is a native Git client for CMS/z/VM 6.3 Evaluation Edition, using only development facilities already present on the system.

Current proven toolchain:

- REXX command layer (`GIT EXEC`)
- Assembler XF native module (`GITCORE MODULE`)
- CMS preferred macros through `DMSGPI`
- `ASSEMBLE` -> `TEXT` -> `LOAD` -> `GENMOD` -> `MODULE`
- REXX -> CMS MODULE invocation and return-code handling
- EPLIST command argument handling

See `docs/BUILD.md` and `docs/STATUS.md`.
