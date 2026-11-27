package com.strictday.di

import com.strictday.data.repository.AuditRepositoryImpl
import com.strictday.data.repository.DevicePolicyRepositoryImpl
import com.strictday.data.repository.IntegrationRepositoryImpl
import com.strictday.data.repository.ScheduleRepositoryImpl
import com.strictday.data.repository.TaskRepositoryImpl
import com.strictday.data.repository.VerificationRuleRepositoryImpl
import com.strictday.data.repository.VerificationStateRepositoryImpl
import com.strictday.domain.repository.AuditRepository
import com.strictday.domain.repository.DevicePolicyRepository
import com.strictday.domain.repository.IntegrationRepository
import com.strictday.domain.repository.ScheduleRepository
import com.strictday.domain.repository.TaskRepository
import com.strictday.domain.repository.VerificationRuleRepository
import com.strictday.domain.repository.VerificationStateRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds @Singleton abstract fun bindScheduleRepository(impl: ScheduleRepositoryImpl): ScheduleRepository
    @Binds @Singleton abstract fun bindTaskRepository(impl: TaskRepositoryImpl): TaskRepository
    @Binds @Singleton abstract fun bindVerificationRuleRepository(impl: VerificationRuleRepositoryImpl): VerificationRuleRepository
    @Binds @Singleton abstract fun bindDevicePolicyRepository(impl: DevicePolicyRepositoryImpl): DevicePolicyRepository
    @Binds @Singleton abstract fun bindAuditRepository(impl: AuditRepositoryImpl): AuditRepository
    @Binds @Singleton abstract fun bindIntegrationRepository(impl: IntegrationRepositoryImpl): IntegrationRepository
    @Binds @Singleton abstract fun bindVerificationStateRepository(impl: VerificationStateRepositoryImpl): VerificationStateRepository
}