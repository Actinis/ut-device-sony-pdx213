#ifndef HIDL_GENERATED_VENDOR_NXP_NXPNFC_V2_0_BNHWNXPNFC_H
#define HIDL_GENERATED_VENDOR_NXP_NXPNFC_V2_0_BNHWNXPNFC_H

#include <vendor/nxp/nxpnfc/2.0/IHwNxpNfc.h>

namespace vendor {
namespace nxp {
namespace nxpnfc {
namespace V2_0 {

struct BnHwNxpNfc : public ::android::hidl::base::V1_0::BnHwBase {
    explicit BnHwNxpNfc(const ::android::sp<INxpNfc> &_hidl_impl);
    explicit BnHwNxpNfc(const ::android::sp<INxpNfc> &_hidl_impl, const std::string& HidlInstrumentor_package, const std::string& HidlInstrumentor_interface);

    virtual ~BnHwNxpNfc();

    ::android::status_t onTransact(
            uint32_t _hidl_code,
            const ::android::hardware::Parcel &_hidl_data,
            ::android::hardware::Parcel *_hidl_reply,
            uint32_t _hidl_flags = 0,
            TransactCallback _hidl_cb = nullptr) override;


    /**
     * The pure class is what this class wraps.
     */
    typedef INxpNfc Pure;

    /**
     * Type tag for use in template logic that indicates this is a 'native' class.
     */
    typedef ::android::hardware::details::bnhw_tag _hidl_tag;

    ::android::sp<INxpNfc> getImpl() { return _hidl_mImpl; }
    // Methods from ::vendor::nxp::nxpnfc::V2_0::INxpNfc follow.
    static ::android::status_t _hidl_getVendorParam(
            ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
            const ::android::hardware::Parcel &_hidl_data,
            ::android::hardware::Parcel *_hidl_reply,
            TransactCallback _hidl_cb);


    static ::android::status_t _hidl_setVendorParam(
            ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
            const ::android::hardware::Parcel &_hidl_data,
            ::android::hardware::Parcel *_hidl_reply,
            TransactCallback _hidl_cb);


    static ::android::status_t _hidl_resetEse(
            ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
            const ::android::hardware::Parcel &_hidl_data,
            ::android::hardware::Parcel *_hidl_reply,
            TransactCallback _hidl_cb);


    static ::android::status_t _hidl_setEseUpdateState(
            ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
            const ::android::hardware::Parcel &_hidl_data,
            ::android::hardware::Parcel *_hidl_reply,
            TransactCallback _hidl_cb);


    static ::android::status_t _hidl_setNxpTransitConfig(
            ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
            const ::android::hardware::Parcel &_hidl_data,
            ::android::hardware::Parcel *_hidl_reply,
            TransactCallback _hidl_cb);


    static ::android::status_t _hidl_isJcopUpdateRequired(
            ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
            const ::android::hardware::Parcel &_hidl_data,
            ::android::hardware::Parcel *_hidl_reply,
            TransactCallback _hidl_cb);


    static ::android::status_t _hidl_isLsUpdateRequired(
            ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
            const ::android::hardware::Parcel &_hidl_data,
            ::android::hardware::Parcel *_hidl_reply,
            TransactCallback _hidl_cb);



private:
    // Methods from ::vendor::nxp::nxpnfc::V2_0::INxpNfc follow.

    // Methods from ::android::hidl::base::V1_0::IBase follow.
    ::android::hardware::Return<void> ping();
    using getDebugInfo_cb = ::android::hidl::base::V1_0::IBase::getDebugInfo_cb;
    ::android::hardware::Return<void> getDebugInfo(getDebugInfo_cb _hidl_cb);

    ::android::sp<INxpNfc> _hidl_mImpl;
};

}  // namespace V2_0
}  // namespace nxpnfc
}  // namespace nxp
}  // namespace vendor

#endif  // HIDL_GENERATED_VENDOR_NXP_NXPNFC_V2_0_BNHWNXPNFC_H
