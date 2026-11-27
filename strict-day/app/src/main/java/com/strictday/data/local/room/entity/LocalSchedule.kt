package com.strictday.data.local.room.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "schedules")
data class LocalSchedule(
    @PrimaryKey val id: String,
    val userId: String,
    val localDate: String,
    val status: String,
    val createdAt: Long
)
