#define LOG_TAG "vendor.nxp.nxpese@1.0::NxpEse"

#include <log/log.h>
#include <cutils/trace.h>
#include <hidl/HidlTransportSupport.h>

#include <hidl/Static.h>
#include <hwbinder/ProcessState.h>
#include <utils/Trace.h>
#include <android/hidl/manager/1.0/IServiceManager.h>
#include <vendor/nxp/nxpese/1.0/BpHwNxpEse.h>
#include <vendor/nxp/nxpese/1.0/BnHwNxpEse.h>
#include <vendor/nxp/nxpese/1.0/BsNxpEse.h>
#include <android/hidl/base/1.0/BpHwBase.h>
#include <hidl/ServiceManagement.h>

namespace vendor {
namespace nxp {
namespace nxpese {
namespace V1_0 {

const char* INxpEse::descriptor("vendor.nxp.nxpese@1.0::INxpEse");

__attribute__((constructor)) static void static_constructor() {
    ::android::hardware::details::getBnConstructorMap().set(INxpEse::descriptor,
            [](void *iIntf) -> ::android::sp<::android::hardware::IBinder> {
                return new BnHwNxpEse(static_cast<INxpEse *>(iIntf));
            });
    ::android::hardware::details::getBsConstructorMap().set(INxpEse::descriptor,
            [](void *iIntf) -> ::android::sp<::android::hidl::base::V1_0::IBase> {
                return new BsNxpEse(static_cast<INxpEse *>(iIntf));
            });
}

__attribute__((destructor))static void static_destructor() {
    ::android::hardware::details::getBnConstructorMap().erase(INxpEse::descriptor);
    ::android::hardware::details::getBsConstructorMap().erase(INxpEse::descriptor);
}

// Methods from ::vendor::nxp::nxpese::V1_0::INxpEse follow.
// no default implementation for: ::android::hardware::Return<void> INxpEse::ioctl(uint64_t ioctlType, const ::android::hardware::hidl_vec<uint8_t>& inputData, ioctl_cb _hidl_cb)

// Methods from ::android::hidl::base::V1_0::IBase follow.
::android::hardware::Return<void> INxpEse::interfaceChain(interfaceChain_cb _hidl_cb){
    _hidl_cb({
        ::vendor::nxp::nxpese::V1_0::INxpEse::descriptor,
        ::android::hidl::base::V1_0::IBase::descriptor,
    });
    return ::android::hardware::Void();
}

::android::hardware::Return<void> INxpEse::debug(const ::android::hardware::hidl_handle& fd, const ::android::hardware::hidl_vec<::android::hardware::hidl_string>& options){
    (void)fd;
    (void)options;
    return ::android::hardware::Void();
}

::android::hardware::Return<void> INxpEse::interfaceDescriptor(interfaceDescriptor_cb _hidl_cb){
    _hidl_cb(::vendor::nxp::nxpese::V1_0::INxpEse::descriptor);
    return ::android::hardware::Void();
}

::android::hardware::Return<void> INxpEse::getHashChain(getHashChain_cb _hidl_cb){
    _hidl_cb({
        (uint8_t[32]){176,101,30,228,251,145,10,55,34,2,48,88,112,115,0,205,222,158,130,76,251,224,21,229,122,189,39,240,45,75,74,237} /* b0651ee4fb910a3722023058707300cdde9e824cfbe015e57abd27f02d4b4aed */,
        (uint8_t[32]){236,127,215,158,208,45,250,133,188,73,148,38,173,174,62,190,35,239,5,36,243,205,105,87,19,147,36,184,59,24,202,76} /* ec7fd79ed02dfa85bc499426adae3ebe23ef0524f3cd6957139324b83b18ca4c */});
    return ::android::hardware::Void();
}

::android::hardware::Return<void> INxpEse::setHALInstrumentation(){
    return ::android::hardware::Void();
}

::android::hardware::Return<bool> INxpEse::linkToDeath(const ::android::sp<::android::hardware::hidl_death_recipient>& recipient, uint64_t cookie){
    (void)cookie;
    return (recipient != nullptr);
}

::android::hardware::Return<void> INxpEse::ping(){
    return ::android::hardware::Void();
}

::android::hardware::Return<void> INxpEse::getDebugInfo(getDebugInfo_cb _hidl_cb){
    ::android::hidl::base::V1_0::DebugInfo info = {};
    info.pid = -1;
    info.ptr = 0;
    info.arch = 
    #if defined(__LP64__)
    ::android::hidl::base::V1_0::DebugInfo::Architecture::IS_64BIT
    #else
    ::android::hidl::base::V1_0::DebugInfo::Architecture::IS_32BIT
    #endif
    ;
    _hidl_cb(info);
    return ::android::hardware::Void();
}

::android::hardware::Return<void> INxpEse::notifySyspropsChanged(){
    ::android::report_sysprop_change();
    return ::android::hardware::Void();
}

::android::hardware::Return<bool> INxpEse::unlinkToDeath(const ::android::sp<::android::hardware::hidl_death_recipient>& recipient){
    return (recipient != nullptr);
}


::android::hardware::Return<::android::sp<::vendor::nxp::nxpese::V1_0::INxpEse>> INxpEse::castFrom(const ::android::sp<::vendor::nxp::nxpese::V1_0::INxpEse>& parent, bool /* emitError */) {
    return parent;
}

::android::hardware::Return<::android::sp<::vendor::nxp::nxpese::V1_0::INxpEse>> INxpEse::castFrom(const ::android::sp<::android::hidl::base::V1_0::IBase>& parent, bool emitError) {
    return ::android::hardware::details::castInterface<INxpEse, ::android::hidl::base::V1_0::IBase, BpHwNxpEse>(
            parent, "vendor.nxp.nxpese@1.0::INxpEse", emitError);
}

BpHwNxpEse::BpHwNxpEse(const ::android::sp<::android::hardware::IBinder> &_hidl_impl)
        : BpInterface<INxpEse>(_hidl_impl),
          ::android::hardware::details::HidlInstrumentor("vendor.nxp.nxpese@1.0", "INxpEse") {
}

void BpHwNxpEse::onLastStrongRef(const void* id) {
    {
        std::unique_lock<std::mutex> lock(_hidl_mMutex);
        _hidl_mDeathRecipients.clear();
    }

    BpInterface<INxpEse>::onLastStrongRef(id);
}
// Methods from ::vendor::nxp::nxpese::V1_0::INxpEse follow.
::android::hardware::Return<void> BpHwNxpEse::_hidl_ioctl(::android::hardware::IInterface *_hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor, uint64_t ioctlType, const ::android::hardware::hidl_vec<uint8_t>& inputData, ioctl_cb _hidl_cb) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this_instrumentor->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this_instrumentor->getInstrumentationCallbacks();
    #else
    (void) _hidl_this_instrumentor;
    #endif // __ANDROID_DEBUGGABLE__
    ::android::ScopedTrace PASTE(___tracer, __LINE__) (ATRACE_TAG_HAL, "HIDL::INxpEse::ioctl::client");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&ioctlType);
        _hidl_args.push_back((void *)&inputData);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_ENTRY, "vendor.nxp.nxpese", "1.0", "INxpEse", "ioctl", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    ::android::hardware::Parcel _hidl_data;
    ::android::hardware::Parcel _hidl_reply;
    ::android::status_t _hidl_err;
    ::android::status_t _hidl_transact_err;
    ::android::hardware::Status _hidl_status;

