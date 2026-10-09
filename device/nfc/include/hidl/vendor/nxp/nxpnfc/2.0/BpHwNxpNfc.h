#ifndef HIDL_GENERATED_VENDOR_NXP_NXPNFC_V2_0_BPHWNXPNFC_H
#define HIDL_GENERATED_VENDOR_NXP_NXPNFC_V2_0_BPHWNXPNFC_H

#include <hidl/HidlTransportSupport.h>

#include <vendor/nxp/nxpnfc/2.0/IHwNxpNfc.h>

#include <mutex>
namespace vendor {
namespace nxp {
namespace nxpnfc {
namespace V2_0 {

struct BpHwNxpNfc : public ::android::hardware::BpInterface<INxpNfc>, public ::android::hardware::details::HidlInstrumentor {
    explicit BpHwNxpNfc(const ::android::sp<::android::hardware::IBinder> &_hidl_impl);

    /**
     * The pure class is what this class wraps.
     */
    typedef INxpNfc Pure;

    /**
     * Type tag for use in template logic that indicates this is a 'proxy' class.
     */
    typedef ::android::hardware::details::bphw_tag _hidl_tag;

    virtual bool isRemote() const override { return true; }

    void onLastStrongRef(const void* id) override;

    // Methods from ::vendor::nxp::nxpnfc::V2_0::INxpNfc follow.
    static ::android::hardware::Return<void>  _hidl_getVendorParam(::android::hardware::IInterface* _hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor, const ::android::hardware::hidl_string& key, getVendorParam_cb _hidl_cb);
    static ::android::hardware::Return<bool>  _hidl_setVendorParam(::android::hardware::IInterface* _hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor, const ::android::hardware::hidl_string& key, const ::android::hardware::hidl_string& value);
    static ::android::hardware::Return<bool>  _hidl_resetEse(::android::hardware::IInterface* _hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor, uint64_t resetType);
    static ::android::hardware::Return<bool>  _hidl_setEseUpdateState(::android::hardware::IInterface* _hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor, ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState eSEState);
    static ::android::hardware::Return<bool>  _hidl_setNxpTransitConfig(::android::hardware::IInterface* _hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor, const ::android::hardware::hidl_string& transitConfValue);
    static ::android::hardware::Return<bool>  _hidl_isJcopUpdateRequired(::android::hardware::IInterface* _hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor);
    static ::android::hardware::Return<bool>  _hidl_isLsUpdateRequired(::android::hardware::IInterface* _hidl_this, ::android::hardware::details::HidlInstrumentor *_hidl_this_instrumentor);

    // Methods from ::vendor::nxp::nxpnfc::V2_0::INxpNfc follow.
    ::android::hardware::Return<void> getVendorParam(const ::android::hardware::hidl_string& key, getVendorParam_cb _hidl_cb) override;
    ::android::hardware::Return<bool> setVendorParam(const ::android::hardware::hidl_string& key, const ::android::hardware::hidl_string& value) override;
    ::android::hardware::Return<bool> resetEse(uint64_t resetType) override;
    ::android::hardware::Return<bool> setEseUpdateState(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState eSEState) override;
    ::android::hardware::Return<bool> setNxpTransitConfig(const ::android::hardware::hidl_string& transitConfValue) override;
    ::android::hardware::Return<bool> isJcopUpdateRequired() override;
    ::android::hardware::Return<bool> isLsUpdateRequired() override;

    // Methods from ::android::hidl::base::V1_0::IBase follow.
    ::android::hardware::Return<void> interfaceChain(interfaceChain_cb _hidl_cb) override;
    ::android::hardware::Return<void> debug(const ::android::hardware::hidl_handle& fd, const ::android::hardware::hidl_vec<::android::hardware::hidl_string>& options) override;
    ::android::hardware::Return<void> interfaceDescriptor(interfaceDescriptor_cb _hidl_cb) override;
    ::android::hardware::Return<void> getHashChain(getHashChain_cb _hidl_cb) override;
    ::android::hardware::Return<void> setHALInstrumentation() override;
    ::android::hardware::Return<bool> linkToDeath(const ::android::sp<::android::hardware::hidl_death_recipient>& recipient, uint64_t cookie) override;
    ::android::hardware::Return<void> ping() override;
    ::android::hardware::Return<void> getDebugInfo(getDebugInfo_cb _hidl_cb) override;
    ::android::hardware::Return<void> notifySyspropsChanged() override;
    ::android::hardware::Return<bool> unlinkToDeath(const ::android::sp<::android::hardware::hidl_death_recipient>& recipient) override;

private:
    std::mutex _hidl_mMutex;
    std::vector<::android::sp<::android::hardware::hidl_binder_death_recipient>> _hidl_mDeathRecipients;
};

}  // namespace V2_0
}  // namespace nxpnfc
}  // namespace nxp
}  // namespace vendor

#endif  // HIDL_GENERATED_VENDOR_NXP_NXPNFC_V2_0_BPHWNXPNFC_H
