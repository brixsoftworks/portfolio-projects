package com.strictday.ui.planner

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.strictday.data.local.datastore.UserPreferences
import com.strictday.domain.model.AuditEvent
import com.strictday.domain.model.AuditEventType
import com.strictday.domain.model.PlannerInput
import com.strictday.domain.model.PlannerResult
import com.strictday.domain.model.PlannerTask
import com.strictday.domain.model.Schedule
import com.strictday.domain.model.ScheduleStatus
import com.strictday.domain.model.Strictness
import com.strictday.domain.model.Task
import com.strictday.domain.model.TaskStatus
import com.strictday.domain.repository.AuditRepository
import com.strictday.domain.repository.ScheduleRepository
import com.strictday.domain.repository.TaskRepository
import com.strictday.planner.PlannerEngine
import com.strictday.util.IdGenerator
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.datetime.Clock
import kotlinx.datetime.LocalDate
import kotlinx.datetime.TimeZone
import kotlinx.datetime.todayIn

@HiltViewModel
class NightPlannerViewModel @Inject constructor(
    private val plannerEngine: PlannerEngine,
    private val scheduleRepository: ScheduleRepository,
    private val taskRepository: TaskRepository,
    private val userPreferences: UserPreferences,
    private val auditRepository: AuditRepository
) : ViewModel() {

    data class PlannerUiState(
        val date: LocalDate = Clock.System.todayIn(TimeZone.currentSystemDefault()),
        val wakeTime: String = "07:00",
        val sleepTime: String = "23:00",
        val taskInputs: List<PlannerTaskInput> = emptyList(),
        val result: PlannerResult? = null,
        val isLoading: Boolean = false,
        val scheduleLocked: Boolean = false
    )

    data class PlannerTaskInput(
        val title: String = "",
        val durationMinutes: Long = 60,
        val priority: Int = 1,
        val strictness: Strictness = Strictness.NORMAL
    )

    private val _uiState = MutableStateFlow(PlannerUiState())
    val uiState: StateFlow<PlannerUiState> = _uiState.asStateFlow()

    fun addTask() {
        val current = _uiState.value
        if (current.taskInputs.none { it.title.isBlank() }) {
            _uiState.value = current.copy(taskInputs = current.taskInputs + PlannerTaskInput())
        }
    }

    fun updateTaskInput(index: Int, input: PlannerTaskInput) {
        val tasks = _uiState.value.taskInputs.toMutableList()
        if (index in tasks.indices) {
            tasks[index] = input
            _uiState.value = _uiState.value.copy(taskInputs = tasks)
        }
    }

    fun generate() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            val current = _uiState.value
            val tasks = current.taskInputs.filter { it.title.isNotBlank() }.map { input ->
                PlannerTask(
                    title = input.title,
                    description = "",
                    estimatedDurationMinutes = input.durationMinutes,
                    priority = input.priority,
                    strictness = input.strictness,
                    deadline = null,
                    allowedApps = emptyList(),
                    blockedApps = emptyList()
                )
            }
            val input = PlannerInput(
                date = current.date,
                timezone = TimeZone.currentSystemDefault().id,
                sleepStart = current.sleepTime,
                sleepEnd = current.wakeTime,
                fixedCommitments = emptyList(),
                goals = emptyList(),
                tasks = tasks,
                estimatedDurations = tasks.associate { it.title to it.estimatedDurationMinutes },
                priorities = tasks.associate { it.title to it.priority },
                deadlines = emptyMap(),
                preferredFocusWindows = emptyList(),
                travelBuffers = 0,
                historicalDurations = emptyMap()
            )
            val result = plannerEngine.generate(input)
            _uiState.value = _uiState.value.copy(result = result, isLoading = false)
        }
    }

    fun approve() {
        viewModelScope.launch {
            val current = _uiState.value
            val result = current.result ?: return@launch
            val settings = userPreferences.settings.first()

            val scheduleId = IdGenerator.newUuid()
            val schedule = Schedule(
                id = scheduleId,
                userId = settings.userId,
                localDate = current.date,
                status = ScheduleStatus.LOCKED,
                createdAt = Clock.System.now()
            )
            scheduleRepository.createSchedule(schedule)

            result.scheduledTasks.forEachIndexed { index, scheduled ->
                val task = Task(
                    id = IdGenerator.newUuid(),
                    scheduleId = scheduleId,
                    title = scheduled.task.title,
                    description = scheduled.task.description,
                    startsAt = scheduled.startsAt,
                    endsAt = scheduled.endsAt,
                    strictness = scheduled.task.strictness,
                    status = TaskStatus.PENDING,
                    orderIndex = index,
                    allowedApps = scheduled.task.allowedApps,
                    blockedApps = scheduled.task.blockedApps,
                    createdAt = Clock.System.now()
                )
                taskRepository.createTask(task)
            }

            auditRepository.recordEvent(
                AuditEvent(
                    id = IdGenerator.newUuid(),
                    userId = settings.userId,
                    deviceId = "",
                    taskId = null,
                    type = AuditEventType.SCHEDULE_LOCKED,
                    payload = mapOf("scheduleId" to scheduleId),
                    createdAt = Clock.System.now()
                )
            )

            _uiState.value = _uiState.value.copy(scheduleLocked = true)
        }
    }
}