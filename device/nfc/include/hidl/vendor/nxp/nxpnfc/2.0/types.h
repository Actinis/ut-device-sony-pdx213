#ifndef HIDL_GENERATED_VENDOR_NXP_NXPNFC_V2_0_TYPES_H
#define HIDL_GENERATED_VENDOR_NXP_NXPNFC_V2_0_TYPES_H

#include <hidl/HidlSupport.h>
#include <hidl/MQDescriptor.h>
#include <utils/NativeHandle.h>
#include <utils/misc.h>

namespace vendor {
namespace nxp {
namespace nxpnfc {
namespace V2_0 {

// Forward declaration for forward reference support:
enum class NxpNfcHalEseState : uint64_t;

enum class NxpNfcHalEseState : uint64_t {
    HAL_NFC_ESE_UPDATE_COMPLETED = 0ull,
    HAL_NFC_ESE_UPDATE_STARTED = 1ull /* ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState.HAL_NFC_ESE_UPDATE_COMPLETED implicitly + 1 */,
    HAL_NFC_ESE_JCOP_UPDATE_REQUIRED = 2ull /* ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState.HAL_NFC_ESE_UPDATE_STARTED implicitly + 1 */,
    HAL_NFC_ESE_JCOP_UPDATE_COMPLETED = 3ull /* ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState.HAL_NFC_ESE_JCOP_UPDATE_REQUIRED implicitly + 1 */,
    HAL_NFC_ESE_LS_UPDATE_REQUIRED = 4ull /* ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState.HAL_NFC_ESE_JCOP_UPDATE_COMPLETED implicitly + 1 */,
    HAL_NFC_ESE_LS_UPDATE_COMPLETED = 5ull /* ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState.HAL_NFC_ESE_LS_UPDATE_REQUIRED implicitly + 1 */,
};

//
// type declarations for package
//

template<typename>
static inline std::string toString(uint64_t o);
static inline std::string toString(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState o);
static inline void PrintTo(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState o, ::std::ostream* os);
constexpr uint64_t operator|(const ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState lhs, const ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState rhs) {
    return static_cast<uint64_t>(static_cast<uint64_t>(lhs) | static_cast<uint64_t>(rhs));
}
constexpr uint64_t operator|(const uint64_t lhs, const ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState rhs) {
    return static_cast<uint64_t>(lhs | static_cast<uint64_t>(rhs));
}
constexpr uint64_t operator|(const ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState lhs, const uint64_t rhs) {
    return static_cast<uint64_t>(static_cast<uint64_t>(lhs) | rhs);
}
constexpr uint64_t operator&(const ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState lhs, const ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState rhs) {
    return static_cast<uint64_t>(static_cast<uint64_t>(lhs) & static_cast<uint64_t>(rhs));
}
constexpr uint64_t operator&(const uint64_t lhs, const ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState rhs) {
    return static_cast<uint64_t>(lhs & static_cast<uint64_t>(rhs));
}
constexpr uint64_t operator&(const ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState lhs, const uint64_t rhs) {
    return static_cast<uint64_t>(static_cast<uint64_t>(lhs) & rhs);
}
constexpr uint64_t &operator|=(uint64_t& v, const ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState e) {
    v |= static_cast<uint64_t>(e);
    return v;
}
constexpr uint64_t &operator&=(uint64_t& v, const ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState e) {
    v &= static_cast<uint64_t>(e);
    return v;
}

//
// type header definitions for package
//

template<>
inline std::string toString<::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState>(uint64_t o) {
    using ::android::hardware::details::toHexString;
    std::string os;
    ::android::hardware::hidl_bitfield<::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState> flipped = 0;
    bool first = true;
    if ((o & ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_UPDATE_COMPLETED) == static_cast<uint64_t>(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_UPDATE_COMPLETED)) {
        os += (first ? "" : " | ");
        os += "HAL_NFC_ESE_UPDATE_COMPLETED";
        first = false;
        flipped |= ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_UPDATE_COMPLETED;
    }
    if ((o & ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_UPDATE_STARTED) == static_cast<uint64_t>(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_UPDATE_STARTED)) {
        os += (first ? "" : " | ");
        os += "HAL_NFC_ESE_UPDATE_STARTED";
        first = false;
        flipped |= ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_UPDATE_STARTED;
    }
    if ((o & ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_JCOP_UPDATE_REQUIRED) == static_cast<uint64_t>(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_JCOP_UPDATE_REQUIRED)) {
        os += (first ? "" : " | ");
        os += "HAL_NFC_ESE_JCOP_UPDATE_REQUIRED";
        first = false;
        flipped |= ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_JCOP_UPDATE_REQUIRED;
    }
    if ((o & ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_JCOP_UPDATE_COMPLETED) == static_cast<uint64_t>(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_JCOP_UPDATE_COMPLETED)) {
        os += (first ? "" : " | ");
        os += "HAL_NFC_ESE_JCOP_UPDATE_COMPLETED";
        first = false;
        flipped |= ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_JCOP_UPDATE_COMPLETED;
    }
    if ((o & ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_LS_UPDATE_REQUIRED) == static_cast<uint64_t>(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_LS_UPDATE_REQUIRED)) {
        os += (first ? "" : " | ");
        os += "HAL_NFC_ESE_LS_UPDATE_REQUIRED";
        first = false;
        flipped |= ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_LS_UPDATE_REQUIRED;
    }
    if ((o & ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_LS_UPDATE_COMPLETED) == static_cast<uint64_t>(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_LS_UPDATE_COMPLETED)) {
        os += (first ? "" : " | ");
        os += "HAL_NFC_ESE_LS_UPDATE_COMPLETED";
        first = false;
        flipped |= ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_LS_UPDATE_COMPLETED;
    }
    if (o != flipped) {
        os += (first ? "" : " | ");
        os += toHexString(o & (~flipped));
    }os += " (";
    os += toHexString(o);
    os += ")";
    return os;
}

static inline std::string toString(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState o) {
    using ::android::hardware::details::toHexString;
    if (o == ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_UPDATE_COMPLETED) {
        return "HAL_NFC_ESE_UPDATE_COMPLETED";
    }
    if (o == ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_UPDATE_STARTED) {
        return "HAL_NFC_ESE_UPDATE_STARTED";
    }
    if (o == ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_JCOP_UPDATE_REQUIRED) {
        return "HAL_NFC_ESE_JCOP_UPDATE_REQUIRED";
    }
    if (o == ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_JCOP_UPDATE_COMPLETED) {
        return "HAL_NFC_ESE_JCOP_UPDATE_COMPLETED";
    }
    if (o == ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_LS_UPDATE_REQUIRED) {
        return "HAL_NFC_ESE_LS_UPDATE_REQUIRED";
    }
    if (o == ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_LS_UPDATE_COMPLETED) {
        return "HAL_NFC_ESE_LS_UPDATE_COMPLETED";
    }
    std::string os;
    os += toHexString(static_cast<uint64_t>(o));
    return os;
}

static inline void PrintTo(::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState o, ::std::ostream* os) {
    *os << toString(o);
}


}  // namespace V2_0
}  // namespace nxpnfc
}  // namespace nxp
}  // namespace vendor

//
// global type declarations for package
//

namespace android {
namespace hardware {
namespace details {
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wc++17-extensions"
template<> inline constexpr std::array<::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState, 6> hidl_enum_values<::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState> = {
    ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_UPDATE_COMPLETED,
    ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_UPDATE_STARTED,
    ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_JCOP_UPDATE_REQUIRED,
    ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_JCOP_UPDATE_COMPLETED,
    ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_LS_UPDATE_REQUIRED,
    ::vendor::nxp::nxpnfc::V2_0::NxpNfcHalEseState::HAL_NFC_ESE_LS_UPDATE_COMPLETED,
};
#pragma clang diagnostic pop
}  // namespace details
}  // namespace hardware
}  // namespace android


#endif  // HIDL_GENERATED_VENDOR_NXP_NXPNFC_V2_0_TYPES_H
