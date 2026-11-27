package com.strictday.ui.onboarding

import android.content.Context
import android.content.Intent
import android.os.Build
import android.provider.Settings as AndroidSettings
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.OpenInNew
import androidx.compose.material.icons.filled.PictureInPicture
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.outlined.Circle
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.strictday.domain.model.Strictness
import com.strictday.enforcement.DeviceCapabilitiesReport

private const val TOTAL_STEPS = 4

@Composable
fun OnboardingScreen(
    onComplete: () -> Unit,
    viewModel: OnboardingViewModel = hiltViewModel(),
) {
    val state by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Spacer(Modifier.height(16.dp))

            LinearProgressIndicator(
                progress = { (state.currentStep.toFloat() + 1f) / TOTAL_STEPS.toFloat() },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(4.dp),
                color = MaterialTheme.colorScheme.primary,
                trackColor = MaterialTheme.colorScheme.surfaceVariant,
            )

            Spacer(Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center,
            ) {
                repeat(TOTAL_STEPS) { index ->
                    Icon(
                        imageVector = if (index <= state.currentStep) {
                            Icons.Filled.CheckCircle
                        } else {
                            Icons.Outlined.Circle
                        },
                        contentDescription = null,
                        modifier = Modifier.size(12.dp),
                        tint = if (index <= state.currentStep) {
                            MaterialTheme.colorScheme.primary
                        } else {
                            MaterialTheme.colorScheme.surfaceVariant
                        },
                    )
                    if (index < TOTAL_STEPS - 1) {
                        Spacer(Modifier.width(8.dp))
                    }
                }
            }

            Spacer(Modifier.height(32.dp))

            AnimatedContent(
                targetState = state.currentStep,
                transitionSpec = {
                    (slideInHorizontally { it } + fadeIn()).togetherWith(
                        slideOutHorizontally { -it } + fadeOut(),
                    )
                },
                label = "step_transition",
            ) { step ->
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f)
                        .verticalScroll(rememberScrollState()),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    when (step) {
                        0 -> StepWelcome()
                        1 -> StepEnforcementPreference(
                            selectedPreference = state.preferredStrictness.toEnforcementLevel(),
                            onSelect = { level -> viewModel.selectStrictness(level.toStrictness()) },
                        )
                        2 -> StepPermissions(
                            context = context,
                            capabilities = state.deviceCapabilities,
                        )
                        3 -> StepIntegrations()
                    }
                }
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 24.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                if (state.currentStep > 0) {
                    OutlinedButton(
                        onClick = viewModel::previousStep,
                        modifier = Modifier.weight(1f),
                    ) {
                        Text("Back")
                    }
                }

                if (state.currentStep < TOTAL_STEPS - 1) {
                    FilledTonalButton(
                        onClick = viewModel::nextStep,
                        modifier = Modifier.weight(if (state.currentStep > 0) 1f else 2f),
                        enabled = state.canAdvance,
                    ) {
                        Text("Continue")
                        Spacer(Modifier.width(8.dp))
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowForward,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp),
                        )
                    }
                } else {
                    FilledTonalButton(
                        onClick = onComplete,
                        modifier = Modifier.weight(2f),
                    ) {
                        Text("Start")
                        Spacer(Modifier.width(8.dp))
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowForward,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp),
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun StepWelcome() {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
        modifier = Modifier.fillMaxWidth(),
    ) {
        Spacer(Modifier.height(48.dp))

        Icon(
            imageVector = Icons.Default.Lock,
            contentDescription = null,
            modifier = Modifier.size(72.dp),
            tint = MaterialTheme.colorScheme.primary,
        )

        Spacer(Modifier.height(24.dp))

        Text(
            text = "Take control of your day.",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onBackground,
        )

        Spacer(Modifier.height(16.dp))

        Text(
            text = "Strict Day turns your plans into enforceable actions. " +
                "Set your schedule, choose how strictly you want to be held, " +
                "and let the system hold you accountable.",
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(horizontal = 16.dp),
        )
    }
}

@Composable
private fun StepEnforcementPreference(
    selectedPreference: EnforcementLevel?,
    onSelect: (EnforcementLevel) -> Unit,
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text(
            text = "Enforcement Level",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground,
        )

        Spacer(Modifier.height(8.dp))

        Text(
            text = "Choose how strictly your schedule is enforced. " +
                "This determines what the app is permitted to do on your device.",
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Spacer(Modifier.height(24.dp))

        EnforcementLevel.entries.forEach { level ->
            EnforcementCard(
                level = level,
                isSelected = selectedPreference == level,
                onSelect = { onSelect(level) },
            )
            Spacer(Modifier.height(12.dp))
        }
    }
}

