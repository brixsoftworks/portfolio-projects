package com.strictday.verification

import com.strictday.domain.model.NormalizedVerificationEvent
import kotlinx.coroutines.flow.Flow
import kotlinx.datetime.Instant

interface VerificationEngine {
    fun verificationState(taskId: String): Flow<VerificationState>
    suspend fun refreshVerification(taskId: String): VerificationState
    suspend fun recordProviderEvents(taskId: String, events: List<NormalizedVerificationEvent>)
    fun pendingVerificationTasks(): Flow<List<String>>
}

data class VerificationState(
    val taskId: String,
    val isVerified: Boolean,
    val rulesMet: Int,
    val rulesTotal: Int,
    val lastCheckedAt: Instant,
    val details: List<VerificationDetail>
)

data class VerificationDetail(
    val ruleId: String,
    val description: String,
    val isMet: Boolean,
    val actualValue: String?,
    val targetValue: String
)