    _hidl_err = _hidl_data.writeInterfaceToken(BpHwNxpEse::descriptor);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_err = _hidl_data.writeUint64(ioctlType);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    size_t _hidl_inputData_parent;

    _hidl_err = _hidl_data.writeBuffer(&inputData, sizeof(inputData), &_hidl_inputData_parent);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    size_t _hidl_inputData_child;

    _hidl_err = ::android::hardware::writeEmbeddedToParcel(
            inputData,
            &_hidl_data,
            _hidl_inputData_parent,
            0 /* parentOffset */, &_hidl_inputData_child);

    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_transact_err = ::android::hardware::IInterface::asBinder(_hidl_this)->transact(1 /* ioctl */, _hidl_data, &_hidl_reply, 0 /* flags */, [&] (::android::hardware::Parcel& _hidl_reply) {
        const ::android::hardware::hidl_vec<uint8_t>* _hidl_out_outputData;


        _hidl_err = ::android::hardware::readFromParcel(&_hidl_status, _hidl_reply);
        if (_hidl_err != ::android::OK) { return; }

        if (!_hidl_status.isOk()) { return; }

        size_t _hidl__hidl_out_outputData_parent;

        _hidl_err = _hidl_reply.readBuffer(sizeof(*_hidl_out_outputData), &_hidl__hidl_out_outputData_parent,  reinterpret_cast<const void **>(&_hidl_out_outputData));

        if (_hidl_err != ::android::OK) { return; }

        size_t _hidl__hidl_out_outputData_child;

        _hidl_err = ::android::hardware::readEmbeddedFromParcel(
                const_cast<::android::hardware::hidl_vec<uint8_t> &>(*_hidl_out_outputData),
                _hidl_reply,
                _hidl__hidl_out_outputData_parent,
                0 /* parentOffset */, &_hidl__hidl_out_outputData_child);

        if (_hidl_err != ::android::OK) { return; }

        _hidl_cb(*_hidl_out_outputData);

        #ifdef __ANDROID_DEBUGGABLE__
        if (UNLIKELY(mEnableInstrumentation)) {
            std::vector<void *> _hidl_args;
            _hidl_args.push_back((void *)_hidl_out_outputData);
            for (const auto &callback: mInstrumentationCallbacks) {
                callback(InstrumentationEvent::CLIENT_API_EXIT, "vendor.nxp.nxpese", "1.0", "INxpEse", "ioctl", &_hidl_args);
            }
        }
        #endif // __ANDROID_DEBUGGABLE__

    });
    if (_hidl_transact_err != ::android::OK) {
        _hidl_err = _hidl_transact_err;
        goto _hidl_error;
    }

