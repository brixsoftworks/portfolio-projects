package com.strictday.verification

import com.strictday.domain.model.NormalizedVerificationEvent

interface VerificationEventNormalizer {
    fun normalize(rawEvent: Map<String, Any>): NormalizedVerificationEvent
    fun normalizeAll(rawEvents: List<Map<String, Any>>): List<NormalizedVerificationEvent>
}
