package com.strictday.data.remote.supabase

import com.strictday.domain.model.AuditEvent
import com.strictday.domain.model.Schedule
import com.strictday.domain.model.Task
import io.github.jan.supabase.SupabaseClient
import io.github.jan.supabase.postgrest.from
import io.github.jan.supabase.postgrest.postgrest
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import javax.inject.Inject
import javax.inject.Singleton

private val syncJson = Json { ignoreUnknownKeys = true }

@Serializable
data class ScheduleRow(
    @SerialName("id") val id: String,
    @SerialName("user_id") val userId: String,
    @SerialName("local_date") val localDate: String,
    @SerialName("status") val status: String,
    @SerialName("created_at") val createdAt: Long,
)

@Serializable
data class TaskRow(
    @SerialName("id") val id: String,
    @SerialName("schedule_id") val scheduleId: String,
    @SerialName("user_id") val userId: String,
    @SerialName("title") val title: String,
    @SerialName("description") val description: String,
    @SerialName("starts_at") val startsAt: Long,
    @SerialName("ends_at") val endsAt: Long,
    @SerialName("strictness") val strictness: String,
    @SerialName("status") val status: String,
    @SerialName("order_index") val orderIndex: Int,
    @SerialName("allowed_apps") val allowedAppsJson: String,
    @SerialName("blocked_apps") val blockedAppsJson: String,
    @SerialName("created_at") val createdAt: Long,
)

@Serializable
data class AuditEventRow(
    @SerialName("user_id") val userId: String,
    @SerialName("device_id") val deviceId: String,
    @SerialName("task_id") val taskId: String? = null,
    @SerialName("type") val type: String,
    @SerialName("payload") val payload: JsonElement,
)

/**
 * Minimal write-path for the Supabase backend.
 *
 * The client is null when the feature flag is off or the project is
 * unconfigured; every method then becomes a no-op returning false, so callers
 * do not need to branch themselves. All uploads are authenticated with the
 * token currently held in [SessionTokenStore]; with no token, RLS on the
 * server rejects the write, which is the correct honest behaviour until a real
 * session exists. Errors (network, permission, conflict) are swallowed and
 * reported as false - the sync worker decides whether to retry.
 */
@Singleton
class SupabaseSyncService @Inject constructor(
    private val client: SupabaseClient?,
) {

    val isAvailable: Boolean get() = client != null

    suspend fun pushSchedule(schedule: Schedule, userId: String): Boolean {
        if (!isAvailable) return false
        val row = ScheduleRow(
            id = schedule.id,
            userId = userId,
            localDate = schedule.localDate.toString(),
            status = schedule.status.name.lowercase(),
            createdAt = schedule.createdAt.toEpochMilliseconds(),
        )
        return runCatching {
            client!!.postgrest.from("schedules").upsert(row, onConflict = "id")
        }.isSuccess
    }

    suspend fun pushTasks(tasks: List<Task>, userId: String): Boolean {
        if (!isAvailable || tasks.isEmpty()) return false
        val rows = tasks.map { task ->
            TaskRow(
                id = task.id,
                scheduleId = task.scheduleId,
                userId = userId,
                title = task.title,
                description = task.description,
                startsAt = task.startsAt.toEpochMilliseconds(),
                endsAt = task.endsAt.toEpochMilliseconds(),
                strictness = task.strictness.name.lowercase(),
                status = task.status.name.lowercase(),
                orderIndex = task.orderIndex,
                allowedAppsJson = syncJson.encodeToString(task.allowedApps),
                blockedAppsJson = syncJson.encodeToString(task.blockedApps),
                createdAt = task.createdAt.toEpochMilliseconds(),
            )
        }
        return runCatching {
            client!!.postgrest.from("tasks").upsert(rows, onConflict = "id")
        }.isSuccess
    }

    suspend fun pushAuditEvent(event: AuditEvent): Boolean {
        if (!isAvailable) return false
        val payload: JsonElement = runCatching {
            syncJson.parseToJsonElement(syncJson.encodeToString(event.payload))
        }.getOrDefault(JsonObject(emptyMap()))
        val row = AuditEventRow(
            userId = event.userId,
            deviceId = event.deviceId,
            taskId = event.taskId,
            type = event.type.name.lowercase(),
            payload = payload,
        )
        return runCatching {
            client!!.postgrest.from("audit_events").insert(row)
        }.isSuccess
    }
}