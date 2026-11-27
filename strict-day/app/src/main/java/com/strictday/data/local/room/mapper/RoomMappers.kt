package com.strictday.data.local.room.mapper

import com.strictday.data.local.room.entity.*
import com.strictday.domain.model.*
import kotlinx.datetime.Instant
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

private val json = Json { ignoreUnknownKeys = true }

fun LocalSchedule.toDomain(): Schedule = Schedule(
    id = id,
    userId = userId,
    localDate = kotlinx.datetime.LocalDate.parse(localDate),
    status = ScheduleStatus.valueOf(status),
    createdAt = Instant.fromEpochMilliseconds(createdAt)
)

fun Schedule.toLocal(): LocalSchedule = LocalSchedule(
    id = id,
    userId = userId,
    localDate = localDate.toString(),
    status = status.name,
    createdAt = createdAt.toEpochMilliseconds()
)

fun LocalTask.toDomain(): Task = Task(
    id = id,
    scheduleId = scheduleId,
    title = title,
    description = description,
    startsAt = Instant.fromEpochMilliseconds(startsAt),
    endsAt = Instant.fromEpochMilliseconds(endsAt),
    strictness = Strictness.valueOf(strictness),
    status = TaskStatus.valueOf(status),
    orderIndex = orderIndex,
    allowedApps = json.decodeFromString<List<String>>(allowedApps),
    blockedApps = json.decodeFromString<List<String>>(blockedApps),
    createdAt = Instant.fromEpochMilliseconds(createdAt)
)

fun Task.toLocal(): LocalTask = LocalTask(
    id = id,
    scheduleId = scheduleId,
    title = title,
    description = description,
    startsAt = startsAt.toEpochMilliseconds(),
    endsAt = endsAt.toEpochMilliseconds(),
    strictness = strictness.name,
    status = status.name,
    orderIndex = orderIndex,
    allowedApps = json.encodeToString(allowedApps),
    blockedApps = json.encodeToString(blockedApps),
    createdAt = createdAt.toEpochMilliseconds()
)

fun LocalVerificationRule.toDomain(): VerificationRule = VerificationRule(
    id = id,
    taskId = taskId,
    provider = VerificationProvider.valueOf(provider),
    eventType = eventType,
    operator = VerificationOperator.valueOf(operator),
    targetValue = targetValue,
    minCount = minCount,
    minDurationSeconds = minDurationSeconds,
    createdAt = Instant.fromEpochMilliseconds(createdAt)
)

fun VerificationRule.toLocal(): LocalVerificationRule = LocalVerificationRule(
    id = id,
    taskId = taskId,
    provider = provider.name,
    eventType = eventType,
    operator = operator.name,
    targetValue = targetValue,
    minCount = minCount,
    minDurationSeconds = minDurationSeconds,
    createdAt = createdAt.toEpochMilliseconds()
)

fun LocalDevicePolicy.toDomain(): DevicePolicy = DevicePolicy(
    id = id,
    userId = userId,
    taskId = taskId,
    deviceId = deviceId,
    mode = DevicePolicyMode.valueOf(mode),
    allowedPackages = json.decodeFromString<List<String>>(allowedPackages),
    blockedPackages = json.decodeFromString<List<String>>(blockedPackages),
    status = DevicePolicyStatus.valueOf(status),
    startTime = Instant.fromEpochMilliseconds(startTime),
    endTime = Instant.fromEpochMilliseconds(endTime),
    unlockCondition = unlockCondition,
    emergencyAccessAllowed = emergencyAccessAllowed,
    activatedAt = activatedAt?.let { Instant.fromEpochMilliseconds(it) },
    releasedAt = releasedAt?.let { Instant.fromEpochMilliseconds(it) }
)

fun DevicePolicy.toLocal(): LocalDevicePolicy = LocalDevicePolicy(
    id = id,
    userId = userId,
    taskId = taskId,
    deviceId = deviceId,
    mode = mode.name,
    allowedPackages = json.encodeToString(allowedPackages),
    blockedPackages = json.encodeToString(blockedPackages),
    status = status.name,
    startTime = startTime.toEpochMilliseconds(),
    endTime = endTime.toEpochMilliseconds(),
    unlockCondition = unlockCondition,
    emergencyAccessAllowed = emergencyAccessAllowed,
    activatedAt = activatedAt?.toEpochMilliseconds(),
    releasedAt = releasedAt?.toEpochMilliseconds()
)

fun LocalAuditEvent.toDomain(): AuditEvent = AuditEvent(
    id = id,
    userId = userId,
    deviceId = deviceId,
    taskId = taskId,
    type = AuditEventType.valueOf(type),
    payload = json.decodeFromString<Map<String, Any>>(payload),
    createdAt = Instant.fromEpochMilliseconds(createdAt)
)

fun AuditEvent.toLocal(): LocalAuditEvent = LocalAuditEvent(
    id = id,
    userId = userId,
    deviceId = deviceId,
    taskId = taskId,
    type = type.name,
    payload = json.encodeToString(payload),
    createdAt = createdAt.toEpochMilliseconds()
)

fun LocalIntegration.toDomain(): Integration = Integration(
    id = id,
    userId = userId,
    provider = VerificationProvider.valueOf(provider),
    status = IntegrationStatus.valueOf(status),
    scopes = json.decodeFromString<List<String>>(scopes),
    metadata = json.decodeFromString<Map<String, String>>(metadataJson),
    createdAt = Instant.fromEpochMilliseconds(createdAt)
)

fun Integration.toLocal(): LocalIntegration = LocalIntegration(
    id = id,
    userId = userId,
    provider = provider.name,
    status = status.name,
    scopes = json.encodeToString(scopes),
    metadataJson = json.encodeToString(metadata),
    createdAt = createdAt.toEpochMilliseconds()
)
