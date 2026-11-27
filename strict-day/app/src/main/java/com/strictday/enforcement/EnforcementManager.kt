package com.strictday.enforcement

import kotlinx.coroutines.flow.Flow

interface EnforcementManager {
    suspend fun activate(policy: EnforcementPolicy): EnforcementResult
    suspend fun deactivate(taskId: String): EnforcementResult
    fun isActive(): Flow<Boolean>
    fun currentPolicy(): Flow<EnforcementPolicy?>
    fun handleBlockedAppAttempt(): Flow<BlockedAppAttemptResult>
    suspend fun refreshPolicy(): EnforcementResult
    fun deviceCapabilities(): Flow<DeviceCapabilitiesReport>
}

sealed class EnforcementResult {
    data object Success : EnforcementResult()
    data class Failure(val reason: String) : EnforcementResult()
}

data class BlockedAppAttemptResult(
    val packageName: String,
    val isBlocked: Boolean,
    val policyMet: Boolean
)