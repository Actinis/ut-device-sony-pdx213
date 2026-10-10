# Noble Qt camera microphone startup

Source: UBports qtubuntu-camera, commit
`a1674289b1da9129231ba100ab4474b59b5c834c`, LGPL-3.0.
The patch changes only recorder startup and microphone-worker cancellation.

Android calls the audio-read callback from a protected Binder frame. Starting
Qt's worker there initializes Qt thread-local state inside Android's TLS context
and the observed `MediaRecorder::readAudio` stack-protector check aborts.
Simply queuing the start to the recorder's Qt thread cannot complete while that
thread waits inside Android recorder startup. The microphone worker now starts
on the owning Qt thread before the blocking Android start call. Its FIFO open
waits for Android's reader without blocking cancellation. The Android callback
performs no Qt work. Stack protection remains enabled.

The FIFO waiting loop uses an atomic stop flag; cancellation also works when
requested before the worker begins. Recording-stop ordering is preserved so
Android's writer teardown still receives audio until recorder stop completes.
Sony CamX cleanup compatibility remains a separate rootfs integration.

`inputs.json` pins the source, patch, distribution baseline and all 22 target
SDK packages. Noble's ARM64 `moc 5.15.13` runs under explicitly selected QEMU
with the locked rootfs libraries. No desktop Qt headers or tools are used.
The NDK and rootfs come from `sources.lock.json`; QEMU version/hash and all
runtime library hashes are recorded in the component build report.

`fifo-cancel.cpp` runs the real microphone worker against a temporary FIFO
without a reader, then cancels it. It never opens the host microphone or the
real `/dev/socket/micshm`. The test is compiled for ARM64 and run under QEMU.
Device video proof is separate: see the hardware qualification evidence.

The build includes the upstream LGPL `COPYING` file. Userdata assembly verifies
component/build/lock identity and the official rootfs camera-plugin SHA256
before replacing it. Temporary probes, private cores and recordings are not
part of this component.
