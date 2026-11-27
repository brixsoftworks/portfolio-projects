package com.strictday.verification.providers.notion

import com.strictday.domain.model.NormalizedVerificationEvent
import com.strictday.domain.model.VerificationProvider
import com.strictday.verification.ProviderConnectionStatus
import com.strictday.verification.VerificationProvider as VerificationProviderInterface
import com.strictday.verification.VerificationRuleSpec
import kotlinx.datetime.Instant
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class NotionProvider @Inject constructor() : VerificationProviderInterface {
    override val type: VerificationProvider = VerificationProvider.NOTION

    override suspend fun fetchEvents(
        taskId: String,
        rule: VerificationRuleSpec,
        startTime: Instant,
        endTime: Instant
    ): List<NormalizedVerificationEvent> {
        return emptyList()
    }

    override fun isConnected(): Boolean = false

    override fun connectionStatus(): ProviderConnectionStatus = ProviderConnectionStatus.NotConnected
}
