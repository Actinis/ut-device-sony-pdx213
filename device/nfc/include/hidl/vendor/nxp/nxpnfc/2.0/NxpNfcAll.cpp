#define LOG_TAG "vendor.nxp.nxpnfc@2.0::NxpNfc"

#include <log/log.h>
#include <cutils/trace.h>
#include <hidl/HidlTransportSupport.h>

#include <hidl/Static.h>
#include <hwbinder/ProcessState.h>
#include <utils/Trace.h>
#include <android/hidl/manager/1.0/IServiceManager.h>
#include <vendor/nxp/nxpnfc/2.0/BpHwNxpNfc.h>
#include <vendor/nxp/nxpnfc/2.0/BnHwNxpNfc.h>
#include <vendor/nxp/nxpnfc/2.0/BsNxpNfc.h>
#include <android/hidl/base/1.0/BpHwBase.h>
#include <hidl/ServiceManagement.h>

namespace vendor {
namespace nxp {
namespace nxpnfc {
namespace V2_0 {

const char* INxpNfc::descriptor("vendor.nxp.nxpnfc@2.0::INxpNfc");

__attribute__((constructor)) static void static_constructor() {
    ::android::hardware::details::getBnConstructorMap().set(INxpNfc::descriptor,
            [](void *iIntf) -> ::android::sp<::android::hardware::IBinder> {
                return new BnHwNxpNfc(static_cast<INxpNfc *>(iIntf));
            });
    ::android::hardware::details::getBsConstructorMap().set(INxpNfc::descriptor,
            [](void *iIntf) -> ::android::sp<::android::hidl::base::V1_0::IBase> {
                return new BsNxpNfc(static_cast<INxpNfc *>(iIntf));
            });
}

__attribute__((destructor))static void static_destructor() {
    ::android::hardware::details::getBnConstructorMap().erase(INxpNfc::descriptor);
    ::android::hardware::details::getBsConstructorMap().erase(INxpNfc::descriptor);
}

// Methods from ::vendor::nxp::nxpnfc::V2_0::INxpNfc follow.
// no default implementation for: ::android::hardware::Return<void> INxpNfc::getVendorParam(const ::android::hardware::hidl_string& key, getVendorParam_cb _hidl_cb)
// no default implementation for: ::android::hardware::Return<bool> INxpNfc::setVendorParam(const ::android::hardware::hidl_string& key, const ::android::hardware::hidl_string& value)
// no default implementation for: ::android::hardware::Return<bool> INxpNfc::resetEse(uint64_t resetType)
// no default implementation for: ::android::hardware::Return<bool> INxpNfc::setEseUpdateState(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState eSEState)
// no default implementation for: ::android::hardware::Return<bool> INxpNfc::setNxpTransitConfig(const ::android::hardware::hidl_string& transitConfValue)
// no default implementation for: ::android::hardware::Return<bool> INxpNfc::isJcopUpdateRequired()
// no default implementation for: ::android::hardware::Return<bool> INxpNfc::isLsUpdateRequired()

// Methods from ::android::hidl::base::V1_0::IBase follow.
::android::hardware::Return<void> INxpNfc::interfaceChain(interfaceChain_cb _hidl_cb){
    _hidl_cb({
        ::vendor::nxp::nxpnfc::V2_0::INxpNfc::descriptor,
        ::android::hidl::base::V1_0::IBase::descriptor,
    });
    return ::android::hardware::Void();
}

::android::hardware::Return<void> INxpNfc::debug(const ::android::hardware::hidl_handle& fd, const ::android::hardware::hidl_vec<::android::hardware::hidl_string>& options){
    (void)fd;
    (void)options;
    return ::android::hardware::Void();
}

::android::hardware::Return<void> INxpNfc::interfaceDescriptor(interfaceDescriptor_cb _hidl_cb){
    _hidl_cb(::vendor::nxp::nxpnfc::V2_0::INxpNfc::descriptor);
    return ::android::hardware::Void();
}

::android::hardware::Return<void> INxpNfc::getHashChain(getHashChain_cb _hidl_cb){
    _hidl_cb({
        (uint8_t[32]){230,95,81,116,140,17,75,212,223,229,125,172,76,43,214,144,0,12,119,14,118,197,45,247,110,35,79,174,197,0,162,72} /* e65f51748c114bd4dfe57dac4c2bd690000c770e76c52df76e234faec500a248 */,
        (uint8_t[32]){236,127,215,158,208,45,250,133,188,73,148,38,173,174,62,190,35,239,5,36,243,205,105,87,19,147,36,184,59,24,202,76} /* ec7fd79ed02dfa85bc499426adae3ebe23ef0524f3cd6957139324b83b18ca4c */});
    return ::android::hardware::Void();
}

::android::hardware::Return<void> INxpNfc::setHALInstrumentation(){
    return ::android::hardware::Void();
}

::android::hardware::Return<bool> INxpNfc::linkToDeath(const ::android::sp<::android::hardware::hidl_death_recipient>& recipient, uint64_t cookie){
    (void)cookie;
    return (recipient != nullptr);
}

::android::hardware::Return<void> INxpNfc::ping(){
    return ::android::hardware::Void();
}

::android::hardware::Return<void> INxpNfc::getDebugInfo(getDebugInfo_cb _hidl_cb){
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

::android::hardware::Return<void> INxpNfc::notifySyspropsChanged(){
    ::android::report_sysprop_change();
    return ::android::hardware::Void();
}

::android::hardware::Return<bool> INxpNfc::unlinkToDeath(const ::android::sp<::android::hardware::hidl_death_recipient>& recipient){
    return (recipient != nullptr);
}


::android::hardware::Return<::android::sp<::vendor::nxp::nxpnfc::V2_0::INxpNfc>> INxpNfc::castFrom(const ::android::sp<::vendor::nxp::nxpnfc::V2_0::INxpNfc>& parent, bool /* emitError */) {
    return parent;
}

::android::hardware::Return<::android::sp<::vendor::nxp::nxpnfc::V2_0::INxpNfc>> INxpNfc::castFrom(const ::android::sp<::android::hidl::base::V1_0::IBase>& parent, bool emitError) {
    return ::android::hardware::details::castInterface<INxpNfc, ::android::hidl::base::V1_0::IBase, BpHwNxpNfc>(
            parent, "vendor.nxp.nxpnfc@2.0::INxpNfc", emitError);
}

BpHwNxpNfc::BpHwNxpNfc(const ::android::sp<::android::hardware::IBinder> &_hidl_impl)
        : BpInterface<INxpNfc>(_hidl_impl),
          ::android::hardware::details::HidlInstrumentor("vendor.nxp.nxpnfc@2.0", "INxpNfc") {
}

void BpHwNxpNfc::onLastStrongRef(const void* id) {
    {
        std::unique_lock<std::mutex> lock(_hidl_mMutex);
        _hidl_mDeathRecipients.clear();
    }

    BpInterface<INxpNfc>::onLastStrongRef(id);
}
// Methods from ::vendor::nxp::nxpnfc::V2_0::INxpNfc follow.
::android::hardware::Return<void> BpHwNxpNfc::_hidl_getVendorParam(::android::hardware::IInterface *_hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor, const ::android::hardware::hidl_string& key, getVendorParam_cb _hidl_cb) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this_instrumentor->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this_instrumentor->getInstrumentationCallbacks();
    #else
    (void) _hidl_this_instrumentor;
    #endif // __ANDROID_DEBUGGABLE__
    ::android::ScopedTrace PASTE(___tracer, __LINE__) (ATRACE_TAG_HAL, "HIDL::INxpNfc::getVendorParam::client");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&key);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "getVendorParam", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    ::android::hardware::Parcel _hidl_data;
    ::android::hardware::Parcel _hidl_reply;
    ::android::status_t _hidl_err;
    ::android::status_t _hidl_transact_err;
    ::android::hardware::Status _hidl_status;

