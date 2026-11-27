package com.strictday.data.local.room.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "device_policies")
data class LocalDevicePolicy(
    @PrimaryKey val id: String,
    val userId: String,
    val taskId: String,
    val deviceId: String,
    val mode: String,
    val allowedPackages: String,
    val blockedPackages: String,
    val status: String,
    val startTime: Long,
    val endTime: Long,
    val unlockCondition: String,
    val emergencyAccessAllowed: Boolean,
    val activatedAt: Long?,
    val releasedAt: Long?
)
