package com.strictday.data.local.room.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.strictday.data.local.room.entity.LocalAuditEvent
import kotlinx.coroutines.flow.Flow

@Dao
interface AuditEventDao {
    @Query("SELECT * FROM audit_events WHERE userId = :userId ORDER BY createdAt DESC LIMIT :limit")
    fun getRecentEvents(userId: String, limit: Int = 100): Flow<List<LocalAuditEvent>>

    @Query("SELECT * FROM audit_events WHERE taskId = :taskId ORDER BY createdAt DESC")
    fun getEventsForTask(taskId: String): Flow<List<LocalAuditEvent>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(event: LocalAuditEvent)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(events: List<LocalAuditEvent>)
}
