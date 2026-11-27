package com.strictday.data.local.room.entity

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "verification_rules",
    foreignKeys = [
        ForeignKey(
            entity = LocalTask::class,
            parentColumns = ["id"],
            childColumns = ["taskId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("taskId")]
)
data class LocalVerificationRule(
    @PrimaryKey val id: String,
    val taskId: String,
    val provider: String,
    val eventType: String,
    val operator: String,
    val targetValue: String,
    val minCount: Int,
    val minDurationSeconds: Long,
    val createdAt: Long
)
