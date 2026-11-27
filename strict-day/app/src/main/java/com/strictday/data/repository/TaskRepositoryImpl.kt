package com.strictday.data.repository

import com.strictday.data.local.room.dao.TaskDao
import com.strictday.data.local.room.mapper.toDomain
import com.strictday.data.local.room.mapper.toLocal
import com.strictday.domain.model.Task
import com.strictday.domain.model.TaskStatus
import com.strictday.domain.repository.TaskRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TaskRepositoryImpl @Inject constructor(
    private val taskDao: TaskDao
) : TaskRepository {

    override fun getTasksForSchedule(scheduleId: String): Flow<List<Task>> {
        return taskDao.getTasksForSchedule(scheduleId).map { list -> list.map { it.toDomain() } }
    }

    override fun getTaskById(taskId: String): Flow<Task?> {
        return taskDao.getTaskById(taskId).map { it?.toDomain() }
    }

    override fun getActiveTask(scheduleId: String): Flow<Task?> {
        return taskDao.getActiveTask(scheduleId).map { it?.toDomain() }
    }

    override fun getNextPendingTask(scheduleId: String): Flow<Task?> {
        return taskDao.getNextPendingTask(scheduleId).map { it?.toDomain() }
    }

    override fun getVerifiedTaskCount(scheduleId: String): Flow<Int> {
        return taskDao.getVerifiedTaskCount(scheduleId)
    }

    override fun getTotalTaskCount(scheduleId: String): Flow<Int> {
        return taskDao.getTotalTaskCount(scheduleId)
    }

    override suspend fun createTask(task: Task) {
        taskDao.upsert(task.toLocal())
    }

    override suspend fun updateTask(task: Task) {
        taskDao.update(task.toLocal())
    }

    override suspend fun updateTaskStatus(taskId: String, status: TaskStatus) {
        taskDao.updateTaskStatus(taskId, status.name)
    }

    override suspend fun deleteTask(task: Task) {
        taskDao.delete(task.toLocal())
    }

    override suspend fun reorderTasks(scheduleId: String, taskIds: List<String>) {
        taskIds.forEachIndexed { index, taskId ->
            taskDao.getTaskById(taskId).map { it?.toDomain() }
        }
    }

    override suspend fun getTasksForScheduleList(scheduleId: String): List<Task> {
        return taskDao.getTasksForScheduleList(scheduleId).map { it.toDomain() }
    }
}
