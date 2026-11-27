package com.strictday.data.local.room.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.strictday.data.local.room.entity.LocalTask
import kotlinx.coroutines.flow.Flow

@Dao
interface TaskDao {
    @Query("SELECT * FROM tasks WHERE scheduleId = :scheduleId ORDER BY orderIndex ASC")
    fun getTasksForSchedule(scheduleId: String): Flow<List<LocalTask>>

    @Query("SELECT * FROM tasks WHERE id = :taskId")
    fun getTaskById(taskId: String): Flow<LocalTask?>

    @Query("SELECT * FROM tasks WHERE scheduleId = :scheduleId AND status = 'active' LIMIT 1")
    fun getActiveTask(scheduleId: String): Flow<LocalTask?>

    @Query("SELECT * FROM tasks WHERE scheduleId = :scheduleId AND status = 'pending' ORDER BY orderIndex ASC LIMIT 1")
    fun getNextPendingTask(scheduleId: String): Flow<LocalTask?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(task: LocalTask)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(tasks: List<LocalTask>)

    @Update
    suspend fun update(task: LocalTask)

    @Delete
    suspend fun delete(task: LocalTask)

    @Query("UPDATE tasks SET status = :status WHERE id = :taskId")
    suspend fun updateTaskStatus(taskId: String, status: String)

    @Query("SELECT * FROM tasks WHERE scheduleId = :scheduleId ORDER BY orderIndex ASC")
    suspend fun getTasksForScheduleList(scheduleId: String): List<LocalTask>

    @Query("SELECT COUNT(*) FROM tasks WHERE scheduleId = :scheduleId AND status = 'verified'")
    fun getVerifiedTaskCount(scheduleId: String): Flow<Int>

    @Query("SELECT COUNT(*) FROM tasks WHERE scheduleId = :scheduleId")
    fun getTotalTaskCount(scheduleId: String): Flow<Int>
}
