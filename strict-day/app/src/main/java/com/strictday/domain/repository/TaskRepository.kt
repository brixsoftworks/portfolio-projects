package com.strictday.domain.repository

import com.strictday.domain.model.Task
import com.strictday.domain.model.TaskStatus
import kotlinx.coroutines.flow.Flow

interface TaskRepository {
    fun getTasksForSchedule(scheduleId: String): Flow<List<Task>>
    fun getTaskById(taskId: String): Flow<Task?>
    fun getActiveTask(scheduleId: String): Flow<Task?>
    fun getNextPendingTask(scheduleId: String): Flow<Task?>
    fun getVerifiedTaskCount(scheduleId: String): Flow<Int>
    fun getTotalTaskCount(scheduleId: String): Flow<Int>
    suspend fun createTask(task: Task)
    suspend fun updateTask(task: Task)
    suspend fun updateTaskStatus(taskId: String, status: TaskStatus)
    suspend fun deleteTask(task: Task)
    suspend fun reorderTasks(scheduleId: String, taskIds: List<String>)
    suspend fun getTasksForScheduleList(scheduleId: String): List<Task>
}
