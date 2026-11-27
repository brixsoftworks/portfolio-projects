package com.strictday.enforcement

import com.strictday.domain.model.DevicePolicyMode
import kotlinx.datetime.Instant
import kotlinx.serialization.KSerializer
import kotlinx.serialization.Serializable
import kotlinx.serialization.descriptors.PrimitiveKind
import kotlinx.serialization.descriptors.PrimitiveSerialDescriptor
import kotlinx.serialization.descriptors.SerialDescriptor
import kotlinx.serialization.encoding.Decoder
import kotlinx.serialization.encoding.Encoder

@Serializable
data class EnforcementPolicy(
    val mode: DevicePolicyMode,
    val taskId: String,
    val allowedPackages: List<String>,
    val blockedPackages: List<String>,
    @Serializable(with = InstantEpochMillisSerializer::class) val startTime: Instant,
    @Serializable(with = InstantEpochMillisSerializer::class) val endTime: Instant,
    val unlockCondition: String,
    val emergencyAccess: EmergencyAccess
)

@Serializable
data class EmergencyAccess(
    val alwaysAllowed: Boolean,
    val requiresConfirmation: Boolean,
    val disabledDuringIronMode: Boolean
)

object InstantEpochMillisSerializer : KSerializer<Instant> {
    override val descriptor: SerialDescriptor =
        PrimitiveSerialDescriptor("kotlinx.datetime.Instant", PrimitiveKind.LONG)

    override fun serialize(encoder: Encoder, value: Instant) {
        encoder.encodeLong(value.toEpochMilliseconds())
    }

    override fun deserialize(decoder: Decoder): Instant {
        return Instant.fromEpochMilliseconds(decoder.decodeLong())
    }
}