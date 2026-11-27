package com.strictday.domain.repository

import com.strictday.domain.model.Schedule
import com.strictday.domain.model.ScheduleStatus
import kotlinx.coroutines.flow.Flow
import kotlinx.datetime.LocalDate

interface ScheduleRepository {
    fun getScheduleByDate(userId: String, date: LocalDate): Flow<Schedule?>
    fun getAllSchedules(userId: String): Flow<List<Schedule>>
    suspend fun createSchedule(schedule: Schedule)
    suspend fun updateSchedule(schedule: Schedule)
    suspend fun updateScheduleStatus(scheduleId: String, status: ScheduleStatus)
    suspend fun deleteSchedule(schedule: Schedule)
    suspend fun syncSchedules(userId: String)
}
