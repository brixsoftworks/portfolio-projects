package com.strictday.data.local.room.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.strictday.data.local.room.entity.LocalSchedule
import kotlinx.coroutines.flow.Flow

@Dao
interface ScheduleDao {
    @Query("SELECT * FROM schedules WHERE userId = :userId AND localDate = :date LIMIT 1")
    fun getScheduleByDate(userId: String, date: String): Flow<LocalSchedule?>

    @Query("SELECT * FROM schedules WHERE userId = :userId ORDER BY localDate DESC")
    fun getAllSchedules(userId: String): Flow<List<LocalSchedule>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(schedule: LocalSchedule)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(schedules: List<LocalSchedule>)

    @Delete
    suspend fun delete(schedule: LocalSchedule)

    @Query("DELETE FROM schedules WHERE userId = :userId")
    suspend fun deleteAllForUser(userId: String)
}
