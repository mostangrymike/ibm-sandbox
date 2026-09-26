# CMS/z/VM build and transfer workflow

## Canonical workflow

GitHub `main` is canonical. Edit there first. On the Mac, work from the local
`ibm-sandbox/src` directory, pull, then transfer only the files needed for the
next target gate.

For EXEC files:

    git pull
    ./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/NAME.EXEC

For assembler source:

    git pull
    ./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/NAME.ASSEMBLE

The established helper drives the single interactive c3270 instance through its
local script port and uses DFT file transfer. c3270 DFT 2048 is target-proven.
An absolute LocalFile path is preferred because c3270 resolves relative paths
from its own launch directory.

CMS filenames and filetypes are each limited to eight characters. Check this
before creating a target file.

## CMS assembler rules

`PROFILE EXEC` globalizes the preferred CMS macro library:

    GLOBAL MACLIB DMSGPI

Build a native module only after assembly succeeds:

    ASSEMBLE NAME
    LOAD NAME
    GENMOD NAME

Do not replace a known-good MODULE after an assembly failure. For fixed-card
assembler, keep ordinary source through column 71 unless an intentional
continuation is used. Assembler symbols must be at most eight characters.
SS-format MVC/XC explicit lengths must not exceed 256 bytes.

## CMS networking

Current routed TAP configuration:

- CMS/z/VM OSA1: `192.168.200.2/24`
- EC2 Debian tap0: `192.168.200.1/24`
- CMS default gateway: `192.168.200.1`
- DNS: `8.8.8.8`
- EC2 outbound NAT: MASQUERADE through ens5

MAINT's profile links TCPMAINT 592 read-only and accesses it as T so TCP/IP
client commands remain available.

## HTTPS bridge

The practical GitHub HTTPS path uses stunnel on EC2. The listener is bound only
to the TAP address:

    192.168.200.1:8443

Its outbound side connects to `github.com:443` with certificate-chain
validation, hostname validation, SNI, and TLS 1.2 or newer.

The EC2-local plaintext-to-stunnel test returned GitHub HTTP/1.1 200. The CMS
M11BRAW test then connected to `192.168.200.1:8443`, sent exact raw HTTP
bytes, received 176 bytes, saw wire prefix
`485454502F312E3120333031204D6F76` (`HTTP/1.1 301 Mov`), and passed its
bounded binary-safe socket gate. This proves CMS -> TAP -> stunnel -> verified
TLS -> GitHub -> CMS.

`M12PRXY EXEC` is the isolated `Host: github.com` probe. Live Git smart-HTTP
is now proven through `M12GDISC`, `GIT12CHK`, `M12JPOST`, and `M12KPACK`.
The captured live PACK is 340,027 bytes with 1,808 objects and verified SHA-1
`8C92E274ECA84B797F8925A6082915DD6CCDE196`. Keep the already-proven M11BRAW
core intact.

## Native System SSL

`M12TLS4 ASSEMBLE` and related diagnostics are preserved for native z/VM
Dynamic SSL research. They are not required for the practical stunnel transport.
Do not regress the target-proven VMCF callcodes or retry certificate-validation
bypass attempts; server-certificate validation is mandatory on this path.

## GCCCMS native build checkpoint (2026-09-26)

The original `GITCLNK EXEC` proved the compiler/linker path through
`GITCWALK` and `GITCIDX`. The canonical replacement is now the
neutral `CMSCLNK EXEC` (7-character CMS name), intended to live on
the existing GCCCMS F disk. The default `NAPI` mode retains the
exact required GCCE, Assembler XF, GITCAPI/GITINFA and PDPCLIB
linkage. Optional `PLAIN` builds C modules that do not call the
native inflater (such as `GITCIDX`), without assembling those
adapters. Both modes must be proven on actual CMS before retiring
the previous A-disk copy of `GITCLNK`.

## Installing the build EXEC on the GCC F disk

GitHub `src/CMSCLNK.EXEC` is canonical. Upload through the
existing *single* c3270 file-transfer session; the uploader places
it on CMS A first. On the Mac from `ibm-sandbox/src`:

```sh
git pull
./cms-upload.sh /Users/mikewommack/ibm-sandbox/src/CMSCLNK.EXEC
```

On CMS, **first** check whether the GCC F disk is read/write:

```text
QUERY DISK F
```

If it reports `R/W`, copy the new EXEC to F and confirm it exists:

```text
COPYFILE CMSCLNK EXEC A CMSCLNK EXEC F
STATE CMSCLNK EXEC F
```

For an F disk reporting `R/O`, **do not attempt a destructive
remount or modify GCC installation**. The A-disk copy is usable
temporarily; installing on F requires authorized read/write access
to that minidisk. Never assume the F disk can be written merely
because GCC is installed there.

Once the copy to F succeeds and is verified, remove **only the
new A-disk copy** (`ERASE CMSCLNK EXEC A`) to ensure subsequent
`CMSCLNK` commands resolve to F, leaving the proven
`GITCLNK EXEC A` available until the new build is CMS-validated.
The runtime build uses source and generated assembler on A; moving
the tool itself to F does **not** move the Git-specific adapter
sources from A or overwrite working modules.

Usage once F is ready:

```text
CMSCLNK GITCWALK
CMSCLNK GITCIDX PLAIN
```

The default `NAPI` mode uses the original target-proven sequence.
`PLAIN` is new and needs one real CMS link test. Avoid needless
rebuilding of the working `GITCWALK MODULE` while validating
installation; begin with `CMSCLNK GITCIDX PLAIN` after copying
the new tool to F. Once its module builds and runs normally,
`GITCLNK EXEC A` can be retired. IBM's `QUERY DISK F` reports
`R/W` or `R/O` and `COPYFILE` supports copying across accessed
minidisks; a file is only writable on a disk accessed `R/W`.

## Confirmed GCC F-disk access (2026-09-26)

User's live `Q DISK` shows `GCCLIB` at VDEV `29D`, accessed as
**F R/W**, 20 cylinders, 2,055 free 4K blocks, 38 files. Therefore
`CMSCLNK EXEC` can be copied directly from A to F; no relink,
reaccess, remount, or permission change is required. Do not claim
installation is complete until `STATE CMSCLNK EXEC F` and the new
CMSCLNK PLAIN build succeed on CMS. Existing GITCLNK EXEC A is
rollback until that test. The only necessary F-disk installation
commands after Mac upload are:

```text
COPYFILE CMSCLNK EXEC A CMSCLNK EXEC F
STATE CMSCLNK EXEC F
ERASE CMSCLNK EXEC A
CMSCLNK GITCIDX PLAIN
```

Run `ERASE` only after confirming the preceding `COPYFILE` and
`STATE` succeeded; never erase the original GITCLNK EXEC A at
this checkpoint. Once the new compile succeeds, run the separate
AUDIT/SBUILD/SCHECK/SGET gate in docs/NATIVE_INDEX.md.

For historic compile fixture results, see `docs/STATUS.md`;
for the native object-store next gate, see `docs/NATIVE_INDEX.md`.
