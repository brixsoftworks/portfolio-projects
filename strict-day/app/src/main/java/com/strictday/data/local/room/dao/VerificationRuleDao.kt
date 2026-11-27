package com.strictday.data.local.room.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.strictday.data.local.room.entity.LocalVerificationRule
import kotlinx.coroutines.flow.Flow

@Dao
interface VerificationRuleDao {
    @Query("SELECT * FROM verification_rules WHERE taskId = :taskId")
    fun getRulesForTask(taskId: String): Flow<List<LocalVerificationRule>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(rule: LocalVerificationRule)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(rules: List<LocalVerificationRule>)

    @Delete
    suspend fun delete(rule: LocalVerificationRule)

    @Query("DELETE FROM verification_rules WHERE taskId = :taskId")
    suspend fun deleteAllForTask(taskId: String)
}
