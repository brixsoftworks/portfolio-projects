package com.strictday.data.repository

import com.strictday.data.local.room.dao.AuditEventDao
import com.strictday.data.local.room.mapper.toDomain
import com.strictday.data.local.room.mapper.toLocal
import com.strictday.domain.model.AuditEvent
import com.strictday.domain.repository.AuditRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuditRepositoryImpl @Inject constructor(
    private val auditEventDao: AuditEventDao
) : AuditRepository {

    override fun getRecentEvents(userId: String, limit: Int): Flow<List<AuditEvent>> {
        return auditEventDao.getRecentEvents(userId, limit).map { list -> list.map { it.toDomain() } }
    }

    override fun getEventsForTask(taskId: String): Flow<List<AuditEvent>> {
        return auditEventDao.getEventsForTask(taskId).map { list -> list.map { it.toDomain() } }
    }

    override suspend fun recordEvent(event: AuditEvent) {
        auditEventDao.insert(event.toLocal())
    }
}