    _hidl_err = _hidl_data.writeInterfaceToken(BpHwNxpNfc::descriptor);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    size_t _hidl_key_parent;

    _hidl_err = _hidl_data.writeBuffer(&key, sizeof(key), &_hidl_key_parent);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_err = ::android::hardware::writeEmbeddedToParcel(
            key,
            &_hidl_data,
            _hidl_key_parent,
            0 /* parentOffset */);

    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_transact_err = ::android::hardware::IInterface::asBinder(_hidl_this)->transact(1 /* getVendorParam */, _hidl_data, &_hidl_reply, 0 /* flags */, [&] (::android::hardware::Parcel& _hidl_reply) {
        const ::android::hardware::hidl_string* _hidl_out_value;


        _hidl_err = ::android::hardware::readFromParcel(&_hidl_status, _hidl_reply);
        if (_hidl_err != ::android::OK) { return; }

        if (!_hidl_status.isOk()) { return; }

        size_t _hidl__hidl_out_value_parent;

        _hidl_err = _hidl_reply.readBuffer(sizeof(*_hidl_out_value), &_hidl__hidl_out_value_parent,  reinterpret_cast<const void **>(&_hidl_out_value));

        if (_hidl_err != ::android::OK) { return; }

        _hidl_err = ::android::hardware::readEmbeddedFromParcel(
                const_cast<::android::hardware::hidl_string &>(*_hidl_out_value),
                _hidl_reply,
                _hidl__hidl_out_value_parent,
                0 /* parentOffset */);

        if (_hidl_err != ::android::OK) { return; }

        _hidl_cb(*_hidl_out_value);

        #ifdef __ANDROID_DEBUGGABLE__
        if (UNLIKELY(mEnableInstrumentation)) {
            std::vector<void *> _hidl_args;
            _hidl_args.push_back((void *)_hidl_out_value);
            for (const auto &callback: mInstrumentationCallbacks) {
                callback(InstrumentationEvent::CLIENT_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "getVendorParam", &_hidl_args);
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

::android::hardware::Return<bool> BpHwNxpNfc::_hidl_setVendorParam(::android::hardware::IInterface *_hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor, const ::android::hardware::hidl_string& key, const ::android::hardware::hidl_string& value) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this_instrumentor->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this_instrumentor->getInstrumentationCallbacks();
    #else
    (void) _hidl_this_instrumentor;
    #endif // __ANDROID_DEBUGGABLE__
    ::android::ScopedTrace PASTE(___tracer, __LINE__) (ATRACE_TAG_HAL, "HIDL::INxpNfc::setVendorParam::client");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&key);
        _hidl_args.push_back((void *)&value);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "setVendorParam", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    ::android::hardware::Parcel _hidl_data;
    ::android::hardware::Parcel _hidl_reply;
    ::android::status_t _hidl_err;
    ::android::status_t _hidl_transact_err;
    ::android::hardware::Status _hidl_status;

    bool _hidl_out_status;

    _hidl_err = _hidl_data.writeInterfaceToken(BpHwNxpNfc::descriptor);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    size_t _hidl_key_parent;

    _hidl_err = _hidl_data.writeBuffer(&key, sizeof(key), &_hidl_key_parent);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_err = ::android::hardware::writeEmbeddedToParcel(
            key,
            &_hidl_data,
            _hidl_key_parent,
            0 /* parentOffset */);

    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    size_t _hidl_value_parent;

    _hidl_err = _hidl_data.writeBuffer(&value, sizeof(value), &_hidl_value_parent);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_err = ::android::hardware::writeEmbeddedToParcel(
            value,
            &_hidl_data,
            _hidl_value_parent,
            0 /* parentOffset */);

    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_transact_err = ::android::hardware::IInterface::asBinder(_hidl_this)->transact(2 /* setVendorParam */, _hidl_data, &_hidl_reply, 0 /* flags */);
    if (_hidl_transact_err != ::android::OK) 
    {
        _hidl_err = _hidl_transact_err;
        goto _hidl_error;
    }

    _hidl_err = ::android::hardware::readFromParcel(&_hidl_status, _hidl_reply);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    if (!_hidl_status.isOk()) { return _hidl_status; }

    _hidl_err = _hidl_reply.readBool(&_hidl_out_status);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&_hidl_out_status);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "setVendorParam", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    return ::android::hardware::Return<bool>(_hidl_out_status);

_hidl_error:
    _hidl_status.setFromStatusT(_hidl_err);
    return ::android::hardware::Return<bool>(_hidl_status);
}

::android::hardware::Return<bool> BpHwNxpNfc::_hidl_resetEse(::android::hardware::IInterface *_hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor, uint64_t resetType) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this_instrumentor->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this_instrumentor->getInstrumentationCallbacks();
    #else
    (void) _hidl_this_instrumentor;
    #endif // __ANDROID_DEBUGGABLE__
    ::android::ScopedTrace PASTE(___tracer, __LINE__) (ATRACE_TAG_HAL, "HIDL::INxpNfc::resetEse::client");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&resetType);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "resetEse", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    ::android::hardware::Parcel _hidl_data;
    ::android::hardware::Parcel _hidl_reply;
    ::android::status_t _hidl_err;
    ::android::status_t _hidl_transact_err;
    ::android::hardware::Status _hidl_status;

