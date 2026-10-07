#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
g = (root / "src" / "GIT.EXEC").read_text()
v = (root / "src" / "GITVREF.EXEC").read_text()
disc = (root / "src" / "GITFETCH.EXEC").read_text()
post = (root / "src" / "GITPOST.EXEC").read_text()
chk = (root / "src" / "M170CHK.EXEC").read_text()

gm = re.search(r"GIT EXEC LEVEL M(\d+)", g)
vm = re.search(r"GITVREF EXEC LEVEL M(\d+)", v)
assert gm and vm and gm.group(1) == vm.group(1)
assert int(gm.group(1)) >= 170

for path in (
    root / "src" / "GIT.EXEC",
    root / "src" / "GITVREF.EXEC",
    root / "src" / "GITFETCH.EXEC",
    root / "src" / "GITPOST.EXEC",
    root / "src" / "M170CHK.EXEC",
):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        assert len(line) <= 80, (path.name, number, len(line))

assert "FETCH OID' targetoid" in disc
assert "EXEC GITPOST POST" in g
for forbidden in (
    "M11BODY DATA A",
    "M12BODY DATA A",
    "GITPBUF PACK A",
    "GITPMETA PACK A",
):
    assert forbidden not in post

for needle in (
    "wantoid=translate(oid,'abcdef','ABCDEF')",
    "side-band-64k ofs-delta",
    "Content-Type: application/x-git-upload-pack-request",
    "Accept: application/x-git-upload-pack-result",
    "Content-Length: '||clen",
    "Socket('Recv',s,256)",
    "total>16777216",
    "pneed>65516",
    "ppay\\='4E414B0A'",
    "pband='03'",
    "left(packhead,8)\\='5041434B'",
    "M170 FETCH POST PASS",
):
    assert needle in post

# HTTP and pkt streaming scratch state must remain disjoint.
chunk = post[post.index("chunkfeed:"):post.index("pktfeed:")]
pkt = post[post.index("pktfeed:"):post.index("pktlen:")]
for needle in ("parse arg cwork", "ctake=cneed", "cneed=cneed-ctake"):
    assert needle in chunk
for needle in ("parse arg pwork", "ptake=pneed", "pneed=pneed-ptake"):
    assert needle in pkt

# Exact minimal upload-pack request body used by the target-proven M12 path,
# now generated dynamically from the discovered OID.
oid = "ABCDEF0123456789ABCDEF0123456789ABCDEF01"
wire_oid = oid.lower()
want = f"want {wire_oid} side-band-64k ofs-delta\n".encode("ascii")
want_pkt = f"{len(want)+4:04x}".encode("ascii") + want
body = want_pkt + b"0000" + b"0009done\n"
assert want_pkt[:4] == b"004a"
assert len(body) == 87
assert wire_oid.encode("ascii") in body
assert oid.encode("ascii") not in body

# Independent response model: NAK followed by side-band channel 1 PACK bytes.
pack = b"PACK" + (2).to_bytes(4, "big") + (3).to_bytes(4, "big")
pack += b"fixture-payload"
nak = b"0008NAK\n"
side_payload = b"\x01" + pack
side = f"{len(side_payload)+4:04x}".encode("ascii") + side_payload
entity = nak + side + b"0000"
assert entity[:8] == b"0008NAK\n"
assert side_payload[1:5] == b"PACK"
assert int.from_bytes(side_payload[5:9], "big") == 2
assert int.from_bytes(side_payload[9:13], "big") == 3

# Dynamic composition gate must use discovery output, never a fixed SHA-1.
assert "PIPE CMS' cmd '| STEM d.'" in chk
assert "M170 LIVE OID" in chk
assert "EXEC GIT FETCH-POST" in chk
assert "M170 DYNAMIC WANT MATCH PASS" in chk
for old in (
    "C6E42C8EFC3BFC1C7331BEA300FFE94765861033",
    "8C92E274ECA84B797F8925A6082915DD6CCDE196",
):
    assert old not in chk
    assert old not in post

print("M170 DYNAMIC UPLOAD-PACK POST HOST MODEL PASSED")
