package com.strictday.enforcement

data class DeviceState(
    val isActive: Boolean,
    val currentForegroundApp: String?,
    val currentPolicy: EnforcementPolicy?,
    val capabilities: DeviceCapabilitiesReport
)

data class DeviceCapabilitiesReport(
    val canRestrictApps: String,
    val canUseUsageStats: String,
    val canUseAccessibility: String,
    val isDeviceOwner: String,
    val canUseLockTask: String,
    val canControlNotifications: String
) {
    companion object {
        const val SUPPORTED = "SUPPORTED"
        const val PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
        const val REQUIRES_DEVICE_OWNER = "REQUIRES_DEVICE_OWNER"
        const val REQUIRES_USER_PERMISSION = "REQUIRES_USER_PERMISSION"
        const val NOT_AVAILABLE = "NOT_AVAILABLE"
    }
}