    bool _hidl_out_status;

    _hidl_err = _hidl_data.writeInterfaceToken(BpHwNxpNfc::descriptor);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_err = _hidl_data.writeUint64(resetType);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_transact_err = ::android::hardware::IInterface::asBinder(_hidl_this)->transact(3 /* resetEse */, _hidl_data, &_hidl_reply, 0 /* flags */);
    if (_hidl_transact_err != ::android::OK) 
    {
        _hidl_err = _hidl_transact_err;
        goto _hidl_error;
    }

    _hidl_err = ::android::hardware::readFromParcel(&_hidl_status, _hidl_reply);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    if (!_hidl_status.isOk()) { return _hidl_status; }

    _hidl_err = _hidl_reply.readBool(&_hidl_out_status);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&_hidl_out_status);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "resetEse", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    return ::android::hardware::Return<bool>(_hidl_out_status);

_hidl_error:
    _hidl_status.setFromStatusT(_hidl_err);
    return ::android::hardware::Return<bool>(_hidl_status);
}

::android::hardware::Return<bool> BpHwNxpNfc::_hidl_setEseUpdateState(::android::hardware::IInterface *_hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor, ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState eSEState) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this_instrumentor->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this_instrumentor->getInstrumentationCallbacks();
    #else
    (void) _hidl_this_instrumentor;
    #endif // __ANDROID_DEBUGGABLE__
    ::android::ScopedTrace PASTE(___tracer, __LINE__) (ATRACE_TAG_HAL, "HIDL::INxpNfc::setEseUpdateState::client");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&eSEState);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "setEseUpdateState", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    ::android::hardware::Parcel _hidl_data;
    ::android::hardware::Parcel _hidl_reply;
    ::android::status_t _hidl_err;
    ::android::status_t _hidl_transact_err;
    ::android::hardware::Status _hidl_status;

    bool _hidl_out_status;

    _hidl_err = _hidl_data.writeInterfaceToken(BpHwNxpNfc::descriptor);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_err = _hidl_data.writeUint64((uint64_t)eSEState);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_transact_err = ::android::hardware::IInterface::asBinder(_hidl_this)->transact(4 /* setEseUpdateState */, _hidl_data, &_hidl_reply, 0 /* flags */);
    if (_hidl_transact_err != ::android::OK) 
    {
        _hidl_err = _hidl_transact_err;
        goto _hidl_error;
    }

    _hidl_err = ::android::hardware::readFromParcel(&_hidl_status, _hidl_reply);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    if (!_hidl_status.isOk()) { return _hidl_status; }

    _hidl_err = _hidl_reply.readBool(&_hidl_out_status);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&_hidl_out_status);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "setEseUpdateState", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    return ::android::hardware::Return<bool>(_hidl_out_status);

_hidl_error:
    _hidl_status.setFromStatusT(_hidl_err);
    return ::android::hardware::Return<bool>(_hidl_status);
}

::android::hardware::Return<bool> BpHwNxpNfc::_hidl_setNxpTransitConfig(::android::hardware::IInterface *_hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor, const ::android::hardware::hidl_string& transitConfValue) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this_instrumentor->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this_instrumentor->getInstrumentationCallbacks();
    #else
    (void) _hidl_this_instrumentor;
    #endif // __ANDROID_DEBUGGABLE__
    ::android::ScopedTrace PASTE(___tracer, __LINE__) (ATRACE_TAG_HAL, "HIDL::INxpNfc::setNxpTransitConfig::client");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&transitConfValue);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "setNxpTransitConfig", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    ::android::hardware::Parcel _hidl_data;
    ::android::hardware::Parcel _hidl_reply;
    ::android::status_t _hidl_err;
    ::android::status_t _hidl_transact_err;
    ::android::hardware::Status _hidl_status;

    bool _hidl_out_status;

    _hidl_err = _hidl_data.writeInterfaceToken(BpHwNxpNfc::descriptor);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    size_t _hidl_transitConfValue_parent;

    _hidl_err = _hidl_data.writeBuffer(&transitConfValue, sizeof(transitConfValue), &_hidl_transitConfValue_parent);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_err = ::android::hardware::writeEmbeddedToParcel(
            transitConfValue,
            &_hidl_data,
            _hidl_transitConfValue_parent,
            0 /* parentOffset */);

    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_transact_err = ::android::hardware::IInterface::asBinder(_hidl_this)->transact(5 /* setNxpTransitConfig */, _hidl_data, &_hidl_reply, 0 /* flags */);
    if (_hidl_transact_err != ::android::OK) 
    {
        _hidl_err = _hidl_transact_err;
        goto _hidl_error;
    }

    _hidl_err = ::android::hardware::readFromParcel(&_hidl_status, _hidl_reply);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    if (!_hidl_status.isOk()) { return _hidl_status; }

    _hidl_err = _hidl_reply.readBool(&_hidl_out_status);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&_hidl_out_status);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "setNxpTransitConfig", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    return ::android::hardware::Return<bool>(_hidl_out_status);