    if (!_hidl_status.isOk()) { return _hidl_status; }
    return ::android::hardware::Return<void>();

_hidl_error:
    _hidl_status.setFromStatusT(_hidl_err);
    return ::android::hardware::Return<void>(_hidl_status);
}


// Methods from ::vendor::nxp::nxpese::V1_0::INxpEse follow.
::android::hardware::Return<void> BpHwNxpEse::ioctl(uint64_t ioctlType, const ::android::hardware::hidl_vec<uint8_t>& inputData, ioctl_cb _hidl_cb){
    ::android::hardware::Return<void>  _hidl_out = ::vendor::nxp::nxpese::V1_0::BpHwNxpEse::_hidl_ioctl(this, this, ioctlType, inputData, _hidl_cb);

    return _hidl_out;
}


// Methods from ::android::hidl::base::V1_0::IBase follow.
::android::hardware::Return<void> BpHwNxpEse::interfaceChain(interfaceChain_cb _hidl_cb){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_interfaceChain(this, this, _hidl_cb);

    return _hidl_out;
}

::android::hardware::Return<void> BpHwNxpEse::debug(const ::android::hardware::hidl_handle& fd, const ::android::hardware::hidl_vec<::android::hardware::hidl_string>& options){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_debug(this, this, fd, options);

    return _hidl_out;
}

::android::hardware::Return<void> BpHwNxpEse::interfaceDescriptor(interfaceDescriptor_cb _hidl_cb){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_interfaceDescriptor(this, this, _hidl_cb);

    return _hidl_out;
}

::android::hardware::Return<void> BpHwNxpEse::getHashChain(getHashChain_cb _hidl_cb){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_getHashChain(this, this, _hidl_cb);

    return _hidl_out;
}

::android::hardware::Return<void> BpHwNxpEse::setHALInstrumentation(){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_setHALInstrumentation(this, this);

    return _hidl_out;
}

::android::hardware::Return<bool> BpHwNxpEse::linkToDeath(const ::android::sp<::android::hardware::hidl_death_recipient>& recipient, uint64_t cookie){
    ::android::hardware::ProcessState::self()->startThreadPool();
    ::android::hardware::hidl_binder_death_recipient *binder_recipient = new ::android::hardware::hidl_binder_death_recipient(recipient, cookie, this);
    std::unique_lock<std::mutex> lock(_hidl_mMutex);
    _hidl_mDeathRecipients.push_back(binder_recipient);
    return (remote()->linkToDeath(binder_recipient) == ::android::OK);
}

::android::hardware::Return<void> BpHwNxpEse::ping(){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_ping(this, this);

    return _hidl_out;
}

::android::hardware::Return<void> BpHwNxpEse::getDebugInfo(getDebugInfo_cb _hidl_cb){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_getDebugInfo(this, this, _hidl_cb);

    return _hidl_out;
}

::android::hardware::Return<void> BpHwNxpEse::notifySyspropsChanged(){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_notifySyspropsChanged(this, this);

    return _hidl_out;
}

::android::hardware::Return<bool> BpHwNxpEse::unlinkToDeath(const ::android::sp<::android::hardware::hidl_death_recipient>& recipient){
    std::unique_lock<std::mutex> lock(_hidl_mMutex);
    for (auto it = _hidl_mDeathRecipients.rbegin();it != _hidl_mDeathRecipients.rend();++it) {
        if ((*it)->getRecipient() == recipient) {
            ::android::status_t status = remote()->unlinkToDeath(*it);
            _hidl_mDeathRecipients.erase(it.base()-1);
            return status == ::android::OK;
        }
    }
    return false;
}


BnHwNxpEse::BnHwNxpEse(const ::android::sp<INxpEse> &_hidl_impl)
        : ::android::hidl::base::V1_0::BnHwBase(_hidl_impl, "vendor.nxp.nxpese@1.0", "INxpEse") { 
            _hidl_mImpl = _hidl_impl;
            auto prio = ::android::hardware::getMinSchedulerPolicy(_hidl_impl);
            mSchedPolicy = prio.sched_policy;
            mSchedPriority = prio.prio;
            setRequestingSid(::android::hardware::getRequestingSid(_hidl_impl));
}

BnHwNxpEse::~BnHwNxpEse() {
    ::android::hardware::details::gBnMap->eraseIfEqual(_hidl_mImpl.get(), this);
}

// Methods from ::vendor::nxp::nxpese::V1_0::INxpEse follow.
::android::status_t BnHwNxpEse::_hidl_ioctl(
        ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
        const ::android::hardware::Parcel &_hidl_data,
        ::android::hardware::Parcel *_hidl_reply,
        TransactCallback _hidl_cb) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this->getInstrumentationCallbacks();
    #endif // __ANDROID_DEBUGGABLE__

