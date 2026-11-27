package com.strictday.domain.repository

import kotlinx.coroutines.flow.Flow

data class LocalVerificationState(
    val taskId: String,
    val provider: String,
    val isVerified: Boolean,
    val lastCheckedAt: Long,
    val eventsJson: String
)

interface VerificationStateRepository {
    fun getVerificationState(taskId: String): Flow<LocalVerificationState?>
    suspend fun updateVerificationState(state: LocalVerificationState)
}
