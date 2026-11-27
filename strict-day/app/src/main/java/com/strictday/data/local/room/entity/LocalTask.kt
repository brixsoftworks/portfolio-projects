package com.strictday.data.local.room.entity

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "tasks",
    foreignKeys = [
        ForeignKey(
            entity = LocalSchedule::class,
            parentColumns = ["id"],
            childColumns = ["scheduleId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("scheduleId"), Index("status")]
)
data class LocalTask(
    @PrimaryKey val id: String,
    val scheduleId: String,
    val title: String,
    val description: String,
    val startsAt: Long,
    val endsAt: Long,
    val strictness: String,
    val status: String,
    val orderIndex: Int,
    val allowedApps: String,
    val blockedApps: String,
    val createdAt: Long
)
