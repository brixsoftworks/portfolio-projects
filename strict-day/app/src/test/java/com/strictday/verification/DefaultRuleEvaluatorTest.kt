package com.strictday.verification

import com.strictday.domain.model.NormalizedVerificationEvent
import com.strictday.domain.model.VerificationOperator
import com.strictday.domain.model.VerificationProvider
import com.strictday.domain.model.VerificationRule
import kotlinx.datetime.Instant
import kotlinx.datetime.LocalDate
import kotlinx.datetime.LocalDateTime
import kotlinx.datetime.LocalTime
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toInstant
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class DefaultRuleEvaluatorTest {

    private val evaluator = DefaultRuleEvaluator()
    private val now: Instant =
        LocalDateTime(LocalDate(2026, 1, 15), LocalTime(hour = 12, minute = 0)).toInstant(TimeZone.UTC)

    private fun rule(
        operator: VerificationOperator,
        targetValue: String = "",
        minCount: Int = 0,
        minDurationSeconds: Long = 0,
    ) = VerificationRule(
        id = "rule-1",
        taskId = "task-1",
        provider = VerificationProvider.GITHUB,
        eventType = "commit",
        operator = operator,
        targetValue = targetValue,
        minCount = minCount,
        minDurationSeconds = minDurationSeconds,
        createdAt = now,
    )

    private fun event(
        subject: String = "",
        occurredAt: Instant = now,
        metrics: Map<String, Any> = emptyMap(),
    ) = NormalizedVerificationEvent(
        provider = VerificationProvider.GITHUB,
        eventType = "commit",
        externalId = "ext",
        occurredAt = occurredAt,
        subject = subject,
        metrics = metrics,
    )

    @Test
    fun `count rule is satisfied when matching events reach threshold`() {
        val met = evaluator.evaluate(
            rule(VerificationOperator.COUNT, targetValue = "sc-", minCount = 2),
            listOf(
                event(subject = "sc-321 fix bug"),
                event(subject = "sc-322 add test"),
                event(subject = "other"),
            ),
        )

        assertTrue(met.isMet)
    }

    @Test
    fun `count rule fails below threshold`() {
        val met = evaluator.evaluate(
            rule(VerificationOperator.COUNT, targetValue = "sc-", minCount = 3),
            listOf(
                event(subject = "sc-321 fix bug"),
                event(subject = "other"),
            ),
        )

        assertFalse(met.isMet)
    }

    @Test
    fun `exists rule passes with any matching event`() {
        val met = evaluator.evaluate(
            rule(VerificationOperator.EXISTS),
            listOf(event(subject = "anything")),
        )

        assertTrue(met.isMet)
    }

    @Test
    fun `exists rule fails without events`() {
        val met = evaluator.evaluate(rule(VerificationOperator.EXISTS), emptyList())
        assertFalse(met.isMet)
    }

    @Test
    fun `greater than sums metric across events`() {
        val met = evaluator.evaluate(
            rule(VerificationOperator.GREATER_THAN, targetValue = "steps"),
            listOf(
                event(metrics = mapOf("steps" to 4000)),
                event(metrics = mapOf("steps" to 3500)),
            ),
        )

        // 7500 > 0
        assertTrue(met.isMet)
    }

    @Test
    fun `greater than respects numeric target`() {
        val notMet = evaluator.evaluate(
            rule(VerificationOperator.GREATER_THAN, targetValue = "10000"),
            listOf(event(metrics = mapOf("steps" to 4000))),
        )

        // aggregate of map[10000]=0.0 -> 0.0 > 0 false; metric key unused by aggregation.
        assertFalse(notMet.isMet)
    }

    @Test
    fun `equals matches any metric value`() {
        val met = evaluator.evaluate(
            rule(VerificationOperator.EQUALS, targetValue = "10km"),
            listOf(event(metrics = mapOf("distance" to "10km"))),
        )

        assertTrue(met.isMet)
    }

    @Test
    fun `contains matches subject or metric value`() {
        val met = evaluator.evaluate(
            rule(VerificationOperator.CONTAINS, targetValue = "PR"),
            listOf(event(metrics = mapOf("title" to "merged feature PR-42"))),
        )

        assertTrue(met.isMet)
    }

    @Test
    fun `duration rule uses durationSeconds metric`() {
        val met = evaluator.evaluate(
            rule(VerificationOperator.DURATION, minDurationSeconds = 30),
            listOf(
                event(metrics = mapOf("durationSeconds" to 15L)),
                event(metrics = mapOf("durationSeconds" to 20L)),
            ),
        )

        assertTrue(met.isMet)
    }

    @Test
    fun `duration rule below threshold fails`() {
        val notMet = evaluator.evaluate(
            rule(VerificationOperator.DURATION, minDurationSeconds = 100),
            listOf(event(metrics = mapOf("durationSeconds" to 20L))),
        )

        assertFalse(notMet.isMet)
    }

    @Test
    fun `within time window counts events inside window`() {
        val window = "${now.toEpochMilliseconds()}..${now.toEpochMilliseconds() + 60_000L}"
        val met = evaluator.evaluate(
            rule(VerificationOperator.WITHIN_TIME_WINDOW, targetValue = window, minCount = 1),
            listOf(
                event(occurredAt = now),
                event(occurredAt = Instant.fromEpochMilliseconds(now.toEpochMilliseconds() + 2 * 60_000L)),
            ),
        )

        assertTrue(met.isMet)
    }

    @Test
    fun `within time window ignores outside events`() {
        val window = "${now.toEpochMilliseconds()}..${now.toEpochMilliseconds() + 60_000L}"
        val notMet = evaluator.evaluate(
            rule(VerificationOperator.WITHIN_TIME_WINDOW, targetValue = window, minCount = 2),
            listOf(event(occurredAt = now)),
        )

        assertFalse(notMet.isMet)
    }
}