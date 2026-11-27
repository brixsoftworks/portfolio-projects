package com.strictday.domain.model

import kotlinx.datetime.Instant

data class VerificationEvent(
    val id: String,
    val userId: String,
    val taskId: String,
    val provider: VerificationProvider,
    val eventType: String,
    val externalId: String,
    val payload: Map<String, Any>,
    val occurredAt: Instant,
    val receivedAt: Instant
)
