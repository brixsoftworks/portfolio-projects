# Add project specific ProGuard rules here.
-keepattributes *Annotation*
-keep class com.strictday.data.local.room.entity.** { *; }
-keep class com.strictday.domain.model.** { *; }
-dontwarn kotlinx.serialization.**
-keepclassmembers class kotlinx.serialization.json.** { *** Companion; }
-keepclasseswithmembers class com.strictday.** { kotlinx.serialization.KSerializer serializer(...); }
