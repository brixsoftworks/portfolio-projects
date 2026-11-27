package com.strictday.ui.task

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.strictday.data.local.datastore.UserPreferences
import com.strictday.domain.model.Strictness
import com.strictday.domain.model.Task
import com.strictday.domain.model.TaskStatus
import com.strictday.domain.model.VerificationOperator
import com.strictday.domain.model.VerificationProvider
import com.strictday.domain.model.VerificationRule
import com.strictday.domain.repository.TaskRepository
import com.strictday.domain.repository.VerificationRuleRepository
import com.strictday.util.IdGenerator
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.datetime.Clock
import kotlinx.datetime.Instant
import kotlinx.datetime.LocalDateTime
import kotlinx.datetime.LocalTime
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toInstant
import kotlinx.datetime.toLocalDateTime

@HiltViewModel
class TaskEditorViewModel @Inject constructor(
    private val taskRepository: TaskRepository,
    private val verificationRuleRepository: VerificationRuleRepository,
    private val userPreferences: UserPreferences
) : ViewModel() {

    data class TaskEditorUiState(
        val taskId: String? = null,
        val title: String = "",
        val description: String = "",
        val startHour: Int = 9,
        val startMinute: Int = 0,
        val durationMinutes: Long = 60,
        val strictness: Strictness = Strictness.NORMAL,
        val allowedApps: List<String> = emptyList(),
        val blockedApps: List<String> = emptyList(),
        val verificationProvider: VerificationProvider? = null,
        val verificationEventType: String = "commit",
        val verificationOperator: VerificationOperator = VerificationOperator.COUNT,
        val verificationTarget: String = "",
        val minCount: Int = 1,
        val isLoading: Boolean = false
    )

    private val _uiState = MutableStateFlow(TaskEditorUiState())
    val uiState: StateFlow<TaskEditorUiState> = _uiState.asStateFlow()

    private var scheduleId: String = ""

    fun load(taskId: String?, scheduleId: String) {
        this.scheduleId = scheduleId
        if (taskId == null) return
        viewModelScope.launch {
            taskRepository.getTaskById(taskId).first()?.let { task ->
                _uiState.value = _uiState.value.copy(
                    taskId = task.id,
                    title = task.title,
                    description = task.description,
                    strictness = task.strictness,
                    allowedApps = task.allowedApps,
                    blockedApps = task.blockedApps
                )
                val dt = task.startsAt.toLocalDateTime(TimeZone.currentSystemDefault())
                _uiState.value = _uiState.value.copy(
                    startHour = dt.hour,
                    startMinute = dt.minute,
                    durationMinutes = task.durationMinutes
                )
                verificationRuleRepository.getRulesForTask(task.id).first().firstOrNull()?.let { rule ->
                    _uiState.value = _uiState.value.copy(
                        verificationProvider = rule.provider,
                        verificationEventType = rule.eventType,
                        verificationOperator = rule.operator,
                        verificationTarget = rule.targetValue,
                        minCount = rule.minCount
                    )
                }
            }
        }
    }

    fun onTitleChange(value: String) {
        _uiState.value = _uiState.value.copy(title = value)
    }

    fun onDescriptionChange(value: String) {
        _uiState.value = _uiState.value.copy(description = value)
    }

    fun onStartHourChange(value: Int) {
        _uiState.value = _uiState.value.copy(startHour = value)
    }

    fun onStartMinuteChange(value: Int) {
        _uiState.value = _uiState.value.copy(startMinute = value)
    }

    fun onDurationChange(value: Long) {
        _uiState.value = _uiState.value.copy(durationMinutes = value)
    }

    fun onStrictnessChange(value: Strictness) {
        _uiState.value = _uiState.value.copy(strictness = value)
    }

    fun onAllowedAppsChange(value: List<String>) {
        _uiState.value = _uiState.value.copy(allowedApps = value)
    }

    fun onBlockedAppsChange(value: List<String>) {
        _uiState.value = _uiState.value.copy(blockedApps = value)
    }

    fun onVerificationProviderChange(value: VerificationProvider?) {
        _uiState.value = _uiState.value.copy(verificationProvider = value)
    }

    fun onVerificationEventTypeChange(value: String) {
        _uiState.value = _uiState.value.copy(verificationEventType = value)
    }

    fun onVerificationOperatorChange(value: VerificationOperator) {
        _uiState.value = _uiState.value.copy(verificationOperator = value)
    }

    fun onVerificationTargetChange(value: String) {
        _uiState.value = _uiState.value.copy(verificationTarget = value)
    }

    fun onMinCountChange(value: Int) {
        _uiState.value = _uiState.value.copy(minCount = value)
    }

    fun save() {
        viewModelScope.launch {
            val current = _uiState.value
            if (current.title.isBlank()) return@launch
            val startInstant = LocalDateTime(
                Clock.System.now().toLocalDateTime(TimeZone.currentSystemDefault()).date,
                LocalTime(current.startHour, current.startMinute)
            ).toInstant(TimeZone.currentSystemDefault())
            val endInstant = Instant.fromEpochMilliseconds(
                startInstant.toEpochMilliseconds() + current.durationMinutes * 60_000
            )

            val task = Task(
                id = current.taskId ?: IdGenerator.newUuid(),
                scheduleId = scheduleId,
                title = current.title,
                description = current.description,
                startsAt = startInstant,
                endsAt = endInstant,
                strictness = current.strictness,
                status = TaskStatus.PENDING,
                orderIndex = 0,
                allowedApps = current.allowedApps,
                blockedApps = current.blockedApps,
                createdAt = Clock.System.now()
            )

            if (current.taskId == null) {
                taskRepository.createTask(task)
            } else {
                taskRepository.updateTask(task)
            }

            if (current.verificationProvider != null) {
                val rule = VerificationRule(
                    id = IdGenerator.newUuid(),
                    taskId = task.id,
                    provider = current.verificationProvider,
                    eventType = current.verificationEventType,
                    operator = current.verificationOperator,
                    targetValue = current.verificationTarget,
                    minCount = current.minCount,
                    minDurationSeconds = 0,
                    createdAt = Clock.System.now()
                )
                verificationRuleRepository.createRule(rule)
            }
        }
    }
}