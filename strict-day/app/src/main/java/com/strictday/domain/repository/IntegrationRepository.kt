package com.strictday.domain.repository

import com.strictday.domain.model.Integration
import com.strictday.domain.model.VerificationProvider
import kotlinx.coroutines.flow.Flow

interface IntegrationRepository {
    fun getIntegrations(userId: String): Flow<List<Integration>>
    fun getIntegrationByProvider(userId: String, provider: VerificationProvider): Flow<Integration?>
    suspend fun connectIntegration(integration: Integration)
    suspend fun disconnectIntegration(id: String)
    suspend fun syncIntegrations(userId: String)
}
