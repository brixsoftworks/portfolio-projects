package com.strictday.data.repository

import com.strictday.data.local.room.dao.DevicePolicyDao
import com.strictday.data.local.room.mapper.toDomain
import com.strictday.data.local.room.mapper.toLocal
import com.strictday.domain.model.DevicePolicy
import com.strictday.domain.model.DevicePolicyStatus
import com.strictday.domain.repository.DevicePolicyRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.datetime.Clock
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DevicePolicyRepositoryImpl @Inject constructor(
    private val devicePolicyDao: DevicePolicyDao
) : DevicePolicyRepository {

    override fun getActivePolicy(): Flow<DevicePolicy?> {
        return devicePolicyDao.getActivePolicy().map { it?.toDomain() }
    }

    override fun getActivePolicyForTask(taskId: String): Flow<DevicePolicy?> {
        return devicePolicyDao.getActivePolicyForTask(taskId).map { it?.toDomain() }
    }

    override fun getAllPolicies(userId: String): Flow<List<DevicePolicy>> {
        return devicePolicyDao.getAllPolicies(userId).map { list -> list.map { it.toDomain() } }
    }

    override suspend fun createPolicy(policy: DevicePolicy) {
        devicePolicyDao.upsert(policy.toLocal())
    }

    override suspend fun updatePolicyStatus(policyId: String, status: DevicePolicyStatus) {
        // Simplified - in production, fetch and update
    }

    override suspend fun releasePolicy(policyId: String) {
        devicePolicyDao.updatePolicyStatus(
            policyId = policyId,
            status = DevicePolicyStatus.RELEASED.name,
            releasedAt = Clock.System.now().toEpochMilliseconds()
        )
    }
}
