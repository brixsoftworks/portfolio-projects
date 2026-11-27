package com.strictday.domain.usecase

import com.strictday.data.local.datastore.UserPreferences
import com.strictday.domain.model.Schedule
import com.strictday.domain.repository.ScheduleRepository
import com.strictday.domain.repository.TaskRepository
import javax.inject.Inject
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.flowOf
import kotlinx.datetime.Clock
import kotlinx.datetime.LocalDate
import kotlinx.datetime.TimeZone
import kotlinx.datetime.todayIn

data class TodaySchedule(
    val schedule: Schedule?,
    val hasSchedule: Boolean
)

@OptIn(ExperimentalCoroutinesApi::class)
class GetTodayScheduleUseCase @Inject constructor(
    private val scheduleRepository: ScheduleRepository,
    private val taskRepository: TaskRepository,
    private val userPreferences: UserPreferences
) {
    operator fun invoke(): Flow<TodaySchedule> {
        return userPreferences.settings.flatMapLatest { settings ->
            if (settings.userId.isBlank()) {
                flowOf(TodaySchedule(null, false))
            } else {
                val today = Clock.System.todayIn(TimeZone.of(settings.timezone)).toString()
                scheduleRepository.getScheduleByDate(settings.userId, LocalDate.parse(today))
                    .flatMapLatest { schedule ->
                        if (schedule == null) {
                            flowOf(TodaySchedule(null, false))
                        } else {
                            flowOf(TodaySchedule(schedule, true))
                        }
                    }
            }
        }
    }
}