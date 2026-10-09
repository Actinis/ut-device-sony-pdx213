/* Sony's unpatched Android 11 vendor manager requires SELinux status even
 * when the host uses AppArmor. Apply only to that manager, never globally.
 * Native Binder identity checks remain in the manager; this supplies the
 * SELinux-disabled behavior already used by the Halium system manager.
 */
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

int selinux_status_open(int fallback) { (void)fallback; return 0; }
int selinux_status_updated(void) { return 0; }
int selinux_status_getenforce(void) { return 0; }
int getcon(char **context) {
    *context = strdup("u:r:vndservicemanager:s0");
    return *context ? 0 : -1;
}
int getpidcon(pid_t pid, char **context) {
    (void)pid;
    *context = strdup("u:r:unconfined:s0");
    return *context ? 0 : -1;
}
int selinux_check_access(const char *source, const char *target,
                         const char *class_name, const char *permission,
                         void *audit) {
    (void)source; (void)target; (void)class_name; (void)permission; (void)audit;
    return 0;
}
