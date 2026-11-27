package com.strictday.domain.model

import kotlinx.datetime.Instant

data class NormalizedVerificationEvent(
    val provider: VerificationProvider,
    val eventType: String,
    val externalId: String,
    val occurredAt: Instant,
    val subject: String,
    val metrics: Map<String, Any>
)
