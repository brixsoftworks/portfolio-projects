package com.strictday.data.local.datastore

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.longPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "user_preferences")

data class UserSettings(
    val userId: String = "",
    val defaultStrictness: String = "NORMAL",
    val wakeTime: String = "07:00",
    val sleepTime: String = "23:00",
    val emergencyOverrideEnabled: Boolean = true,
    val emergencyOverrideRequiresConfirm: Boolean = true,
    val ironModeOverrideDisabled: Boolean = false,
    val timezone: String = "UTC",
    val onboardingCompleted: Boolean = false,
    val supabaseSessionToken: String = ""
)

@Singleton
class UserPreferences @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val dataStore = context.dataStore

    private object Keys {
        val USER_ID = stringPreferencesKey("user_id")
        val DEFAULT_STRICTNESS = stringPreferencesKey("default_strictness")
        val WAKE_TIME = stringPreferencesKey("wake_time")
        val SLEEP_TIME = stringPreferencesKey("sleep_time")
        val EMERGENCY_OVERRIDE_ENABLED = stringPreferencesKey("emergency_override_enabled")
        val EMERGENCY_OVERRIDE_CONFIRM = stringPreferencesKey("emergency_override_confirm")
        val IRON_OVERRIDE_DISABLED = stringPreferencesKey("iron_override_disabled")
        val TIMEZONE = stringPreferencesKey("timezone")
        val ONBOARDING_COMPLETED = stringPreferencesKey("onboarding_completed")
        val SUPABASE_SESSION_TOKEN = stringPreferencesKey("supabase_session_token")
    }

    val settings: Flow<UserSettings> = dataStore.data.map { prefs ->
        UserSettings(
            userId = prefs[Keys.USER_ID] ?: "",
            defaultStrictness = prefs[Keys.DEFAULT_STRICTNESS] ?: "NORMAL",
            wakeTime = prefs[Keys.WAKE_TIME] ?: "07:00",
            sleepTime = prefs[Keys.SLEEP_TIME] ?: "23:00",
            emergencyOverrideEnabled = prefs[Keys.EMERGENCY_OVERRIDE_ENABLED] != "false",
            emergencyOverrideRequiresConfirm = prefs[Keys.EMERGENCY_OVERRIDE_CONFIRM] != "false",
            ironModeOverrideDisabled = prefs[Keys.IRON_OVERRIDE_DISABLED] == "true",
            timezone = prefs[Keys.TIMEZONE] ?: "UTC",
            onboardingCompleted = prefs[Keys.ONBOARDING_COMPLETED] == "true",
            supabaseSessionToken = prefs[Keys.SUPABASE_SESSION_TOKEN] ?: ""
        )
    }

    suspend fun updateUserId(userId: String) {
        dataStore.edit { it[Keys.USER_ID] = userId }
    }

    suspend fun updateDefaultStrictness(strictness: String) {
        dataStore.edit { it[Keys.DEFAULT_STRICTNESS] = strictness }
    }

    suspend fun updateWakeTime(time: String) {
        dataStore.edit { it[Keys.WAKE_TIME] = time }
    }

    suspend fun updateSleepTime(time: String) {
        dataStore.edit { it[Keys.SLEEP_TIME] = time }
    }

    suspend fun updateEmergencyOverride(enabled: Boolean, requiresConfirm: Boolean, ironDisabled: Boolean) {
        dataStore.edit {
            it[Keys.EMERGENCY_OVERRIDE_ENABLED] = enabled.toString()
            it[Keys.EMERGENCY_OVERRIDE_CONFIRM] = requiresConfirm.toString()
            it[Keys.IRON_OVERRIDE_DISABLED] = ironDisabled.toString()
        }
    }

    suspend fun updateTimezone(timezone: String) {
        dataStore.edit { it[Keys.TIMEZONE] = timezone }
    }

    suspend fun completeOnboarding() {
        dataStore.edit { it[Keys.ONBOARDING_COMPLETED] = "true" }
    }

    suspend fun updateSupabaseSessionToken(token: String) {
        dataStore.edit { it[Keys.SUPABASE_SESSION_TOKEN] = token }
    }
}
