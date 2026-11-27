package com.strictday.util

import kotlinx.datetime.Clock
import kotlinx.datetime.Instant
import kotlinx.datetime.LocalDateTime
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toInstant
import kotlinx.datetime.toLocalDateTime

object TimeUtils {
    fun formatRemaining(seconds: Long): String {
        val h = seconds / 3600
        val m = (seconds % 3600) / 60
        val s = seconds % 60
        return "%02d:%02d:%02d".format(h, m, s)
    }

    fun formatTime(instant: Instant, timeZone: TimeZone): String {
        val dt = instant.toLocalDateTime(timeZone)
        return "%02d:%02d".format(dt.hour, dt.minute)
    }

    fun formatDuration(minutes: Long): String {
        val h = minutes / 60
        val m = minutes % 60
        return when {
            h == 0L -> "${m}m"
            else -> "${h}h ${m}m"
        }
    }
}