package com.strictday.data.local.room

import androidx.room.Database
import androidx.room.RoomDatabase
import com.strictday.data.local.room.dao.AuditEventDao
import com.strictday.data.local.room.dao.DevicePolicyDao
import com.strictday.data.local.room.dao.IntegrationDao
import com.strictday.data.local.room.dao.ScheduleDao
import com.strictday.data.local.room.dao.TaskDao
import com.strictday.data.local.room.dao.VerificationRuleDao
import com.strictday.data.local.room.dao.VerificationStateDao
import com.strictday.data.local.room.entity.LocalAuditEvent
import com.strictday.data.local.room.entity.LocalDevicePolicy
import com.strictday.data.local.room.entity.LocalIntegration
import com.strictday.data.local.room.entity.LocalSchedule
import com.strictday.data.local.room.entity.LocalTask
import com.strictday.data.local.room.entity.LocalVerificationRule
import com.strictday.data.local.room.entity.LocalVerificationState

@Database(
    entities = [
        LocalSchedule::class,
        LocalTask::class,
        LocalVerificationRule::class,
        LocalDevicePolicy::class,
        LocalVerificationState::class,
        LocalAuditEvent::class,
        LocalIntegration::class
    ],
    version = 1,
    exportSchema = true
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun scheduleDao(): ScheduleDao
    abstract fun taskDao(): TaskDao
    abstract fun verificationRuleDao(): VerificationRuleDao
    abstract fun devicePolicyDao(): DevicePolicyDao
    abstract fun verificationStateDao(): VerificationStateDao
    abstract fun auditEventDao(): AuditEventDao
    abstract fun integrationDao(): IntegrationDao
}
