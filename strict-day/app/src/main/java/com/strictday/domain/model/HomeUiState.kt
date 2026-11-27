package com.strictday.domain.model

data class HomeUiState(
    val currentTask: Task? = null,
    val nextTask: Task? = null,
    val remainingSeconds: Long = 0,
    val verificationProgress: VerificationProgress = VerificationProgress(),
    val todayScore: Float = 0f,
    val tasksCompleted: Int = 0,
    val tasksTotal: Int = 0,
    val isLoading: Boolean = true
)

data class VerificationProgress(
    val provider: VerificationProvider? = null,
    val requirements: List<VerificationRequirement> = emptyList(),
    val isVerified: Boolean = false
)

data class VerificationRequirement(
    val description: String,
    val isMet: Boolean
)
