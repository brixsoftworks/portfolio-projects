package com.strictday.verification

import com.strictday.domain.model.NormalizedVerificationEvent
import com.strictday.domain.model.VerificationOperator
import com.strictday.domain.model.VerificationRule
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DefaultRuleEvaluator @Inject constructor() : VerificationRuleEvaluator {

    override fun evaluate(rule: VerificationRule, events: List<NormalizedVerificationEvent>): RuleEvaluation {
        val matching = events.filter { it.eventType.equals(rule.eventType, ignoreCase = true) }

        val isMet = when (rule.operator) {
            VerificationOperator.COUNT -> matching.count { eventMatches(rule, it) } >= rule.minCount
            VerificationOperator.EXISTS -> matching.isNotEmpty()
            VerificationOperator.GREATER_THAN -> aggregateMetric(rule, matching) > rule.targetValue.toDoubleOrNull() ?: 0.0
            VerificationOperator.LESS_THAN -> aggregateMetric(rule, matching) < rule.targetValue.toDoubleOrNull() ?: 0.0
            VerificationOperator.EQUALS -> matching.any { eventEquals(rule, it) }
            VerificationOperator.CONTAINS -> matching.any { eventContains(rule, it) }
            VerificationOperator.DURATION -> matching.sumOf { extractDurationSeconds(it) } >= rule.minDurationSeconds
            VerificationOperator.WITHIN_TIME_WINDOW -> matching.count { eventWithinWindow(rule, it) } >= rule.minCount
        }

        return RuleEvaluation(rule = rule, isMet = isMet)
    }

    private fun eventMatches(rule: VerificationRule, event: NormalizedVerificationEvent): Boolean {
        return event.subject.contains(rule.targetValue, ignoreCase = true)
    }

    private fun aggregateMetric(rule: VerificationRule, events: List<NormalizedVerificationEvent>): Double {
        return events.sumOf { event ->
            event.metrics[rule.targetValue]?.let {
                when (it) {
                    is Long -> it.toDouble()
                    is Int -> it.toDouble()
                    is Double -> it
                    is Float -> it.toDouble()
                    else -> 0.0
                }
            } ?: 0.0
        }
    }

    private fun extractDurationSeconds(event: NormalizedVerificationEvent): Long {
        return when (val v = event.metrics["durationSeconds"]) {
            is Long -> v
            is Int -> v.toLong()
            is Double -> v.toLong()
            is Float -> v.toLong()
            else -> 0L
        }
    }

    private fun eventEquals(rule: VerificationRule, event: NormalizedVerificationEvent): Boolean {
        return event.metrics.values.any { value ->
            value.toString().equals(rule.targetValue, ignoreCase = true)
        }
    }

    private fun eventContains(rule: VerificationRule, event: NormalizedVerificationEvent): Boolean {
        if (event.subject.contains(rule.targetValue, ignoreCase = true)) return true
        return event.metrics.values.any { value ->
            value.toString().contains(rule.targetValue, ignoreCase = true)
        }
    }

    private fun eventWithinWindow(rule: VerificationRule, event: NormalizedVerificationEvent): Boolean {
        return rule.targetValue.split("..").let { parts ->
            if (parts.size == 2) {
                val start = parts[0].toLongOrNull()
                val end = parts[1].toLongOrNull()
                if (start != null && end != null) {
                    event.occurredAt.toEpochMilliseconds() in start..end
                } else false
            } else false
        }
    }
}
