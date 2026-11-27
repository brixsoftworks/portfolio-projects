package com.strictday.planner

import com.strictday.domain.model.PlannerTask
import com.strictday.domain.model.ScheduledTask
import com.strictday.domain.model.Strictness
import kotlinx.datetime.Instant
import kotlinx.datetime.LocalDate
import kotlinx.datetime.LocalDateTime
import kotlinx.datetime.LocalTime
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toInstant
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ScheduleValidatorTest {

    private val date = LocalDate(2026, 1, 15)
    private val validator = ScheduleValidator()

    private fun at(hour: Int, minute: Int = 0): Instant =
        LocalDateTime(date, LocalTime(hour = hour, minute = minute)).toInstant(TimeZone.UTC)

    private fun task(title: String, startsAt: Instant, endsAt: Instant) = ScheduledTask(
        task = PlannerTask(
            title = title,
            description = "",
            estimatedDurationMinutes = 60,
            priority = 1,
            strictness = Strictness.NORMAL,
            deadline = null,
            allowedApps = emptyList(),
            blockedApps = emptyList(),
        ),
        startsAt = startsAt,
        endsAt = endsAt,
    )

    @Test
    fun `empty schedule validates`() {
        val result = validator.validate(emptyList())
        assertTrue(result.isValid)
        assertFalse(result.hasOverlaps)
        assertTrue(result.warnings.isEmpty())
    }

    @Test
    fun `adjacent tasks do not overlap`() {
        val result = validator.validate(
            listOf(
                task("A", at(9, 0), at(10, 0)),
                task("B", at(10, 0), at(11, 0)),
            ),
        )

        assertTrue(result.isValid)
        assertFalse(result.hasOverlaps)
    }

    @Test
    fun `overlapping tasks are reported`() {
        val result = validator.validate(
            listOf(
                task("A", at(9, 0), at(11, 0)),
                task("B", at(10, 0), at(12, 0)),
            ),
        )

        assertFalse(result.isValid)
        assertTrue(result.hasOverlaps)
        assertEquals(1, result.overlapDetails.size)
        val overlap = result.overlapDetails[0]
        assertEquals("A", overlap.taskA)
        assertEquals("B", overlap.taskB)
        assertEquals(at(10, 0), overlap.overlapStart)
        assertEquals(at(11, 0), overlap.overlapEnd)
    }

    @Test
    fun `zero duration task produces warning`() {
        val result = validator.validate(listOf(task("A", at(9, 0), at(9, 0))))

        assertFalse(result.isValid)
        assertFalse(result.hasOverlaps)
        assertTrue(result.warnings.any { it.contains("zero or negative duration") })
    }
}