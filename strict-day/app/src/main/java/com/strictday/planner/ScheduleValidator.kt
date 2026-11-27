package com.strictday.planner

import com.strictday.domain.model.ScheduledTask
import kotlinx.datetime.Instant
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ScheduleValidator @Inject constructor() {

    data class ValidationResult(
        val hasOverlaps: Boolean,
        val overlapDetails: List<OverlapDetail>,
        val warnings: List<String>,
        val isValid: Boolean
    )

    data class OverlapDetail(
        val taskA: String,
        val taskB: String,
        val overlapStart: Instant,
        val overlapEnd: Instant
    )

    fun validate(scheduledTasks: List<ScheduledTask>): ValidationResult {
        val sorted = scheduledTasks.sortedBy { it.startsAt.toEpochMilliseconds() }
        val overlaps = mutableListOf<OverlapDetail>()
        val warnings = mutableListOf<String>()

        for (i in sorted.indices) {
            val current = sorted[i]
            for (j in i + 1 until sorted.size) {
                val other = sorted[j]
                val otherStart = other.startsAt
                val currentEnd = current.endsAt
                if (currentEnd > otherStart) {
                    val overlapStart = otherStart
                    val overlapEnd = minOf(currentEnd, other.endsAt)
                    overlaps.add(
                        OverlapDetail(
                            taskA = current.task.title,
                            taskB = other.task.title,
                            overlapStart = overlapStart,
                            overlapEnd = overlapEnd
                        )
                    )
                }
            }
        }

        scheduledTasks.forEach {
            if (it.endsAt <= it.startsAt) {
                warnings.add("Task '${it.task.title}' has zero or negative duration")
            }
        }

        return ValidationResult(
            hasOverlaps = overlaps.isNotEmpty(),
            overlapDetails = overlaps,
            warnings = warnings,
            isValid = overlaps.isEmpty() && warnings.isEmpty()
        )
    }
}
