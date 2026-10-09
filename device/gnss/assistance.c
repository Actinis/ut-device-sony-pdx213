// SPDX-License-Identifier: MIT
// Linux-side assistance for the existing Ubuntu platform GPS API.
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>
#include <pthread.h>
#include <dlfcn.h>
#include <time.h>
#include <ubuntu/hardware/gps.h>

static UHardwareGpsParams original;
static UHardwareGps handle;
static atomic_int closing, pending, callbacks_running;
static pthread_t worker;
static atomic_int has_worker;
static void nap(void) { struct timespec t={0,100000000}; nanosleep(&t,0); }
static void (*connection_open)(UHardwareGps,const char*);
static void (*connection_closed)(UHardwareGps);
static void (*connection_failed)(UHardwareGps);

static void *assist(void *unused) {
    (void)unused;
    while (!atomic_load(&closing)) {
        int event=atomic_exchange(&pending,0);
        if (event==1) {
            char apn[128]={0};
            FILE *p=popen("/usr/local/lib/utxperia/gnss_active_apn.py", "r");
            int okay=p && fgets(apn,sizeof(apn),p);
            if (p && pclose(p)!=0) okay=0;
            size_t n=strcspn(apn,"\r\n"); apn[n]=0;
            if (!n || strspn(apn,"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")!=n) okay=0;
            if (!atomic_load(&closing) && atomic_load(&pending)!=2) {
                if (okay) connection_open(handle,apn);
                else connection_failed(handle);
            }
        } else if (event==2 && !atomic_load(&closing)) connection_closed(handle);
        nap();
    }
    return 0;
}
static void status(UHardwareGpsAGpsStatus *value,void *context) {
    if (atomic_load(&closing)) return;
    atomic_fetch_add(&callbacks_running,1);
    if (!atomic_load(&closing)) {
        if (original.agps_status_cb) original.agps_status_cb(value,context);
        // Only ordinary SUPL; no emergency, IMS or C2K handling.
        if (has_worker && value && value->type==U_HARDWARE_GPS_AGPS_TYPE_SUPL && (value->status==1 || value->status==2)) atomic_store(&pending,value->status);
    }
    atomic_fetch_sub(&callbacks_running,1);
}
UHardwareGps u_hardware_gps_new(UHardwareGpsParams *params) {
    UHardwareGps (*create)(UHardwareGpsParams*)=dlsym(RTLD_NEXT,"u_hardware_gps_new");
    const char *host=getenv("UTXPERIA_GNSS_SUPL_HOST");
    if (!host || !*host) return create(params);
    original=*params;UHardwareGpsParams wrapped=*params;wrapped.agps_status_cb=status;
    atomic_store(&closing,0);atomic_store(&pending,0);
    connection_open=dlsym(RTLD_NEXT,"u_hardware_gps_agps_notify_connection_is_open");
    connection_closed=dlsym(RTLD_NEXT,"u_hardware_gps_agps_notify_connection_is_closed");
    connection_failed=dlsym(RTLD_NEXT,"u_hardware_gps_agps_notify_connection_not_available");
    if (!connection_open || !connection_closed || !connection_failed) return create(params);
    handle=create(&wrapped);
    if (!handle) return 0;
    void (*server)(UHardwareGps,UHardwareGpsAGpsType,const char*,uint16_t)=dlsym(RTLD_NEXT,"u_hardware_gps_agps_set_server_for_type");
    if (server) server(handle,U_HARDWARE_GPS_AGPS_TYPE_SUPL,host,7275);
    has_worker=pthread_create(&worker,0,assist,0)==0;
    return handle;
}
void u_hardware_gps_delete(UHardwareGps value) {
    void (*destroy)(UHardwareGps)=dlsym(RTLD_NEXT,"u_hardware_gps_delete");
    if (value==handle) {
        atomic_store(&closing,1);
        if (has_worker) pthread_join(worker,0);
        while (atomic_load(&callbacks_running)) nap();
        has_worker=0;handle=0;
    }
    destroy(value);
}
