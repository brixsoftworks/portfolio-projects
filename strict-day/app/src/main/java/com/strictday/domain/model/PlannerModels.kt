package com.strictday.domain.model

import kotlinx.datetime.Instant
import kotlinx.datetime.LocalDate

data class PlannerInput(
    val date: LocalDate,
    val timezone: String,
    val sleepStart: String,
    val sleepEnd: String,
    val fixedCommitments: List<FixedCommitment>,
    val goals: List<String>,
    val tasks: List<PlannerTask>,
    val estimatedDurations: Map<String, Long>,
    val priorities: Map<String, Int>,
    val deadlines: Map<String, Instant>,
    val preferredFocusWindows: List<TimeWindow>,
    val travelBuffers: Long,
    val historicalDurations: Map<String, List<Long>>
)

data class FixedCommitment(
    val title: String,
    val startTime: Instant,
    val endTime: Instant
)

data class PlannerTask(
    val title: String,
    val description: String,
    val estimatedDurationMinutes: Long,
    val priority: Int,
    val strictness: Strictness,
    val deadline: Instant?,
    val allowedApps: List<String>,
    val blockedApps: List<String>
)

data class TimeWindow(
    val startHour: Int,
    val endHour: Int
)

data class PlannerResult(
    val scheduledTasks: List<ScheduledTask>,
    val warnings: List<String>,
    val assumptions: List<String>,
    val unscheduledTasks: List<PlannerTask>
)

data class ScheduledTask(
    val task: PlannerTask,
    val startsAt: Instant,
    val endsAt: Instant
)
