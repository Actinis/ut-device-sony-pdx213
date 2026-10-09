# Wi-Fi PMF key installation repair

The Sony 4.19 kernel's beacon-protection backport in
`net/wireless/util.c:cfg80211_valid_key_idx` used two independent `if`
statements. For a device supporting IGTK but not beacon protection, the second
statement reset the maximum group-key index from 5 to 3. Installing or deleting
IGTK index 4 therefore returned `-EINVAL` before reaching the WLAN driver.
NetworkManager interpreted repeated association failures as a reason to ask for
the already saved password again.

`tools/fix_cfg80211_pmf.py` restores one mutually exclusive capability chain:
pairwise indices 0–3, beacon-protection group indices 0–7, IGTK group indices
0–5, otherwise group indices 0–3. Cipher, length, sequence and group/pairwise
validation remain intact. No PMF capability is disabled and no failed key
installation is ignored. The regular kernel build applies the fix idempotently.

`tools/test_cfg80211_pmf.py` compiles the actual function from the kernel source
with capability stubs and checks 80 combinations of pairwise/group, IGTK,
beacon support, negative indices and indices 0–8. The original code fails at
group index 4 with IGTK enabled and beacon protection absent; the repair passes
all cases. This is host evidence; on-device PMF qualification is recorded below
only after flashing the repaired kernel.

The earlier per-profile PMF-disable workaround was removed before the repaired
kernel test. It is not part of the release configuration.

## Device qualification

On XQ-BT52, boot image `boot-ubuntu-pmf-v13.img` contains the repaired kernel
and a byte-identical v12 release ramdisk. After flashing only boot_a, the saved
5 GHz network automatically connected with `key_mgmt=SAE`, `pmf=1`,
`mgmt_group_cipher=BIP` and `wpa_state=COMPLETED`. Three explicit reconnects with
NetworkManager PMF set to required repeated those results without requesting a
password. HTTPS fetched through the Wi-Fi source address succeeded. The profile
was then restored to the default automatic PMF policy, not disabled.
System failed units were empty and AppArmor remained enabled.
Evidence: `/hdd1/ut-xperia/evidence/wifi-pmf-v13-reconnect.txt`.
Long-duration operation and other routers/cipher suites remain unqualified.
