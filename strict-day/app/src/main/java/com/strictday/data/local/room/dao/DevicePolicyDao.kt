package com.strictday.data.local.room.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.strictday.data.local.room.entity.LocalDevicePolicy
import kotlinx.coroutines.flow.Flow

@Dao
interface DevicePolicyDao {
    @Query("SELECT * FROM device_policies WHERE taskId = :taskId AND status = 'active' LIMIT 1")
    fun getActivePolicyForTask(taskId: String): Flow<LocalDevicePolicy?>

    @Query("SELECT * FROM device_policies WHERE status = 'active' LIMIT 1")
    fun getActivePolicy(): Flow<LocalDevicePolicy?>

    @Query("SELECT * FROM device_policies WHERE userId = :userId ORDER BY activatedAt DESC")
    fun getAllPolicies(userId: String): Flow<List<LocalDevicePolicy>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(policy: LocalDevicePolicy)

    @Update
    suspend fun update(policy: LocalDevicePolicy)

    @Query("UPDATE device_policies SET status = :status, releasedAt = :releasedAt WHERE id = :policyId")
    suspend fun updatePolicyStatus(policyId: String, status: String, releasedAt: Long?)
}