    ::android::status_t _hidl_err = ::android::OK;
    if (!_hidl_data.enforceInterface(BnHwNxpEse::Pure::descriptor)) {
        _hidl_err = ::android::BAD_TYPE;
        return _hidl_err;
    }

    uint64_t ioctlType;
    const ::android::hardware::hidl_vec<uint8_t>* inputData;

    _hidl_err = _hidl_data.readUint64(&ioctlType);
    if (_hidl_err != ::android::OK) { return _hidl_err; }

    size_t _hidl_inputData_parent;

    _hidl_err = _hidl_data.readBuffer(sizeof(*inputData), &_hidl_inputData_parent,  reinterpret_cast<const void **>(&inputData));

    if (_hidl_err != ::android::OK) { return _hidl_err; }

    size_t _hidl_inputData_child;

    _hidl_err = ::android::hardware::readEmbeddedFromParcel(
            const_cast<::android::hardware::hidl_vec<uint8_t> &>(*inputData),
            _hidl_data,
            _hidl_inputData_parent,
            0 /* parentOffset */, &_hidl_inputData_child);

    if (_hidl_err != ::android::OK) { return _hidl_err; }

    atrace_begin(ATRACE_TAG_HAL, "HIDL::INxpEse::ioctl::server");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&ioctlType);
        _hidl_args.push_back((void *)inputData);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_ENTRY, "vendor.nxp.nxpese", "1.0", "INxpEse", "ioctl", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    bool _hidl_callbackCalled = false;

    ::android::hardware::Return<void> _hidl_ret = static_cast<INxpEse*>(_hidl_this->getImpl().get())->ioctl(ioctlType, *inputData, [&](const auto &_hidl_out_outputData) {
        if (_hidl_callbackCalled) {
            LOG_ALWAYS_FATAL("ioctl: _hidl_cb called a second time, but must be called once.");
        }
        _hidl_callbackCalled = true;

        ::android::hardware::writeToParcel(::android::hardware::Status::ok(), _hidl_reply);

        size_t _hidl__hidl_out_outputData_parent;

        _hidl_err = _hidl_reply->writeBuffer(&_hidl_out_outputData, sizeof(_hidl_out_outputData), &_hidl__hidl_out_outputData_parent);
        if (_hidl_err != ::android::OK) { goto _hidl_error; }

        size_t _hidl__hidl_out_outputData_child;

        _hidl_err = ::android::hardware::writeEmbeddedToParcel(
                _hidl_out_outputData,
                _hidl_reply,
                _hidl__hidl_out_outputData_parent,
                0 /* parentOffset */, &_hidl__hidl_out_outputData_child);

        if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_error:
        atrace_end(ATRACE_TAG_HAL);
        #ifdef __ANDROID_DEBUGGABLE__
        if (UNLIKELY(mEnableInstrumentation)) {
            std::vector<void *> _hidl_args;
            _hidl_args.push_back((void *)&_hidl_out_outputData);
            for (const auto &callback: mInstrumentationCallbacks) {
                callback(InstrumentationEvent::SERVER_API_EXIT, "vendor.nxp.nxpese", "1.0", "INxpEse", "ioctl", &_hidl_args);
            }
        }
        #endif // __ANDROID_DEBUGGABLE__

        if (_hidl_err != ::android::OK) { return; }
        _hidl_cb(*_hidl_reply);
    });

    _hidl_ret.assertOk();
    if (!_hidl_callbackCalled) {
        LOG_ALWAYS_FATAL("ioctl: _hidl_cb not called, but must be called once.");
    }

    return _hidl_err;
}


