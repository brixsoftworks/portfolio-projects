package com.strictday.domain.repository

import com.strictday.domain.model.VerificationRule
import kotlinx.coroutines.flow.Flow

interface VerificationRuleRepository {
    fun getRulesForTask(taskId: String): Flow<List<VerificationRule>>
    suspend fun createRule(rule: VerificationRule)
    suspend fun updateRule(rule: VerificationRule)
    suspend fun deleteRule(rule: VerificationRule)
    suspend fun deleteAllForTask(taskId: String)
}
