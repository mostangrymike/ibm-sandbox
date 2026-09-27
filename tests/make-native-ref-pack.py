#!/usr/bin/env python3
"""Write bounded CMS text-record PACK v2 native REF_DELTA fixtures."""
import hashlib
import pathlib
import sys
import zlib


def oid(blob):
    return hashlib.sha1(b"blob " + str(len(blob)).encode("ascii")
                        + b"\x00" + blob).digest()


def header(kind, size):
    first = (kind << 4) | (size & 15)
    size >>= 4
    out = bytearray()
    while size:
        out.append(first | 128)
        first = size & 127
        size >>= 7
    out.append(first)
    return bytes(out)


def ordinary(body):
    return header(3, len(body)) + zlib.compress(body)


def refdelta(base, delta):
    return header(7, len(delta)) + base + zlib.compress(delta)


def make_pack(entries):
    data = b"PACK" + (2).to_bytes(4, "big")
    data += len(entries).to_bytes(4, "big") + b"".join(entries)
    return data + hashlib.sha1(data).digest()


def write_records(path, data):
    with path.open("w", encoding="ascii", newline="\n") as out:
        for at in range(0, len(data), 32):
            out.write(data[at:at + 32].hex().upper() + "\n")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: make-native-ref-pack.py OUTPUT_DIRECTORY")
    folder = pathlib.Path(sys.argv[1])
    folder.mkdir(parents=True, exist_ok=True)
    delta1 = bytes((3, 4, 0x90, 3, 1, ord("d")))
    delta2 = bytes((4, 5, 0x90, 4, 1, ord("e")))
    first = ordinary(b"abc")
    second = refdelta(oid(b"abc"), delta1)
    third = refdelta(oid(b"abcd"), delta2)
    good = make_pack((first, second, third))
    unknown = bytearray(oid(b"abc"))
    unknown[0] ^= 1
    bad = make_pack((first, refdelta(unknown, delta1), third))
    forward = make_pack((second, first))
    wrong_size = make_pack((first, refdelta(oid(b"abc"),
                            bytes((4, 4, 0x90, 3, 1, ord("d"))))))
    forward_chain = make_pack((refdelta(oid(b"abcd"), delta2),
                               second, first))
    external = make_pack((second,))
    external_missing = make_pack((refdelta(oid(b"missing"), delta1),))
    # Copy the real first 270-byte commit through a thin REF delta.
    # Its canonical OID was independently verified on target.
    real_commit = bytes.fromhex("00D8D63229305230C8D37F884CE87F9E1A89468C")
    real_copy = bytes((0x8e, 0x02, 0x8e, 0x02,
                       0xb0, 0x0e, 0x01))
    external_real = make_pack((refdelta(real_commit, real_copy),))
    wrong_sha = good[:-1] + bytes((good[-1] ^ 1,))
    for name, pack in (
        ("REFPACK.PACK", good),
        ("REFBAD.PACK", bad),
        ("REFFWD.PACK", forward),
        ("REFSIZE.PACK", wrong_size),
        ("REFSHA.PACK", wrong_sha),
        ("XPACK.PACK", external),
        ("XBAD.PACK", external_missing),
        ("FCHAIN.PACK", forward_chain),
        ("XREAL.PACK", external_real),
    ):
        write_records(folder / name, pack)
        if name == "REFPACK.PACK":
            (folder / "REFPACK.bin").write_bytes(pack)
        if name == "FCHAIN.PACK":
            (folder / "FCHAIN.bin").write_bytes(pack)
        print(name, len(pack), "bytes")
    abc_hex = oid(b"abc").hex().upper()
    (folder / "EXTBASE.DATA").write_text(
        "OBJ 1 3 3 " + abc_hex + "\n616263\n", encoding="ascii"
    )
    (folder / "EXTBAD.DATA").write_text(
        "OBJ 1 3 3 " + abc_hex + "\n616264\n", encoding="ascii"
    )
    (folder / "EXTMISS.DATA").write_text(
        "OBJ 1 3 5 " + oid(b"other").hex().upper()
        + "\n6F74686572\n", encoding="ascii"
    )
    (folder / "EXTMULT.DATA").write_text(
        "OBJ 1 3 5 " + oid(b"other").hex().upper()
        + "\n6F74686572\nOBJ 2 3 3 " + abc_hex
        + "\n616263\n", encoding="ascii"
    )
    (folder / "EXTDUP.DATA").write_text(
        "OBJ 1 3 3 " + abc_hex + "\n616263\n"
        + "OBJ 2 3 3 " + abc_hex + "\n616263\n",
        encoding="ascii"
    )
    print("OID ABC", oid(b"abc").hex().upper())
    print("OID ABCD", oid(b"abcd").hex().upper())
    print("OID ABCDE", oid(b"abcde").hex().upper())


if __name__ == "__main__":
    main()
