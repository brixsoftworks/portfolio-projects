package com.strictday.enforcement

import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.Json

@Singleton
class PolicyPersistence @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val policyState = MutableStateFlow<EnforcementPolicy?>(loadPersisted())

    fun current(): Flow<EnforcementPolicy?> = policyState

    suspend fun save(policy: EnforcementPolicy) = withContext(Dispatchers.IO) {
        val file = File(context.filesDir, POLICY_FILE)
        file.writeText(Json.encodeToString(EnforcementPolicy.serializer(), policy))
        policyState.value = policy
    }

    suspend fun clear() = withContext(Dispatchers.IO) {
        File(context.filesDir, POLICY_FILE).delete()
        policyState.value = null
    }

    private fun loadPersisted(): EnforcementPolicy? {
        return try {
            val file = File(context.filesDir, POLICY_FILE)
            if (file.exists()) {
                Json.decodeFromString(EnforcementPolicy.serializer(), file.readText())
            } else null
        } catch (_: Exception) {
            null
        }
    }

    companion object {
        private const val POLICY_FILE = "enforcement_policy.json"
    }
}