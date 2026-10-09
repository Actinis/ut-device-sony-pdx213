# GNSS on pdx213 Noble

The adaptation uses GNSS and AGnss HIDL 2.0 where available, with older interface
fallbacks. Callback objects retain their HIDL lifetime. The legacy satellite
API reports only GPS PRNs 1–32 using PRN-based masks; other constellations can
contribute to fixes but are not represented by that legacy satellite list.

SUPL assistance is optional and disabled in the distributed configuration.
To opt in, uncomment `UTXPERIA_GNSS_SUPL_HOST=supl.google.com` in
`/etc/utxperia/gnss-assistance.conf`, then restart `lomiri-location-service`. If doing this inside an active graphical
session, also restart that session's `lomiri-location-service-trust-stored.service`
(or its Wayland variant) and reopen the browser: the current trust-store agent
can fail to register against a restarted service. Do not bypass app permissions.
This contacts the selected assistance server and shares network/location data;
normal application permission checks still apply. It requires one already active
IPv4 internet context and uses its current APN. It does not enable mobile data,
activate a SIM, handle emergency/IMS SUPL, alter modem NV settings or disable TLS.
No Wi-Fi-only assistance or IPv6-only connection is currently qualified.
Without assistance, GNSS reception and time to first fix need outdoor qualification.

On the tested XQ-BT52, real GNSS fixes and Google Maps in Morph were confirmed
with assistance. Three automated Maps requests with the permanently installed
libraries returned fresh positions (3–12 ms age) while GNSS callbacks continued.
Reported indoor accuracy was 131–254 m; this is not outdoor accuracy evidence.
The GNSS component also built in an isolated source copy against glibc extracted
directly from the locked rootfs, matching the installed library hashes.
A user-performed reboot was also checked: the permanent libraries and SUPL
configuration loaded automatically, permission registration succeeded without
manual restarts, and two Maps requests returned fresh fixes (3–14 ms age,
58–75 m reported indoor accuracy), with fresh GNSS callbacks.
This does not establish outdoor accuracy, cold start without assistance
or suspend/resume qualification. After changing/restarting the location service, reload
the application's position request; stale sessions can remain in an open browser.