_hidl_error:
    _hidl_status.setFromStatusT(_hidl_err);
    return ::android::hardware::Return<bool>(_hidl_status);
}

::android::hardware::Return<bool> BpHwNxpNfc::_hidl_isJcopUpdateRequired(::android::hardware::IInterface *_hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this_instrumentor->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this_instrumentor->getInstrumentationCallbacks();
    #else
    (void) _hidl_this_instrumentor;
    #endif // __ANDROID_DEBUGGABLE__
    ::android::ScopedTrace PASTE(___tracer, __LINE__) (ATRACE_TAG_HAL, "HIDL::INxpNfc::isJcopUpdateRequired::client");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "isJcopUpdateRequired", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    ::android::hardware::Parcel _hidl_data;
    ::android::hardware::Parcel _hidl_reply;
    ::android::status_t _hidl_err;
    ::android::status_t _hidl_transact_err;
    ::android::hardware::Status _hidl_status;

    bool _hidl_out_status;

    _hidl_err = _hidl_data.writeInterfaceToken(BpHwNxpNfc::descriptor);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_transact_err = ::android::hardware::IInterface::asBinder(_hidl_this)->transact(6 /* isJcopUpdateRequired */, _hidl_data, &_hidl_reply, 0 /* flags */);
    if (_hidl_transact_err != ::android::OK) 
    {
        _hidl_err = _hidl_transact_err;
        goto _hidl_error;
    }

    _hidl_err = ::android::hardware::readFromParcel(&_hidl_status, _hidl_reply);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    if (!_hidl_status.isOk()) { return _hidl_status; }

    _hidl_err = _hidl_reply.readBool(&_hidl_out_status);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&_hidl_out_status);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "isJcopUpdateRequired", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    return ::android::hardware::Return<bool>(_hidl_out_status);

_hidl_error:
    _hidl_status.setFromStatusT(_hidl_err);
    return ::android::hardware::Return<bool>(_hidl_status);
}

::android::hardware::Return<bool> BpHwNxpNfc::_hidl_isLsUpdateRequired(::android::hardware::IInterface *_hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this_instrumentor->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this_instrumentor->getInstrumentationCallbacks();
    #else
    (void) _hidl_this_instrumentor;
    #endif // __ANDROID_DEBUGGABLE__
    ::android::ScopedTrace PASTE(___tracer, __LINE__) (ATRACE_TAG_HAL, "HIDL::INxpNfc::isLsUpdateRequired::client");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "isLsUpdateRequired", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    ::android::hardware::Parcel _hidl_data;
    ::android::hardware::Parcel _hidl_reply;
    ::android::status_t _hidl_err;
    ::android::status_t _hidl_transact_err;
    ::android::hardware::Status _hidl_status;

    bool _hidl_out_status;

    _hidl_err = _hidl_data.writeInterfaceToken(BpHwNxpNfc::descriptor);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_transact_err = ::android::hardware::IInterface::asBinder(_hidl_this)->transact(7 /* isLsUpdateRequired */, _hidl_data, &_hidl_reply, 0 /* flags */);
    if (_hidl_transact_err != ::android::OK) 
    {
        _hidl_err = _hidl_transact_err;
        goto _hidl_error;
    }

    _hidl_err = ::android::hardware::readFromParcel(&_hidl_status, _hidl_reply);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    if (!_hidl_status.isOk()) { return _hidl_status; }

    _hidl_err = _hidl_reply.readBool(&_hidl_out_status);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&_hidl_out_status);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::CLIENT_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "isLsUpdateRequired", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    return ::android::hardware::Return<bool>(_hidl_out_status);

_hidl_error:
    _hidl_status.setFromStatusT(_hidl_err);
    return ::android::hardware::Return<bool>(_hidl_status);
}


// Methods from ::vendor::nxp::nxpnfc::V2_0::INxpNfc follow.
::android::hardware::Return<void> BpHwNxpNfc::getVendorParam(const ::android::hardware::hidl_string& key, getVendorParam_cb _hidl_cb){
    ::android::hardware::Return<void>  _hidl_out = ::vendor::nxp::nxpnfc::V2_0::BpHwNxpNfc::_hidl_getVendorParam(this, this, key, _hidl_cb);

    return _hidl_out;
}

::android::hardware::Return<bool> BpHwNxpNfc::setVendorParam(const ::android::hardware::hidl_string& key, const ::android::hardware::hidl_string& value){
    ::android::hardware::Return<bool>  _hidl_out = ::vendor::nxp::nxpnfc::V2_0::BpHwNxpNfc::_hidl_setVendorParam(this, this, key, value);

    return _hidl_out;
}

::android::hardware::Return<bool> BpHwNxpNfc::resetEse(uint64_t resetType){
    ::android::hardware::Return<bool>  _hidl_out = ::vendor::nxp::nxpnfc::V2_0::BpHwNxpNfc::_hidl_resetEse(this, this, resetType);

    return _hidl_out;
}

::android::hardware::Return<bool> BpHwNxpNfc::setEseUpdateState(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState eSEState){
    ::android::hardware::Return<bool>  _hidl_out = ::vendor::nxp::nxpnfc::V2_0::BpHwNxpNfc::_hidl_setEseUpdateState(this, this, eSEState);

    return _hidl_out;
}

::android::hardware::Return<bool> BpHwNxpNfc::setNxpTransitConfig(const ::android::hardware::hidl_string& transitConfValue){
    ::android::hardware::Return<bool>  _hidl_out = ::vendor::nxp::nxpnfc::V2_0::BpHwNxpNfc::_hidl_setNxpTransitConfig(this, this, transitConfValue);

    return _hidl_out;
}

