# Clean Belkin F9K1103 v1 Gargoyle 1.12 port

Based on pristine Gargoyle branch 1.12 and its own pinned official OpenWrt 18.06
commit 5625f5bc36954d644cb80adf8de47854c65d91c3.

Original Gargoyle package files, build.sh, UI, QoS, DDNS, email notifications,
netfilter scripts and generic patches are UNMODIFIED. CI tests this.
F9K1103 hardware is staged only into the temporary official OpenWrt tree.
The DTS is copied exactly from the existing Belkin 17.01.5 donor repository:
diablomike20/Belkin-F9K1103-Firmware/firmware/f9k1103-lede-17.01.5/F9K1103.dts.

The device profile is generated in CI from the original Gargoyle 1.12
ramips/default config with all Gargoyle package selections preserved.
Only board target, initramfs selection and required device drivers differ.
Modular packages are not claimed to fit inside 8MB on flash.

Hardware: RTL8367R-VB, RT3883/RT3091, U-Boot name N750F9K1103VB,
firmware partition 0x50000..0x7f0000 (7808 KiB).
Do not overwrite bootloader, env, factory EEPROM or user-cfg.

Known blocker from previous experimental builds: original Gargoyle 1.12
msmtp and email-notifications packages may cause recursive Kconfig dependencies.
DO NOT patch or remove either package without explicit review/approval.
Full build may also fail on historical netfilter/hostapd patch compatibility.

Original Gargoyle 1.12 has NO Hungarian language pack in the checked repo.
Build logs and static validation are required before any image can be shared.
Hardware runtime NOT TESTED; never flash without independent verification.
