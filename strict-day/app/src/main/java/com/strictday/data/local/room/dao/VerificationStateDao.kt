package com.strictday.data.local.room.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.strictday.data.local.room.entity.LocalVerificationState
import kotlinx.coroutines.flow.Flow

@Dao
interface VerificationStateDao {
    @Query("SELECT * FROM verification_state WHERE taskId = :taskId")
    fun getVerificationState(taskId: String): Flow<LocalVerificationState?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(state: LocalVerificationState)

    @Update
    suspend fun update(state: LocalVerificationState)
}
