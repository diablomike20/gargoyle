#!/usr/bin/env python3
"""Device-only overlay on pinned OFFICIAL OpenWrt 18.06. Gargoyle files untouched."""
from pathlib import Path
import shutil
import sys

if len(sys.argv) != 2:
    sys.exit("Usage: stage_openwrt.py <clean-OpenWrt-tree>")
root = Path(sys.argv[1]).resolve()
here = Path(__file__).resolve().parent

def add(path, anchor, insertion):
    target = root / path
    old = target.read_text()
    if old.count(anchor) != 1 or insertion.strip() in old:
        sys.exit("BLOCKED: mismatched source anchor or already applied: " + path)
    target.write_text(old.replace(anchor, insertion + anchor, 1))

add("target/linux/ramips/image/rt3883.mk", "define Device/tew-691gr\n",
    """define Device/f9k1103
  DTS := F9K1103
  BLOCKSIZE := 64k
  IMAGE_SIZE := 7808k
  UIMAGE_NAME := N750F9K1103VB
  KERNEL := kernel-bin | append-dtb | lzma -d16 | uImage lzma
  DEVICE_TITLE := Belkin F9K1103 v1
  DEVICE_PACKAGES := kmod-usb-core kmod-usb-ohci kmod-usb2 swconfig
endef
TARGET_DEVICES += f9k1103

""")
path = "target/linux/ramips/base-files/etc/board.d/02_network"
add(path, "\trt-n56u)\n\t\tucidef_add_switch",
    '\tf9k1103)\n\t\tucidef_add_switch "switch0" \\\n'
    '\t\t\t"0:lan" "1:lan" "2:lan" "3:lan" "4:wan" "5@eth0"\n'
    '\t\t;;\n')
add(path, "\trt-n56u)\n\t\tlan_mac=$(cat /sys/class/net/eth0/address)",
    '\tf9k1103)\n'
    '\t\twan_mac=$(mtd_get_mac_ascii uboot-env HW_WAN_MAC)\n'
    '\t\tlan_mac=$(mtd_get_mac_ascii uboot-env HW_LAN_MAC)\n'
    '\t\t;;\n')
add("target/linux/ramips/base-files/lib/ramips.sh", '\t*"RT-N56U")\n',
    '\t*"Belkin F9K1103"*)\n\t\tname="f9k1103"\n\t\t;;\n')
add("target/linux/ramips/base-files/lib/upgrade/platform.sh",
    "\trt-n56u|\\\n", "\tf9k1103|\\\n")
dts = root / "target/linux/ramips/dts/F9K1103.dts"
if dts.exists():
    sys.exit("BLOCKED: refusing DTS overwrite")
shutil.copyfile(here / "F9K1103.dts", dts)
assert "reg = <0x050000 0x7a0000>" in dts.read_text()
print("PASS: staged ONLY the F9K1103 device port in official OpenWrt.")
