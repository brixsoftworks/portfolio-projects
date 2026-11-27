package com.strictday.ui.schedule

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.strictday.data.local.datastore.UserPreferences
import com.strictday.domain.model.Schedule
import com.strictday.domain.model.Task
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

@OptIn(ExperimentalCoroutinesApi::class)
@HiltViewModel
class ScheduleViewModel @Inject constructor(
    private val scheduleRepository: ScheduleRepository,
    private val taskRepository: TaskRepository,
    private val userPreferences: UserPreferences
) : ViewModel() {

    data class ScheduleUiState(
        val schedule: Schedule? = null,
        val tasks: List<Task> = emptyList(),
        val isLoading: Boolean = true,
        val conflicts: List<ScheduleConflict> = emptyList()
    )

    data class ScheduleConflict(
        val taskAId: String,
        val taskAName: String,
        val taskBId: String,
        val taskBName: String
    )

    private val _uiState = MutableStateFlow(ScheduleUiState())
    val uiState: StateFlow<ScheduleUiState> = _uiState.asStateFlow()

    private var currentScheduleId: String? = null

    init {
        viewModelScope.launch {
            userPreferences.settings.flatMapLatest { settings ->
                if (settings.userId.isBlank()) return@flatMapLatest flowOf(ScheduleUiState(isLoading = false))
                val today = Clock.System.todayIn(TimeZone.of(settings.timezone)).toString()
                scheduleRepository.getScheduleByDate(settings.userId, LocalDate.parse(today))
                    .flatMapLatest { schedule ->
                        if (schedule == null) {
                            flowOf(ScheduleUiState(isLoading = false))
                        } else {
                            currentScheduleId = schedule.id
                            taskRepository.getTasksForSchedule(schedule.id).map { tasks ->
                                ScheduleUiState(
                                    schedule = schedule,
                                    tasks = tasks,
                                    isLoading = false,
                                    conflicts = detectConflicts(tasks)
                                )
                            }
                        }
                    }
            }.collect { _uiState.value = it }
        }
    }

    private fun detectConflicts(tasks: List<Task>): List<ScheduleConflict> {
        val conflicts = mutableListOf<ScheduleConflict>()
        val sorted = tasks.sortedBy { it.startsAt.toEpochMilliseconds() }
        for (i in sorted.indices) {
            for (j in i + 1 until sorted.size) {
                if (sorted[i].endsAt > sorted[j].startsAt) {
                    conflicts.add(
                        ScheduleConflict(
                            taskAId = sorted[i].id,
                            taskAName = sorted[i].title,
                            taskBId = sorted[j].id,
                            taskBName = sorted[j].title
                        )
                    )
                }
            }
        }
        return conflicts
    }

    fun createTask(task: Task) {
        viewModelScope.launch {
            taskRepository.createTask(task)
        }
    }

    fun updateTask(task: Task) {
        viewModelScope.launch {
            taskRepository.updateTask(task)
        }
    }

    fun deleteTask(task: Task) {
        viewModelScope.launch {
            taskRepository.deleteTask(task)
        }
    }
}