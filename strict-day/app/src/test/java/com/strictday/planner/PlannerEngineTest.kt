package com.strictday.planner

import com.strictday.domain.model.PlannerInput
import com.strictday.domain.model.PlannerTask
import com.strictday.domain.model.Strictness
import kotlinx.datetime.LocalDate
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class PlannerEngineTest {

    private val engine = PlannerEngine(ConstraintSolver(), ScheduleValidator())

    private fun input(tasks: List<PlannerTask> = emptyList()) = PlannerInput(
        date = LocalDate(2026, 1, 15),
        timezone = "UTC",
        sleepStart = "00:00",
        sleepEnd = "06:00",
        fixedCommitments = emptyList(),
        goals = emptyList(),
        tasks = tasks,
        estimatedDurations = emptyMap(),
        priorities = emptyMap(),
        deadlines = emptyMap(),
        preferredFocusWindows = emptyList(),
        travelBuffers = 0,
        historicalDurations = emptyMap(),
    )

    private fun task(title: String, durationMinutes: Long) = PlannerTask(
        title = title,
        description = "",
        estimatedDurationMinutes = durationMinutes,
        priority = 1,
        strictness = Strictness.NORMAL,
        deadline = null,
        allowedApps = emptyList(),
        blockedApps = emptyList(),
    )

    @Test
    fun `valid schedule has no overlap warnings from validator`() {
        val result = engine.generate(
            input(
                listOf(
                    task("One", 60),
                    task("Two", 60),
                ),
            ),
        )

        assertEquals(listOf("One", "Two"), result.scheduledTasks.map { it.task.title })
        assertTrue(result.warnings.any { it.contains("Sleep window") })
        assertTrue(result.warnings.none { it.contains("overlap") })
    }

    @Test
    fun `unscheduled task produces warning and is surfaced`() {
        val result = engine.generate(input(listOf(task("Impossible", 24 * 60))))

        assertTrue(result.scheduledTasks.isEmpty())
        assertEquals(listOf("Impossible"), result.unscheduledTasks.map { it.title })
        assertTrue(result.warnings.any { it.contains("No slot found") })
    }

    @Test
    fun `sleep reservation warnings are merged with validator warnings`() {
        val result = engine.generate(input(listOf(task("Task", 30))))

        assertTrue(result.warnings.any { it.contains("Sleep window") })
    }
}