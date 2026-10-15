#!/usr/bin/env python3
"""Fail closed on firmware-port regressions, without editing upstream Gargoyle."""
from pathlib import Path
import re
import sys

stock = Path("targets/ramips/profiles/default/config").read_text()
device = Path("targets/ramips/profiles/f9k1103v1/config").read_text()
tree = Path("downloaded/openwrt-18.06-5625f5b")

def require(ok, msg):
    if not ok:
        sys.exit("BLOCKED BY PORT PREFLIGHT: " + msg)

def gargoyle_options(text):
    return {
        m.group(1): m.group(2)
        for m in re.finditer(r"^CONFIG_PACKAGE_((?:plugin-gargoyle|gargoyle|qos-gargoyle|ddns-gargoyle)[A-Za-z0-9_-]*)=(y|m)$", text, re.M)
    }

stockopts = gargoyle_options(stock)
currentopts = gargoyle_options(device)
require(len(stockopts) > 15, "too few stock Gargoyle package options")
require(stockopts == currentopts, "Gargoyle feature selections differ from the stock Gargoyle 1.12 profile")
require("CONFIG_TARGET_ramips_rt3883_DEVICE_f9k1103=y" in device, "Belkin target unset")
require("CONFIG_TARGET_ROOTFS_SQUASHFS=y" in device, "SquashFS unset")
require("CONFIG_PACKAGE_kmod-rt2x00-pci=y" in device, "RT3091 rt2x00 PCI transport missing")
require("CONFIG_PACKAGE_kmod-rt2800-pci=y" in device, "RT3091 wireless driver missing")

dts = (tree / "target/linux/ramips/dts/F9K1103.dts").read_text()
require('model = "Belkin F9K1103 Version 1.0"' in dts, "wrong board model")
require('reg = <0x050000 0x7a0000>;' in dts, "wrong firmware flash partition")
require('reg = <0x7f0000 0x010000>;' in dts, "missing protected user-cfg partition")
for part in ("u-boot", "uboot-env", "factory", "user-cfg"):
    require(re.search(r"label = \"" + re.escape(part) + r"\";\s*reg = [^;]+;\s*read-only;", dts)
            is not None, "flash partition not protected: " + part)

recipe = (tree / "target/linux/ramips/image/rt3883.mk").read_text()
require("define Device/f9k1103" in recipe and "IMAGE_SIZE := 7808k" in recipe,
        "wrong image profile or flash size")
require("UIMAGE_NAME := N750F9K1103VB" in recipe, "incorrect uImage name")
require("KERNEL := kernel-bin | append-dtb | lzma -d16 | uImage lzma" in recipe,
        "incorrect boot envelope")
network = (tree / "target/linux/ramips/base-files/etc/board.d/02_network").read_text()
require('"5@eth0"' in network and "\tf9k1103)" in network, "LAN/WAN switch map absent")
for f in ("build.sh", "package/plugin-gargoyle-email-notifications/Makefile",
          "package/msmtp/Makefile"):
    require(Path(f).is_file(), "missing original Gargoyle file: " + f)
print("PASS: stock Gargoyle package selections and Belkin boot/flash safeguards verified.")
