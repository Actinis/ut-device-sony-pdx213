// Minimal AArch64 Linux reboot(RESTART2, "bootloader"); no libc dependencies.
.section .text
.global _start
_start:
    // Flush filesystem writes before a bounded boot experiment restarts.
    mov x8, #162
    svc #0
    movz x0, #0xdead
    movk x0, #0xfee1, lsl #16
    movz x1, #0x1969
    movk x1, #0x2812, lsl #16
    movz x2, #0xc3d4
    movk x2, #0xa1b2, lsl #16
    adr x3, target
    mov x8, #142
    svc #0
    neg x0, x0
    mov x8, #93
    svc #0
target:
    .asciz "bootloader"
