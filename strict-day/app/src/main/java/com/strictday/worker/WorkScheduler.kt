package com.strictday.worker

import android.content.Context
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import dagger.hilt.android.qualifiers.ApplicationContext
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class WorkScheduler @Inject constructor(
    @ApplicationContext private val context: Context
) {

    fun scheduleEnforcement() {
        val request = PeriodicWorkRequestBuilder<ScheduleActivationWorker>(
            15, TimeUnit.MINUTES
        ).build()
        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            WorkNames.SCHEDULE_ACTIVATION,
            ExistingPeriodicWorkPolicy.UPDATE,
            request
        )
    }

    fun scheduleVerification() {
        val request = PeriodicWorkRequestBuilder<VerificationWorker>(
            30, TimeUnit.MINUTES
        ).build()
        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            WorkNames.VERIFICATION,
            ExistingPeriodicWorkPolicy.UPDATE,
            request
        )
    }

    fun scheduleSync() = SyncWorker.enqueuePeriodic(context)

    fun scheduleAll() {
        scheduleEnforcement()
        scheduleVerification()
        scheduleSync()
    }
}
