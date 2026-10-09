#ifndef HIDL_GENERATED_VENDOR_NXP_NXPESE_V1_0_BNHWNXPESE_H
#define HIDL_GENERATED_VENDOR_NXP_NXPESE_V1_0_BNHWNXPESE_H

#include <vendor/nxp/nxpese/1.0/IHwNxpEse.h>

namespace vendor {
namespace nxp {
namespace nxpese {
namespace V1_0 {

struct BnHwNxpEse : public ::android::hidl::base::V1_0::BnHwBase {
    explicit BnHwNxpEse(const ::android::sp<INxpEse> &_hidl_impl);
    explicit BnHwNxpEse(const ::android::sp<INxpEse> &_hidl_impl, const std::string& HidlInstrumentor_package, const std::string& HidlInstrumentor_interface);

    virtual ~BnHwNxpEse();

    ::android::status_t onTransact(
            uint32_t _hidl_code,
            const ::android::hardware::Parcel &_hidl_data,
            ::android::hardware::Parcel *_hidl_reply,
            uint32_t _hidl_flags = 0,
            TransactCallback _hidl_cb = nullptr) override;


    /**
     * The pure class is what this class wraps.
     */
    typedef INxpEse Pure;

    /**
     * Type tag for use in template logic that indicates this is a 'native' class.
     */
    typedef ::android::hardware::details::bnhw_tag _hidl_tag;

    ::android::sp<INxpEse> getImpl() { return _hidl_mImpl; }
    // Methods from ::vendor::nxp::nxpese::V1_0::INxpEse follow.
    static ::android::status_t _hidl_ioctl(
            ::android::hidl::base::V1_0::BnHwBase* _hidl_this,
            const ::android::hardware::Parcel &_hidl_data,
            ::android::hardware::Parcel *_hidl_reply,
            TransactCallback _hidl_cb);



private:
    // Methods from ::vendor::nxp::nxpese::V1_0::INxpEse follow.

    // Methods from ::android::hidl::base::V1_0::IBase follow.
    ::android::hardware::Return<void> ping();
    using getDebugInfo_cb = ::android::hidl::base::V1_0::IBase::getDebugInfo_cb;
    ::android::hardware::Return<void> getDebugInfo(getDebugInfo_cb _hidl_cb);

    ::android::sp<INxpEse> _hidl_mImpl;
};

}  // namespace V1_0
}  // namespace nxpese
}  // namespace nxp
}  // namespace vendor

#endif  // HIDL_GENERATED_VENDOR_NXP_NXPESE_V1_0_BNHWNXPESE_H
