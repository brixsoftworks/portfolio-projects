package com.strictday.ui.verification

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.strictday.domain.model.Task
import com.strictday.domain.repository.TaskRepository
import com.strictday.verification.VerificationEngine
import com.strictday.verification.VerificationState
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class VerificationUiState(
    val task: Task? = null,
    val verificationState: VerificationState? = null,
    val isLoading: Boolean = true
)

@HiltViewModel
class VerificationViewModel @Inject constructor(
    private val verificationEngine: VerificationEngine,
    private val taskRepository: TaskRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(VerificationUiState())
    val uiState: StateFlow<VerificationUiState> = _uiState.asStateFlow()

    private var taskId: String? = null

    fun load(taskId: String) {
        this.taskId = taskId
        viewModelScope.launch {
            taskRepository.getTaskById(taskId).collect { task ->
                _uiState.update { it.copy(task = task, isLoading = task == null) }
            }
        }
        viewModelScope.launch {
            verificationEngine.verificationState(taskId).collect { state ->
                _uiState.update { it.copy(verificationState = state, isLoading = false) }
            }
        }
    }

    fun refresh() {
        val id = taskId ?: return
        viewModelScope.launch {
            val state = verificationEngine.refreshVerification(id)
            _uiState.update { it.copy(verificationState = state, isLoading = false) }
        }
    }
}