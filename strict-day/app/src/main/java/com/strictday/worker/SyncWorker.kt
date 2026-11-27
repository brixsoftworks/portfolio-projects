package com.strictday.worker

import android.content.Context
import android.util.Log
import androidx.hilt.work.HiltWorker
import androidx.work.CoroutineWorker
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import com.strictday.data.local.datastore.UserPreferences
import com.strictday.data.remote.supabase.SessionTokenStore
import com.strictday.data.remote.supabase.SupabaseSyncService
import com.strictday.domain.repository.AuditRepository
import com.strictday.domain.repository.ScheduleRepository
import com.strictday.domain.repository.TaskRepository
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.flow.first

@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted appContext: Context,
    @Assisted params: WorkerParameters,
    private val syncService: SupabaseSyncService,
    private val tokenStore: SessionTokenStore,
    private val userPreferences: UserPreferences,
    private val scheduleRepository: ScheduleRepository,
    private val taskRepository: TaskRepository,
    private val auditRepository: AuditRepository,
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result {
        if (!syncService.isAvailable) {
            Log.d(TAG, "Supabase sync is not configured; skipping")
            return Result.success()
        }

        val prefs = userPreferences.settings.first()
        val token = prefs.supabaseSessionToken
        if (token.isBlank()) {
            Log.d(TAG, "No Supabase session token; nothing to sync")
            return Result.success()
        }
        val userId = prefs.userId
        if (userId.isBlank()) {
            Log.d(TAG, "No local user id; nothing to sync")
            return Result.success()
        }

        tokenStore.update(token)

        val schedules = scheduleRepository.getAllSchedules(userId).first()
        schedules.forEach { schedule ->
            val schedulePushed = runCatching {
                syncService.pushSchedule(schedule, userId)
            }.getOrDefault(false)
            if (schedulePushed) {
                val tasks = taskRepository.getTasksForScheduleList(schedule.id)
                syncService.pushTasks(tasks, userId)
            }
        }

        val auditEvents = auditRepository.getRecentEvents(userId, limit = 200).first()
        auditEvents.forEach { event ->
            runCatching { syncService.pushAuditEvent(event) }
        }

        Log.d(TAG, "Sync finished: ${schedules.size} schedules, ${auditEvents.size} audit events")
        return Result.success()
    }

    companion object {
        private const val TAG = "SyncWorker"

        fun enqueuePeriodic(context: Context) {
            val request = PeriodicWorkRequestBuilder<SyncWorker>(6, TimeUnit.HOURS)
                .build()
            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                WorkNames.SYNC,
                ExistingPeriodicWorkPolicy.KEEP,
                request
            )
        }
    }
}