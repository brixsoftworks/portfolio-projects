package com.strictday.ui.task

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.MenuAnchorType
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.strictday.domain.model.Strictness
import com.strictday.domain.model.VerificationOperator
import com.strictday.domain.model.VerificationProvider

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TaskEditorScreen(
    taskId: String?,
    scheduleId: String = "",
    onDone: () -> Unit,
    viewModel: TaskEditorViewModel = hiltViewModel()
) {
    val state by viewModel.uiState.collectAsState()

    LaunchedEffect(taskId, scheduleId) {
        viewModel.load(taskId, scheduleId)
    }

    var allowedAppsText by remember(state.allowedApps) {
        mutableStateOf(state.allowedApps.joinToString(", "))
    }
    var blockedAppsText by remember(state.blockedApps) {
        mutableStateOf(state.blockedApps.joinToString(", "))
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(if (taskId == null) "Create Task" else "Edit Task") },
                navigationIcon = {
                    IconButton(onClick = onDone) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item { Spacer(Modifier.height(8.dp)) }

            item {
                OutlinedTextField(
                    value = state.title,
                    onValueChange = viewModel::onTitleChange,
                    label = { Text("Title") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
            }

            item {
                OutlinedTextField(
                    value = state.description,
                    onValueChange = viewModel::onDescriptionChange,
                    label = { Text("Description") },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 3,
                    maxLines = 6
                )
            }

            item {
                Text("Start Time", style = MaterialTheme.typography.titleSmall)
                Spacer(Modifier.height(4.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    TimeDropdown(
                        label = "Hour",
                        value = state.startHour,
                        values = (0..23).toList(),
                        onValueChange = viewModel::onStartHourChange,
                        modifier = Modifier.weight(1f)
                    )
                    TimeDropdown(
                        label = "Minute",
                        value = state.startMinute,
                        values = listOf(0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55),
                        onValueChange = viewModel::onStartMinuteChange,
                        modifier = Modifier.weight(1f)
                    )
                }
            }

            item {
                Text("Duration", style = MaterialTheme.typography.titleSmall)
                Slider(
                    value = state.durationMinutes.toFloat(),
                    onValueChange = { viewModel.onDurationChange(it.toLong()) },
                    valueRange = 15f..480f,
                    steps = 29,
                    modifier = Modifier.fillMaxWidth()
                )
                Text(
                    "${state.durationMinutes} minutes",
                    style = MaterialTheme.typography.bodyMedium
                )
            }

            item {
                Text("Strictness", style = MaterialTheme.typography.titleSmall)
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.padding(top = 4.dp)
                ) {
                    Strictness.entries.forEach { mode ->
                        FilterChip(
                            selected = state.strictness == mode,
                            onClick = { viewModel.onStrictnessChange(mode) },
                            label = { Text(mode.name.lowercase().replaceFirstChar { it.uppercase() }) }
                        )
                    }
                }
            }

            item {
                OutlinedTextField(
                    value = allowedAppsText,
                    onValueChange = { text ->
                        allowedAppsText = text
                        viewModel.onAllowedAppsChange(
                            text.split(",").map { it.trim() }.filter { it.isNotEmpty() }
                        )
                    },
                    label = { Text("Allowed Apps (comma-separated package names)") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
            }

            item {
                OutlinedTextField(
                    value = blockedAppsText,
                    onValueChange = { text ->
                        blockedAppsText = text
                        viewModel.onBlockedAppsChange(
                            text.split(",").map { it.trim() }.filter { it.isNotEmpty() }
                        )
                    },
                    label = { Text("Blocked Apps (comma-separated package names)") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
            }

            if (state.strictness == Strictness.STRICT || state.strictness == Strictness.IRON) {
                item {
                    Text("Verification", style = MaterialTheme.typography.titleSmall)
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.padding(top = 4.dp)
                    ) {
                        FilterChip(
                            selected = state.verificationProvider == null,
                            onClick = { viewModel.onVerificationProviderChange(null) },
                            label = { Text("None") }
                        )
                        VerificationProvider.entries.forEach { provider ->
                            FilterChip(
                                selected = state.verificationProvider == provider,
                                onClick = { viewModel.onVerificationProviderChange(provider) },
                                label = {
                                    Text(
                                        when (provider) {
                                            VerificationProvider.GITHUB -> "GitHub"
                                            VerificationProvider.GOOGLE_DOCS -> "Google Docs"
                                            VerificationProvider.NOTION -> "Notion"
                                            VerificationProvider.FITNESS -> "Fitness"
                                        }
                                    )
                                }
                            )
                        }
                    }
                }

                if (state.verificationProvider != null) {
                    item {
                        OutlinedTextField(
                            value = state.verificationEventType,
                            onValueChange = viewModel::onVerificationEventTypeChange,
                            label = { Text("Event Type") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true
                        )
                    }

                    item {
                        VerificationOperatorDropdown(
                            selected = state.verificationOperator,
                            onSelect = viewModel::onVerificationOperatorChange,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }

                    item {
                        OutlinedTextField(
                            value = state.verificationTarget,
                            onValueChange = viewModel::onVerificationTargetChange,
                            label = { Text("Target Value") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true
                        )
                    }

                    item {
                        Text("Min Count", style = MaterialTheme.typography.titleSmall)
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            modifier = Modifier.padding(top = 4.dp)
                        ) {
                            FilterChip(
                                selected = false,
                                onClick = {
                                    if (state.minCount > 1) viewModel.onMinCountChange(state.minCount - 1)
                                },
                                label = { Text("-") }
                            )
                            Text(
                                "${state.minCount}",
                                modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp),
                                style = MaterialTheme.typography.bodyLarge
                            )
                            FilterChip(
                                selected = false,
                                onClick = { viewModel.onMinCountChange(state.minCount + 1) },
                                label = { Text("+") }
                            )
                        }
                    }
                }
            }

            item {
                Button(
                    onClick = {
                        viewModel.save()
                        onDone()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = state.title.isNotBlank() && !state.isLoading
                ) {
                    Text("Save")
                }
            }

            item {
                Text(
                    "Restrictions depend on device permissions",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            item { Spacer(Modifier.height(16.dp)) }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun TimeDropdown(
    label: String,
    value: Int,
    values: List<Int>,
    onValueChange: (Int) -> Unit,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }

    ExposedDropdownMenuBox(
        expanded = expanded,
        onExpandedChange = { expanded = it },
        modifier = modifier
    ) {
        OutlinedTextField(
            value = String.format("%02d", value),
            onValueChange = {},
            readOnly = true,
            label = { Text(label) },
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded) },
            modifier = Modifier.menuAnchor(MenuAnchorType.PrimaryNotEditable)
        )
        ExposedDropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            values.forEach { option ->
                DropdownMenuItem(
                    text = { Text(String.format("%02d", option)) },
                    onClick = {
                        onValueChange(option)
                        expanded = false
                    }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun VerificationOperatorDropdown(
    selected: VerificationOperator,
    onSelect: (VerificationOperator) -> Unit,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }

    ExposedDropdownMenuBox(
        expanded = expanded,
        onExpandedChange = { expanded = it },
        modifier = modifier
    ) {
        OutlinedTextField(
            value = selected.name.lowercase().replace("_", " ").replaceFirstChar { it.uppercase() },
            onValueChange = {},
            readOnly = true,
            label = { Text("Operator") },
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded) },
            modifier = Modifier.menuAnchor(MenuAnchorType.PrimaryNotEditable)
        )
        ExposedDropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            VerificationOperator.entries.forEach { op ->
                DropdownMenuItem(
                    text = {
                        Text(op.name.lowercase().replace("_", " ").replaceFirstChar { it.uppercase() })
                    },
                    onClick = {
                        onSelect(op)
                        expanded = false
                    }
                )
            }
        }
    }
}