::android::hardware::Return<bool> BpHwNxpNfc::isJcopUpdateRequired(){
    ::android::hardware::Return<bool>  _hidl_out = ::vendor::nxp::nxpnfc::V2_0::BpHwNxpNfc::_hidl_isJcopUpdateRequired(this, this);

    return _hidl_out;
}

::android::hardware::Return<bool> BpHwNxpNfc::isLsUpdateRequired(){
    ::android::hardware::Return<bool>  _hidl_out = ::vendor::nxp::nxpnfc::V2_0::BpHwNxpNfc::_hidl_isLsUpdateRequired(this, this);

    return _hidl_out;
}


// Methods from ::android::hidl::base::V1_0::IBase follow.
::android::hardware::Return<void> BpHwNxpNfc::interfaceChain(interfaceChain_cb _hidl_cb){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_interfaceChain(this, this, _hidl_cb);

    return _hidl_out;
}

::android::hardware::Return<void> BpHwNxpNfc::debug(const ::android::hardware::hidl_handle& fd, const ::android::hardware::hidl_vec<::android::hardware::hidl_string>& options){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_debug(this, this, fd, options);

    return _hidl_out;
}

::android::hardware::Return<void> BpHwNxpNfc::interfaceDescriptor(interfaceDescriptor_cb _hidl_cb){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_interfaceDescriptor(this, this, _hidl_cb);

    return _hidl_out;
}

::android::hardware::Return<void> BpHwNxpNfc::getHashChain(getHashChain_cb _hidl_cb){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_getHashChain(this, this, _hidl_cb);

    return _hidl_out;
}

::android::hardware::Return<void> BpHwNxpNfc::setHALInstrumentation(){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_setHALInstrumentation(this, this);

    return _hidl_out;
}

::android::hardware::Return<bool> BpHwNxpNfc::linkToDeath(const ::android::sp<::android::hardware::hidl_death_recipient>& recipient, uint64_t cookie){
    ::android::hardware::ProcessState::self()->startThreadPool();
    ::android::hardware::hidl_binder_death_recipient *binder_recipient = new ::android::hardware::hidl_binder_death_recipient(recipient, cookie, this);
    std::unique_lock<std::mutex> lock(_hidl_mMutex);
    _hidl_mDeathRecipients.push_back(binder_recipient);
    return (remote()->linkToDeath(binder_recipient) == ::android::OK);
}

::android::hardware::Return<void> BpHwNxpNfc::ping(){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_ping(this, this);

    return _hidl_out;
}

::android::hardware::Return<void> BpHwNxpNfc::getDebugInfo(getDebugInfo_cb _hidl_cb){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_getDebugInfo(this, this, _hidl_cb);

    return _hidl_out;
}

::android::hardware::Return<void> BpHwNxpNfc::notifySyspropsChanged(){
    ::android::hardware::Return<void>  _hidl_out = ::android::hidl::base::V1_0::BpHwBase::_hidl_notifySyspropsChanged(this, this);

    return _hidl_out;
}

::android::hardware::Return<bool> BpHwNxpNfc::unlinkToDeath(const ::android::sp<::android::hardware::hidl_death_recipient>& recipient){
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


BnHwNxpNfc::BnHwNxpNfc(const ::android::sp<INxpNfc> &_hidl_impl)
        : ::android::hidl::base::V1_0::BnHwBase(_hidl_impl, "vendor.nxp.nxpnfc@2.0", "INxpNfc") { 
            _hidl_mImpl = _hidl_impl;
            auto prio = ::android::hardware::getMinSchedulerPolicy(_hidl_impl);
            mSchedPolicy = prio.sched_policy;
            mSchedPriority = prio.prio;
            setRequestingSid(::android::hardware::getRequestingSid(_hidl_impl));
}

BnHwNxpNfc::~BnHwNxpNfc() {
    ::android::hardware::details::gBnMap->eraseIfEqual(_hidl_mImpl.get(), this);
}

// Methods from ::vendor::nxp::nxpnfc::V2_0::INxpNfc follow.
::android::status_t BnHwNxpNfc::_hidl_getVendorParam(
        ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
        const ::android::hardware::Parcel &_hidl_data,
        ::android::hardware::Parcel *_hidl_reply,
        TransactCallback _hidl_cb) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this->getInstrumentationCallbacks();
    #endif // __ANDROID_DEBUGGABLE__

    ::android::status_t _hidl_err = ::android::OK;
    if (!_hidl_data.enforceInterface(BnHwNxpNfc::Pure::descriptor)) {
        _hidl_err = ::android::BAD_TYPE;
        return _hidl_err;
    }

    const ::android::hardware::hidl_string* key;

    size_t _hidl_key_parent;

    _hidl_err = _hidl_data.readBuffer(sizeof(*key), &_hidl_key_parent,  reinterpret_cast<const void **>(&key));

    if (_hidl_err != ::android::OK) { return _hidl_err; }

    _hidl_err = ::android::hardware::readEmbeddedFromParcel(
            const_cast<::android::hardware::hidl_string &>(*key),
            _hidl_data,
            _hidl_key_parent,
            0 /* parentOffset */);

    if (_hidl_err != ::android::OK) { return _hidl_err; }

    atrace_begin(ATRACE_TAG_HAL, "HIDL::INxpNfc::getVendorParam::server");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)key);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "getVendorParam", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    bool _hidl_callbackCalled = false;

    ::android::hardware::Return<void> _hidl_ret = static_cast<INxpNfc*>(_hidl_this->getImpl().get())->getVendorParam(*key, [&](const auto &_hidl_out_value) {
        if (_hidl_callbackCalled) {
            LOG_ALWAYS_FATAL("getVendorParam: _hidl_cb called a second time, but must be called once.");
        }
        _hidl_callbackCalled = true;

        ::android::hardware::writeToParcel(::android::hardware::Status::ok(), _hidl_reply);

        size_t _hidl__hidl_out_value_parent;

        _hidl_err = _hidl_reply->writeBuffer(&_hidl_out_value, sizeof(_hidl_out_value), &_hidl__hidl_out_value_parent);
        if (_hidl_err != ::android::OK) { goto _hidl_error; }

        _hidl_err = ::android::hardware::writeEmbeddedToParcel(
                _hidl_out_value,
                _hidl_reply,
                _hidl__hidl_out_value_parent,
                0 /* parentOffset */);

        if (_hidl_err != ::android::OK) { goto _hidl_error; }

    _hidl_error:
        atrace_end(ATRACE_TAG_HAL);
        #ifdef __ANDROID_DEBUGGABLE__
        if (UNLIKELY(mEnableInstrumentation)) {
            std::vector<void *> _hidl_args;
            _hidl_args.push_back((void *)&_hidl_out_value);
            for (const auto &callback: mInstrumentationCallbacks) {
                callback(InstrumentationEvent::SERVER_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "getVendorParam", &_hidl_args);
            }
        }
        #endif // __ANDROID_DEBUGGABLE__

        if (_hidl_err != ::android::OK) { return; }
        _hidl_cb(*_hidl_reply);
    });

    _hidl_ret.assertOk();
    if (!_hidl_callbackCalled) {
        LOG_ALWAYS_FATAL("getVendorParam: _hidl_cb not called, but must be called once.");
    }

    return _hidl_err;
}

