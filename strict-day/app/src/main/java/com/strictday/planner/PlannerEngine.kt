package com.strictday.planner

import com.strictday.domain.model.PlannerInput
import com.strictday.domain.model.PlannerResult
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PlannerEngine @Inject constructor(
    private val constraintSolver: ConstraintSolver,
    private val scheduleValidator: ScheduleValidator
) {

    fun generate(input: PlannerInput): PlannerResult {
        val solved = constraintSolver.solve(input)

        val validation = scheduleValidator.validate(solved.scheduledTasks)
        val warnings = solved.warnings + validation.warnings

        return solved.copy(
            scheduledTasks = solved.scheduledTasks,
            warnings = warnings,
            assumptions = solved.assumptions,
            unscheduledTasks = solved.unscheduledTasks
        )
    }
}
