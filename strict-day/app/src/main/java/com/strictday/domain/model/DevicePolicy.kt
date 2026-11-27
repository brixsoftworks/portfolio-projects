package com.strictday.domain.model

import kotlinx.datetime.Instant

data class DevicePolicy(
    val id: String,
    val userId: String,
    val taskId: String,
    val deviceId: String,
    val mode: DevicePolicyMode,
    val allowedPackages: List<String>,
    val blockedPackages: List<String>,
    val status: DevicePolicyStatus,
    val startTime: Instant,
    val endTime: Instant,
    val unlockCondition: String,
    val emergencyAccessAllowed: Boolean,
    val activatedAt: Instant?,
    val releasedAt: Instant?
)
