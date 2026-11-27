package com.strictday.data.local.room.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "audit_events",
    indices = [Index("userId"), Index("taskId")]
)
data class LocalAuditEvent(
    @PrimaryKey val id: String,
    val userId: String,
    val deviceId: String,
    val taskId: String?,
    val type: String,
    val payload: String,
    val createdAt: Long
)
