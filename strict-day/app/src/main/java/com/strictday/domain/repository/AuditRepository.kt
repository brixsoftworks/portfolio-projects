package com.strictday.domain.repository

import com.strictday.domain.model.AuditEvent
import kotlinx.coroutines.flow.Flow

interface AuditRepository {
    fun getRecentEvents(userId: String, limit: Int = 100): Flow<List<AuditEvent>>
    fun getEventsForTask(taskId: String): Flow<List<AuditEvent>>
    suspend fun recordEvent(event: AuditEvent)
}
