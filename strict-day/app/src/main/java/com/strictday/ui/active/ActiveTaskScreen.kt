package com.strictday.ui.active

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.strictday.domain.model.Strictness
import com.strictday.enforcement.DeviceCapabilitiesReport
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun ActiveTaskScreen(
    taskId: String?,
    onDone: () -> Unit,
    onNavigateToVerification: (String) -> Unit,
    viewModel: ActiveTaskViewModel = hiltViewModel()
) {
    val state by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(taskId) {
        viewModel.load(taskId)
    }

    LaunchedEffect(state.task) {
        viewModel.startTicker()
    }

    val task = state.task
    val strictnessColor = when (task?.strictness) {
        Strictness.IRON, Strictness.STRICT -> MaterialTheme.colorScheme.errorContainer
        Strictness.FOCUS -> MaterialTheme.colorScheme.tertiaryContainer
        Strictness.NORMAL, null -> MaterialTheme.colorScheme.surfaceVariant
    }
    val strictnessOnColor = when (task?.strictness) {
        Strictness.IRON, Strictness.STRICT -> MaterialTheme.colorScheme.onErrorContainer
        Strictness.FOCUS -> MaterialTheme.colorScheme.onTertiaryContainer
        Strictness.NORMAL, null -> MaterialTheme.colorScheme.onSurfaceVariant
    }
    val strictnessLabel = when (task?.strictness) {
        Strictness.IRON -> "IRON MODE"
        Strictness.STRICT -> "STRICT MODE"
        Strictness.FOCUS -> "FOCUS MODE"
        Strictness.NORMAL -> "NORMAL"
        null -> ""
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(strictnessLabel) },
                navigationIcon = {
                    IconButton(onClick = onDone) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = strictnessColor,
                    titleContentColor = strictnessOnColor,
                    navigationIconContentColor = strictnessOnColor
                )
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        if (state.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .verticalScroll(rememberScrollState())
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    "CURRENT TASK",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Spacer(Modifier.height(12.dp))

                Text(
                    task?.title ?: "Untitled",
                    style = MaterialTheme.typography.headlineLarge,
                    textAlign = TextAlign.Center
                )

                if (task != null) {
                    Spacer(Modifier.height(8.dp))
                    val tz = TimeZone.currentSystemDefault()
                    val startStr = task.startsAt.toLocalDateTime(tz).let {
                        String.format("%02d:%02d", it.hour, it.minute)
                    }
                    val endStr = task.endsAt.toLocalDateTime(tz).let {
                        String.format("%02d:%02d", it.hour, it.minute)
                    }
                    Text(
                        "$startStr \u2192 $endStr",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Spacer(Modifier.height(24.dp))

                Text(
                    fmtRemaining(state.remainingSeconds),
                    style = MaterialTheme.typography.displayMedium,
                    textAlign = TextAlign.Center
                )
                Text(
                    "remaining",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Spacer(Modifier.height(32.dp))

                val vs = state.verificationState
                if (vs != null && !vs.isVerified) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.surfaceVariant
                        )
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(
                                "Verification",
                                style = MaterialTheme.typography.titleSmall
                            )
                            Spacer(Modifier.height(4.dp))
                            Text(
                                "${vs.rulesMet}/${vs.rulesTotal} requirements met",
                                style = MaterialTheme.typography.bodyMedium
                            )
                            Spacer(Modifier.height(12.dp))
                            Button(
                                onClick = { onNavigateToVerification(vs.taskId) },
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text("VIEW VERIFICATION")
                            }
                        }
                    }
                    Spacer(Modifier.height(16.dp))
                }

                if (task != null) {
                    if (task.allowedApps.isNotEmpty()) {
                        Text(
                            "ALLOWED",
                            style = MaterialTheme.typography.labelLarge,
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(bottom = 4.dp)
                        )
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            task.allowedApps.forEach { pkg ->
                                FilterChip(
                                    selected = true,
                                    onClick = {},
                                    label = { Text(pkg) }
                                )
                            }
                        }
                        Spacer(Modifier.height(12.dp))
                    }

                    if (task.blockedApps.isNotEmpty()) {
                        Text(
                            "BLOCKED",
                            style = MaterialTheme.typography.labelLarge,
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(bottom = 4.dp)
                        )
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            task.blockedApps.forEach { pkg ->
                                FilterChip(
                                    selected = false,
                                    onClick = {},
                                    label = { Text(pkg) }
                                )
                            }
                        }
                        Spacer(Modifier.height(12.dp))
                    }
                }

                val caps = state.capabilities
                if (caps != null) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.surfaceVariant
                        )
                    ) {
                        Column(modifier = Modifier.padding(12.dp)) {
                            Text(
                                "Device Capabilities",
                                style = MaterialTheme.typography.labelMedium
                            )
                            Spacer(Modifier.height(4.dp))
                            CapabilityLine("App restriction", caps.canRestrictApps)
                            CapabilityLine("Usage stats", caps.canUseUsageStats)
                            CapabilityLine("Accessibility", caps.canUseAccessibility)
                            CapabilityLine("Device owner", caps.isDeviceOwner)
                            CapabilityLine("Lock task", caps.canUseLockTask)
                            CapabilityLine("Notifications", caps.canControlNotifications)
                        }
                    }
                    Spacer(Modifier.height(24.dp))
                }

                if (!state.isActive && task != null) {
                    Button(
                        onClick = { viewModel.activateEnforcement() },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("START ENFORCEMENT")
                    }
                    Spacer(Modifier.height(8.dp))
                }

                if (state.isActive && task != null && task.strictness != Strictness.IRON) {
                    Button(
                        onClick = { viewModel.activateEnforcement() },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("OPEN WORKSPACE")
                    }
                    Spacer(Modifier.height(8.dp))
                }

                TextButton(
                    onClick = {
                        viewModel.refreshVerification()
                    }
                ) {
                    Text("EMERGENCY OVERRIDE")
                }

                Spacer(Modifier.height(16.dp))
            }
        }
    }
}

@Composable
private fun CapabilityLine(label: String, status: String) {
    val color = when (status) {
        DeviceCapabilitiesReport.SUPPORTED -> MaterialTheme.colorScheme.primary
        DeviceCapabilitiesReport.PARTIALLY_SUPPORTED -> MaterialTheme.colorScheme.tertiary
        else -> MaterialTheme.colorScheme.error
    }
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 1.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(label, style = MaterialTheme.typography.bodySmall)
        Text(status, style = MaterialTheme.typography.bodySmall, color = color)
    }
}

private fun fmtRemaining(seconds: Long): String {
    val h = seconds / 3600
    val m = (seconds % 3600) / 60
    val s = seconds % 60
    return String.format("%02d:%02d:%02d", h, m, s)
}
