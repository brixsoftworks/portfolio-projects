package com.strictday.data.repository

import com.strictday.data.local.room.dao.VerificationRuleDao
import com.strictday.data.local.room.mapper.toDomain
import com.strictday.data.local.room.mapper.toLocal
import com.strictday.domain.model.VerificationRule
import com.strictday.domain.repository.VerificationRuleRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class VerificationRuleRepositoryImpl @Inject constructor(
    private val verificationRuleDao: VerificationRuleDao
) : VerificationRuleRepository {

    override fun getRulesForTask(taskId: String): Flow<List<VerificationRule>> {
        return verificationRuleDao.getRulesForTask(taskId).map { list -> list.map { it.toDomain() } }
    }

    override suspend fun createRule(rule: VerificationRule) {
        verificationRuleDao.upsert(rule.toLocal())
    }

    override suspend fun updateRule(rule: VerificationRule) {
        verificationRuleDao.upsert(rule.toLocal())
    }

    override suspend fun deleteRule(rule: VerificationRule) {
        verificationRuleDao.delete(rule.toLocal())
    }

    override suspend fun deleteAllForTask(taskId: String) {
        verificationRuleDao.deleteAllForTask(taskId)
    }
}
