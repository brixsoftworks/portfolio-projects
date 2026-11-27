package com.strictday.domain.model

import kotlinx.datetime.Instant

data class Task(
    val id: String,
    val scheduleId: String,
    val title: String,
    val description: String,
    val startsAt: Instant,
    val endsAt: Instant,
    val strictness: Strictness,
    val status: TaskStatus,
    val orderIndex: Int,
    val allowedApps: List<String>,
    val blockedApps: List<String>,
    val createdAt: Instant
) {
    val durationMinutes: Long
        get() = (endsAt - startsAt).inWholeMinutes

    val isActive: Boolean
        get() = status == TaskStatus.ACTIVE

    val isVerificationRequired: Boolean
        get() = strictness == Strictness.STRICT || strictness == Strictness.IRON
}
