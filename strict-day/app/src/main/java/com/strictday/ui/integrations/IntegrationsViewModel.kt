package com.strictday.ui.integrations

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.strictday.data.local.datastore.UserPreferences
import com.strictday.domain.model.Integration
import com.strictday.domain.model.IntegrationStatus
import com.strictday.domain.model.VerificationProvider
import com.strictday.domain.repository.IntegrationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.launch
import kotlinx.coroutines.ExperimentalCoroutinesApi

enum class ProviderConnectionStatus {
    CONNECTED,
    CONNECTING,
    NOT_CONNECTED,
    ERROR
}

data class IntegrationItem(
    val integration: Integration?,
    val provider: VerificationProvider,
    val providerName: String,
    val connectionStatus: ProviderConnectionStatus
)

data class IntegrationsUiState(
    val providers: List<IntegrationItem> = emptyList(),
    val isLoading: Boolean = true
)

@OptIn(ExperimentalCoroutinesApi::class)
@HiltViewModel
class IntegrationsViewModel @Inject constructor(
    private val integrationRepository: IntegrationRepository,
    private val userPreferences: UserPreferences
) : ViewModel() {

    private val _uiState = MutableStateFlow(IntegrationsUiState())
    val uiState: StateFlow<IntegrationsUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            userPreferences.settings.flatMapLatest { settings ->
                if (settings.userId.isBlank()) {
                    flowOf(emptyList())
                } else {
                    integrationRepository.getIntegrations(settings.userId)
                }
            }.map { integrations ->
                IntegrationsUiState(
                    providers = VerificationProvider.entries.map { provider ->
                        val integration = integrations.firstOrNull { it.provider == provider }
                        IntegrationItem(
                            integration = integration,
                            provider = provider,
                            providerName = displayName(provider),
                            connectionStatus = when (integration?.status) {
                                null -> ProviderConnectionStatus.NOT_CONNECTED
                                IntegrationStatus.CONNECTED -> ProviderConnectionStatus.CONNECTED
                                IntegrationStatus.DISCONNECTED -> ProviderConnectionStatus.NOT_CONNECTED
                                IntegrationStatus.ERROR -> ProviderConnectionStatus.ERROR
                                IntegrationStatus.EXPIRED -> ProviderConnectionStatus.ERROR
                            }
                        )
                    },
                    isLoading = false
                )
            }.collect { _uiState.value = it }
        }
    }

    fun disconnect(item: IntegrationItem) {
        val integrationId = item.integration?.id ?: return
        viewModelScope.launch {
            integrationRepository.disconnectIntegration(integrationId)
        }
    }

    private fun displayName(provider: VerificationProvider): String = when (provider) {
        VerificationProvider.GITHUB -> "GitHub"
        VerificationProvider.GOOGLE_DOCS -> "Google Docs"
        VerificationProvider.NOTION -> "Notion"
        VerificationProvider.FITNESS -> "Fitness"
    }
}