::android::status_t BnHwNxpNfc::_hidl_setVendorParam(
        ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
        const ::android::hardware::Parcel &_hidl_data,
        ::android::hardware::Parcel *_hidl_reply,
        TransactCallback _hidl_cb) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this->getInstrumentationCallbacks();
    #endif // __ANDROID_DEBUGGABLE__

    ::android::status_t _hidl_err = ::android::OK;
    if (!_hidl_data.enforceInterface(BnHwNxpNfc::Pure::descriptor)) {
        _hidl_err = ::android::BAD_TYPE;
        return _hidl_err;
    }

    const ::android::hardware::hidl_string* key;
    const ::android::hardware::hidl_string* value;

    size_t _hidl_key_parent;

    _hidl_err = _hidl_data.readBuffer(sizeof(*key), &_hidl_key_parent,  reinterpret_cast<const void **>(&key));

    if (_hidl_err != ::android::OK) { return _hidl_err; }

    _hidl_err = ::android::hardware::readEmbeddedFromParcel(
            const_cast<::android::hardware::hidl_string &>(*key),
            _hidl_data,
            _hidl_key_parent,
            0 /* parentOffset */);

    if (_hidl_err != ::android::OK) { return _hidl_err; }

    size_t _hidl_value_parent;

    _hidl_err = _hidl_data.readBuffer(sizeof(*value), &_hidl_value_parent,  reinterpret_cast<const void **>(&value));

    if (_hidl_err != ::android::OK) { return _hidl_err; }

    _hidl_err = ::android::hardware::readEmbeddedFromParcel(
            const_cast<::android::hardware::hidl_string &>(*value),
            _hidl_data,
            _hidl_value_parent,
            0 /* parentOffset */);

    if (_hidl_err != ::android::OK) { return _hidl_err; }

    atrace_begin(ATRACE_TAG_HAL, "HIDL::INxpNfc::setVendorParam::server");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)key);
        _hidl_args.push_back((void *)value);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "setVendorParam", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    bool _hidl_out_status = static_cast<INxpNfc*>(_hidl_this->getImpl().get())->setVendorParam(*key, *value);

    ::android::hardware::writeToParcel(::android::hardware::Status::ok(), _hidl_reply);

    _hidl_err = _hidl_reply->writeBool(_hidl_out_status);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

_hidl_error:
    atrace_end(ATRACE_TAG_HAL);
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&_hidl_out_status);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "setVendorParam", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    if (_hidl_err != ::android::OK) { return _hidl_err; }
    _hidl_cb(*_hidl_reply);
    return _hidl_err;
}

::android::status_t BnHwNxpNfc::_hidl_resetEse(
        ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
        const ::android::hardware::Parcel &_hidl_data,
        ::android::hardware::Parcel *_hidl_reply,
        TransactCallback _hidl_cb) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this->getInstrumentationCallbacks();
    #endif // __ANDROID_DEBUGGABLE__

    ::android::status_t _hidl_err = ::android::OK;
    if (!_hidl_data.enforceInterface(BnHwNxpNfc::Pure::descriptor)) {
        _hidl_err = ::android::BAD_TYPE;
        return _hidl_err;
    }

    uint64_t resetType;

    _hidl_err = _hidl_data.readUint64(&resetType);
    if (_hidl_err != ::android::OK) { return _hidl_err; }

    atrace_begin(ATRACE_TAG_HAL, "HIDL::INxpNfc::resetEse::server");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&resetType);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "resetEse", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    bool _hidl_out_status = static_cast<INxpNfc*>(_hidl_this->getImpl().get())->resetEse(resetType);

    ::android::hardware::writeToParcel(::android::hardware::Status::ok(), _hidl_reply);

    _hidl_err = _hidl_reply->writeBool(_hidl_out_status);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

_hidl_error:
    atrace_end(ATRACE_TAG_HAL);
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&_hidl_out_status);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "resetEse", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    if (_hidl_err != ::android::OK) { return _hidl_err; }
    _hidl_cb(*_hidl_reply);
    return _hidl_err;
}

