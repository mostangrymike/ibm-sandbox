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

`M12PRXY EXEC` is the isolated follow-up probe using `Host: github.com`.
Keep the already-proven M11BRAW core intact.

## Native System SSL

`M12TLS4 ASSEMBLE` and related diagnostics are preserved for native z/VM
Dynamic SSL research. They are not required for the practical stunnel transport.
Do not regress the target-proven VMCF callcodes or retry certificate-validation
bypass attempts; server-certificate validation is mandatory on this path.
