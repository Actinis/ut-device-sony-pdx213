# Mobile data

Enable mobile data using the standard Ubuntu Touch cellular settings or network
indicator and select the intended SIM. The connectivity service persists this
choice; NetworkManager activation alone does not change that setting.

On the XQ-BT52 prototype, the existing operator-provisioned internet context
activated successfully. DNS and HTTPS through the cellular interface passed with
Wi-Fi disabled. The owner confirmed browser access, recovery after switching
Wi-Fi, and operation after reboot once mobile data was enabled through the
standard connectivity-service API.

If NetworkManager connects during boot and the session later disconnects it,
check the saved mobile-data switch before changing the APN or adding startup
services. A disabled switch intentionally takes precedence over connection
autoconnect. No forced activation service or user-specific SIM configuration is
included in the port.

These results qualify the installed prototype. Fresh-install SIM provisioning,
other operators, roaming, SIM2, IPv6-only data and hotspot cellular upstream
remain unqualified. New images must be tested separately; source and CI checks
do not establish runtime behavior on a freshly installed phone.
