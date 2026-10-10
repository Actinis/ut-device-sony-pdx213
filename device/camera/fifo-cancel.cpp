#include "audiocapture.h"
#include <atomic>
#include <chrono>
#include <thread>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/stat.h>
#include <cstring>
#include <cstdarg>
#include <cstdio>
static const char *fifo;
extern "C" int open(const char *path, int flags, ...)
{
    mode_t mode=0;
    if (flags & O_CREAT) { va_list args; va_start(args,flags);mode=va_arg(args,int);va_end(args); }
    if (std::strcmp(path,"/dev/socket/micshm")==0) path=fifo;
    return syscall(SYS_openat,AT_FDCWD,path,flags,mode);
}
extern "C" void android_recorder_set_audio_read_cb(MediaRecorderWrapper *,on_recorder_read_audio,void *) {}
int main()
{
    char path[]="/tmp/ut-camera-cancel-XXXXXX";
    int fd=mkstemp(path);if(fd<0)return 2;close(fd);unlink(path);
    if(mkfifo(path,0600))return 2;fifo=path;
    int result=0;
    for (bool cancelBeforeStart : {false,true}) {
        AudioCapture capture(nullptr);
        auto start=std::chrono::steady_clock::now();
        if(cancelBeforeStart)capture.stopCapture();
        std::thread worker([&]{capture.run();});
        if(!cancelBeforeStart) {
            std::this_thread::sleep_for(std::chrono::milliseconds(35));
            capture.stopCapture();
        }
        worker.join();
        auto elapsed=std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-start).count();
        std::printf("Cancelled FIFO worker (%s) in %lld ms\n",cancelBeforeStart?"before start":"waiting for reader",(long long)elapsed);
        if(elapsed>=500)result=1;
    }
    unlink(path);
    return result;
}
