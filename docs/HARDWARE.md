# XQ-BT52 hardware qualification

Ubuntu Touch 24.04 Noble, native Android 11 adaptation and Sony 4.19 kernel.
Results are from the working XQ-BT52 prototype, not from a newly flashed source-import build. No raw private logs or recordings are published. Other variants remain unqualified.

| Component | Result and evidence |
| --- | --- |
| Display / GPU / touch | Accelerated Lomiri, Adreno 619, 1080×2520; Settings/browser/OpenStore and touch calculation captured in `evidence/`. |
| Wi-Fi station | WPA2/CCMP 2.4 GHz association, DHCP, HTTPS and screen-off/on passed. The kernel repairs Sony cfg80211's IGTK index-validation regression. The saved 5 GHz network automatically connected using WPA3/SAE with PMF and BIP; three reconnects with PMF required and HTTPS through wlan0 passed without password prompts. Automatic PMF policy is enabled. See WIFI.md. Long-duration use and other routers/cipher suites remain unqualified. |
| Wi-Fi hotspot | Real host client on 2.4 GHz and 5 GHz channel 36 (5180 MHz), DHCP and 3/3 successful pings in each test. Mobile-data upstream through the hotspot remains untested. |
| Speaker / microphones | Generated 1 kHz tone played through phone speaker and recorded by both microphone routes. Peak tone amplitudes ~3025 and ~463 vs low background. Raw recordings deleted; metrics retained. |
| Main / front cameras | Stock `multiCameraEnable=FALSE`: real JPEG files saved from both cameras, switching tested. Native provider remained alive in the successful stock-mode test. |
| Video | Sony CamX partial-initialization cleanup repair: main-camera H.264 1080×1080 + stereo AAC 48 kHz clips of 69.781 s, 89.728 s and 11.840 s; front-camera 1920×1080 clip of 69.654 s. Every clip passed complete strict ffmpeg decoding. Main/front JPEG capture and switching followed recording stops; provider PID 1349 stayed unchanged with an empty crash buffer. See CAMERA.md and evidence/camera-guard-suite.json. Other codecs and longer sessions remain untested. |
| Extra rear lenses | Experimental TRUE mode exposes three rear cameras + front. Front capture/switching reproduces vendor provider abort (`pthread_mutex_lock` on destroyed ResultBatcher mutex). Reverted; extra lenses are not enabled in the installed system. Increasing result wait or disabling offline noise reprocessing did not make this mode reliable. |
| MTP | Legacy `mtp.gs0` alongside RNDIS is configured 90 s after boot. Automatic cold-start succeeded; exact-target libmtp probe uploaded, downloaded, compared and deleted its synthetic object. Normal lock-screen restrictions remain. |
| Accelerometer / gyro / magnetometer / compass / rotation | Live SensorFW readings, valid timestamps and stream data. Orientation is a derived sensor. Calibration, motion accuracy and real-world compass heading are untested. |
| Proximity | Live non-wakeup HAL data, SensorFW reports 5 cm with a valid timestamp. A covered/uncovered physical test and call-related screen blanking remain untested. |
| Ambient light / auto brightness | HAL lists stk_stk3a5x light sensors and emits events. Repowerd uses ordered/preloaded SensorFW startup. Stationary dark readings are zero; controlled changes in illumination and adaptive brightness are not yet qualified. |
| Step counter | Qualcomm pedometer type 19 is present and activates successfully. Enabled in SensorFW; stationary zero steps does not prove walking/count accuracy. |
| Vibration | HFD 150 ms request activated the vibrator sysfs state and automatically stopped. |
| Notification LED | HFD color/state control exercised; green brightness reached 255 and returned to zero. |
| Flashlight | Deviceinfo selects explicit Qualcomm torch/switch paths with narrowly scoped session write permissions. Standard Ayatana `flashlight` action sets torch brightness 255 / switch 1, then switch 0. |
| GNSS | 30 s direct platform-api/HIDL test: started/stopped successfully, 197 NMEA callbacks, 29 satellite callbacks, maximum 1 visible satellite; no indoor position fix. Normal app permission flow, fix accuracy and outdoors reception remain untested. |
| NFC | Native HAL and NFC daemon initialized; RF Initiator polling reports Powered/Polling true. No tag read/write test available. StopPollLoop is advertised but returns not implemented. |
| Bluetooth | Exact-peer bonding and encryption completed. Three 44-byte L2CAP echo requests returned (0% loss). Remote services resolve on the phone after scoped trust; host SDP/profile resolution remains unreliable. aptX HD A2DP transmission now confirmed with the computer as receiver: 44.1 kHz stereo, 660,884 captured frames, 430,973 nonzero frames, detected 1 kHz tone amplitude ~1983. The PipeWire input node needed an explicit capture link. SBC, HFP calls and actual headset compatibility remain unqualified. Temporary test trust and pairing were removed. |
| Modem | SIM installed: owner confirmed call establishment and SMS in both directions. QTI audio slot mapping and call-only single-microphone route repair restored bidirectional audio. Owner confirmed both directions after reboot with the earpiece and speakerphone; the original dual-mic mode was restored automatically after hangup. See CALL_AUDIO.md. Mobile-data DNS and HTTPS passed through the cellular interface with Wi-Fi disabled; the owner confirmed browser access, recovery after Wi-Fi switching and operation after reboot with mobile data enabled through the standard connectivity setting. See MOBILE_DATA.md. VoLTE and second-SIM behavior remain untested. |
| Fingerprint | Native fingerprint HAL and biometryd present; Android backend is registered. Enrollment, matching and unlock are untested. |
| Charging / thermal | Battery reports Charging/Fast/Good, capacity/current/voltage/temperature values. USB power input and telemetry work; charging-rate accuracy and thermal throttling are untested. |
| Sleep | Screen-off/on works. RTC alarm can be set. Manual deep-suspend tests with attached cable fail in `a600000.ssusb` with EBUSY / “USB is outside LPM”, including temporarily unbinding the gadget. USB/autosleep restored. Unplugged deep sleep and battery drain remain unqualified. |
| Jack / OTG / external accessories | Headphone routes and host-controller support are advertised; no physical accessory attached, so no functional claim. |


Build checks and device qualification are separate. Full stock-baseline installation/restoration, disconnected battery/deep sleep and the unresolved functions above are release gates.
