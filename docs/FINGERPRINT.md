# Fingerprint on XQ-BT52

Sony Android 11 fingerprint HAL is used by the distribution biometryd Android backend. Enrollment and lock-screen unlock were physically confirmed by the owner. No fingerprint templates or private device data are shipped.

The port retries biometryd initialization exit status 78 for up to 40 seconds. Other exits retain their normal meaning. The service retains Type=dbus: initial readiness requires ownership of the real biometryd bus name. LightDM optionally waits for this initial startup, bounded by a 45-second service timeout; a failed scanner must not block PIN/password login. Subsequent failures use systemd restart with a five-second delay. This ordering prevents Lomiri from initially caching an unavailable backend. Runtime recovery of an already-running Lomiri after a later daemon failure remains unqualified.

Set a PIN or password, enroll a finger, and enable fingerprint identification in the normal security settings. Enrollment alone does not enable unlocking. The installed Lomiri starts identification only while the display is on. Unlock once with PIN/password after first login before testing fingerprint screen-lock unlock.

After a device reboot, biometryd became active before LightDM, the enabled identification setting persisted, and Lomiri created an identification operation without manual service restart. The owner confirmed unlock with the enrolled finger after this reboot and rejection of a different, unenrolled finger. Suspend and long-duration behavior remain unqualified. Authentication policy and lockout rules are unchanged.
