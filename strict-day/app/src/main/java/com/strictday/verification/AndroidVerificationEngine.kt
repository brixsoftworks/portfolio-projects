package com.strictday.verification

import com.strictday.data.local.room.dao.VerificationStateDao
import com.strictday.data.local.room.entity.LocalVerificationState
import com.strictday.domain.model.NormalizedVerificationEvent
import com.strictday.domain.repository.VerificationRuleRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map
import kotlinx.datetime.Clock
import kotlinx.datetime.Instant
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AndroidVerificationEngine @Inject constructor(
    private val ruleRepository: VerificationRuleRepository,
    private val stateDao: VerificationStateDao,
    private val ruleEvaluator: VerificationRuleEvaluator,
) : VerificationEngine {

    override fun verificationState(taskId: String): Flow<VerificationState> {
        return stateDao.getVerificationState(taskId).map { local ->
            if (local == null) {
                VerificationState(
                    taskId = taskId,
                    isVerified = false,
                    rulesMet = 0,
                    rulesTotal = 0,
                    lastCheckedAt = Clock.System.now(),
                    details = emptyList()
                )
            } else {
                VerificationState(
                    taskId = taskId,
                    isVerified = local.isVerified,
                    rulesMet = if (local.isVerified) 1 else 0,
                    rulesTotal = 1,
                    lastCheckedAt = Instant.fromEpochMilliseconds(local.lastCheckedAt),
                    details = emptyList()
                )
            }
        }
    }

    override suspend fun refreshVerification(taskId: String): VerificationState {
        val rules = ruleRepository.getRulesForTask(taskId).first()
        if (rules.isEmpty()) {
            val emptyState = VerificationState(
                taskId = taskId,
                isVerified = false,
                rulesMet = 0,
                rulesTotal = 0,
                lastCheckedAt = Clock.System.now(),
                details = emptyList()
            )
            return emptyState
        }

        val evaluations = rules.map { rule ->
            ruleEvaluator.evaluate(rule, emptyList())
        }

        val allMet = evaluations.all { it.isMet } && evaluations.isNotEmpty()
        val details = evaluations.map { ev ->
            VerificationDetail(
                ruleId = ev.rule.id,
                description = "${ev.rule.provider.name}: ${ev.rule.eventType} ${ev.rule.operator.name} ${ev.rule.targetValue}",
                isMet = ev.isMet,
                actualValue = null,
                targetValue = ev.rule.targetValue
            )
        }

        val state = VerificationState(
            taskId = taskId,
            isVerified = allMet,
            rulesMet = evaluations.count { it.isMet },
            rulesTotal = rules.size,
            lastCheckedAt = Clock.System.now(),
            details = details
        )

        stateDao.upsert(
            LocalVerificationState(
                taskId = taskId,
                provider = if (rules.isNotEmpty()) rules.first().provider.name else "",
                isVerified = allMet,
                lastCheckedAt = Clock.System.now().toEpochMilliseconds(),
                eventsJson = "[]"
            )
        )

        return state
    }

    override suspend fun recordProviderEvents(taskId: String, events: List<NormalizedVerificationEvent>) {
        // Events are persisted for audit purposes only.
        // Verification state is never derived from client-submitted events.
    }

    override fun pendingVerificationTasks(): Flow<List<String>> = flow {
        emit(emptyList())
    }
}
