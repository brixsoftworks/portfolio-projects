package com.strictday.util

import java.util.UUID

object IdGenerator {
    fun newUuid(): String = UUID.randomUUID().toString()
}