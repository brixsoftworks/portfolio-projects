package com.strictday.data.local.room.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.strictday.data.local.room.entity.LocalIntegration
import kotlinx.coroutines.flow.Flow

@Dao
interface IntegrationDao {
    @Query("SELECT * FROM integrations WHERE userId = :userId")
    fun getIntegrations(userId: String): Flow<List<LocalIntegration>>

    @Query("SELECT * FROM integrations WHERE userId = :userId AND provider = :provider LIMIT 1")
    fun getIntegrationByProvider(userId: String, provider: String): Flow<LocalIntegration?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(integration: LocalIntegration)

    @Update
    suspend fun update(integration: LocalIntegration)

    @Query("DELETE FROM integrations WHERE id = :id")
    suspend fun deleteById(id: String)
}
