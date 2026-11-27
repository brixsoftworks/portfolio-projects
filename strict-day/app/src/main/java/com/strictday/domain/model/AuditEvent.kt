package com.strictday.domain.model

import kotlinx.datetime.Instant

data class AuditEvent(
    val id: String,
    val userId: String,
    val deviceId: String,
    val taskId: String?,
    val type: AuditEventType,
    val payload: Map<String, Any>,
    val createdAt: Instant
)
