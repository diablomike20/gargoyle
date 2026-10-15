#!/usr/bin/env python3
"""Derive Belkin profile from Gargoyle 1.12 stock config with no feature removal."""
from pathlib import Path
import sys

original = Path("targets/ramips/profiles/default/config").read_text()

def replace_once(a, b):
    global original
    if original.count(a) != 1:
        sys.exit("BLOCKED: unexpected Gargoyle default profile: " + a)
    original = original.replace(a, b, 1)

replace_once("CONFIG_TARGET_ramips_rt305x=y",
             "# CONFIG_TARGET_ramips_rt305x is not set")
replace_once("# CONFIG_TARGET_ramips_rt3883 is not set",
             "CONFIG_TARGET_ramips_rt3883=y\nCONFIG_TARGET_ramips_rt3883_DEVICE_f9k1103=y")
replace_once("CONFIG_TARGET_ramips_rt305x_Default=y",
             "# CONFIG_TARGET_ramips_rt305x_Default is not set")
replace_once('CONFIG_TARGET_SUBTARGET="rt305x"', 'CONFIG_TARGET_SUBTARGET="rt3883"')
replace_once('CONFIG_TARGET_PROFILE="Default"', 'CONFIG_TARGET_PROFILE="DEVICE_f9k1103"')
replace_once("CONFIG_TARGET_ROOTFS_INITRAMFS=y",
             "# CONFIG_TARGET_ROOTFS_INITRAMFS is not set")
replace_once("# CONFIG_PACKAGE_kmod-usb-ohci is not set",
             "CONFIG_PACKAGE_kmod-usb-ohci=y")
replace_once("CONFIG_PACKAGE_kmod-usb2=m", "CONFIG_PACKAGE_kmod-usb2=y")
original += "\n# Belkin RT3091 PCI radio, device-specific driver\nCONFIG_PACKAGE_kmod-rt2800-pci=y\n"
out = Path("targets/ramips/profiles/f9k1103v1/config")
out.parent.mkdir(parents=True, exist_ok=True)
if out.exists():
    sys.exit("BLOCKED: refusing to overwrite generated profile")
out.write_text(original)
required = ["CONFIG_PACKAGE_gargoyle=y",
            "CONFIG_PACKAGE_plugin-gargoyle-email-notifications=m",
            "CONFIG_PACKAGE_plugin-gargoyle-qos=y",
            "CONFIG_PACKAGE_plugin-gargoyle-ddns=y",
            "CONFIG_PACKAGE_qos-gargoyle=y"]
for item in required:
    if item not in original:
        sys.exit("BLOCKED: missing original Gargoyle functionality " + item)
print("PASS: stock Gargoyle 1.12 package selections preserved.")
