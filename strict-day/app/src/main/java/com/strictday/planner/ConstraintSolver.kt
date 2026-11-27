package com.strictday.planner

import com.strictday.domain.model.FixedCommitment
import com.strictday.domain.model.PlannerInput
import com.strictday.domain.model.PlannerResult
import com.strictday.domain.model.PlannerTask
import com.strictday.domain.model.ScheduledTask
import kotlinx.datetime.Instant
import kotlinx.datetime.LocalDate
import kotlinx.datetime.LocalDateTime
import kotlinx.datetime.LocalTime
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toInstant
import kotlinx.datetime.toLocalDateTime
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ConstraintSolver @Inject constructor() {

    fun solve(input: PlannerInput): PlannerResult {
        val timezone = TimeZone.of(input.timezone)
        val date = input.date

        val freeWindows = mutableListOf<TimeSlot>()
        val scheduled = mutableListOf<ScheduledTask>()
        val warnings = mutableListOf<String>()
        val assumptions = mutableListOf<String>()
        val unscheduled = mutableListOf<PlannerTask>()

        // Compute the sleep segment (a single continuous block that may cross midnight).
        val sleepWindows = resolveSleepWindow(date, input.sleepStart, input.sleepEnd, timezone)
        if (sleepWindows == null) {
            // Invalid or unparseable sleep configuration; fall back to a sensible default
            // of a 00:00-23:59 active day and record an assumption.
            assumptions.add(
                "Sleep time '${input.sleepStart}' to '${input.sleepEnd}' could not be parsed; " +
                    "using fallback wake window 09:00-23:00"
            )
            freeWindows.add(
                TimeSlot(
                    LocalDateTime(date, LocalTime(hour = 9, minute = 0)).toInstant(timezone),
                    LocalDateTime(date, LocalTime(hour = 23, minute = 0)).toInstant(timezone)
                )
            )
        } else {
            sleepWindows.forEach { window ->
                warnings.add(
                    "Sleep window reserved from ${todayTime(window.start)} to ${todayTime(window.end)}"
                )
            }

            // Start with the full day and subtract the sleep windows.
            val dayStart = LocalDateTime(
                date, LocalTime(hour = 0, minute = 0)
            ).toInstant(timezone)
            val dayEnd = LocalDateTime(
                date, LocalTime(hour = 23, minute = 59)
            ).toInstant(timezone)
            freeWindows.add(TimeSlot(dayStart, dayEnd))

            sleepWindows.onEach { sleep ->
                removeFromWindows(freeWindows, sleep.start, sleep.end)
            }
        }

        // Remove fixed commitments from free windows.
        input.fixedCommitments.forEach { commitment ->
            warnings.add(
                "Fixed commitment '${commitment.title}' reserved from " +
                    "${timeOfDay(commitment.startTime, timezone)} to " +
                    "${timeOfDay(commitment.endTime, timezone)}"
            )
            removeFromWindows(freeWindows, commitment.startTime, commitment.endTime)
        }

        // Sort tasks by priority descending, then by deadline ascending.
        val remaining = input.tasks.sortedWith(
            compareByDescending<PlannerTask> { task -> input.priorities[task.title] ?: 1 }
                .thenBy { task -> task.deadline?.toEpochMilliseconds() ?: Long.MAX_VALUE }
        )

        remaining.forEach { task ->
            val duration = input.estimatedDurations[task.title]
                ?: task.estimatedDurationMinutes
            if (duration <= 0) {
                warnings.add("Task '${task.title}' has non-positive duration; unscheduled")
                unscheduled.add(task)
                return@forEach
            }

            val slot = freeWindows.find { window ->
                duration <= window.durationMinutes()
            }
            if (slot != null) {
                val start = slot.start
                val end = Instant.fromEpochMilliseconds(
                    start.toEpochMilliseconds() + duration * 60_000L
                )
                scheduled.add(
                    ScheduledTask(
                        task = task,
                        startsAt = start,
                        endsAt = end
                    )
                )
                removeFromWindows(freeWindows, start, end)
            } else {
                warnings.add("No slot found for '${task.title}' - unscheduled")
                unscheduled.add(task)
            }
        }

        // Record travel-buffer assumption if one is declared.
        if (input.travelBuffers > 0) {
            assumptions.add(
                "Travel buffers of ${input.travelBuffers} minute(s) were not yet " +
                    "applied between commitments"
            )
        }

        return PlannerResult(
            scheduledTasks = scheduled,
            warnings = warnings,
            assumptions = assumptions,
            unscheduledTasks = unscheduled
        )
    }

    /**
     * Resolve sleepStart/sleepEnd (formats like "07:00") into concrete [TimeSlot] windows
     * for the target date. Returns null when the inputs cannot be parsed.
     */
    private fun resolveSleepWindow(
        date: LocalDate,
        sleepStart: String,
        sleepEnd: String,
        timezone: TimeZone
    ): List<TimeSlot>? {
        val start = parseMinutes(sleepStart) ?: return null
        val end = parseMinutes(sleepEnd) ?: return null
        if (start == end) return null

        val midnight = LocalDateTime(date, LocalTime(hour = 0, minute = 0)).toInstant(timezone)
        val startInstant = Instant.fromEpochMilliseconds(
            midnight.toEpochMilliseconds() + start * 60_000L
        )
        val endInstant = Instant.fromEpochMilliseconds(
            midnight.toEpochMilliseconds() + end * 60_000L
        )

        return if (end > start) {
            // Same-day block, e.g. 23:00 -> 07:00 handled below when crossing; a
            // same-day block like 22:00 -> 23:00 stays within the date.
            listOf(TimeSlot(startInstant, endInstant))
        } else {
            // Block crosses midnight (sleepStart later than sleepEnd), e.g. 23:00 -> 07:00.
            // It splits into [startInstant, dayEnd] and [dayStart, endInstant on next day].
            val dayEnd = LocalDateTime(date, LocalTime(hour = 23, minute = 59)).toInstant(timezone)
            val nextDayStart = LocalDateTime(
                kotlinx.datetime.LocalDate.fromEpochDays(date.toEpochDays() + 1),
                LocalTime(hour = 0, minute = 0)
            ).toInstant(timezone)
            val nextDayEnd = Instant.fromEpochMilliseconds(
                LocalDateTime(
                    kotlinx.datetime.LocalDate.fromEpochDays(date.toEpochDays() + 1),
                    LocalTime(hour = 0, minute = 0)
                )
                    .toInstant(timezone).toEpochMilliseconds() + end * 60_000L
            )
            listOf(
                TimeSlot(startInstant, dayEnd),
                TimeSlot(nextDayStart, nextDayEnd)
            )
        }
    }

    private fun parseMinutes(time: String): Long? {
        val parts = time.split(":")
        if (parts.size != 2) return null
        val hour = parts[0].toIntOrNull() ?: return null
        val minute = parts[1].toIntOrNull() ?: return null
        if (hour !in 0..23 || minute !in 0..59) return null
        return hour * 60L + minute
    }

    private fun todayTime(instant: Instant): String =
        timeOfDay(instant, TimeZone.UTC)

    private fun timeOfDay(instant: Instant, timezone: TimeZone): String {
        val time = instant.toLocalDateTime(timezone).time
        return "%02d:%02d".format(time.hour, time.minute)
    }

    private fun removeFromWindows(windows: MutableList<TimeSlot>, start: Instant, end: Instant) {
        val newWindows = mutableListOf<TimeSlot>()
        windows.forEach { window ->
            if (end <= window.start || start >= window.end) {
                newWindows.add(window)
            } else {
                if (start > window.start) newWindows.add(TimeSlot(window.start, start))
                if (end < window.end) newWindows.add(TimeSlot(end, window.end))
            }
        }
        windows.clear()
        windows.addAll(newWindows)
    }

    private data class TimeSlot(val start: Instant, val end: Instant) {
        fun durationMinutes(): Long = (end - start).inWholeMinutes
    }
}