::android::status_t BnHwNxpNfc::_hidl_setEseUpdateState(
        ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
        const ::android::hardware::Parcel &_hidl_data,
        ::android::hardware::Parcel *_hidl_reply,
        TransactCallback _hidl_cb) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this->getInstrumentationCallbacks();
    #endif // __ANDROID_DEBUGGABLE__

    ::android::status_t _hidl_err = ::android::OK;
    if (!_hidl_data.enforceInterface(BnHwNxpNfc::Pure::descriptor)) {
        _hidl_err = ::android::BAD_TYPE;
        return _hidl_err;
    }

    ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState eSEState;

    _hidl_err = _hidl_data.readUint64((uint64_t *)&eSEState);
    if (_hidl_err != ::android::OK) { return _hidl_err; }

    atrace_begin(ATRACE_TAG_HAL, "HIDL::INxpNfc::setEseUpdateState::server");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&eSEState);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "setEseUpdateState", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    bool _hidl_out_status = static_cast<INxpNfc*>(_hidl_this->getImpl().get())->setEseUpdateState(eSEState);

    ::android::hardware::writeToParcel(::android::hardware::Status::ok(), _hidl_reply);

    _hidl_err = _hidl_reply->writeBool(_hidl_out_status);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

_hidl_error:
    atrace_end(ATRACE_TAG_HAL);
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&_hidl_out_status);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "setEseUpdateState", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    if (_hidl_err != ::android::OK) { return _hidl_err; }
    _hidl_cb(*_hidl_reply);
    return _hidl_err;
}

::android::status_t BnHwNxpNfc::_hidl_setNxpTransitConfig(
        ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
        const ::android::hardware::Parcel &_hidl_data,
        ::android::hardware::Parcel *_hidl_reply,
        TransactCallback _hidl_cb) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this->getInstrumentationCallbacks();
    #endif // __ANDROID_DEBUGGABLE__

    ::android::status_t _hidl_err = ::android::OK;
    if (!_hidl_data.enforceInterface(BnHwNxpNfc::Pure::descriptor)) {
        _hidl_err = ::android::BAD_TYPE;
        return _hidl_err;
    }

    const ::android::hardware::hidl_string* transitConfValue;

    size_t _hidl_transitConfValue_parent;

    _hidl_err = _hidl_data.readBuffer(sizeof(*transitConfValue), &_hidl_transitConfValue_parent,  reinterpret_cast<const void **>(&transitConfValue));

    if (_hidl_err != ::android::OK) { return _hidl_err; }

    _hidl_err = ::android::hardware::readEmbeddedFromParcel(
            const_cast<::android::hardware::hidl_string &>(*transitConfValue),
            _hidl_data,
            _hidl_transitConfValue_parent,
            0 /* parentOffset */);

    if (_hidl_err != ::android::OK) { return _hidl_err; }

    atrace_begin(ATRACE_TAG_HAL, "HIDL::INxpNfc::setNxpTransitConfig::server");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)transitConfValue);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "setNxpTransitConfig", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    bool _hidl_out_status = static_cast<INxpNfc*>(_hidl_this->getImpl().get())->setNxpTransitConfig(*transitConfValue);

    ::android::hardware::writeToParcel(::android::hardware::Status::ok(), _hidl_reply);

    _hidl_err = _hidl_reply->writeBool(_hidl_out_status);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

_hidl_error:
    atrace_end(ATRACE_TAG_HAL);
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&_hidl_out_status);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "setNxpTransitConfig", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    if (_hidl_err != ::android::OK) { return _hidl_err; }
    _hidl_cb(*_hidl_reply);
    return _hidl_err;
}

::android::status_t BnHwNxpNfc::_hidl_isJcopUpdateRequired(
        ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
        const ::android::hardware::Parcel &_hidl_data,
        ::android::hardware::Parcel *_hidl_reply,
        TransactCallback _hidl_cb) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this->getInstrumentationCallbacks();
    #endif // __ANDROID_DEBUGGABLE__

    ::android::status_t _hidl_err = ::android::OK;
    if (!_hidl_data.enforceInterface(BnHwNxpNfc::Pure::descriptor)) {
        _hidl_err = ::android::BAD_TYPE;
        return _hidl_err;
    }

    atrace_begin(ATRACE_TAG_HAL, "HIDL::INxpNfc::isJcopUpdateRequired::server");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "isJcopUpdateRequired", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    bool _hidl_out_status = static_cast<INxpNfc*>(_hidl_this->getImpl().get())->isJcopUpdateRequired();

    ::android::hardware::writeToParcel(::android::hardware::Status::ok(), _hidl_reply);

    _hidl_err = _hidl_reply->writeBool(_hidl_out_status);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

_hidl_error:
    atrace_end(ATRACE_TAG_HAL);
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&_hidl_out_status);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "isJcopUpdateRequired", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    if (_hidl_err != ::android::OK) { return _hidl_err; }
    _hidl_cb(*_hidl_reply);
    return _hidl_err;
}

::android::status_t BnHwNxpNfc::_hidl_isLsUpdateRequired(
        ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
        const ::android::hardware::Parcel &_hidl_data,
        ::android::hardware::Parcel *_hidl_reply,
        TransactCallback _hidl_cb) {
    #ifdef __ANDROID_DEBUGGABLE__
    bool mEnableInstrumentation = _hidl_this->isInstrumentationEnabled();
    const auto &mInstrumentationCallbacks = _hidl_this->getInstrumentationCallbacks();
    #endif // __ANDROID_DEBUGGABLE__

    ::android::status_t _hidl_err = ::android::OK;
    if (!_hidl_data.enforceInterface(BnHwNxpNfc::Pure::descriptor)) {
        _hidl_err = ::android::BAD_TYPE;
        return _hidl_err;
    }

    atrace_begin(ATRACE_TAG_HAL, "HIDL::INxpNfc::isLsUpdateRequired::server");
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_ENTRY, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "isLsUpdateRequired", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    bool _hidl_out_status = static_cast<INxpNfc*>(_hidl_this->getImpl().get())->isLsUpdateRequired();

    ::android::hardware::writeToParcel(::android::hardware::Status::ok(), _hidl_reply);

    _hidl_err = _hidl_reply->writeBool(_hidl_out_status);
    if (_hidl_err != ::android::OK) { goto _hidl_error; }

_hidl_error:
    atrace_end(ATRACE_TAG_HAL);
    #ifdef __ANDROID_DEBUGGABLE__
    if (UNLIKELY(mEnableInstrumentation)) {
        std::vector<void *> _hidl_args;
        _hidl_args.push_back((void *)&_hidl_out_status);
        for (const auto &callback: mInstrumentationCallbacks) {
            callback(InstrumentationEvent::SERVER_API_EXIT, "vendor.nxp.nxpnfc", "2.0", "INxpNfc", "isLsUpdateRequired", &_hidl_args);
        }
    }
    #endif // __ANDROID_DEBUGGABLE__

    if (_hidl_err != ::android::OK) { return _hidl_err; }
    _hidl_cb(*_hidl_reply);
    return _hidl_err;
}


