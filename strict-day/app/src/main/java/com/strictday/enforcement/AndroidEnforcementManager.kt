package com.strictday.enforcement

import android.util.Log
import com.strictday.domain.model.DevicePolicyMode
import javax.inject.Inject
import javax.inject.Singleton
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.filterNotNull
import kotlinx.coroutines.flow.first

@Singleton
class AndroidEnforcementManager @Inject constructor(
    private val policyPersistence: PolicyPersistence,
    private val deviceCapabilities: DeviceCapabilities,
    private val appRestrictionManager: AppRestrictionManager,
    private val allowedAppResolver: AllowedAppResolver
) : EnforcementManager {

    private val activeFlow = MutableStateFlow(false)
    private val currentPolicyFlow = MutableStateFlow<EnforcementPolicy?>(null)
    private val blockedAttemptsFlow = MutableStateFlow<BlockedAppAttemptResult?>(null)

    override suspend fun activate(policy: EnforcementPolicy): EnforcementResult {
        val caps = deviceCapabilities.current()
        val needsDeviceOwner = policy.mode == DevicePolicyMode.IRON || policy.mode == DevicePolicyMode.STRICT

        if (needsDeviceOwner && caps.canRestrictApps != DeviceCapabilitiesReport.SUPPORTED) {
            // Honest report: hard blocking is not available without device owner.
            // Activate as a soft lock; consumers should surface the capability report.
            Log.w(
                TAG,
                "Policy ${policy.taskId} requested ${policy.mode} but hard app restriction is " +
                    "${caps.canRestrictApps}; activating soft lock only"
            )
        }

        policyPersistence.save(policy)
        currentPolicyFlow.value = policy
        activeFlow.value = true
        return EnforcementResult.Success
    }

    override suspend fun deactivate(taskId: String): EnforcementResult {
        val current = policyPersistence.current().first()
        if (current?.taskId == taskId) {
            policyPersistence.clear()
            currentPolicyFlow.value = null
            activeFlow.value = false
        }
        return EnforcementResult.Success
    }

    override fun isActive(): Flow<Boolean> = activeFlow

    override fun currentPolicy(): Flow<EnforcementPolicy?> = currentPolicyFlow

    override fun handleBlockedAppAttempt(): Flow<BlockedAppAttemptResult> =
        blockedAttemptsFlow.filterNotNull()

    override suspend fun refreshPolicy(): EnforcementResult {
        // Re-read from persistence to ensure local policy survives restarts
        policyPersistence.current().first()?.let {
            currentPolicyFlow.value = it
            activeFlow.value = true
        }
        return EnforcementResult.Success
    }

    override fun deviceCapabilities(): Flow<DeviceCapabilitiesReport> = deviceCapabilities.flow()

    private companion object {
        private const val TAG = "EnforcementManager"
    }
}