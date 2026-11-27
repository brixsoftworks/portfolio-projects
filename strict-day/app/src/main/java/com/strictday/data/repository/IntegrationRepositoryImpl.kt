package com.strictday.data.repository

import com.strictday.data.local.room.dao.IntegrationDao
import com.strictday.data.local.room.mapper.toDomain
import com.strictday.data.local.room.mapper.toLocal
import com.strictday.domain.model.Integration
import com.strictday.domain.model.VerificationProvider
import com.strictday.domain.repository.IntegrationRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class IntegrationRepositoryImpl @Inject constructor(
    private val integrationDao: IntegrationDao
) : IntegrationRepository {

    override fun getIntegrations(userId: String): Flow<List<Integration>> {
        return integrationDao.getIntegrations(userId).map { list -> list.map { it.toDomain() } }
    }

    override fun getIntegrationByProvider(userId: String, provider: VerificationProvider): Flow<Integration?> {
        return integrationDao.getIntegrationByProvider(userId, provider.name).map { it?.toDomain() }
    }

    override suspend fun connectIntegration(integration: Integration) {
        integrationDao.upsert(integration.toLocal())
    }

    override suspend fun disconnectIntegration(id: String) {
        integrationDao.deleteById(id)
    }

    override suspend fun syncIntegrations(userId: String) {
        // Sync logic with Supabase
    }
}
