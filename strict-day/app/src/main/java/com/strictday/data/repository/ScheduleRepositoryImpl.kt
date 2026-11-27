package com.strictday.data.repository

import com.strictday.data.local.room.dao.ScheduleDao
import com.strictday.data.local.room.mapper.toDomain
import com.strictday.data.local.room.mapper.toLocal
import com.strictday.domain.model.Schedule
import com.strictday.domain.model.ScheduleStatus
import com.strictday.domain.repository.ScheduleRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.datetime.LocalDate
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ScheduleRepositoryImpl @Inject constructor(
    private val scheduleDao: ScheduleDao
) : ScheduleRepository {

    override fun getScheduleByDate(userId: String, date: LocalDate): Flow<Schedule?> {
        return scheduleDao.getScheduleByDate(userId, date.toString()).map { it?.toDomain() }
    }

    override fun getAllSchedules(userId: String): Flow<List<Schedule>> {
        return scheduleDao.getAllSchedules(userId).map { list -> list.map { it.toDomain() } }
    }

    override suspend fun createSchedule(schedule: Schedule) {
        scheduleDao.upsert(schedule.toLocal())
    }

    override suspend fun updateSchedule(schedule: Schedule) {
        scheduleDao.upsert(schedule.toLocal())
    }

    override suspend fun updateScheduleStatus(scheduleId: String, status: ScheduleStatus) {
        // This is a simplified approach; in production, fetch and update
    }

    override suspend fun deleteSchedule(schedule: Schedule) {
        scheduleDao.delete(schedule.toLocal())
    }

    override suspend fun syncSchedules(userId: String) {
        // Sync logic will be implemented with Supabase
    }
}
