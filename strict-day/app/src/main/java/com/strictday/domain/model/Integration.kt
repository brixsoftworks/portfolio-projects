package com.strictday.domain.model

import kotlinx.datetime.Instant

data class Integration(
    val id: String,
    val userId: String,
    val provider: VerificationProvider,
    val status: IntegrationStatus,
    val scopes: List<String>,
    val metadata: Map<String, String>,
    val createdAt: Instant
)
