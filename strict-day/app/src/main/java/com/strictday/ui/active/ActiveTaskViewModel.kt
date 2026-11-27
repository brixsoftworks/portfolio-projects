package com.strictday.ui.active

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.strictday.domain.model.AuditEvent
import com.strictday.domain.model.AuditEventType
import com.strictday.domain.model.Strictness
import com.strictday.domain.model.Task
import com.strictday.domain.model.TaskStatus
import com.strictday.domain.model.DevicePolicyMode
import com.strictday.domain.repository.AuditRepository
import com.strictday.domain.repository.TaskRepository
import com.strictday.enforcement.DeviceCapabilitiesReport
import com.strictday.enforcement.EmergencyAccess
import com.strictday.enforcement.EnforcementManager
import com.strictday.enforcement.EnforcementPolicy
import com.strictday.security.DeviceIdentity
import com.strictday.util.IdGenerator
import com.strictday.verification.VerificationEngine
import com.strictday.verification.VerificationState
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.datetime.Clock

@HiltViewModel
class ActiveTaskViewModel @Inject constructor(
    private val taskRepository: TaskRepository,
    private val enforcementManager: EnforcementManager,
    private val verificationEngine: VerificationEngine,
    private val auditRepository: AuditRepository,
    private val deviceIdentity: DeviceIdentity
) : ViewModel() {

    data class ActiveTaskUiState(
        val task: Task? = null,
        val remainingSeconds: Long = 0,
        val isActive: Boolean = false,
        val verificationState: VerificationState? = null,
        val capabilities: DeviceCapabilitiesReport? = null,
        val isLoading: Boolean = true
    )

    private val _uiState = MutableStateFlow(ActiveTaskUiState())
    val uiState: StateFlow<ActiveTaskUiState> = _uiState.asStateFlow()

    fun load(taskId: String?) {
        if (taskId == null) return
        viewModelScope.launch {
            val task = taskRepository.getTaskById(taskId).first()
            _uiState.update { current ->
                current.copy(
                    task = task,
                    isLoading = false,
                    remainingSeconds = task?.let {
                        ((it.endsAt.toEpochMilliseconds() - Clock.System.now().toEpochMilliseconds()) / 1000)
                            .coerceAtLeast(0)
                    } ?: 0
                )
            }
        }
        viewModelScope.launch {
            verificationEngine.verificationState(taskId).collect { state ->
                _uiState.update { it.copy(verificationState = state) }
            }
        }
        viewModelScope.launch {
            enforcementManager.deviceCapabilities().collect { caps ->
                _uiState.update { it.copy(capabilities = caps) }
            }
        }
        startTicker()
    }

    fun activateEnforcement() {
        viewModelScope.launch {
            val task = _uiState.value.task ?: return@launch
            val policy = EnforcementPolicy(
                mode = when (task.strictness) {
                    Strictness.NORMAL -> DevicePolicyMode.NORMAL
                    Strictness.FOCUS -> DevicePolicyMode.FOCUS
                    Strictness.STRICT -> DevicePolicyMode.STRICT
                    Strictness.IRON -> DevicePolicyMode.IRON
                },
                taskId = task.id,
                allowedPackages = task.allowedApps,
                blockedPackages = task.blockedApps,
                startTime = task.startsAt,
                endTime = task.endsAt,
                unlockCondition = if (task.isVerificationRequired) "verification" else "manual",
                emergencyAccess = EmergencyAccess(
                    alwaysAllowed = true,
                    requiresConfirmation = true,
                    disabledDuringIronMode = task.strictness == Strictness.IRON
                )
            )
            enforcementManager.activate(policy)
            taskRepository.updateTaskStatus(task.id, TaskStatus.ACTIVE)
            _uiState.update { it.copy(isActive = true) }
            auditRepository.recordEvent(
                AuditEvent(
                    id = IdGenerator.newUuid(),
                    userId = "",
                    deviceId = deviceIdentity.deviceId(),
                    taskId = task.id,
                    type = AuditEventType.TASK_STARTED,
                    payload = mapOf("strictness" to task.strictness.name),
                    createdAt = Clock.System.now()
                )
            )
        }
    }

    fun refreshVerification() {
        viewModelScope.launch {
            val task = _uiState.value.task ?: return@launch
            val state = verificationEngine.refreshVerification(task.id)
            _uiState.update { it.copy(verificationState = state) }
        }
    }

    fun startTicker() {
        viewModelScope.launch {
            while (true) {
                val task = _uiState.value.task ?: break
                _uiState.update {
                    it.copy(
                        remainingSeconds = ((task.endsAt.toEpochMilliseconds() - Clock.System.now().toEpochMilliseconds()) / 1000)
                            .coerceAtLeast(0)
                    )
                }
                delay(1_000)
            }
        }
    }
}