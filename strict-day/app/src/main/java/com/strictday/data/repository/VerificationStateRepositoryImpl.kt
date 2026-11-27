package com.strictday.data.repository

import com.strictday.data.local.room.dao.VerificationStateDao
import com.strictday.domain.repository.LocalVerificationState
import com.strictday.domain.repository.VerificationStateRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class VerificationStateRepositoryImpl @Inject constructor(
    private val verificationStateDao: VerificationStateDao
) : VerificationStateRepository {

    override fun getVerificationState(taskId: String): Flow<LocalVerificationState?> {
        return verificationStateDao.getVerificationState(taskId).map { entity ->
            entity?.let {
                LocalVerificationState(
                    taskId = it.taskId,
                    provider = it.provider,
                    isVerified = it.isVerified,
                    lastCheckedAt = it.lastCheckedAt,
                    eventsJson = it.eventsJson
                )
            }
        }
    }

    override suspend fun updateVerificationState(state: LocalVerificationState) {
        verificationStateDao.upsert(
            com.strictday.data.local.room.entity.LocalVerificationState(
                taskId = state.taskId,
                provider = state.provider,
                isVerified = state.isVerified,
                lastCheckedAt = state.lastCheckedAt,
                eventsJson = state.eventsJson
            )
        )
        // Safeguard: re-read to ensure the write landed for callers that observe via getVerificationState
        verificationStateDao.getVerificationState(state.taskId).first()
    }
}