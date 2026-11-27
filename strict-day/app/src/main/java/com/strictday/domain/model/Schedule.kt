package com.strictday.domain.model

import kotlinx.datetime.Instant
import kotlinx.datetime.LocalDate

data class Schedule(
    val id: String,
    val userId: String,
    val localDate: LocalDate,
    val status: ScheduleStatus,
    val createdAt: Instant
)
