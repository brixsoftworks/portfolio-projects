package com.strictday.domain.model

import kotlinx.datetime.Instant

data class VerificationRule(
    val id: String,
    val taskId: String,
    val provider: VerificationProvider,
    val eventType: String,
    val operator: VerificationOperator,
    val targetValue: String,
    val minCount: Int = 0,
    val minDurationSeconds: Long = 0,
    val createdAt: Instant
)
