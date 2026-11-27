package com.strictday.enforcement

import android.content.Context
import android.content.pm.PackageManager
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AllowedAppResolver @Inject constructor(
    @ApplicationContext private val context: Context
) {
    fun resolveAllowedPackages(canonicalNames: List<String>): List<String> {
        val pm = context.packageManager
        return canonicalNames.mapNotNull { name ->
            val trimmed = name.trim()
            when {
                trimmed.matches(PACKAGE_PATTERN) -> trimmed
                else -> resolveCanonical(trimmed, pm)
            }
        }.distinct()
    }

    fun resolveCanonical(name: String, pm: PackageManager): String? {
        return when (name.lowercase()) {
            "chrome" -> "com.android.chrome"
            "instagram" -> "com.instagram.android"
            "youtube" -> "com.google.android.youtube"
            "twitter", "x" -> "com.twitter.android"
            "reddit" -> "com.reddit.frontpage"
            "whatsapp" -> "com.whatsapp"
            "telegram" -> "org.telegram.messenger"
            "gmail" -> "com.google.android.gm"
            "docs", "google docs" -> "com.google.android.apps.docs"
            "vscode", "code", "visual studio code" -> resolveCodeEditor(pm)
            else -> null
        }
    }

    private fun resolveCodeEditor(pm: PackageManager): String? {
        return try {
            pm.getInstalledApplications(0)
                .mapNotNull { app ->
                    val label = runCatching { pm.getApplicationLabel(app).toString() }.getOrNull() ?: ""
                    app.packageName to label
                }
                .firstOrNull { (pkg, label) ->
                    pkg.contains("vscode", ignoreCase = true) ||
                        label.contains("vscode", ignoreCase = true) ||
                        pkg.contains("jlerrich", ignoreCase = true) ||
                        label.contains("jlerrich", ignoreCase = true) ||
                        (
                            label.contains("code", ignoreCase = true) &&
                                (label.contains("editor", ignoreCase = true) || label.contains("server", ignoreCase = true))
                            )
                }?.first
        } catch (_: Exception) {
            null
        }
    }

    fun isPackageInstalled(packageName: String): Boolean {
        return try {
            context.packageManager.getPackageInfo(packageName, 0)
            true
        } catch (e: PackageManager.NameNotFoundException) {
            false
        }
    }

    private companion object {
        val PACKAGE_PATTERN = Regex("^[a-zA-Z][a-zA-Z0-9_]*(\\.[a-zA-Z0-9_]+)+$")
    }
}