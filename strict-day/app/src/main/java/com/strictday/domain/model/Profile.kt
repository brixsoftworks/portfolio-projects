package com.strictday.domain.model

import kotlinx.datetime.Instant

data class Profile(
    val id: String,
    val displayName: String,
    val timezone: String,
    val createdAt: Instant
)
