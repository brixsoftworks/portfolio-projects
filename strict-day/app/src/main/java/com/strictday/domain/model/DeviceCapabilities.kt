package com.strictday.domain.model

data class DeviceCapabilities(
    val canRestrictApps: CapabilityStatus,
    val canUseUsageStats: CapabilityStatus,
    val canUseAccessibility: CapabilityStatus,
    val isDeviceOwner: CapabilityStatus,
    val canUseLockTask: CapabilityStatus,
    val canControlNotifications: CapabilityStatus,
    val canDrawOverlays: CapabilityStatus
)