@Composable
private fun EnforcementCard(
    level: EnforcementLevel,
    isSelected: Boolean,
    onSelect: () -> Unit,
) {
    Card(
        onClick = onSelect,
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) {
                MaterialTheme.colorScheme.primaryContainer
            } else {
                MaterialTheme.colorScheme.surface
            },
        ),
        border = CardDefaults.outlinedCardBorder().takeIf { isSelected }?.let {
            CardDefaults.outlinedCardBorder().copy(
                brush = androidx.compose.ui.graphics.SolidColor(MaterialTheme.colorScheme.primary),
            )
        },
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = when (level) {
                        EnforcementLevel.NORMAL -> Icons.Default.Visibility
                        EnforcementLevel.FOCUS -> Icons.Default.PictureInPicture
                        EnforcementLevel.STRICT -> Icons.Default.Security
                        EnforcementLevel.IRON -> Icons.Default.Lock
                    },
                    contentDescription = null,
                    tint = if (isSelected) {
                        MaterialTheme.colorScheme.onPrimaryContainer
                    } else {
                        MaterialTheme.colorScheme.onSurface
                    },
                )
                Spacer(Modifier.width(12.dp))
                Text(
                    text = level.displayName,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = if (isSelected) {
                        MaterialTheme.colorScheme.onPrimaryContainer
                    } else {
                        MaterialTheme.colorScheme.onSurface
                    },
                )
            }
            Spacer(Modifier.height(8.dp))
            Text(
                text = level.description,
                style = MaterialTheme.typography.bodySmall,
                color = if (isSelected) {
                    MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.8f)
                } else {
                    MaterialTheme.colorScheme.onSurfaceVariant
                },
            )
        }
    }
}

@Composable
private fun StepPermissions(
    context: Context,
    capabilities: DeviceCapabilitiesReport?,
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text(
            text = "Device Permissions",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground,
        )

        Spacer(Modifier.height(8.dp))

        Text(
            text = "Strict Day needs certain permissions to enforce your schedule. " +
                "Tap each to open system settings. No permissions are requested silently.",
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Spacer(Modifier.height(24.dp))

        val caps = capabilities
        if (caps == null) {
            CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
            return
        }

        PermissionRow(
            label = "Usage Access",
            description = "Required to monitor which apps are open and enforce blocking.",
            isGranted = caps.canUseUsageStats != DeviceCapabilitiesReport.NOT_AVAILABLE,
            statusText = mapCapabilityStatus(caps.canUseUsageStats),
            onClick = {
                context.startActivity(
                    Intent(AndroidSettings.ACTION_USAGE_ACCESS_SETTINGS),
                )
            },
        )

        Spacer(Modifier.height(12.dp))

        PermissionRow(
            label = "Notification Access",
            description = "Allows silencing notifications during focused time blocks.",
            isGranted = caps.canControlNotifications != DeviceCapabilitiesReport.NOT_AVAILABLE,
            statusText = mapCapabilityStatus(caps.canControlNotifications),
            onClick = {
                context.startActivity(
                    Intent(AndroidSettings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS),
                )
            },
        )

        Spacer(Modifier.height(12.dp))

        PermissionRow(
            label = "Display Over Other Apps",
            description = "Needed to show blocking overlays on restricted apps.",
            isGranted = caps.canRestrictApps != DeviceCapabilitiesReport.NOT_AVAILABLE,
            statusText = mapCapabilityStatus(caps.canRestrictApps),
            onClick = {
                context.startActivity(
                    Intent(
                        AndroidSettings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        android.net.Uri.parse("package:${context.packageName}"),
                    ),
                )
            },
        )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            Spacer(Modifier.height(12.dp))

            PermissionRow(
                label = "Usage Stats",
                description = "Provides app usage data for accurate tracking.",
                isGranted = caps.canRestrictApps != DeviceCapabilitiesReport.NOT_AVAILABLE,
                statusText = mapCapabilityStatus(caps.canUseUsageStats),
                onClick = {
                    context.startActivity(
                        Intent(AndroidSettings.ACTION_USAGE_ACCESS_SETTINGS),
                    )
                },
            )
        }
    }
}