// Methods from ::vendor::nxp::nxpnfc::V2_0::INxpNfc follow.

// Methods from ::android::hidl::base::V1_0::IBase follow.
::android::hardware::Return<void> BnHwNxpNfc::ping() {
    return ::android::hardware::Void();
}
::android::hardware::Return<void> BnHwNxpNfc::getDebugInfo(getDebugInfo_cb _hidl_cb) {
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

::android::status_t BnHwNxpNfc::onTransact(
        uint32_t _hidl_code,
        const ::android::hardware::Parcel &_hidl_data,
        ::android::hardware::Parcel *_hidl_reply,
        uint32_t _hidl_flags,
        TransactCallback _hidl_cb) {
    ::android::status_t _hidl_err = ::android::OK;

    switch (_hidl_code) {
        case 1 /* getVendorParam */:
        {
            _hidl_err = ::vendor::nxp::nxpnfc::V2_0::BnHwNxpNfc::_hidl_getVendorParam(this, _hidl_data, _hidl_reply, _hidl_cb);
            break;
        }

        case 2 /* setVendorParam */:
        {
            _hidl_err = ::vendor::nxp::nxpnfc::V2_0::BnHwNxpNfc::_hidl_setVendorParam(this, _hidl_data, _hidl_reply, _hidl_cb);
            break;
        }

        case 3 /* resetEse */:
        {
            _hidl_err = ::vendor::nxp::nxpnfc::V2_0::BnHwNxpNfc::_hidl_resetEse(this, _hidl_data, _hidl_reply, _hidl_cb);
            break;
        }

        case 4 /* setEseUpdateState */:
        {
            _hidl_err = ::vendor::nxp::nxpnfc::V2_0::BnHwNxpNfc::_hidl_setEseUpdateState(this, _hidl_data, _hidl_reply, _hidl_cb);
            break;
        }

        case 5 /* setNxpTransitConfig */:
        {
            _hidl_err = ::vendor::nxp::nxpnfc::V2_0::BnHwNxpNfc::_hidl_setNxpTransitConfig(this, _hidl_data, _hidl_reply, _hidl_cb);
            break;
        }

        case 6 /* isJcopUpdateRequired */:
        {
            _hidl_err = ::vendor::nxp::nxpnfc::V2_0::BnHwNxpNfc::_hidl_isJcopUpdateRequired(this, _hidl_data, _hidl_reply, _hidl_cb);
            break;
        }

        case 7 /* isLsUpdateRequired */:
        {
            _hidl_err = ::vendor::nxp::nxpnfc::V2_0::BnHwNxpNfc::_hidl_isLsUpdateRequired(this, _hidl_data, _hidl_reply, _hidl_cb);
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

BsNxpNfc::BsNxpNfc(const ::android::sp<::vendor::nxp::nxpnfc::V2_0::INxpNfc> impl) : ::android::hardware::details::HidlInstrumentor("vendor.nxp.nxpnfc@2.0", "INxpNfc"), mImpl(impl) {
    mOnewayQueue.start(3000 /* similar limit to binderized */);
}

::android::hardware::Return<void> BsNxpNfc::addOnewayTask(std::function<void(void)> fun) {
    if (!mOnewayQueue.push(fun)) {
        return ::android::hardware::Status::fromExceptionCode(
                ::android::hardware::Status::EX_TRANSACTION_FAILED,
                "Passthrough oneway function queue exceeds maximum size.");
    }
    return ::android::hardware::Status();
}

::android::sp<INxpNfc> INxpNfc::tryGetService(const std::string &serviceName, const bool getStub) {
    return ::android::hardware::details::getServiceInternal<BpHwNxpNfc>(serviceName, false, getStub);
}

::android::sp<INxpNfc> INxpNfc::getService(const std::string &serviceName, const bool getStub) {
    return ::android::hardware::details::getServiceInternal<BpHwNxpNfc>(serviceName, true, getStub);
}

::android::status_t INxpNfc::registerAsService(const std::string &serviceName) {
    return ::android::hardware::details::registerAsServiceInternal(this, serviceName);
}

bool INxpNfc::registerForNotifications(
        const std::string &serviceName,
        const ::android::sp<::android::hidl::manager::V1_0::IServiceNotification> &notification) {
    const ::android::sp<::android::hidl::manager::V1_0::IServiceManager> sm
            = ::android::hardware::defaultServiceManager();
    if (sm == nullptr) {
        return false;
    }
    ::android::hardware::Return<bool> success =
            sm->registerForNotifications("vendor.nxp.nxpnfc@2.0::INxpNfc",
                    serviceName, notification);
    return success.isOk() && success;
}

static_assert(sizeof(::android::hardware::MQDescriptor<char, ::android::hardware::kSynchronizedReadWrite>) == 32, "wrong size");
static_assert(sizeof(::android::hardware::hidl_handle) == 16, "wrong size");
static_assert(sizeof(::android::hardware::hidl_memory) == 40, "wrong size");
static_assert(sizeof(::android::hardware::hidl_string) == 16, "wrong size");
static_assert(sizeof(::android::hardware::hidl_vec<char>) == 16, "wrong size");

}  // namespace V2_0
}  // namespace nxpnfc
}  // namespace nxp
}  // namespace vendor
