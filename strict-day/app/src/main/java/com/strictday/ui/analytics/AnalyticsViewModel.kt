package com.strictday.ui.analytics

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.strictday.data.local.datastore.UserPreferences
import com.strictday.domain.model.Task
import com.strictday.domain.model.TaskStatus
import com.strictday.domain.repository.ScheduleRepository
import com.strictday.domain.repository.TaskRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.launch
import kotlinx.datetime.Clock
import kotlinx.datetime.LocalDate
import kotlinx.datetime.TimeZone
import kotlinx.datetime.todayIn

data class TaskMetric(
    val task: Task,
    val scheduledMinutes: Long,
    val statusLabel: String
)

data class DailyMetricsUiState(
    val date: LocalDate? = null,
    val scheduledMinutes: Long = 0,
    val completedMinutes: Long = 0,
    val verifiedCount: Int = 0,
    val pendingCount: Int = 0,
    val failedCount: Int = 0,
    val skippedCount: Int = 0,
    val overdueCount: Int = 0,
    val totalCount: Int = 0,
    val completionRate: Float = 0f,
    val tasks: List<TaskMetric> = emptyList(),
    val isLoading: Boolean = true
)

@OptIn(ExperimentalCoroutinesApi::class)
@HiltViewModel
class AnalyticsViewModel @Inject constructor(
    private val taskRepository: TaskRepository,
    private val scheduleRepository: ScheduleRepository,
    private val userPreferences: UserPreferences
) : ViewModel() {

    private val _uiState = MutableStateFlow(DailyMetricsUiState())
    val uiState: StateFlow<DailyMetricsUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            userPreferences.settings.flatMapLatest { settings ->
                if (settings.userId.isBlank()) {
                    flowOf(DailyMetricsUiState(isLoading = false))
                } else {
                    val today = Clock.System.todayIn(TimeZone.of(settings.timezone))
                    scheduleRepository.getScheduleByDate(settings.userId, today)
                        .flatMapLatest { schedule ->
                            if (schedule == null) {
                                flowOf(DailyMetricsUiState(isLoading = false))
                            } else {
                                taskRepository.getTasksForSchedule(schedule.id).map { tasks ->
                                    computeMetrics(schedule.localDate, tasks)
                                }
                            }
                        }
                }
            }.collect { _uiState.value = it }
        }
    }

    private fun computeMetrics(date: LocalDate, tasks: List<Task>): DailyMetricsUiState {
        val nowMillis = Clock.System.now().toEpochMilliseconds()
        val verified = tasks.filter { it.status == TaskStatus.VERIFIED }
        val inProgress = tasks.count {
            it.status == TaskStatus.PENDING ||
                it.status == TaskStatus.ACTIVE ||
                it.status == TaskStatus.VERIFICATION_PENDING
        }
        val overdue = tasks.count {
            (it.status == TaskStatus.PENDING || it.status == TaskStatus.ACTIVE) &&
                it.endsAt.toEpochMilliseconds() < nowMillis
        }
        val total = tasks.size

        return DailyMetricsUiState(
            date = date,
            scheduledMinutes = tasks.sumOf { it.durationMinutes },
            completedMinutes = verified.sumOf { it.durationMinutes },
            verifiedCount = verified.size,
            pendingCount = inProgress,
            failedCount = tasks.count { it.status == TaskStatus.FAILED },
            skippedCount = tasks.count { it.status == TaskStatus.SKIPPED || it.status == TaskStatus.OVERRIDDEN },
            overdueCount = overdue,
            totalCount = total,
            completionRate = if (total > 0) verified.size.toFloat() / total.toFloat() else 0f,
            tasks = tasks.sortedBy { it.startsAt }.map { task ->
                TaskMetric(
                    task = task,
                    scheduledMinutes = task.durationMinutes,
                    statusLabel = statusLabel(task.status)
                )
            },
            isLoading = false
        )
    }

    private fun statusLabel(status: TaskStatus): String = when (status) {
        TaskStatus.PENDING -> "Pending"
        TaskStatus.ACTIVE -> "In progress"
        TaskStatus.VERIFICATION_PENDING -> "Awaiting verification"
        TaskStatus.VERIFIED -> "Verified"
        TaskStatus.SKIPPED -> "Skipped"
        TaskStatus.FAILED -> "Failed"
        TaskStatus.OVERRIDDEN -> "Overridden"
    }
}