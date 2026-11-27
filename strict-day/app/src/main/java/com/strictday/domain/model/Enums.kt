package com.strictday.domain.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
enum class Strictness {
    @SerialName("normal") NORMAL,
    @SerialName("focus") FOCUS,
    @SerialName("strict") STRICT,
    @SerialName("iron") IRON
}

@Serializable
enum class TaskStatus {
    @SerialName("pending") PENDING,
    @SerialName("active") ACTIVE,
    @SerialName("verification_pending") VERIFICATION_PENDING,
    @SerialName("verified") VERIFIED,
    @SerialName("skipped") SKIPPED,
    @SerialName("failed") FAILED,
    @SerialName("overridden") OVERRIDDEN
}

@Serializable
enum class ScheduleStatus {
    @SerialName("draft") DRAFT,
    @SerialName("locked") LOCKED,
    @SerialName("active") ACTIVE,
    @SerialName("completed") COMPLETED
}

@Serializable
enum class VerificationProvider {
    @SerialName("github") GITHUB,
    @SerialName("google_docs") GOOGLE_DOCS,
    @SerialName("notion") NOTION,
    @SerialName("fitness") FITNESS
}

@Serializable
enum class VerificationOperator {
    @SerialName("equals") EQUALS,
    @SerialName("contains") CONTAINS,
    @SerialName("greater_than") GREATER_THAN,
    @SerialName("less_than") LESS_THAN,
    @SerialName("count") COUNT,
    @SerialName("duration") DURATION,
    @SerialName("exists") EXISTS,
    @SerialName("within_time_window") WITHIN_TIME_WINDOW
}

@Serializable
enum class DevicePolicyMode {
    @SerialName("none") NONE,
    @SerialName("normal") NORMAL,
    @SerialName("focus") FOCUS,
    @SerialName("strict") STRICT,
    @SerialName("iron") IRON
}

@Serializable
enum class DevicePolicyStatus {
    @SerialName("inactive") INACTIVE,
    @SerialName("active") ACTIVE,
    @SerialName("released") RELEASED,
    @SerialName("failed") FAILED
}

@Serializable
enum class AuditEventType {
    @SerialName("policy_activated") POLICY_ACTIVATED,
    @SerialName("policy_released") POLICY_RELEASED,
    @SerialName("task_started") TASK_STARTED,
    @SerialName("task_completed") TASK_COMPLETED,
    @SerialName("task_failed") TASK_FAILED,
    @SerialName("override_used") OVERRIDE_USED,
    @SerialName("verification_attempted") VERIFICATION_ATTEMPTED,
    @SerialName("verification_passed") VERIFICATION_PASSED,
    @SerialName("verification_failed") VERIFICATION_FAILED,
    @SerialName("schedule_locked") SCHEDULE_LOCKED,
    @SerialName("schedule_completed") SCHEDULE_COMPLETED
}

@Serializable
enum class IntegrationStatus {
    @SerialName("connected") CONNECTED,
    @SerialName("disconnected") DISCONNECTED,
    @SerialName("error") ERROR,
    @SerialName("expired") EXPIRED
}

@Serializable
enum class CapabilityStatus {
    @SerialName("supported") SUPPORTED,
    @SerialName("partially_supported") PARTIALLY_SUPPORTED,
    @SerialName("requires_device_owner") REQUIRES_DEVICE_OWNER,
    @SerialName("requires_user_permission") REQUIRES_USER_PERMISSION,
    @SerialName("not_available") NOT_AVAILABLE
}
