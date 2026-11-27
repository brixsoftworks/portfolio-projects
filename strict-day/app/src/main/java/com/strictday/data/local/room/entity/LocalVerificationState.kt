package com.strictday.data.local.room.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "verification_state")
data class LocalVerificationState(
    @PrimaryKey val taskId: String,
    val provider: String,
    val isVerified: Boolean,
    val lastCheckedAt: Long,
    val eventsJson: String
)
