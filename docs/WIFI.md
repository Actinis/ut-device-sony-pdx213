# Wi-Fi PMF support

The kernel source includes the cfg80211 IGTK index-validation repair. Group
indices 4/5 are valid for IGTK-capable devices without beacon protection;
pairwise and unsupported-cipher limits remain enforced. No failed key installation
is ignored and PMF is not disabled.

The kernel CI test compiles the actual validator and covers 80 capability/index
combinations. On the XQ-BT52 prototype, the saved 5 GHz network automatically
connected with WPA3/SAE, PMF and BIP. Three explicit reconnects with PMF required
passed without password entry, and HTTPS through the WLAN source address worked.
The saved profile uses the standard automatic PMF policy. Long-duration use,
other routers and other cipher suites remain unqualified.
