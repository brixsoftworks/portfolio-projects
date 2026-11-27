package com.strictday.ui.onboarding

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.strictday.data.local.datastore.UserPreferences
import com.strictday.domain.model.Strictness
import com.strictday.enforcement.DeviceCapabilitiesReport
import com.strictday.enforcement.EnforcementManager
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class OnboardingUiState(
    val currentStep: Int = 0,
    val totalSteps: Int = 4,
    val preferredStrictness: Strictness = Strictness.NORMAL,
    val deviceCapabilities: DeviceCapabilitiesReport? = null,
    val isLoadingCapabilities: Boolean = true,
    val isComplete: Boolean = false,
    val canAdvance: Boolean = true
)

@HiltViewModel
class OnboardingViewModel @Inject constructor(
    private val userPreferences: UserPreferences,
    private val enforcementManager: EnforcementManager
) : ViewModel() {

    private val _uiState = MutableStateFlow(OnboardingUiState())
    val uiState: StateFlow<OnboardingUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            enforcementManager.deviceCapabilities().collect { capabilities ->
                _uiState.update {
                    it.copy(
                        deviceCapabilities = capabilities,
                        isLoadingCapabilities = false
                    )
                }
            }
        }
    }

    fun selectStrictness(strictness: Strictness) {
        _uiState.update { it.copy(preferredStrictness = strictness) }
    }

    fun nextStep() {
        val current = _uiState.value
        if (current.currentStep < current.totalSteps - 1) {
            _uiState.update { it.copy(currentStep = it.currentStep + 1) }
        } else {
            completeOnboarding()
        }
    }

    fun previousStep() {
        val current = _uiState.value
        if (current.currentStep > 0) {
            _uiState.update { it.copy(currentStep = it.currentStep - 1) }
        }
    }

    fun completeOnboarding() {
        viewModelScope.launch {
            userPreferences.updateDefaultStrictness(_uiState.value.preferredStrictness.name)
            userPreferences.completeOnboarding()
            _uiState.update { it.copy(isComplete = true) }
        }
    }
}