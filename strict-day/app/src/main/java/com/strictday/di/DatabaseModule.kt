package com.strictday.di

import android.content.Context
import androidx.room.Room
import com.strictday.data.local.room.AppDatabase
import com.strictday.data.local.room.dao.AuditEventDao
import com.strictday.data.local.room.dao.DevicePolicyDao
import com.strictday.data.local.room.dao.IntegrationDao
import com.strictday.data.local.room.dao.ScheduleDao
import com.strictday.data.local.room.dao.TaskDao
import com.strictday.data.local.room.dao.VerificationRuleDao
import com.strictday.data.local.room.dao.VerificationStateDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides
    @Singleton
    fun provideAppDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(context, AppDatabase::class.java, "strict_day.db")
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides fun provideScheduleDao(db: AppDatabase): ScheduleDao = db.scheduleDao()
    @Provides fun provideTaskDao(db: AppDatabase): TaskDao = db.taskDao()
    @Provides fun provideVerificationRuleDao(db: AppDatabase): VerificationRuleDao = db.verificationRuleDao()
    @Provides fun provideDevicePolicyDao(db: AppDatabase): DevicePolicyDao = db.devicePolicyDao()
    @Provides fun provideVerificationStateDao(db: AppDatabase): VerificationStateDao = db.verificationStateDao()
    @Provides fun provideAuditEventDao(db: AppDatabase): AuditEventDao = db.auditEventDao()
    @Provides fun provideIntegrationDao(db: AppDatabase): IntegrationDao = db.integrationDao()
}