// Methods from ::vendor::nxp::nxpese::V1_0::INxpEse follow.

// Methods from ::android::hidl::base::V1_0::IBase follow.
::android::hardware::Return<void> BnHwNxpEse::ping() {
    return ::android::hardware::Void();
}
::android::hardware::Return<void> BnHwNxpEse::getDebugInfo(getDebugInfo_cb _hidl_cb) {
    ::android::hidl::base::V1_0::DebugInfo info = {};
    info.pid = ::android::hardware::details::getPidIfSharable();
    info.ptr = ::android::hardware::details::debuggable()? reinterpret_cast<uint64_t>(this) : 0;
    info.arch = 
    #if defined(__LP64__)
    ::android::hidl::base::V1_0::DebugInfo::Architecture::IS_64BIT
    #else
    ::android::hidl::base::V1_0::DebugInfo::Architecture::IS_32BIT
    #endif
    ;
    _hidl_cb(info);
    return ::android::hardware::Void();
}

::android::status_t BnHwNxpEse::onTransact(
        uint32_t _hidl_code,
        const ::android::hardware::Parcel &_hidl_data,
        ::android::hardware::Parcel *_hidl_reply,
        uint32_t _hidl_flags,
        TransactCallback _hidl_cb) {
    ::android::status_t _hidl_err = ::android::OK;

    switch (_hidl_code) {
        case 1 /* ioctl */:
        {
            _hidl_err = ::vendor::nxp::nxpese::V1_0::BnHwNxpEse::_hidl_ioctl(this, _hidl_data, _hidl_reply, _hidl_cb);
            break;
        }

        default:
        {
            return ::android::hidl::base::V1_0::BnHwBase::onTransact(
                    _hidl_code, _hidl_data, _hidl_reply, _hidl_flags, _hidl_cb);
        }
    }

    if (_hidl_err == ::android::UNEXPECTED_NULL) {
        _hidl_err = ::android::hardware::writeToParcel(
                ::android::hardware::Status::fromExceptionCode(::android::hardware::Status::EX_NULL_POINTER),
                _hidl_reply);
    }return _hidl_err;
}

BsNxpEse::BsNxpEse(const ::android::sp<::vendor::nxp::nxpese::V1_0::INxpEse> impl) : ::android::hardware::details::HidlInstrumentor("vendor.nxp.nxpese@1.0", "INxpEse"), mImpl(impl) {
    mOnewayQueue.start(3000 /* similar limit to binderized */);
}

::android::hardware::Return<void> BsNxpEse::addOnewayTask(std::function<void(void)> fun) {
    if (!mOnewayQueue.push(fun)) {
        return ::android::hardware::Status::fromExceptionCode(
                ::android::hardware::Status::EX_TRANSACTION_FAILED,
                "Passthrough oneway function queue exceeds maximum size.");
    }
    return ::android::hardware::Status();
}

::android::sp<INxpEse> INxpEse::tryGetService(const std::string &serviceName, const bool getStub) {
    return ::android::hardware::details::getServiceInternal<BpHwNxpEse>(serviceName, false, getStub);
}

::android::sp<INxpEse> INxpEse::getService(const std::string &serviceName, const bool getStub) {
    return ::android::hardware::details::getServiceInternal<BpHwNxpEse>(serviceName, true, getStub);
}

::android::status_t INxpEse::registerAsService(const std::string &serviceName) {
    return ::android::hardware::details::registerAsServiceInternal(this, serviceName);
}

bool INxpEse::registerForNotifications(
        const std::string &serviceName,
        const ::android::sp<::android::hidl::manager::V1_0::IServiceNotification> &notification) {
    const ::android::sp<::android::hidl::manager::V1_0::IServiceManager> sm
            = ::android::hardware::defaultServiceManager();
    if (sm == nullptr) {
        return false;
    }
    ::android::hardware::Return<bool> success =
            sm->registerForNotifications("vendor.nxp.nxpese@1.0::INxpEse",
                    serviceName, notification);
    return success.isOk() && success;
}

static_assert(sizeof(::android::hardware::MQDescriptor<char, ::android::hardware::kSynchronizedReadWrite>) == 32, "wrong size");
static_assert(sizeof(::android::hardware::hidl_handle) == 16, "wrong size");
static_assert(sizeof(::android::hardware::hidl_memory) == 40, "wrong size");
static_assert(sizeof(::android::hardware::hidl_string) == 16, "wrong size");
static_assert(sizeof(::android::hardware::hidl_vec<char>) == 16, "wrong size");

}  // namespace V1_0
}  // namespace nxpese
}  // namespace nxp
}  // namespace vendor
