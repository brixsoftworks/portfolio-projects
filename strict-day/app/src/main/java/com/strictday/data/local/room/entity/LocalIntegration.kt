package com.strictday.data.local.room.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "integrations")
data class LocalIntegration(
    @PrimaryKey val id: String,
    val userId: String,
    val provider: String,
    val status: String,
    val scopes: String,
    val metadataJson: String,
    val createdAt: Long
)
