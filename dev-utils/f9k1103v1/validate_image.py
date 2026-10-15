#!/usr/bin/env python3
"""Static CRC/partition/image validator, no flashing or hardware claims."""
from pathlib import Path
import hashlib
import json
import struct
import sys
import zlib

limit = 0x7a0000
images = sorted(Path("images/ramips").glob("*f9k1103*squashfs*sysupgrade.bin"))
if not images:
    sys.exit("FAIL: no F9K1103 sysupgrade image was produced")
out = Path("f9k1103v1-output")
out.mkdir(exist_ok=True)
report = []
for path in images:
    data = path.read_bytes()
    if not 64 < len(data) <= limit:
        sys.exit("FAIL: invalid firmware partition size")
    magic, hcrc, _, length, load, entry, crc = struct.unpack_from(">7I", data)
    hdr = bytearray(data[:64])
    hdr[4:8] = b"\0\0\0\0"
    if magic != 0x27051956 or zlib.crc32(hdr) & 0xffffffff != hcrc:
        sys.exit("FAIL: invalid uImage header")
    if not 0 < length <= len(data) - 64:
        sys.exit("FAIL: invalid kernel payload length")
    if zlib.crc32(data[64:64 + length]) & 0xffffffff != crc:
        sys.exit("FAIL: invalid uImage data CRC")
    if (data[29], data[31], load, entry) != (5, 3, 0x80000000, 0x80000000):
        sys.exit("FAIL: unsupported arch/compression/entry")
    if data[32:64].split(b"\0", 1)[0] != b"N750F9K1103VB":
        sys.exit("FAIL: incorrect bootloader image name")
    if data.find(b"hsqs", 64 + length) < 0:
        sys.exit("FAIL: missing SquashFS")
    (out / path.name).write_bytes(data)
    report.append(dict(file=path.name, bytes=len(data),
                       sha256=hashlib.sha256(data).hexdigest(), hardware_tested=False))
(out / "VALIDATION.json").write_text(json.dumps(report, indent=2) + "\n")
(out / "SHA256SUMS.txt").write_text(
    "".join(x["sha256"] + "  " + x["file"] + "\n" for x in report))
print(json.dumps(report, indent=2))
