package com.strictday.planner

import com.strictday.domain.model.FixedCommitment
import com.strictday.domain.model.PlannerInput
import com.strictday.domain.model.PlannerTask
import com.strictday.domain.model.Strictness
import kotlinx.datetime.Instant
import kotlinx.datetime.LocalDate
import kotlinx.datetime.LocalDateTime
import kotlinx.datetime.LocalTime
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toInstant
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ConstraintSolverTest {

    private val date = LocalDate(2026, 1, 15)
    private val timezone = "UTC"
    private val solver = ConstraintSolver()

    private fun at(hour: Int, minute: Int = 0): Instant =
        LocalDateTime(date, LocalTime(hour = hour, minute = minute)).toInstant(TimeZone.UTC)

    private fun task(
        title: String,
        durationMinutes: Long,
        priority: Int = 1,
        deadline: Instant? = null,
    ) = PlannerTask(
        title = title,
        description = "",
        estimatedDurationMinutes = durationMinutes,
        priority = priority,
        strictness = Strictness.NORMAL,
        deadline = deadline,
        allowedApps = emptyList(),
        blockedApps = emptyList(),
    )

    private fun input(
        sleepStart: String = "00:00",
        sleepEnd: String = "06:00",
        commitments: List<FixedCommitment> = emptyList(),
        tasks: List<PlannerTask> = emptyList(),
        durations: Map<String, Long> = emptyMap(),
        priorities: Map<String, Int> = emptyMap(),
    ) = PlannerInput(
        date = date,
        timezone = timezone,
        sleepStart = sleepStart,
        sleepEnd = sleepEnd,
        fixedCommitments = commitments,
        goals = emptyList(),
        tasks = tasks,
        estimatedDurations = durations,
        priorities = priorities,
        deadlines = emptyMap(),
        preferredFocusWindows = emptyList(),
        travelBuffers = 0,
        historicalDurations = emptyMap(),
    )

    @Test
    fun `schedules single task at start of available window`() {
        val result = solver.solve(
            input(
                sleepStart = "00:00",
                sleepEnd = "06:00",
                tasks = listOf(task("Deep Work", durationMinutes = 60)),
            ),
        )

        assertEquals(listOf("Deep Work"), result.scheduledTasks.map { it.task.title })
        assertEquals(at(6, 0), result.scheduledTasks[0].startsAt)
        assertEquals(at(7, 0), result.scheduledTasks[0].endsAt)
        assertTrue(result.unscheduledTasks.isEmpty())
    }

    @Test
    fun `tasks scheduled in priority order`() {
        val result = solver.solve(
            input(
                sleepStart = "00:00",
                sleepEnd = "06:00",
                tasks = listOf(
                    task("Low", durationMinutes = 30),
                    task("High", durationMinutes = 30),
                    task("Medium", durationMinutes = 30),
                ),
                priorities = mapOf(
                    "High" to 5,
                    "Medium" to 3,
                    "Low" to 1,
                ),
            ),
        )

        assertEquals(listOf("High", "Medium", "Low"), result.scheduledTasks.map { it.task.title })
    }

    @Test
    fun `fixed commitment is excluded from free windows`() {
        val result = solver.solve(
            input(
                sleepStart = "00:00",
                sleepEnd = "06:00",
                commitments = listOf(
                    FixedCommitment(
                        title = "Standup",
                        startTime = at(9, 0),
                        endTime = at(9, 30),
                    ),
                ),
                tasks = listOf(task("Focused Writing", durationMinutes = 60)),
            ),
        )

        val scheduled = result.scheduledTasks[0]
        // First free window is 06:00-09:00; the task fills 30 of 180 minutes there.
        assertEquals(at(6, 0), scheduled.startsAt)
        assertEquals(at(7, 0), scheduled.endsAt)
        assertTrue(result.warnings.any { it.contains("Standup") })
    }

    @Test
    fun `oversized task is unscheduled with warning`() {
        val result = solver.solve(
            input(
                sleepStart = "00:00",
                sleepEnd = "23:00",
                tasks = listOf(task("Too Big", durationMinutes = 24 * 60)),
            ),
        )

        assertTrue(result.scheduledTasks.isEmpty())
        assertEquals(listOf("Too Big"), result.unscheduledTasks.map { it.title })
        assertTrue(result.warnings.any { it.contains("Too Big") })
    }

    @Test
    fun `non positive duration is unscheduled`() {
        val result = solver.solve(
            input(
                sleepStart = "00:00",
                sleepEnd = "06:00",
                tasks = listOf(task("Broken", durationMinutes = 0)),
            ),
        )

        assertTrue(result.scheduledTasks.isEmpty())
        assertEquals(listOf("Broken"), result.unscheduledTasks.map { it.title })
    }

    @Test
    fun `sleep window crossing midnight splits into two blocks`() {
        val result = solver.solve(
            input(
                sleepStart = "23:00",
                sleepEnd = "07:00",
            ),
        )

        // No tasks, so we only verify the sleep reservation warnings and that the
        // crossing-midnight window was accepted.
        val sleep = result.warnings.filter { it.contains("Sleep window") }
        assertEquals(2, sleep.size)
        assertEquals("Sleep window reserved from 23:00 to 23:59", sleep[0])
        assertEquals("Sleep window reserved from 00:00 to 07:00", sleep[1])
    }

    @Test
    fun `unparseable sleep window falls back with assumption`() {
        val result = solver.solve(
            input(
                sleepStart = "garbage",
                sleepEnd = "07:00",
                tasks = listOf(task("Morning Task", durationMinutes = 30)),
            ),
        )

        assertTrue(result.assumptions.any { it.contains("could not be parsed") })
        // Fallback active window is 09:00-23:00.
        assertEquals(at(9, 0), result.scheduledTasks[0].startsAt)
    }

    @Test
    fun `sleep start equal to end is treated as unparseable`() {
        val result = solver.solve(
            input(
                sleepStart = "07:00",
                sleepEnd = "07:00",
                tasks = listOf(task("Task", durationMinutes = 60)),
            ),
        )

        assertTrue(result.assumptions.any { it.contains("could not be parsed") })
    }

    @Test
    fun `travel buffers record assumption without changing scheduling`() {
        val result = solver.solve(
            input(
                sleepStart = "00:00",
                sleepEnd = "06:00",
                tasks = listOf(task("Task", durationMinutes = 30)),
            ).let { input ->
                input.copy(travelBuffers = 15)
            },
        )

        assertTrue(result.assumptions.any { it.contains("Travel buffers of 15") })
        assertEquals("Task", result.scheduledTasks.first().task.title)
    }

    @Test
    fun `multiple tasks pack sequentially into same window`() {
        val result = solver.solve(
            input(
                sleepStart = "00:00",
                sleepEnd = "06:00",
                tasks = listOf(
                    task("First", durationMinutes = 30),
                    task("Second", durationMinutes = 30),
                ),
            ),
        )

        assertEquals(listOf("First", "Second"), result.scheduledTasks.map { it.task.title })
        assertEquals(at(6, 30), result.scheduledTasks[1].startsAt)
        assertEquals(at(7, 0), result.scheduledTasks[1].endsAt)
    }
}