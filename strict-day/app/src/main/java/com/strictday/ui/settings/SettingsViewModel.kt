package com.strictday.ui.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.strictday.data.local.datastore.UserPreferences
import com.strictday.domain.model.Strictness
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class SettingsUiState(
    val defaultStrictness: Strictness = Strictness.NORMAL,
    val wakeTime: String = "07:00",
    val sleepTime: String = "23:00",
    val emergencyOverrideEnabled: Boolean = true,
    val emergencyOverrideRequiresConfirm: Boolean = true,
    val ironModeOverrideDisabled: Boolean = false,
    val timezone: String = "UTC",
    val userId: String = "",
    val onboardingCompleted: Boolean = false
)

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val userPreferences: UserPreferences
) : ViewModel() {

    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            userPreferences.settings.collect { settings ->
                _uiState.value = SettingsUiState(
                    defaultStrictness = runCatching { Strictness.valueOf(settings.defaultStrictness) }
                        .getOrDefault(Strictness.NORMAL),
                    wakeTime = settings.wakeTime,
                    sleepTime = settings.sleepTime,
                    emergencyOverrideEnabled = settings.emergencyOverrideEnabled,
                    emergencyOverrideRequiresConfirm = settings.emergencyOverrideRequiresConfirm,
                    ironModeOverrideDisabled = settings.ironModeOverrideDisabled,
                    timezone = settings.timezone,
                    userId = settings.userId,
                    onboardingCompleted = settings.onboardingCompleted
                )
            }
        }
    }

    fun updateDefaultStrictness(strictness: Strictness) {
        viewModelScope.launch {
            userPreferences.updateDefaultStrictness(strictness.name)
        }
    }

    fun updateWakeTime(value: String) {
        viewModelScope.launch {
            userPreferences.updateWakeTime(value)
        }
    }

    fun updateSleepTime(value: String) {
        viewModelScope.launch {
            userPreferences.updateSleepTime(value)
        }
    }

    fun updateEmergencyOverride(enabled: Boolean, requiresConfirm: Boolean, ironDisabled: Boolean) {
        viewModelScope.launch {
            userPreferences.updateEmergencyOverride(enabled, requiresConfirm, ironDisabled)
        }
    }

    fun updateTimezone(value: String) {
        viewModelScope.launch {
            userPreferences.updateTimezone(value)
        }
    }
}