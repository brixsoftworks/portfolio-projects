package com.strictday.domain.repository

import com.strictday.domain.model.DevicePolicy
import com.strictday.domain.model.DevicePolicyStatus
import kotlinx.coroutines.flow.Flow

interface DevicePolicyRepository {
    fun getActivePolicy(): Flow<DevicePolicy?>
    fun getActivePolicyForTask(taskId: String): Flow<DevicePolicy?>
    fun getAllPolicies(userId: String): Flow<List<DevicePolicy>>
    suspend fun createPolicy(policy: DevicePolicy)
    suspend fun updatePolicyStatus(policyId: String, status: DevicePolicyStatus)
    suspend fun releasePolicy(policyId: String)
}
