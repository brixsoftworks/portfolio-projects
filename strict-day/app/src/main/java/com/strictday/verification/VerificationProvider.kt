package com.strictday.verification

import com.strictday.domain.model.NormalizedVerificationEvent
import com.strictday.domain.model.VerificationOperator
import com.strictday.domain.model.VerificationProvider as ProviderType
import kotlinx.datetime.Instant

interface VerificationProvider {
    val type: ProviderType
    suspend fun fetchEvents(
        taskId: String,
        rule: VerificationRuleSpec,
        startTime: Instant,
        endTime: Instant
    ): List<NormalizedVerificationEvent>

    fun isConnected(): Boolean
    fun connectionStatus(): ProviderConnectionStatus
}

data class VerificationRuleSpec(
    val provider: ProviderType,
    val eventType: String,
    val operator: VerificationOperator,
    val targetValue: String,
    val minCount: Int,
    val minDurationSeconds: Long
)

sealed class ProviderConnectionStatus {
    data object Connected : ProviderConnectionStatus()
    data object NotConnected : ProviderConnectionStatus()
    data class Error(val message: String) : ProviderConnectionStatus()
}
