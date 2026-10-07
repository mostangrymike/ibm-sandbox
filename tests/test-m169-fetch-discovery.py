#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
src = (root / "src" / "GITFETCH.EXEC").read_text()

for number, line in enumerate(src.splitlines(), 1):
    assert len(line) <= 80, (number, len(line))

for needle in (
    "ep=bytepos('3B',ch)",
    "cv=x2d(substr(ch,cj,2))",
    "if cv>=48 & cv<=57 then cn=cv-48",
    "else if cv>=65 & cv<=70 then cn=cv-55",
    "else if cv>=97 & cv<=102 then cn=cv-87",
    "cneed=cneed*16+cn",
):
    assert needle in src

# REXX internal routines share variables unless isolated explicitly.
# Keep HTTP and pkt streaming scratch variables disjoint.
chunk = src[src.index("chunkfeed:"):src.index("pktfeed:")]
pkt = src[src.index("pktfeed:"):src.index("processpkt:")]
for needle in ("parse arg cwork","cavail=length(cwork)%2","ctake=cneed",
               "cpiece=left(cwork,ctake*2)","cneed=cneed-ctake"):
    assert needle in chunk
for forbidden in ("parse arg work","avail=length(work)%2","take=cneed"):
    assert forbidden not in chunk
for needle in ("parse arg pwork","pavail=length(pwork)%2","ptake=pneed",
               "ppay=ppay||left(pwork,ptake*2)","pneed=pneed-ptake"):
    assert needle in pkt
for forbidden in ("parse arg work","avail=length(work)%2","take=pneed"):
    assert forbidden not in pkt

for forbidden in (
    "M11BODY DATA A",
    "M12BODY DATA A",
    "GITPBUF PACK A",
    "M11META DATA A",
    "M12CMETA DATA A",
):
    assert forbidden not in src

for needle in (
    "GITFETCH DISCOVER bridge port host repo branch",
    "GET '||path||' HTTP/1.1",
    "application/x-git-upload-pack-advertisement",
    "Socket('Recv',s,256)",
    "total>4194304",
    "TRANSFER-ENCODING:",
    "CHUNKED",
    "pneed>4096",
    "refs>10000",
    "SIDE-BAND-64K",
    "OFS-DELTA",
    "targetcount\\=1",
    "M169 FETCH DISCOVERY PASS",
    "GITFETCH: discovery failed at",
    "GITFETCH: states",
    "GITFETCH: counts",
    "GITFETCH: connect target",
    "GITFETCH: connect RC",
    "GITFETCH: post-flush bytes",
):
    assert needle in src

# Both conversion routines must carry a complete 256-byte table.
blocks = re.findall(
    r"e2a='([0-9A-F]+)'((?:\n e2a=e2a\|\|'[0-9A-F]+';?)+)",
    src,
)
assert len(blocks) == 2
tables = []
for first, rest in blocks:
    parts = [first] + re.findall(r"'([0-9A-F]+)'", rest)
    table = "".join(parts)
    assert len(table) == 512
    tables.append(table)
assert tables[0] == tables[1]

def pkt(payload: bytes) -> bytes:
    return f"{len(payload)+4:04x}".encode("ascii") + payload

oid_head = "1" * 40
oid_main = "2" * 40
service = pkt(b"# service=git-upload-pack\n") + b"0000"
caps = (
    b"multi_ack thin-pack side-band side-band-64k ofs-delta "
    b"agent=git/2.47.3 symref=HEAD:refs/heads/main"
)
adv = service
adv += pkt(oid_head.encode() + b" HEAD\x00" + caps + b"\n")
adv += pkt(oid_main.encode() + b" refs/heads/main\n")
adv += b"0000"

# Encode the advertisement as deliberately irregular HTTP chunks.
sizes = [3, 1, 17, 5, 29, 2, 11, 7, 64]
chunks = []
pos = 0
si = 0
while pos < len(adv):
    size = min(sizes[si % len(sizes)], len(adv) - pos)
    piece = adv[pos:pos+size]
    chunks.append(f"{size:x}\r\n".encode() + piece + b"\r\n")
    pos += size
    si += 1
body = b"".join(chunks) + b"0\r\n\r\n"
response = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: application/x-git-upload-pack-advertisement\r\n"
    b"Transfer-Encoding: chunked\r\n"
    b"Connection: close\r\n\r\n" + body
)

# Independent model: HTTP framing + chunk decode.
head, encoded = response.split(b"\r\n\r\n", 1)
assert head.startswith(b"HTTP/1.1 200")
assert b"application/x-git-upload-pack-advertisement" in head
assert b"Transfer-Encoding: chunked" in head

decoded = bytearray()
at = 0
while True:
    end = encoded.index(b"\r\n", at)
    size = int(encoded[at:end].split(b";", 1)[0], 16)
    at = end + 2
    if size == 0:
        break
    decoded.extend(encoded[at:at+size])
    at += size
    assert encoded[at:at+2] == b"\r\n"
    at += 2
assert bytes(decoded) == adv

# Independent pkt-line advertisement model.
at = 0
stage = "service"
target = "refs/heads/main"
target_oid = None
refs = 0
caps_seen = None
while at < len(decoded):
    n = int(decoded[at:at+4], 16)
    at += 4
    if n == 0:
        if stage == "service-flush":
            stage = "refs"
            continue
        if stage == "refs":
            stage = "done"
            break
        raise AssertionError(stage)
    payload = bytes(decoded[at:at+n-4])
    at += n - 4
    if stage == "service":
        assert payload == b"# service=git-upload-pack\n"
        stage = "service-flush"
        continue
    assert stage == "refs"
    main, sep, cap = payload.partition(b"\x00")
    main = main.rstrip(b"\n")
    oid, ref = main.decode("ascii").split()
    assert len(oid) == 40
    refs += 1
    if sep:
        assert caps_seen is None
        caps_seen = cap.rstrip(b"\n").decode("ascii").split()
    if ref == target:
        assert target_oid is None
        target_oid = oid.upper()

assert stage == "done"
assert refs == 2
assert target_oid == oid_main
assert caps_seen is not None
assert "side-band-64k" in caps_seen
assert "ofs-delta" in caps_seen

# Fragment the entire response at every small boundary; concatenation must
# preserve the exact wire stream modeled above.
for width in range(1, 33):
    pieces = [response[i:i+width] for i in range(0, len(response), width)]
    assert b"".join(pieces) == response

print("M169 GENERALIZED FETCH DISCOVERY HOST MODEL PASSED")