@Composable
private fun PermissionRow(
    label: String,
    description: String,
    isGranted: Boolean,
    statusText: String,
    onClick: () -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (isGranted) {
                MaterialTheme.colorScheme.surfaceVariant
            } else {
                MaterialTheme.colorScheme.surface
            },
        ),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Text(
                    text = statusText,
                    style = MaterialTheme.typography.labelSmall,
                    color = if (isGranted) {
                        MaterialTheme.colorScheme.primary
                    } else {
                        MaterialTheme.colorScheme.error
                    },
                )
            }
            Spacer(Modifier.width(12.dp))
            OutlinedButton(onClick = onClick) {
                Icon(
                    Icons.Default.OpenInNew,
                    contentDescription = null,
                    modifier = Modifier.size(16.dp),
                )
                Spacer(Modifier.width(4.dp))
                Text("Open Settings")
            }
        }
    }
}

@Composable
private fun StepIntegrations() {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text(
            text = "Connect Integrations",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground,
        )

        Spacer(Modifier.height(8.dp))

        Text(
            text = "Optionally connect services to sync your tasks. " +
                "You can set these up later in Settings.",
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Spacer(Modifier.height(24.dp))

        val integrations = listOf(
            "GitHub" to "Sync issues and pull requests",
            "Google Calendar" to "Import events as schedule blocks",
            "Google Docs" to "Read task lists from documents",
            "Notion" to "Pull tasks from databases",
            "Fitness" to "Track activity alongside focus blocks",
        )

        integrations.forEach { (name, description) ->
            IntegrationRow(
                name = name,
                description = description,
                isConnected = false,
            )
            Spacer(Modifier.height(12.dp))
        }
    }
}

@Composable
private fun IntegrationRow(
    name: String,
    description: String,
    isConnected: Boolean,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface,
        ),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = name,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Text(
                    text = if (isConnected) "Connected" else "Not connected",
                    style = MaterialTheme.typography.labelSmall,
                    color = if (isConnected) {
                        MaterialTheme.colorScheme.primary
                    } else {
                        MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
                    },
                )
            }
            OutlinedButton(onClick = { }) {
                Text(if (isConnected) "Disconnect" else "Connect")
            }
        }
    }
}

private fun mapCapabilityStatus(status: String): String = when (status) {
    DeviceCapabilitiesReport.SUPPORTED -> "Available"
    DeviceCapabilitiesReport.PARTIALLY_SUPPORTED -> "Partially available"
    DeviceCapabilitiesReport.REQUIRES_DEVICE_OWNER -> "Requires device owner"
    DeviceCapabilitiesReport.REQUIRES_USER_PERMISSION -> "Requires user permission"
    DeviceCapabilitiesReport.NOT_AVAILABLE -> "Not available on this device"
    else -> status
}

enum class EnforcementLevel(
    val displayName: String,
    val description: String,
) {
    NORMAL(
        displayName = "Normal",
        description = "Notifications and reminders only. No restrictions on app usage.",
    ),
    FOCUS(
        displayName = "Focus",
        description = "Blocks distracting apps during task windows. " +
            "Requires Usage Access permission.",
    ),
    STRICT(
        displayName = "Strict",
        description = "Enforces schedule with app blocking, notifications suppressed, " +
            "and requires verification. Requires Device Owner or root for full enforcement.",
    ),
    IRON(
        displayName = "Iron",
        description = "Maximum enforcement. Uses Lock Task mode, " +
            "cannot be bypassed without Device Owner provisioning. " +
            "Recommended for shared or managed devices.",
    ),
}

private fun Strictness.toEnforcementLevel(): EnforcementLevel? = when (this) {
    Strictness.NORMAL -> EnforcementLevel.NORMAL
    Strictness.FOCUS -> EnforcementLevel.FOCUS
    Strictness.STRICT -> EnforcementLevel.STRICT
    Strictness.IRON -> EnforcementLevel.IRON
}

private fun EnforcementLevel.toStrictness(): Strictness = when (this) {
    EnforcementLevel.NORMAL -> Strictness.NORMAL
    EnforcementLevel.FOCUS -> Strictness.FOCUS
    EnforcementLevel.STRICT -> Strictness.STRICT
    EnforcementLevel.IRON -> Strictness.IRON
}
