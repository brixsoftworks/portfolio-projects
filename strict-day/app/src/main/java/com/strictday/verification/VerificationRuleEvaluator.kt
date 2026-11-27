package com.strictday.verification

import com.strictday.domain.model.NormalizedVerificationEvent
import com.strictday.domain.model.VerificationRule

interface VerificationRuleEvaluator {
    fun evaluate(rule: VerificationRule, events: List<NormalizedVerificationEvent>): RuleEvaluation
}

data class RuleEvaluation(
    val rule: VerificationRule,
    val isMet: Boolean
)
