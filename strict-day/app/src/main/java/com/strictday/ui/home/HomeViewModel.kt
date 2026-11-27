package com.strictday.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.strictday.data.local.datastore.UserPreferences
import com.strictday.domain.model.HomeUiState
import com.strictday.domain.model.Task
import com.strictday.domain.model.TaskStatus
import com.strictday.domain.repository.ScheduleRepository
import com.strictday.domain.repository.TaskRepository
import com.strictday.enforcement.EnforcementManager
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.launch
import kotlinx.datetime.Clock
import kotlinx.datetime.LocalDate
import kotlinx.datetime.TimeZone
import kotlinx.datetime.todayIn

@OptIn(ExperimentalCoroutinesApi::class)
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val scheduleRepository: ScheduleRepository,
    private val taskRepository: TaskRepository,
    private val userPreferences: UserPreferences,
    private val enforcementManager: EnforcementManager
) : ViewModel() {

    private val uiState = MutableStateFlow(HomeUiState())
    val state: StateFlow<HomeUiState> = uiState.asStateFlow()

    init {
        viewModelScope.launch {
            userPreferences.settings.flatMapLatest { settings ->
                if (settings.userId.isBlank()) return@flatMapLatest flowOf(HomeUiState(isLoading = false))
                val today = Clock.System.todayIn(TimeZone.of(settings.timezone)).toString()
                scheduleRepository.getScheduleByDate(settings.userId, LocalDate.parse(today))
                    .flatMapLatest { schedule ->
                        if (schedule == null) {
                            flowOf(HomeUiState(isLoading = false))
                        } else {
                            combine(
                                taskRepository.getActiveTask(schedule.id),
                                taskRepository.getNextPendingTask(schedule.id),
                                taskRepository.getVerifiedTaskCount(schedule.id),
                                taskRepository.getTotalTaskCount(schedule.id)
                            ) { current, next, verified, total ->
                                HomeUiState(
                                    currentTask = current ?: getDueTask(schedule.id),
                                    nextTask = next,
                                    remainingSeconds = current?.let {
                                        (it.endsAt.toEpochMilliseconds() - Clock.System.now().toEpochMilliseconds()) / 1000
                                    }?.coerceAtLeast(0) ?: 0,
                                    todayScore = if (total > 0) verified.toFloat() / total.toFloat() else 0f,
                                    tasksCompleted = verified,
                                    tasksTotal = total,
                                    isLoading = false
                                )
                            }
                        }
                    }
            }.collect { uiState.value = it }
        }
    }

    private suspend fun getDueTask(scheduleId: String): Task? {
        val tasks = taskRepository.getTasksForScheduleList(scheduleId)
        return tasks.find { task ->
            task.status == TaskStatus.PENDING &&
                task.startsAt.toEpochMilliseconds() <= Clock.System.now().toEpochMilliseconds()
        }
    }
}